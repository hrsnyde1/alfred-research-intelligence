"""Dedicated Research line worker and Memory publication. Connector, Memory and network are test doubles."""
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from alfred_research.integration import desk, research_line
from alfred_research.integration.research_line import ResearchLine, main, private_write
from alfred_research.local.memory import MemoryBlocked, MemoryServicePublisher
from test_multimedia_sources import Responses

desk.log.setLevel(logging.CRITICAL)
research_line.log.setLevel(logging.CRITICAL)
ARTICLE = (b'<html><head><title>Retry guidance</title></head><body><article>'
           b'<p>Idempotent requests can be retried automatically after a connection failure.</p>'
           b'<p>Non-idempotent requests should not be retried without user confirmation.</p></article></body></html>', 'text/html')
ROUTES = [('https://example.org/retries', ARTICLE)]
BINDING = {'line': '+14152250168', 'space': 'research-space', 'sender': 'owner-sender'}
TOKEN = 'r' * 40


class FakeMemory:
    """Mimics focused_v1: create gives agent principals pending unless the kind is auto-approved, and
    reports any duplicate as approved; search shows the agent approved rows only."""
    def __init__(self, auto=('task_progress', 'development_lesson'), kinds=None):
        self.records, self.auto = [], auto
        self.kinds = kinds or ('personal_fact', 'preference', 'standing_instruction', 'decision', 'task_progress', 'development_lesson')
        memory = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                if self.headers.get('Authorization') != 'Bearer ' + TOKEN:
                    return self.reply(403, {'error': 'denied'})
                if body.get('action') == 'search':
                    return self.reply(200, [{'id': r['id'], 'content': r['content']} for r in memory.records
                                            if r['task_id'] == body.get('task_id') and r['review_state'] == 'approved'
                                            and body.get('query', '') in r['content']])
                if body.get('action') != 'create' or body.get('kind') not in memory.kinds:
                    return self.reply(400, {'error': 'invalid request'})
                prior = next((r for r in memory.records if r['source_message_id'] == body['source_message_id']), None)
                if prior:
                    return self.reply(200, {'id': prior['id'], 'review_state': 'approved', 'saved': True, 'duplicate': True})
                record = {**body, 'id': 'mem-' + str(len(memory.records) + 1),
                          'review_state': 'approved' if body['kind'] in memory.auto else 'pending'}
                memory.records.append(record)
                self.reply(200, {'id': record['id'], 'review_state': record['review_state'], 'saved': True, 'duplicate': False})

            def reply(self, status, payload):
                data = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = 'http://127.0.0.1:' + str(self.server.server_address[1]) + '/v1/memory'

    def close(self):
        self.server.shutdown()
        self.server.server_close()


class LineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.ledger = self.root / 'photon-state'
        self.ledger.mkdir(mode=0o700)
        self.token = self.root / 'memory-token'
        self.token.write_text(TOKEN)
        self.token.chmod(0o600)
        self.memory = None
        self.count = 0

    def tearDown(self):
        if self.memory:
            self.memory.close()
        self.temp.cleanup()

    def config(self, memory=False, **extra):
        config = {'enabled': True, 'data_dir': str(self.root / 'line'), 'ledger_dir': str(self.ledger),
                  'outbox_dir': str(self.ledger / 'outbox'), 'binding': dict(BINDING), 'provider': 'extractive'}
        if memory:
            config['memory'] = {'enabled': True, 'url': self.memory.url, 'token_file': str(self.token),
                                'allow_extractive': True}
        config.update(extra)
        return config

    def line(self, memory=False, **extra):
        return ResearchLine(self.config(memory, **extra), runner='inline')

    def inbound(self, text, **research):
        """Write a record exactly as the connector's persist() does."""
        self.count += 1
        key = hashlib.sha256(('event-' + str(self.count)).encode()).hexdigest()
        event = {'messageId': 'research:' + key, 'direction': 'inbound', 'platform': 'imessage', 'project': 'research',
                 'content': {'type': 'text', 'text': text},
                 'research': {'connection_ref': 'research-connection-v1', 'line': BINDING['line'], 'space': BINDING['space'],
                              'sender': BINDING['sender'], 'profile': 'research', 'originalMessageId': 'm' + str(self.count),
                              **research}}
        record = {'schema': 'research.connector.pending/1', 'fingerprint': 'f', 'correlation': 'research-pending:' + key,
                  'event': event, 'status': 'PENDING_INTAKE', 'productionTrusted': False}
        (self.ledger / (key + '.json')).write_text(json.dumps(record))
        (self.ledger / (hashlib.sha256(key.encode()).hexdigest() + '.json')).write_text(json.dumps({'fingerprint': 'x'}))
        return key

    def outbox(self):
        items = [json.loads(p.read_text()) for p in (self.ledger / 'outbox').glob('*.json')]
        return sorted(items, key=lambda r: r['sequence'])

    def test_link_is_acknowledged_researched_and_replied_in_order(self):
        line = self.line()
        key = self.inbound('https://example.org/retries')
        with patch('alfred_research.local.sources.http_get', Responses(ROUTES)):
            self.assertEqual(line.poll_once(), 1)
        ack, final = self.outbox()
        self.assertEqual((ack['operationId'], final['operationId']), ('reply:' + key, 'final:' + key))
        self.assertIn('On it: researching https://example.org/retries', ack['text'])
        self.assertIn('Research complete', final['text'])
        self.assertIn('[article:html-line', final['text'])
        self.assertIn('not published to Alfred\'s Memory', final['text'])
        self.assertEqual(line.poll_once(), 0)
        self.assertEqual(len(self.outbox()), 2)
        mode = (self.ledger / 'outbox' / (hashlib.sha256(('reply:' + key).encode()).hexdigest() + '.json')).stat().st_mode
        self.assertEqual(mode & 0o777, 0o600)

    def test_findings_are_published_to_the_topic_task_as_approved(self):
        self.memory = FakeMemory()
        line = self.line(memory=True)
        self.inbound('https://example.org/retries', topic='Taxes')
        with patch('alfred_research.local.sources.http_get', Responses(ROUTES)):
            line.poll_once()
        final = self.outbox()[-1]['text']
        self.assertIn('saved to Alfred\'s Memory under Taxes as approved; Alfred can now use them', final)
        self.assertEqual(len(self.memory.records), 2)
        record = self.memory.records[0]
        self.assertEqual((record['task_id'], record['kind']), ('research-line/taxes', 'task_progress'))
        self.assertTrue(record['content'].startswith('Research finding: The source states:'))
        self.assertIn('Source: Retry guidance - https://example.org/retries (article:html-line', record['content'])
        self.assertIn('not independently corroborated', record['content'])
        self.assertRegex(record['source_message_id'], r'^research:research-[0-9a-f]{32}:C1$')
        job = line.engine.store.get(line.engine.store.list()[0]['id'])
        publication = job['artifacts']['memory-publication']
        self.assertEqual((publication['status'], publication['topic']), ('published', 'Taxes'))
        self.assertEqual([r['memory_id'] for r in publication['receipts']], ['mem-1', 'mem-2'])

    def test_missing_or_unknown_topic_files_under_general(self):
        self.memory = FakeMemory()
        line = self.line(memory=True)
        self.inbound('https://example.org/retries', topic='Secret')
        with patch('alfred_research.local.sources.http_get', Responses(ROUTES)):
            line.poll_once()
        self.assertEqual({r['task_id'] for r in self.memory.records}, {'research-line/general'})
        self.assertIn('under General as approved', self.outbox()[-1]['text'])

    def test_duplicate_reported_approved_is_checked_against_search(self):
        self.memory = FakeMemory()
        line = self.line(memory=True)
        self.inbound('https://example.org/retries')
        with patch('alfred_research.local.sources.http_get', Responses(ROUTES)):
            line.poll_once()
        self.memory.records[0]['review_state'] = 'pending'  # Memory later holds the first row back
        job = line.engine.store.get(line.engine.store.list()[0]['id'])
        again = line.publisher.publish(job['id'], job['artifacts']['memory-candidate'])
        self.assertEqual(len(self.memory.records), 2)
        self.assertEqual([(r['duplicate'], r['reported_state'], r['review_state']) for r in again['receipts']],
                         [(True, 'approved', 'not_approved'), (True, 'approved', 'approved')])
        self.assertEqual(again['status'], 'pending_review')
        self.assertIn('1 approved under General, 1 not yet approved',
                      desk.memory_line({'artifacts': {desk.PUBLICATION_ARTIFACT: again}}))

    def test_memory_pending_or_refused_is_reported_honestly(self):
        self.memory = FakeMemory(auto=())  # agent principal + non-auto kind -> pending
        line = self.line(memory=True)
        self.inbound('https://example.org/retries')
        with patch('alfred_research.local.sources.http_get', Responses(ROUTES)):
            line.poll_once()
        self.assertIn('0 approved under General, 2 not yet approved', self.outbox()[-1]['text'])
        self.memory.kinds = ('personal_fact',)  # task_progress unknown to this Memory release
        refused = self.line(memory=True)
        self.inbound('research again https://example.org/retries')
        with patch('alfred_research.local.sources.http_get', Responses(ROUTES)):
            refused.poll_once()
        final = self.outbox()[-1]['text']
        self.assertIn('Memory: not saved (Memory refused the request (HTTP 400', final)
        self.assertIn('Research complete', final)

    def test_extractive_findings_are_not_published_by_default(self):
        self.memory = FakeMemory()
        config = self.config(memory=True)
        del config['memory']['allow_extractive']
        line = ResearchLine(config, runner='inline')
        self.inbound('https://example.org/retries')
        with patch('alfred_research.local.sources.http_get', Responses(ROUTES)):
            line.poll_once()
        self.assertEqual(self.memory.records, [])
        self.assertIn('Memory: not published (findings came from the no-model extractive worker', self.outbox()[-1]['text'])
        job = line.engine.store.get(line.engine.store.list()[0]['id'])
        self.assertEqual(job['artifacts']['memory-publication']['status'], 'skipped')

    def test_template_ships_with_memory_publishing_off(self):
        template = json.loads((Path(__file__).resolve().parents[1] / 'staging' / 'research-photon-line-v1' /
                               'line-config.template.json').read_text())
        self.assertIs(template['memory']['enabled'], False)
        self.assertIs(template['enabled'], False)

    def test_binding_mismatch_is_ignored(self):
        line = self.line()
        self.inbound('https://example.org/retries', sender='someone-else')
        self.inbound('https://example.org/retries', line='shared')
        self.assertEqual(line.poll_once(), 2)
        self.assertEqual(self.outbox(), [])
        self.assertEqual(line.engine.store.list(), [])

    def test_commands_questions_and_non_research(self):
        line = self.line()
        self.inbound('help')
        self.inbound('status')
        self.inbound('ok')
        with patch('alfred_research.local.engine.discover', side_effect=RuntimeError('Search offline')):
            self.inbound('What is the history of HTTP idempotency?')
            line.poll_once()
        texts = [r['text'] for r in self.outbox()]
        self.assertTrue(texts[0].startswith('Send me a link'))
        self.assertEqual(texts[1], 'No research jobs yet.')
        self.assertTrue(texts[2].startswith('Nothing to research'))
        self.assertIn('the question "What is the history of HTTP idempotency?"', texts[3])
        self.assertIn('stopped: needs sources', texts[4])

    def test_operational_words_still_research_on_dedicated_line(self):
        line = self.line()
        self.inbound('Send this to the team after you check it https://example.org/retries')
        with patch('alfred_research.local.sources.http_get', Responses(ROUTES)):
            line.poll_once()
        self.assertIn('On it', self.outbox()[0]['text'])

    def test_restart_resumes_and_delivers_once(self):
        line = self.line()
        line.start = lambda job_id: None  # crash after acknowledgement, before execution
        line.deferred = None
        key = self.inbound('https://example.org/retries')
        line.poll_once()
        self.assertEqual(len(self.outbox()), 1)
        with patch('alfred_research.local.sources.http_get', Responses(ROUTES)):
            self.line().resume()
            self.line().resume()
        self.assertEqual([r['operationId'] for r in self.outbox()], ['reply:' + key, 'final:' + key])

    def test_unprotected_directories_and_shared_line_refused(self):
        with self.assertRaisesRegex(ValueError, 'Shared'):
            self.line(binding={**BINDING, 'line': 'shared'})
        self.ledger.chmod(0o755)
        with self.assertRaisesRegex(ValueError, 'Protected'):
            self.line()

    def test_private_write_is_idempotent(self):
        target = self.root / 'x.json'
        self.assertTrue(private_write(target, {'a': 1}))
        self.assertFalse(private_write(target, {'a': 2}))
        self.assertEqual(json.loads(target.read_text()), {'a': 1})

    def test_help_text_follows_memory_setting(self):
        self.assertIn('Memory publishing is off', self.line().help_text())
        self.memory = FakeMemory()
        self.assertIn('save verified findings to Alfred\'s Memory', self.line(memory=True).help_text())

    def test_memory_task_and_kind_come_from_the_topic_not_the_config(self):
        self.memory = FakeMemory()
        for extra in ({'task_id': 'research-line'}, {'kind': 'research_finding'}):
            config = self.config(memory=True)
            config['memory'].update(extra)
            with self.subTest(extra=extra), self.assertRaisesRegex(ValueError, 'per topic'):
                ResearchLine(config, runner='inline')
        config = self.config(memory=True)
        config['memory']['kind'] = 'task_progress'
        ResearchLine(config, runner='inline')

    def test_cli_once_finishes_jobs_before_exiting(self):
        config = self.root / 'config.json'
        config.write_text(json.dumps(self.config()))
        config.chmod(0o600)
        key = self.inbound('https://example.org/retries')
        with patch('alfred_research.local.sources.http_get', Responses(ROUTES)), patch('builtins.print'):
            self.assertEqual(main(['once', str(config)]), 0)
        self.assertEqual([r['operationId'] for r in self.outbox()], ['reply:' + key, 'final:' + key])

    def test_cli_disabled_and_check(self):
        config = self.root / 'config.json'
        config.write_text(json.dumps({**self.config(), 'enabled': False}))
        config.chmod(0o600)
        with patch('builtins.print') as printed:
            self.assertEqual(main(['check', str(config)]), 0)
        self.assertIn('DISABLED', printed.call_args[0][0])
        config.chmod(0o666)
        with self.assertRaisesRegex(ValueError, 'writable'):
            main(['check', str(config)])


class PublisherTests(unittest.TestCase):
    def test_loopback_url_and_private_token_required(self):
        for url in ('https://127.0.0.1:8000/v1/memory', 'http://10.0.0.5:8000/v1/memory', 'http://127.0.0.1/v1/memory',
                    'http://127.0.0.1:8000/other'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                MemoryServicePublisher(url, '/x')
        with tempfile.TemporaryDirectory() as root:
            token = Path(root) / 'token'
            token.write_text(TOKEN)
            token.chmod(0o644)
            publisher = MemoryServicePublisher('http://127.0.0.1:9/v1/memory', token)
            with self.assertRaisesRegex(MemoryBlocked, 'private'):
                publisher.token()

    def test_credential_metadata_matches_connector_rule(self):
        from types import SimpleNamespace
        from alfred_research.local.memory import credential_metadata_allowed
        meta = lambda uid, mode: SimpleNamespace(st_uid=uid, st_mode=0o100000 | mode)
        self.assertTrue(credential_metadata_allowed(meta(0, 0o440), 980))  # systemd LoadCredential
        for uid in (0, 980):
            for mode in (0o400, 0o600):
                self.assertTrue(credential_metadata_allowed(meta(uid, mode), 980))
        for uid, mode in ((980, 0o440), (981, 0o600), (0, 0o444), (0, 0o640), (0, 0o644), (980, 0o620), (0, 0o4400)):
            with self.subTest(uid=uid, mode=oct(mode)):
                self.assertFalse(credential_metadata_allowed(meta(uid, mode), 980))

    def test_tampered_candidate_rejected(self):
        publisher = MemoryServicePublisher('http://127.0.0.1:9/v1/memory', '/x')
        with self.assertRaises(ValueError):
            publisher.publish('research-' + '0' * 32, {'schema': 'research.local.pending-memory/1', 'candidate_sha256': 'bad'})


if __name__ == '__main__':
    unittest.main()
