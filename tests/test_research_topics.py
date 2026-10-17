"""Research topics: the worker's topic list matches alfred-memory r59, and findings land on per-topic Memory tasks.

The mirror and real-Memory tests need an alfred-memory checkout with r59 (obsidian_candidate/routing.py).
Set ALFRED_MEMORY_SRC to its ``src`` folder; without one they are skipped.
"""
import ast
import http.server
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from alfred_research.local import memory  # noqa: E402
from alfred_research.local.workers import digest  # noqa: E402

MEMORY_SRC = Path(os.environ.get('ALFRED_MEMORY_SRC', ''))
ROUTING = MEMORY_SRC / 'obsidian_candidate' / 'routing.py'
ALFRED_TOKEN, FOX_TOKEN = 'a' * 40, 'f' * 40


def routing_constants():
    values = {}
    for node in ast.parse(ROUTING.read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                values[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                pass
    return values


@unittest.skipUnless(ROUTING.is_file(), 'alfred-memory routing.py not found; set ALFRED_MEMORY_SRC')
class MirrorTest(unittest.TestCase):
    def test_topics_kind_and_task_prefix_match_alfred_memory(self):
        r59 = routing_constants()
        self.assertEqual(memory.RESEARCH_TOPICS, r59['RESEARCH_TOPICS'])
        self.assertEqual(memory.DEFAULT_RESEARCH_TOPIC, r59['DEFAULT_RESEARCH_TOPIC'])
        self.assertEqual(memory.RESEARCH_KIND, r59['RESEARCH_KIND'])
        self.assertEqual(memory.RESEARCH_TASK_PREFIX, r59['RESEARCH_TASK_PREFIX'])


class TopicTaskTest(unittest.TestCase):
    def test_unknown_topic_has_no_task(self):
        self.assertEqual([memory.research_task(t) for t in memory.RESEARCH_TOPICS],
                         ['research-line/general', 'research-line/taxes', 'research-line/legal',
                          'research-line/business', 'research-line/personal'])
        for topic in ('taxes', 'Secret', '', None):
            with self.assertRaises(ValueError):
                memory.research_task(topic)


def candidate(job_id, count=2):
    sources = [{'source_id': 'S1', 'locator': 'https://example.com/a', 'acquired_at': '2026-10-17T00:00:00Z',
                'metadata': {'title': 'Example'}, 'evidence': [{'evidence_id': 'S1:E1', 'location': 'p1:char0-10'}]}]
    claims = [{'claim_id': 'C%d' % n, 'source_id': 'S1', 'evidence_id': 'S1:E1', 'kind': 'source_statement',
               'statement': 'Finding number %d from %s.' % (n, job_id)} for n in range(1, count + 1)]
    body = {'schema': 'research.local.pending-memory/1', 'job_id': job_id, 'claims': claims, 'sources': sources}
    return {**body, 'candidate_sha256': digest(body)}


@unittest.skipUnless((MEMORY_SRC / 'focused_v1' / 'server.py').is_file() and ROUTING.is_file(),
                     'alfred-memory checkout not found; set ALFRED_MEMORY_SRC')
class RealMemoryTest(unittest.TestCase):
    """The publisher against the real alfred-memory store and /v1/memory handler on 127.0.0.1."""

    @classmethod
    def setUpClass(cls):
        if str(MEMORY_SRC) not in sys.path:
            sys.path.append(str(MEMORY_SRC))
        try:
            from focused_v1.server import make_handler
            from focused_v1.store import MemoryStore
            from obsidian_candidate import routing
        except ImportError as error:
            raise unittest.SkipTest('alfred-memory not importable: ' + str(error))
        cls.make_handler, cls.MemoryStore, cls.routing = staticmethod(make_handler), MemoryStore, routing

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        os.chmod(self.dir, 0o700)
        self.db = self.dir / 'memory.db'
        self.store = self.MemoryStore(self.db, deletion_key=os.urandom(32), initialize=True)
        self.store.provision('alfred', 'alfred', ALFRED_TOKEN)
        self.store.provision(self.routing.RESEARCH_PRINCIPAL, 'agent', FOX_TOKEN)
        for topic in ('General', 'Taxes', 'Legal', 'Business'):  # Personal deliberately unassigned
            self.store.assign(ALFRED_TOKEN, self.routing.RESEARCH_PRINCIPAL, self.routing.research_task(topic))
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), self.make_handler(self.store))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        token_file = self.dir / 'token'
        token_file.write_text(FOX_TOKEN)
        os.chmod(token_file, 0o600)
        self.publisher = memory.MemoryServicePublisher(
            'http://127.0.0.1:%d/v1/memory' % server.server_address[1], token_file)

    def rows(self):
        with sqlite3.connect(self.db) as db:
            return db.execute('SELECT id,principal,task_id,kind,review_state FROM memories ORDER BY id').fetchall()

    def test_findings_land_on_the_topic_task_and_route_to_the_research_folder(self):
        job = 'research-' + '1' * 32
        result = self.publisher.publish(job, candidate(job), topic='Taxes')
        self.assertEqual((result['status'], result['topic'], result['task_id'], result['kind']),
                         ('published', 'Taxes', 'research-line/taxes', 'task_progress'))
        self.assertEqual([r['review_state'] for r in result['receipts']], ['approved', 'approved'])
        rows = self.rows()
        self.assertEqual({(p, t, k, s) for _, p, t, k, s in rows},
                         {('research-fox', 'research-line/taxes', 'task_progress', 'approved')})
        for record_id, principal, task_id, _, _ in rows:
            topic = self.routing.research_topic(principal, task_id)
            self.assertEqual(self.routing.research_path(topic, record_id), 'Research/Taxes/' + record_id + '.md')

    def test_default_topic_is_general(self):
        job = 'research-' + '2' * 32
        self.assertEqual(self.publisher.publish(job, candidate(job, 1))['task_id'], 'research-line/general')

    def test_duplicate_reported_approved_is_not_trusted_when_the_row_is_pending(self):
        job = 'research-' + '3' * 32
        first = self.publisher.publish(job, candidate(job), topic='Legal')
        self.assertEqual(first['status'], 'published')
        # Memory later holds the first row back (pending review); a retry gets "approved" duplicates.
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE memories SET review_state='pending' WHERE id=?", (first['receipts'][0]['memory_id'],))
        again = self.publisher.publish(job, candidate(job), topic='Legal')
        self.assertEqual([(r['duplicate'], r['reported_state'], r['review_state']) for r in again['receipts']],
                         [(True, 'approved', 'not_approved'), (True, 'approved', 'approved')])
        self.assertEqual(again['status'], 'pending_review')

    def test_a_topic_task_memory_has_not_assigned_is_refused(self):
        job = 'research-' + '4' * 32
        with self.assertRaises(memory.MemoryBlocked):
            self.publisher.publish(job, candidate(job), topic='Personal')
        self.assertEqual(self.rows(), [])


if __name__ == '__main__':
    unittest.main()
