"""Disputed or contradicted claims never reach Alfred Memory, and the candidate records each remaining claim's
corroboration status. Memory and network are test doubles; the corroboration stage is patched."""
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
os.environ['ALFRED_RESEARCH_CORROBORATION'] = 'off'  # engine runs in unit tests never reach the network
sys.path.insert(0, str(Path(__file__).resolve().parent))
from alfred_research.local.memory import AuthoritativeMemoryAdapter, MemoryServicePublisher, withheld_claims
from alfred_research.local.verify import ClaimVerification, VerificationResult
from alfred_research.local.workers import digest
from test_multimedia_sources import Responses
from test_research_line import FakeMemory, LineHarness, ROUTES


def corroboration(claims, statuses, groups=()):
    """A corroboration result as the stage would store it; ``statuses`` maps claim_id -> status.
    ``groups`` is given to every claim, so tests can check it is only counted for corroborated ones."""
    rows = tuple(ClaimVerification(c['claim_id'], c['statement'], statuses.get(c['claim_id'], 'original_source_only'),
                                   c['source_id'], True, independent_groups=tuple(groups),
                                   rationale='because ' + statuses.get(c['claim_id'], 'original_source_only'))
                 for c in claims)
    return VerificationResult(digest(claims), rows, (), 'test', ())


def packet():
    claims = [{'claim_id': 'C' + str(n), 'statement': 'Statement ' + str(n), 'kind': 'source_statement',
               'source_id': 'S1', 'evidence_id': 'S1:e' + str(n)} for n in (1, 2, 3)]
    verification = {'packet_sha256': digest(claims), 'scope': 'source support',
                    'assessments': [{'claim_id': c['claim_id'], 'supported': True} for c in claims]}
    return claims, verification


class PrepareTests(unittest.TestCase):
    def prepare(self, corroboration_dict):
        claims, verification = packet()
        return AuthoritativeMemoryAdapter().prepare('research-' + '0' * 32, {'objective': 'x'}, claims, [], verification,
                                                    '0' * 64, corroboration_dict)

    def test_disputed_and_contradicted_claims_are_left_out_of_the_candidate(self):
        claims, _ = packet()
        candidate = self.prepare(corroboration(claims, {'C1': 'disputed', 'C3': 'contradicted'}).to_dict())
        self.assertEqual([c['claim_id'] for c in candidate['claims']], ['C2'])

    def test_other_statuses_stay_eligible(self):
        claims, _ = packet()
        candidate = self.prepare(corroboration(claims, {'C1': 'corroborated', 'C2': 'unverified', 'C3': 'not_assessable'}).to_dict())
        self.assertEqual([c['claim_id'] for c in candidate['claims']], ['C1', 'C2', 'C3'])

    def test_all_conflicted_means_no_candidate(self):
        claims, _ = packet()
        self.assertIsNone(self.prepare(corroboration(claims, {c['claim_id']: 'contradicted' for c in claims}).to_dict()))

    def test_job_without_corroboration_keeps_support_only_selection(self):
        candidate = self.prepare(None)
        self.assertEqual([c['claim_id'] for c in candidate['claims']], ['C1', 'C2', 'C3'])
        self.assertEqual({c['corroboration']['status'] for c in candidate['claims']}, {'unverified'})

    def test_each_claim_records_its_corroboration_status(self):
        claims, _ = packet()
        result = corroboration(claims, {'C1': 'corroborated', 'C2': 'original_source_only', 'C3': 'unverified'},
                               groups=('reuters', 'apnews'))
        candidate = self.prepare(result.to_dict())
        records = {c['claim_id']: c['corroboration'] for c in candidate['claims']}
        self.assertEqual(records['C1'], {'status': 'corroborated', 'independent_groups': 2, 'note': 'because corroborated'})
        self.assertEqual(records['C2']['status'], 'original_source_only')
        self.assertEqual(records['C3']['status'], 'unverified')

    def test_original_source_only_and_unverified_are_never_marked_corroborated(self):
        claims, _ = packet()
        result = corroboration(claims, {'C1': 'original_source_only', 'C2': 'unverified', 'C3': 'not_assessable'},
                               groups=('reuters', 'apnews'))
        for claim in self.prepare(result.to_dict())['claims']:
            self.assertNotEqual(claim['corroboration']['status'], 'corroborated')
            self.assertEqual(claim['corroboration']['independent_groups'], 0)

    def test_corroboration_for_a_different_packet_is_refused(self):
        claims, _ = packet()
        other = [{**c, 'statement': c['statement'] + ' changed'} for c in claims]
        with self.assertRaises(ValueError):
            self.prepare(corroboration(other, {}).to_dict())

    def test_malformed_corroboration_fails_closed(self):
        with self.assertRaises(ValueError):
            withheld_claims({'schema': 'something-else'})
        with self.assertRaises(ValueError):
            self.prepare({'schema': 'something-else'})


class PublisherExcludeTests(unittest.TestCase):
    def test_all_excluded_publishes_nothing_and_reads_no_token(self):
        claims, verification = packet()
        candidate = AuthoritativeMemoryAdapter().prepare('research-' + '0' * 32, {'objective': 'x'}, claims, [], verification, '0' * 64)
        publisher = MemoryServicePublisher('http://127.0.0.1:9/v1/memory', '/nonexistent-token')
        record = publisher.publish('research-' + '0' * 32, candidate, exclude={'C1', 'C2', 'C3'})
        self.assertEqual((record['status'], record['receipts'], record['withheld']), ('nothing_to_publish', [], ['C1', 'C2', 'C3']))


class LineCorroborationTests(LineHarness):
    """End to end through the Research line: engine candidate plus desk publication."""
    def published_line(self):
        self.memory = FakeMemory()
        return self.line(memory=True)

    def run_job(self, line, text='https://example.org/retries'):
        before = {r['id'] for r in line.engine.store.list()}
        self.inbound(text)
        with patch('alfred_research.local.sources.http_get', Responses(ROUTES)):
            line.poll_once()
        (job_id,) = {r['id'] for r in line.engine.store.list()} - before
        return line.engine.store.get(job_id)

    def test_contradicted_claim_is_never_published(self):
        def stage(sources, claims, support, directory):
            return corroboration(claims, {'C1': 'contradicted'})
        line = self.published_line()
        with patch('alfred_research.local.engine.corroborate', stage):
            job = self.run_job(line)
        self.assertEqual([c['claim_id'] for c in job['artifacts']['memory-candidate']['claims']], ['C2'])
        self.assertEqual([r['source_message_id'].rsplit(':', 1)[-1] for r in self.memory.records], ['C2'])
        self.assertEqual(job['artifacts']['memory-publication']['status'], 'published')
        self.assertIn('not independently corroborated (original source only)', self.memory.records[0]['content'])

    def test_engine_records_corroboration_status_on_the_candidate(self):
        def stage(sources, claims, support, directory):
            return corroboration(claims, {'C1': 'corroborated', 'C2': 'original_source_only'}, groups=('reuters',))
        line = self.published_line()
        with patch('alfred_research.local.engine.corroborate', stage):
            job = self.run_job(line)
        candidate = job['artifacts']['memory-candidate']
        self.assertEqual({c['claim_id']: c['corroboration']['status'] for c in candidate['claims']},
                         {'C1': 'corroborated', 'C2': 'original_source_only'})
        saved = json.loads((Path(job['report_path']).parent / 'memory-candidate.json').read_text())
        self.assertEqual(saved, candidate)
        contents = {r['source_message_id'].rsplit(':', 1)[-1]: r['content'] for r in self.memory.records}
        self.assertIn('independently corroborated by 1 publisher group(s)', contents['C1'])
        self.assertIn('not independently corroborated (original source only)', contents['C2'])

    def test_desk_withholds_conflicts_found_after_the_candidate_and_keeps_old_jobs(self):
        quiet = self.line()                                 # publishing off: candidates kept, nothing sent
        job, old_job = self.run_job(quiet), self.run_job(quiet, 'research again https://example.org/retries')
        self.assertNotIn('memory-publication', job['artifacts'])
        claims = job['artifacts']['research']['claims']
        self.assertEqual(len(job['artifacts']['memory-candidate']['claims']), 2)
        line = self.published_line()

        conflicted = {**job, 'artifacts': {**job['artifacts'],
                                           'corroboration': corroboration(claims, {'C2': 'disputed'}).to_dict()}}
        record = line.publish(conflicted)['artifacts']['memory-publication']
        self.assertEqual(([r['claim_id'] for r in record['receipts']], record['withheld']), (['C1'], ['C2']))
        self.assertEqual([r['source_message_id'].rsplit(':', 1)[-1] for r in self.memory.records], ['C1'])

        older = {k: v for k, v in old_job['artifacts'].items() if k != 'corroboration'}   # pre-corroboration job
        record = line.publish({**old_job, 'artifacts': older})['artifacts']['memory-publication']
        self.assertEqual(([r['claim_id'] for r in record['receipts']], record['withheld']), (['C1', 'C2'], []))


if __name__ == '__main__':
    unittest.main()
