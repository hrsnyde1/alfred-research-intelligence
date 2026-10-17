"""Claude synthesis consumes the corroboration result. SDK responses and the corroboration stage are mocked;
no live model or network call is made by this suite."""
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
os.environ.setdefault('ALFRED_RESEARCH_CORROBORATION', 'off')
from alfred_research.local.director import render_intelligence, validate_synthesis
from alfred_research.local.engine import ResearchEngine
from alfred_research.local.verify import Citation, ClaimVerification, VerificationResult
from alfred_research.local.workers import digest
from alfred_research.integration.desk import final_message

from test_claude_research import ARTICLE, DIRECTOR, FakeClaude, evidence_of, good_specialist

SUPPORT_URL = 'https://en.wikipedia.org/wiki/Example_Privacy_Act'
CONTRA_URL = 'https://regulator.example.gov/notice'
SUPPORT = 'The Example Privacy Act obliges covered companies to delete customer data within 30 days of a verified request.'
CONTRA = 'The Example Privacy Act gives covered companies 45 days to delete customer data after a verified request.'


def cite(url, passage, stance, group):
    return Citation('D1' if stance == 'supports' else 'D2', url, group, '2026-10-17T00:00:00Z', 'secondary', group, stance,
                    passage, 'paragraph:1', 'f' * 64)


def result_for(claims, statuses):
    rows = []
    for claim, status in zip(claims, statuses):
        supporting = (cite(SUPPORT_URL, SUPPORT, 'supports', 'wikipedia.org'),) if status in ('corroborated', 'disputed') else ()
        contradicting = (cite(CONTRA_URL, CONTRA, 'contradicts', 'example.gov'),) if status in ('contradicted', 'disputed') else ()
        rows.append(ClaimVerification(claim['claim_id'], claim['statement'], status, claim['source_id'], True,
                                      supporting, contradicting, independent_groups=tuple(c.independence_group for c in supporting),
                                      sources_checked=2, rationale='Test rationale for ' + status + '.'))
    return VerificationResult(digest(claims), tuple(rows), (), 'deterministic-lexical-stance', ('wikipedia',),
                              ('Lexical stance matching only.',), pid=1)


CLAIMS = [{'claim_id': 'C1', 'kind': 'source_statement', 'source_id': 'S1', 'evidence_id': 'S1:e1', 'confidence': 'high',
           'role': 'legal_regulatory', 'quote': 'delete customer data within 30 days',
           'statement': 'The Example Privacy Act requires covered companies to delete customer data within 30 days.'},
          {'claim_id': 'C2', 'kind': 'source_statement', 'source_id': 'S1', 'evidence_id': 'S1:e2', 'confidence': 'high',
           'role': 'technical', 'quote': 'REST API with OAuth 2.0 authentication',
           'statement': 'The library exposes a REST API with OAuth 2.0 authentication.'},
          {'claim_id': 'C3', 'kind': 'source_statement', 'source_id': 'S1', 'evidence_id': 'S1:e3', 'confidence': 'medium',
           'role': 'legal_regulatory', 'quote': 'fine companies up to $7,500',
           'statement': 'Regulators in California may fine companies up to $7,500 per intentional violation.'}]
SOURCE = {'source_id': 'S1', 'locator': '/owner/article.txt', 'kind': 'article', 'content_basis': 'text', 'metadata': {},
          'acquired_at': '2026-10-17T00:00:00Z', 'sha256': 'a' * 64, 'bytes': 300, 'provenance': {'origin': 'owner-file'},
          'limitations': [], 'flags': [],
          'evidence': [{'evidence_id': 'S1:e' + str(n), 'location': 'line:' + str(n), 'text': t}
                       for n, t in enumerate(ARTICLE.strip().split('\n'), 1)]}
SUPPORTED = {'C1': True, 'C2': True, 'C3': True}
MODEL_OUTPUT = {
    'executive_summary': 'Deletion duty [C1]; API [C2]; fines [C3].', 'source_overview': 'One article.',
    'important_findings': [{'point': 'Thirty-day deletion duty', 'claim_ids': ['C1']},
                           {'point': 'OAuth-protected REST API', 'claim_ids': ['C2']},
                           {'point': 'Fines up to $7,500', 'claim_ids': ['C3']}],
    'verification_assessment': 'Mixed.', 'implications': [], 'opportunities': [], 'recommendations': [], 'limitations': [],
    'knowledge_candidates': [{'claim_id': 'C1', 'note': 'deletion duty'}, {'claim_id': 'C2', 'note': 'api'},
                             {'claim_id': 'C3', 'note': 'fines'}],
    'telegram_summary': 'Covered companies must delete customer data within 30 days under the Example Privacy Act. '
                        'The library offers a REST API with OAuth 2.0. See [C3] for fines.'}


class SynthesisCorroborationTests(unittest.TestCase):
    def setUp(self):
        self.corroboration = result_for(CLAIMS, ['contradicted', 'original_source_only', 'disputed'])

    def synthesis(self, corroboration='default'):
        value = self.corroboration if corroboration == 'default' else corroboration
        return validate_synthesis(MODEL_OUTPUT, CLAIMS, SUPPORTED, value)

    def render(self, synthesis, corroboration='default'):
        value = self.corroboration if corroboration == 'default' else corroboration
        verification = {'assessments': [{'claim_id': c['claim_id'], 'supported': True, 'reason': 'quote found'} for c in CLAIMS],
                        'recommendations_supported': True}
        investigations = [{'investigation_id': 'S1-I1', 'role': 'legal_regulatory', 'question': 'q', 'limitations': [],
                           'rejected_findings': []}]
        settings = SimpleNamespace(research_model='claude-sonnet-5-5', synthesis_model='claude-opus-5-5')
        return render_intelligence('job-1', {'objective': 'Obligations'}, [SOURCE], CLAIMS, investigations, verification,
                                   synthesis, [], None, settings, value)

    def test_conflicted_claims_are_excluded_from_knowledge_candidates(self):
        result = self.synthesis()
        self.assertEqual([c['claim_id'] for c in result['knowledge_candidates']], ['C2'])
        self.assertEqual(result['knowledge_candidates'][0]['corroboration'], 'original_source_only')
        self.assertIn('contradicted or disputed knowledge candidate', result['removed'])

    def test_important_findings_carry_conflict_labels_not_corroboration(self):
        points = {f['claim_ids'][0]: f for f in self.synthesis()['important_findings']}
        self.assertTrue(points['C1']['point'].startswith('(Contradicted by other sources)'))
        self.assertTrue(points['C3']['point'].startswith('(Disputed by other sources)'))
        self.assertEqual(points['C2']['point'], 'OAuth-protected REST API')
        self.assertEqual(points['C2']['corroboration'], ['original_source_only'])

    def test_telegram_summary_does_not_state_conflicted_claims_as_fact(self):
        summary = self.synthesis()['telegram_summary']
        self.assertNotIn('within 30 days', summary)           # restates contradicted C1
        self.assertNotIn('[C3]', summary)                      # cites disputed C3
        self.assertIn('REST API with OAuth 2.0', summary)      # original_source_only claim is kept
        self.assertIn('2 finding(s) contradicted or disputed by other sources (C1, C3); not stated as fact.', summary)
        self.assertLessEqual(len(summary), 600)

    def test_telegram_note_survives_truncation(self):
        long = dict(MODEL_OUTPUT, telegram_summary='Unrelated takeaway about budgets. ' * 40)
        summary = validate_synthesis(long, CLAIMS, SUPPORTED, self.corroboration)['telegram_summary']
        self.assertLessEqual(len(summary), 600)
        self.assertTrue(summary.endswith('not stated as fact.'))

    def test_artifact_dict_is_loaded_with_from_dict(self):
        from_artifact = validate_synthesis(MODEL_OUTPUT, CLAIMS, SUPPORTED, self.corroboration.to_dict())
        self.assertEqual(from_artifact['knowledge_candidates'], self.synthesis()['knowledge_candidates'])
        with self.assertRaises(ValueError):
            validate_synthesis(MODEL_OUTPUT, CLAIMS, SUPPORTED, {'schema': 'something-else'})

    def test_without_corroboration_behaviour_is_unchanged(self):
        result = self.synthesis(corroboration=None)
        self.assertEqual([c['claim_id'] for c in result['knowledge_candidates']], ['C1', 'C2', 'C3'])
        self.assertIn('within 30 days', result['telegram_summary'])
        report = self.render(result, corroboration=None)
        self.assertIn('No independent corroboration from other sources was performed.', report)
        self.assertIn('NOT CHECKED', report)

    def test_report_renders_support_and_contradiction_side_by_side(self):
        report = self.render(self.synthesis())
        evidence = report.split('## Evidence and Citations')[1].split('## Verification Assessment')[0]
        c3 = evidence.split('### C3')[1]
        self.assertIn('| Supporting (independent) | Contradicting |', c3)
        self.assertIn('| "' + SUPPORT + '" — <' + SUPPORT_URL + '> | "' + CONTRA + '" — <' + CONTRA_URL + '> |', c3)
        c1 = evidence.split('### C1')[1].split('### C2')[0]
        self.assertIn('CONTRADICTED by discovered source(s)', c1)
        self.assertIn('| — | "' + CONTRA + '" — <' + CONTRA_URL + '> |', c1)
        # Citations show URL and passage only: no discovery IDs, hashes or publisher internals.
        self.assertNotIn('f' * 64, report)
        self.assertNotIn('D2', evidence)

        assessment = report.split('## Verification Assessment')[1].split('## Implications')[0]
        self.assertIn('| Finding | Corroboration | Supporting (independent) | Contradicting |', assessment)
        self.assertIn('| C3 | disputed | "' + SUPPORT + '" — <' + SUPPORT_URL + '> | "' + CONTRA + '" — <' + CONTRA_URL + '> |', assessment)
        self.assertIn('1 original_source_only, 1 disputed, 1 contradicted', assessment)
        self.assertIn('Contradicted or disputed: C1, C3', assessment)
        self.assertNotIn('No independent corroboration from other sources was performed.', report)
        self.assertIn('Lexical stance matching only.', report.split('## Limitations')[1])

    def test_original_source_only_and_unverified_are_never_presented_as_corroborated(self):
        corroboration = result_for(CLAIMS, ['original_source_only', 'unverified', 'not_assessable'])
        report = self.render(validate_synthesis(MODEL_OUTPUT, CLAIMS, SUPPORTED, corroboration), corroboration)
        self.assertNotIn('CORROBORATED by independent', report)
        self.assertIn('ORIGINAL SOURCE ONLY — not independently corroborated', report)
        self.assertIn('UNVERIFIED — no independent check completed', report)
        self.assertNotIn('| Supporting (independent) |', report)   # no citations to show
        candidates = report.split('## Knowledge Candidates')[1].split('##')[0]
        self.assertIn('(corroboration: original_source_only)', candidates)
        self.assertNotIn('corroboration: corroborated', candidates)

    def test_report_excludes_conflicted_knowledge_candidates_even_if_synthesis_listed_them(self):
        synthesis = self.synthesis(corroboration=None)                  # model listed C1..C3
        candidates = self.render(synthesis).split('## Knowledge Candidates')[1].split('## Sources')[0]
        self.assertNotIn('[C1]', candidates)
        self.assertNotIn('[C3]', candidates)
        self.assertIn('[C2] api', candidates)
        self.assertIn('Excluded as contradicted or disputed: C1, C3.', candidates)


class EngineSynthesisCorroborationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'article.txt'
        self.source.write_text(ARTICLE)

    def tearDown(self):
        self.temp.cleanup()

    def test_engine_passes_stored_corroboration_to_synthesis_prompt_report_and_summary(self):
        seen = {}

        def corroborate(sources, claims, support, directory):
            seen['claims'] = claims
            return result_for(claims, ['contradicted'] + ['corroborated'] * (len(claims) - 1))

        def synthesis(request):
            seen['prompt'] = request['messages'][0]['content']
            seen['system'] = request['system'] if isinstance(request['system'], str) else str(request['system'])
            statement = seen['claims'][0]['statement'].replace('The source says ', '')
            return dict(MODEL_OUTPUT, important_findings=[{'point': 'Lead finding', 'claim_ids': ['C1']}],
                        knowledge_candidates=[{'claim_id': c['claim_id'], 'note': 'n'} for c in seen['claims']],
                        telegram_summary=statement + '. Other findings were corroborated.')

        engine = ResearchEngine(self.root / 'state', claude_client=FakeClaude(DIRECTOR, good_specialist, synthesis))
        with patch('alfred_research.local.engine.corroborate', corroborate):
            job = engine.run(engine.submit('Summarize the obligations and the API', [str(self.source)], provider='claude'))
        self.assertEqual(job['status'], 'needs_more_research', job.get('error'))   # a contradicted claim is never "completed"
        self.assertIn('&quot;corroboration&quot;: &quot;contradicted&quot;', seen['prompt'])
        self.assertIn('must never be stated as fact', seen['system'])

        synthesis_artifact = job['artifacts']['synthesis']
        self.assertNotIn('C1', [c['claim_id'] for c in synthesis_artifact['knowledge_candidates']])
        self.assertTrue(synthesis_artifact['important_findings'][0]['point'].startswith('(Contradicted by other sources)'))
        summary = job['artifacts']['telegram-summary']['text']
        self.assertNotIn(seen['claims'][0]['statement'].replace('The source says ', '')[:60], summary)
        self.assertIn('(C1); not stated as fact.', summary)

        report = job['artifacts']['report']['text']
        self.assertIn(CONTRA_URL, report)
        self.assertIn('CONTRADICTED by discovered source(s)', report)
        self.assertNotIn('[C1]', report.split('## Knowledge Candidates')[1].split('## Sources')[0])
        message = final_message(job)
        self.assertIn('independently corroborated, 1 contradicted or disputed.', message)
        self.assertNotIn('not independently corroborated', message)


if __name__ == '__main__':
    unittest.main()
