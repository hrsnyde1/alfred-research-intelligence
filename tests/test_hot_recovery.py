"""Hot rollback-journal regressions; all files and actors are synthetic."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from dataclasses import replace
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

import test_foundation as foundation
from alfred_research.contracts import ENVIRONMENTS
from alfred_research.registration import OfflineRegistrationAuthority
from alfred_research.persistence import (RecoveryRequiredError, RecoveryValidationError,
                                         UnsupportedSchemaError, open_database, register_database, validate_schema)


class HotRecoveryTests(foundation.FoundationFixture):
    def path(self, env='personal'):
        return Path(self.temp.name) / env / 'research.sqlite3'

    def raw_snapshot(self, path):
        # Do not open SQLite here: a writable reader could recover the journal.
        return {p.name: p.read_bytes() for p in path.parent.iterdir() if p.is_file()}

    def readonly_failure(self, path, env):
        with closing(sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True)) as db:
            with self.assertRaises(sqlite3.OperationalError) as raised:
                validate_schema(db, env)
        self.assertEqual(raised.exception.sqlite_errorname, 'SQLITE_READONLY_ROLLBACK')

    def assert_hot(self, path):
        journal = Path(str(path) + '-journal')
        self.assertTrue(journal.exists())
        self.assertEqual(journal.read_bytes()[:8].hex(), 'd9d505f920a163d7')

    def seed_history(self, env):
        self.provision(env)
        task = self.store.submit(self.ctx(env), replace(foundation.request(env), max_retries=10))
        for before, after in (('received', 'collecting'), ('collecting', 'researching')):
            task = self.store.transition(self.ctx(env), task.task_id, before, after)
        retry = self.store.retry(self.ctx(env), task.task_id, 'committed-retry')
        p1 = foundation.packet(env, task.task_id)
        self.store.put_packet(self.ctx(env), p1)
        d1 = self.decision(p1, 'NEEDS_MORE_RESEARCH')
        self.store.verify(self.ctx(env, 'verifier'), task.task_id, d1)
        p2 = replace(p1, packet_version=2, limitations=('second committed revision',))
        self.store.put_packet(self.ctx(env), p2)
        d2 = replace(self.decision(p2, 'NEEDS_MORE_RESEARCH'), decision_id='d2')
        self.store.verify(self.ctx(env, 'verifier'), task.task_id, d2)
        # Allow another packet without changing the committed retry receipt.
        task = self.store.transition(self.ctx(env), task.task_id, 'needs_more_research', 'researching')
        return task, retry, p1, p2, d1, d2

    def packet_crash(self, env, task_id):
        code = '''
from dataclasses import replace
from pathlib import Path
import os, sys, socket, json
def blocked(*args, **kwargs):
    raise AssertionError('network forbidden')
socket.socket = blocked
sys.path.insert(0, str(Path(sys.argv[4]).parent / 'src'))
from alfred_research.contracts import ModelAssignment
from alfred_research.tenancy import OfflineAuthority
from alfred_research.budgets import ModelConfiguration
from alfred_research.state import ResearchStore
from alfred_research.registration import OfflineRegistrationAuthority
env = sys.argv[3]
a = OfflineAuthority({env+'-researcher': (env,'researcher')})
c = a.context(env+'-researcher')
m = ModelConfiguration((ModelAssignment(environment=env,specialist='researcher',provider='synthetic',model='synthetic-researcher',price_units=2),))
registrations = OfflineRegistrationAuthority.from_test_snapshot(a,sys.argv[1],json.loads(sys.stdin.read()),test_only=True)
s = ResearchStore(sys.argv[1],a,m,budget_limits={env:20},registration_authority=registrations)
p = s.get_packet(c,sys.argv[2])
p = replace(p,packet_version=3,claims=tuple(replace(p.claims[0],claim_id='large-'+str(i),statement='x'*8000) for i in range(500)))
original = s._audit
def crash(db, context, operation, subject):
    original(db,context,operation,subject)
    # Include an uncommitted retry counter change in the same spilled transaction.
    task = s._task(db,context,p.task_id)
    s._save_task(db,replace(task,retries=task.retries+1))
    os._exit(29)
s._audit = crash
s.put_packet(c,p)
'''
        result = subprocess.run([sys.executable, '-c', code, self.temp.name, task_id, env,
                                 str(Path(__file__).parent.resolve())],
                                input=json.dumps(self.registrations.snapshot_for_tests()), text=True, check=False)
        self.assertEqual(result.returncode, 29)
        self.assert_hot(self.path(env))

    def raw_spill_crash(self, path, *, metadata_change=False):
        code = '''
import os, sqlite3, sys, socket
def blocked(*args, **kwargs):
    raise AssertionError('network forbidden')
socket.socket = blocked
with sqlite3.connect(sys.argv[1]) as db:
    db.execute('PRAGMA synchronous=FULL')
    db.execute('BEGIN IMMEDIATE')
    if sys.argv[2] == 'change':
        db.execute('UPDATE metadata SET version=2')
    for i in range(600):
        db.execute('INSERT INTO audit(body) VALUES (?)', ('uncommitted-'+str(i)+'x'*8000,))
    os._exit(30)
'''
        result = subprocess.run([sys.executable, '-c', code, str(path),
                                 'change' if metadata_change else 'unchanged'], check=False)
        self.assertEqual(result.returncode, 30)
        self.assert_hot(path)

    def test_large_packet_crash_reproduces_old_failure_then_recovers_all_committed_state(self):
        for env in ENVIRONMENTS:
            with self.subTest(env=env):
                task, retry, p1, p2, d1, d2 = self.seed_history(env)
                self.packet_crash(env, task.task_id)
                before = self.raw_snapshot(self.path(env))
                # This is the original failing opening sequence, still observable.
                self.readonly_failure(self.path(env), env)
                self.assertEqual(self.raw_snapshot(self.path(env)), before)
                recovered = self.reopen()
                self.assertEqual(recovered.get_task(self.ctx(env), task.task_id), task)
                self.assertFalse(Path(str(self.path(env)) + '-journal').exists())
                self.assertEqual(recovered.packet_history(self.ctx(env), task.task_id), (p1, p2))
                self.assertEqual(recovered.get_packet(self.ctx(env), task.task_id), p2)
                self.assertEqual(recovered.verification_history(self.ctx(env), task.task_id, 1), (d1,))
                self.assertEqual(recovered.verification_history(self.ctx(env), task.task_id, 2), (d2,))
                self.assertEqual(recovered.get_retry(self.ctx(env), task.task_id, 'committed-retry').result, retry)
                self.assertEqual(recovered.retry(self.ctx(env), task.task_id, 'committed-retry'), retry)
                self.assertEqual(recovered.get_task(self.ctx(env), task.task_id).retries, task.retries)
                operations = [e.operation for e in recovered.audit_history(self.ctx(env))]
                self.assertEqual(operations.count('packet.recorded'), 2)
                self.assertEqual(operations.count('task.retry'), 1)
                print(f'Hot recovery {env}: child exit 29; old preflight SQLITE_READONLY_ROLLBACK; '
                      'SQLite recovery succeeded; 2 committed revisions/verdicts and retry preserved')

    def test_concurrent_openers_share_sqlite_hot_journal_recovery(self):
        task, retry, p1, p2, d1, d2 = self.seed_history('personal')
        self.packet_crash('personal', task.task_id)
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: self.reopen().get_task(self.ctx(), task.task_id), range(8)))
        self.assertEqual(results, [task] * 8)
        self.assertFalse(Path(str(self.path()) + '-journal').exists())
        self.assertEqual(self.store.packet_history(self.ctx(), task.task_id), (p1, p2))
        self.assertEqual(self.store.verification_history(self.ctx(), task.task_id), (d1, d2))
        self.assertEqual(self.store.retry(self.ctx(), task.task_id, 'committed-retry'), retry)

    def test_new_database_and_clean_supported_reopen_register_identity_without_sql_mutation(self):
        task = self.advance()
        path = self.path()
        receipt = path.with_name(path.name + '.identity.json')
        self.assertTrue(receipt.exists())
        marker = json.loads(receipt.read_text())
        self.assertEqual(marker['identity']['environment'], 'personal')
        self.assertEqual(marker['identity']['schema_version'], 2)
        self.assertEqual(marker['identity']['inode'], path.stat().st_ino)
        before = self.raw_snapshot(path)
        with closing(open_database(path, 'personal', registration_authority=self.registrations, context=self.ctx())) as db:
            self.assertEqual(db.execute('SELECT version,environment FROM metadata').fetchall(), [(2, 'personal')])
        self.assertEqual(self.raw_snapshot(path), before)
        self.assertEqual(self.reopen().get_task(self.ctx(), task.task_id), task)

    def test_older_clean_v2_file_requires_explicit_director_registration(self):
        self.advance()
        path = self.path()
        receipt = path.with_name(path.name + '.identity.json')
        receipt.unlink()  # Simulate a compatible file created before identity receipts existed.
        before = path.read_bytes()
        with self.assertRaises(RecoveryRequiredError):
            open_database(path, 'personal', registration_authority=self.registrations, context=self.ctx())
        self.assertEqual(path.read_bytes(), before)
        register_database(path, 'personal', registration_authority=self.registrations,
                          context=self.ctx(role='director'), replace=True)
        with closing(open_database(path, 'personal', registration_authority=self.registrations, context=self.ctx())):
            pass
        self.assertEqual(path.read_bytes(), before)
        self.assertTrue(receipt.exists())

    def test_unregistered_hot_supported_file_fails_closed_without_recovery(self):
        task = self.advance()
        path = self.path()
        path.with_name(path.name + '.identity.json').unlink()
        self.raw_spill_crash(path)
        before = self.raw_snapshot(path)
        for _ in range(2):
            with self.assertRaises(RecoveryRequiredError) as raised:
                self.store.get_task(self.ctx(), task.task_id)
            self.assertFalse(raised.exception.recovery_attempted)
            self.assertEqual(self.raw_snapshot(path), before)

    def test_hot_file_with_invalid_or_wrong_environment_receipt_is_not_recovered(self):
        for env, receipt_value in (('personal', 'not json'), ('gabos', None), ('fintra', 'duplicate')):
            task = self.advance(env)
            path = self.path(env)
            receipt = path.with_name(path.name + '.identity.json')
            if receipt_value == 'duplicate':
                receipt.write_text(receipt.read_text()[:-1] + ', "environment": "fintra"}')
            elif receipt_value is None:
                data = json.loads(receipt.read_text())
                data['environment'] = 'fintra'
                receipt.write_text(json.dumps(data))
            else:
                receipt.write_text(receipt_value)
            self.raw_spill_crash(path)
            before = self.raw_snapshot(path)
            with self.assertRaises(RecoveryRequiredError):
                self.store.get_task(self.ctx(env), task.task_id)
            self.assertEqual(self.raw_snapshot(path), before)

    def test_replaced_hot_file_does_not_inherit_receipt_authority(self):
        task = self.advance()
        path = self.path()
        replacement = path.with_name('replacement.sqlite3')
        replacement.write_bytes(path.read_bytes())
        replacement.replace(path)  # Before creating the hot journal; never replace a hot file.
        self.raw_spill_crash(path)
        before = self.raw_snapshot(path)
        with self.assertRaises(RecoveryRequiredError):
            self.store.get_task(self.ctx(), task.task_id)
        self.assertEqual(self.raw_snapshot(path), before)

    def test_unknown_incompatible_hot_database_is_not_mutated(self):
        path = self.path()
        path.parent.mkdir(parents=True)
        with closing(sqlite3.connect(path)) as db:
            with db:
                db.execute('CREATE TABLE metadata (version INTEGER PRIMARY KEY, environment TEXT NOT NULL)')
                db.execute("INSERT INTO metadata VALUES (999,'personal')")
                db.execute('CREATE TABLE audit (body TEXT NOT NULL)')
                db.execute("INSERT INTO audit VALUES ('committed fixture')")
        self.raw_spill_crash(path, metadata_change=True)
        before = self.raw_snapshot(path)
        with self.assertRaises(RecoveryRequiredError):
            self.store.recover(self.ctx())
        self.assertEqual(self.raw_snapshot(path), before)

    def test_known_file_recovering_to_unsupported_version_reports_possible_mutation(self):
        self.advance()
        path = self.path()
        # Simulate a trusted administrator changing a registered file in place.
        with closing(sqlite3.connect(path)) as db:
            with db:
                db.execute('UPDATE metadata SET version=999')
            committed_dump = tuple(db.iterdump())
        self.raw_spill_crash(path, metadata_change=True)
        before = self.raw_snapshot(path)
        with self.assertRaises(RecoveryValidationError) as raised:
            self.store.recover(self.ctx())
        self.assertTrue(raised.exception.recovery_attempted)
        self.assertIn('may have changed', str(raised.exception))
        self.assertIsInstance(raised.exception.__cause__, UnsupportedSchemaError)
        self.assertFalse(Path(str(path) + '-journal').exists())  # SQLite performed rollback.
        self.assertNotEqual(self.raw_snapshot(path), before)
        with closing(sqlite3.connect(path)) as db:
            self.assertEqual(tuple(db.iterdump()), committed_dump)
            self.assertEqual(db.execute('SELECT version FROM metadata').fetchall(), [(999,)])
        # No migration to v2 or application recovery-scan audit was committed.

    def test_unrecognized_readonly_error_does_not_authorize_recovery(self):
        from unittest.mock import patch
        self.advance()
        path = self.path()
        before = self.raw_snapshot(path)
        with patch('alfred_research.persistence.validate_schema', side_effect=sqlite3.OperationalError('unknown failure')):
            with self.assertRaises(sqlite3.OperationalError):
                open_database(path, 'personal', registration_authority=self.registrations, context=self.ctx())
        self.assertEqual(self.raw_snapshot(path), before)
