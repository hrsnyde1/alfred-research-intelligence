"""Local job working storage, deliberately not authoritative Alfred Memory."""
from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3
import time
import uuid


class JobStore:
    def __init__(self, root='data/research-v1'):
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.database = self.root / 'jobs.sqlite3'
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS metadata(version INTEGER NOT NULL);
                INSERT INTO metadata SELECT 1 WHERE NOT EXISTS(SELECT 1 FROM metadata);
                CREATE TABLE IF NOT EXISTS jobs(
                  id TEXT PRIMARY KEY, request_key TEXT UNIQUE, request TEXT NOT NULL,
                  status TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                  error TEXT, report_path TEXT);
                CREATE TABLE IF NOT EXISTS artifacts(
                  job_id TEXT NOT NULL REFERENCES jobs(id), name TEXT NOT NULL, body TEXT NOT NULL,
                  PRIMARY KEY(job_id,name));
                CREATE TABLE IF NOT EXISTS events(
                  sequence INTEGER PRIMARY KEY, job_id TEXT NOT NULL REFERENCES jobs(id),
                  status TEXT NOT NULL, observed_at TEXT NOT NULL, detail TEXT NOT NULL);
            ''')
            if db.execute('SELECT version FROM metadata').fetchall() != [(1,)]:
                raise ValueError('Unsupported local Research schema')
        self.database.chmod(0o600)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.database, timeout=10)
        db.execute('PRAGMA foreign_keys=ON')
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def now():
        return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

    def submit(self, request, request_key=None):
        body = json.dumps(request, sort_keys=True, ensure_ascii=False)
        job_id, now = 'research-' + uuid.uuid4().hex, self.now()
        with self.connect() as db:
            if request_key:
                old = db.execute('SELECT id,request FROM jobs WHERE request_key=?', (request_key,)).fetchone()
                if old:
                    if old[1] != body:
                        raise ValueError('Request key already used with different content')
                    return old[0]
            db.execute('INSERT INTO jobs VALUES(?,?,?,?,?,?,NULL,NULL)',
                       (job_id, request_key, body, 'queued', now, now))
            db.execute('INSERT INTO events(job_id,status,observed_at,detail) VALUES(?,?,?,?)',
                       (job_id, 'queued', now, 'Owner request accepted'))
        return job_id

    def claim(self, job_id):
        with self.connect() as db:
            changed = db.execute("UPDATE jobs SET status='collecting',updated_at=? WHERE id=? AND status='queued'",
                                 (self.now(), job_id)).rowcount
            if changed != 1:
                raise ValueError('Only queued jobs may run; concurrent/repeated execution denied')
            db.execute('INSERT INTO events(job_id,status,observed_at,detail) VALUES(?,?,?,?)',
                       (job_id, 'collecting', self.now(), 'Source acquisition started'))

    def update(self, job_id, status, detail='', report_path=None, error=None):
        with self.connect() as db:
            if db.execute('UPDATE jobs SET status=?,updated_at=?,error=?,report_path=COALESCE(?,report_path) WHERE id=?',
                          (status, self.now(), error, report_path, job_id)).rowcount != 1:
                raise KeyError('Unknown job')
            db.execute('INSERT INTO events(job_id,status,observed_at,detail) VALUES(?,?,?,?)',
                       (job_id, status, self.now(), detail))

    def put(self, job_id, name, value):
        with self.connect() as db:
            db.execute('INSERT INTO artifacts VALUES(?,?,?)', (job_id, name, json.dumps(value, ensure_ascii=False)))

    def get(self, job_id):
        with self.connect() as db:
            db.row_factory = sqlite3.Row
            row = db.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
            if row is None:
                raise KeyError('Unknown job')
            result = dict(row)
            result['request'] = json.loads(result['request'])
            result['artifacts'] = {r['name']: json.loads(r['body']) for r in db.execute('SELECT * FROM artifacts WHERE job_id=?', (job_id,))}
            result['events'] = [dict(r) for r in db.execute('SELECT status,observed_at,detail FROM events WHERE job_id=? ORDER BY sequence', (job_id,))]
            return result

    def by_request_key(self, request_key):
        with self.connect() as db:
            row = db.execute('SELECT id FROM jobs WHERE request_key=?', (request_key,)).fetchone()
        return row[0] if row else None

    def find_recent(self, request, since):
        """Newest job with an identical request created at or after ``since`` (UTC ISO)."""
        body = json.dumps(request, sort_keys=True, ensure_ascii=False)
        with self.connect() as db:
            row = db.execute('SELECT id FROM jobs WHERE request=? AND created_at>=? ORDER BY created_at DESC,id DESC LIMIT 1',
                             (body, since)).fetchone()
        return row[0] if row else None

    def list(self):
        with self.connect() as db:
            db.row_factory = sqlite3.Row
            return [dict(row) for row in db.execute('SELECT id,status,created_at,updated_at,error,report_path FROM jobs ORDER BY created_at DESC,id DESC LIMIT 100')]
