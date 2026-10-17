"""Local execution tests use owner files; network/model fakes are explicitly scoped."""
import copy
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
os.environ.setdefault('ALFRED_RESEARCH_CORROBORATION', 'off')  # engine runs in unit tests never reach the network
from alfred_research.local.engine import ResearchEngine
from alfred_research.local.memory import AuthoritativeMemoryAdapter, MemoryBlocked
from alfred_research.local.sources import acquire, extract, fetch, UnsupportedSource
from alfred_research.local.workers import digest, verify
from alfred_research.integration.local_research import LocalResearchEntryPoint


ARTICLE = 'A client sends a request to the server.\nAn idempotent method has the same intended effect when repeated.\n'


class LocalV1Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'article.txt'
        self.source.write_text(ARTICLE)
        self.engine = ResearchEngine(self.root / 'state')

    def tearDown(self):
        self.temp.cleanup()

    def run_article(self):
        job_id = self.engine.submit('Explain idempotent methods', [str(self.source)], provider='extractive')
        return self.engine.run(job_id)

    def test_real_file_to_report_candidate_and_fresh_retrieval(self):
        job = self.run_article()
        self.assertEqual(job['status'], 'completed')
        verification = job['artifacts']['verification']
        self.assertNotEqual(verification['pid'], os.getpid())
        self.assertTrue(all(r['supported'] for r in verification['assessments']))
        fresh = ResearchEngine(self.root / 'state').store.get(job['id'])
        self.assertEqual(fresh, job)
        self.assertIn('idempotent', Path(job['report_path']).read_text())
        candidate = job['artifacts']['memory-candidate']
        self.assertIsNone(candidate['memory_receipt'])
        self.assertEqual(candidate['promotion_status'], 'BLOCKED')
        self.assertEqual([e['status'] for e in job['events']],
                         ['queued', 'collecting', 'planning', 'researching', 'verifying', 'synthesizing', 'completed'])

    def test_idempotent_submit_conflicting_request_and_no_rerun(self):
        args = ('Question', [str(self.source)])
        first = self.engine.submit(*args, provider='extractive', request_key='same')
        self.assertEqual(first, self.engine.submit(*args, provider='extractive', request_key='same'))
        with self.assertRaises(ValueError):
            self.engine.submit('Changed', request_key='same')
        self.engine.run(first)
        with self.assertRaises(ValueError):
            self.engine.run(first)

    def test_failed_source_is_tracked(self):
        job_id = self.engine.submit('Missing', [str(self.root / 'missing.txt')], provider='extractive')
        job = self.engine.run(job_id)
        self.assertEqual(job['status'], 'failed')
        self.assertIsNone(job['report_path'])
        self.assertNotIn('memory-candidate', job['artifacts'])

    def test_unsupported_pdf_never_claims_success(self):
        pdf = self.root / 'file.pdf'
        pdf.write_bytes(b'%PDF-not-a-working-parser')
        job = self.engine.run(self.engine.submit('Read document', [str(pdf)], provider='extractive'))
        self.assertEqual(job['status'], 'unsupported')
        self.assertNotIn('report', job['artifacts'])

    def test_youtube_needs_actual_transcript(self):
        with self.assertRaisesRegex(UnsupportedSource, 'transcript'):
            acquire('https://youtu.be/somevideo', self.root, 1)
        transcript = self.root / 'captions.vtt'
        transcript.write_text('WEBVTT\n\n00:00.000 --> 00:03.000\nAn actual supplied caption appears here.\n')
        job = self.engine.run(self.engine.submit('Review transcript', [str(transcript)], provider='extractive'))
        self.assertEqual(job['status'], 'completed')
        self.assertIn('owner_file', Path(job['report_path']).read_text())

    def test_partial_acquisition_remains_incomplete(self):
        job = self.engine.run(self.engine.submit('Review', [str(self.source), str(self.root / 'missing')], provider='extractive'))
        self.assertEqual(job['status'], 'needs_more_research')
        self.assertIn('Acquisition failed', Path(job['report_path']).read_text())

    def test_provider_failure_is_not_synthetic_fallback(self):
        with patch('alfred_research.local.engine.research', side_effect=RuntimeError('Provider unavailable')):
            job = self.engine.run(self.engine.submit('Review', [str(self.source)], provider='codex'))
        self.assertEqual(job['status'], 'failed')
        self.assertNotIn('verification', job['artifacts'])

    def test_question_discovery_failure_requests_sources(self):
        with patch('alfred_research.local.engine.discover', side_effect=RuntimeError('Search offline')):
            job = self.engine.run(self.engine.submit('Question without sources', provider='extractive'))
        self.assertEqual(job['status'], 'needs_sources')
        self.assertNotIn('memory-candidate', job['artifacts'])

    def verification_payload(self):
        job = self.run_article()
        return {'sources': [job['artifacts']['source-1']], 'claims': job['artifacts']['research']['claims'],
                'provider': 'extractive', 'recommendations': []}

    def test_verifier_rejects_fabricated_quote(self):
        payload = self.verification_payload()
        payload['claims'][0]['quote'] = 'This quotation never appeared in the original article.'
        result = verify(payload)
        self.assertFalse(result['assessments'][0]['supported'])

    def test_verifier_rejects_changed_snapshot(self):
        payload = self.verification_payload()
        Path(payload['sources'][0]['snapshot']).write_text('Changed contents')
        with self.assertRaisesRegex(ValueError, 'changed'):
            verify(payload)

    def test_verifier_rejects_claim_beyond_quote(self):
        payload = self.verification_payload()
        payload['claims'][0]['statement'] = 'All retries are always safe.'
        self.assertFalse(verify(payload)['assessments'][0]['supported'])

    def test_verifier_rejects_unrelated_source_binding(self):
        payload = self.verification_payload()
        payload['claims'][0]['source_id'] = 'S99'
        self.assertFalse(verify(payload)['assessments'][0]['supported'])

    def test_memory_blocked_and_pending_candidate_preserved(self):
        job = self.run_article()
        candidate = job['artifacts']['memory-candidate']
        adapter = AuthoritativeMemoryAdapter()
        before = self.engine.store.get(job['id'])
        for method in (adapter.submit, adapter.promote):
            with self.assertRaises(MemoryBlocked):
                method(candidate)
        self.assertEqual(before, self.engine.store.get(job['id']))
        changed = copy.deepcopy(candidate)
        changed['claims'][0]['statement'] = 'Tampered'
        with self.assertRaises(ValueError):
            adapter.promote(changed)

    def test_candidate_rejects_verification_for_other_packet(self):
        job = self.run_article()
        claims = job['artifacts']['research']['claims']
        with self.assertRaisesRegex(ValueError, 'packet'):
            AuthoritativeMemoryAdapter().prepare(job['id'], job['request'], [], [], job['artifacts']['verification'], '0' * 64)
        verification = copy.deepcopy(job['artifacts']['verification'])
        verification['assessments'] = []
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            AuthoritativeMemoryAdapter().prepare(job['id'], job['request'], claims, [], verification, '0' * 64)

    def test_long_document_retains_end_evidence(self):
        content = ('Ordinary source text line with no important result.\n' * 5000 +
                   'The final important finding occurs at the end of the document.\n').encode()
        evidence, limitations, _ = extract(content, 'source.txt')
        self.assertIn('final important finding', ''.join(e['text'] for e in evidence))
        self.assertFalse(limitations)

    def test_hidden_html_is_not_evidence(self):
        evidence, _, _ = extract(b'<p>This is an actual visible finding.</p><script>Fabricated hidden claim.</script>', 'source.html')
        self.assertNotIn('Fabricated', json.dumps(evidence))

    def test_private_destinations_denied_before_connect(self):
        for url in ('http://example.com', 'https://127.0.0.1/', 'https://localhost/', 'https://user:pass@example.com/'):
            with self.subTest(url=url), patch('socket.create_connection') as connection:
                with self.assertRaises(ValueError):
                    fetch(url)
                connection.assert_not_called()

    def test_hermes_seam_submits_executes_retrieves_without_host_mutation(self):
        seam = LocalResearchEntryPoint(self.root / 'host-working')
        first = seam.submit('host-1', 'Review article', [str(self.source)], provider='extractive')
        again = seam.submit('host-1', 'Review article', [str(self.source)], provider='extractive')
        self.assertEqual(first['job_id'], again['job_id'])
        self.assertEqual(seam.execute(first['job_id'])['status'], 'completed')
        self.assertIn('idempotent', seam.retrieve(first['job_id'])['report'])

    def test_cli_persistent_retrieval(self):
        job = self.run_article()
        script = str(Path(__file__).resolve().parents[1] / 'scripts' / 'research.py')
        result = subprocess.run([sys.executable, script, '--data', str(self.root / 'state'), 'report', job['id']], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, job['artifacts']['report']['text'])

    def test_abandoned_job_recovery_and_active_lock(self):
        job_id = self.engine.submit('Review', [str(self.source)], provider='extractive')
        self.engine.store.claim(job_id)
        with (self.engine.store.root / (job_id + '.lock')).open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(ValueError, 'still running'):
                self.engine.recover(job_id)
        self.assertEqual(self.engine.recover(job_id)['status'], 'interrupted')
        with self.assertRaises(ValueError):
            self.engine.recover(job_id)

    def test_model_review_can_reject_semantic_claim_even_with_exact_quote(self):
        payload = self.verification_payload()
        payload['provider'] = 'codex'
        review = {'assessments': [{'claim_id': c['claim_id'], 'supported': False,
                                  'reason': 'Quotation does not entail the broader statement'} for c in payload['claims']],
                  'recommendations_supported': False}
        with patch('alfred_research.local.workers.model_call', return_value=review):
            result = verify(payload)
        self.assertFalse(any(x['supported'] for x in result['assessments']))

    def test_model_review_cannot_omit_claims(self):
        payload = self.verification_payload()
        payload['provider'] = 'codex'
        with patch('alfred_research.local.workers.model_call', return_value={'assessments': [], 'recommendations_supported': True}):
            with self.assertRaisesRegex(ValueError, 'omitted'):
                verify(payload)


if __name__ == '__main__':
    unittest.main()
