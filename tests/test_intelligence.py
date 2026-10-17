"""Phase 4 offline catalog acceptance, using actual Phase 3 approvals."""
import test_research as foundation
from alfred_research.intelligence import IntelligenceOrganizer, SPECIALISTS, Proposal
from alfred_research.intelligence.service import classify
from alfred_research.contracts import ENVIRONMENTS, ContractError, hash_content
from alfred_research.tenancy import AuthorizationError
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import unittest

class IntelligenceTests(unittest.TestCase):
    setUp = foundation.ResearchTests.setUp
    ctx = foundation.ResearchTests.ctx
    task = foundation.ResearchTests.task
    runtime = foundation.ResearchTests.runtime
    start = foundation.ResearchTests.start
    review = foundation.ResearchTests.review

    def approved(self, env='personal', text='React UI patterns', request_id='request'):
        task, source = self.task(env, text=text, request_id=request_id)
        director, verifier = self.runtime()
        _, _, packet = self.start(task, source, director=director)
        self.assertEqual(self.review(verifier, packet).verdict, 'APPROVED')
        return packet

    def organizer(self):
        return IntelligenceOrganizer(self.store, clock=lambda: self.now)

    def process(self, organizer, packet, op='op', **kwargs):
        return organizer.process(self.ctx(packet.environment), packet.task_id, packet.packet_version, packet.digest, op, **kwargs)

    def test_all_eleven_specialists_and_secondary(self):
        examples = ('React UI', 'API backend', 'full-stack', 'devops deployment', 'ETL pipeline',
                    'forecast statistics', 'model evaluation', 'connector integration', 'threat security',
                    'android mobile', 'latency performance')
        for specialist, text in zip(SPECIALISTS, examples):
            self.assertIn(specialist, classify(text).specialists)
        classification = classify('React API threat')
        self.assertEqual(classification.primary, 'Development: Frontend')
        self.assertEqual(classification.specialists, ('Frontend', 'Backend', 'Security'))
        self.assertTrue(classify('unclassified capability').escalation)

    def test_categories_and_environment_extensions(self):
        for text, category in (('tax', 'Taxes'), ('compliance', 'Legal and Compliance'),
            ('accounting', 'Finance and Accounting'), ('operations', 'Business Operations'),
            ('marketing', 'Sales and Marketing'), ('personal', 'Personal Research')):
            self.assertEqual(classify(text).primary, category)
        packet = self.approved()
        organizer = IntelligenceOrganizer(self.store, clock=lambda: self.now, extensions={'personal': ('Custom',)})
        self.assertEqual(self.process(organizer, packet, primary='Custom').record.classification.primary, 'Custom')
        with self.assertRaises(ContractError):
            self.process(organizer, packet, 'bad', primary='Unknown')

    def test_multiple_views_and_simulation_only(self):
        packet = self.approved(text='React API threat')
        organizer = self.organizer()
        batch = self.process(organizer, packet)
        for specialist in ('Frontend', 'Backend', 'Security'):
            self.assertEqual(organizer.views(self.ctx(), 'personal', specialist, simulated=True), (batch.record,))
        self.assertFalse(batch.record.memory_eligible)
        self.assertEqual(batch.record.packet.digest, packet.digest)
        self.assertEqual(batch.record.source.submitted, packet.source)
        with self.assertRaises(ContractError):
            organizer.views(self.ctx(), 'personal', 'Frontend')
        self.assertTrue(all(p.status == 'PROPOSAL_ONLY' and p.approval_required for p in batch.proposals))
        self.assertTrue(all(p.source_digest == batch.record.source.digest for p in batch.proposals))

    def test_exact_duplicates_replay_and_distinct_related(self):
        organizer = self.organizer()
        packet = self.approved()
        original = self.process(organizer, packet)
        self.assertEqual(original, self.process(organizer, packet))
        duplicate = self.process(organizer, packet, 'duplicate')
        self.assertEqual(duplicate.relation, 'DUPLICATE')
        self.assertEqual(duplicate.record, original.record)
        self.assertEqual(duplicate.proposals, ())
        other = self.approved(text='React different patterns', request_id='different')
        related = self.process(organizer, other, 'related', relation='RELATED', targets=(original.record.record_id,))
        self.assertNotEqual(related.record.exact_identity, original.record.exact_identity)
        with self.assertRaises(ContractError):
            self.process(organizer, other)

    def test_corrections_history_cas_and_expiry(self):
        organizer = self.organizer()
        first = self.process(organizer, self.approved())
        second_packet = self.approved(text='React corrected patterns', request_id='correct')
        second = self.process(organizer, second_packet, 'correct', relation='CORRECTION',
            targets=(first.record.record_id,), expected_head=hash_content(first.record), valid_until=1002)
        self.assertEqual(organizer._status(first.record, organizer.history(self.ctx(), 'personal')), 'SUPERSEDED')
        with self.assertRaises(ContractError):
            self.process(organizer, second_packet, 'stale', relation='UPDATE', targets=(first.record.record_id,), expected_head=hash_content(first.record))
        self.now = 1003
        self.assertEqual(organizer.views(self.ctx(), 'personal', 'Frontend', simulated=True), ())
        restored = self.organizer()
        self.assertEqual(len(restored.history(self.ctx(), 'personal')), 2)
        self.assertEqual(restored.history(self.ctx(), 'personal')[0].record, first.record)
        self.assertEqual(second.proposals[0].status, 'PROPOSAL_ONLY')

    def test_conflicts_have_no_winner(self):
        organizer = self.organizer()
        first = self.process(organizer, self.approved())
        second = self.process(organizer, self.approved(text='React unsafe patterns', request_id='conflict'), 'conflict',
                              relation='CONFLICT', targets=(first.record.record_id,))
        for record in (first.record, second.record):
            self.assertIn('human escalation', organizer._status(record, organizer.history(self.ctx(), 'personal')))
        self.assertEqual(organizer.views(self.ctx(), 'personal', 'Frontend', simulated=True), ())

    def test_concurrent_replay_and_outbox_repair(self):
        organizer = self.organizer()
        packet = self.approved()
        with patch.object(self.store, 'enqueue', side_effect=RuntimeError('crash before outbox')):
            with self.assertRaises(RuntimeError):
                self.process(organizer, packet)
        with ThreadPoolExecutor(max_workers=4) as pool:
            rows = list(pool.map(lambda _: self.process(self.organizer(), packet), range(8)))
        self.assertTrue(all(row == rows[0] for row in rows))
        organizer.reconcile(self.ctx())
        self.assertEqual(len(organizer.history(self.ctx(), 'personal')), 1)
        events = [e for e in self.store.outbox(self.ctx()) if e.topic == 'offline.intelligence.proposal']
        self.assertEqual(len(events), 1)

    def test_all_twelve_cross_environment_pairs(self):
        organizer = self.organizer()
        packets = {env: self.approved(env) for env in ENVIRONMENTS}
        batches = {env: self.process(organizer, packet) for env, packet in packets.items()}
        for env in ENVIRONMENTS:
            for other in ENVIRONMENTS:
                if env == other:
                    continue
                packet = packets[other]
                for operation in (
                    lambda: organizer.history(self.ctx(env), other),
                    lambda: organizer.views(self.ctx(env), other, 'Frontend', simulated=True),
                    lambda: organizer.proposals(self.ctx(env), other),
                    lambda: organizer.status(self.ctx(env), other, batches[other].record.record_id),
                    lambda: organizer.process(self.ctx(env), packet.task_id, 1, packet.digest, 'forged'),
                    lambda: self.process(organizer, packets[env], 'cross', relation='CONFLICT', targets=(batches[other].record.record_id,))):
                    with self.assertRaises((AuthorizationError, ContractError, KeyError)):
                        operation()
        for role in ('general', 'verifier'):
            with self.assertRaises(AuthorizationError):
                organizer.process(self.ctx(identity=role), packets['personal'].task_id, 1, packets['personal'].digest, 'unauthorized')

    def test_unapproved_and_changed_packets_excluded(self):
        task, source = self.task(complete=False)
        director, verifier = self.runtime()
        _, _, packet = self.start(task, source, director=director)
        self.review(verifier, packet)
        with self.assertRaises(ContractError):
            self.process(self.organizer(), packet)
        approved = self.approved(request_id='approved')
        with self.assertRaises(ContractError):
            self.organizer().process(self.ctx(), approved.task_id, 1, '0' * 64, 'changed')

    def test_proposal_contract_cannot_authorize_execution(self):
        from dataclasses import replace
        batch = self.process(self.organizer(), self.approved())
        for change in ({'approval_required': False}, {'status': 'APPROVED'}):
            with self.assertRaises(ContractError):
                replace(batch.proposals[0], **change)

    def test_multiskill_capabilities_individually_evaluated(self):
        from alfred_research.sources import SourceProcessor, SourceFixture, FixtureFile
        from alfred_research.contracts import SourceIdentity, ResearchRequest
        fixture = SourceFixture(files=(FixtureFile('frontend/SKILL.md', b'React UI patterns'),
            FixtureFile('backend/SKILL.md', b'API backend patterns')), revision='a' * 40)
        source = SourceIdentity(source_id='multi', environment='personal', kind='github',
            locator='fixture://multi', revision=fixture.revision, content_digest=fixture.digest)
        request = ResearchRequest(request_id='multi', environment='personal', requested_by=self.ctx().principal,
                                  objective='Inspect repository', sources=(source,), max_retries=2)
        task = self.store.submit(self.ctx(), request)
        processor = SourceProcessor(self.authority)
        result = processor.process(self.ctx(), source, fixture, processor.grant(self.ctx(), self.ctx(), source))
        director, verifier = self.runtime()
        _, _, packet = self.start(task, result, director=director)
        self.assertEqual(self.review(verifier, packet).verdict, 'APPROVED')
        batch = self.process(self.organizer(), packet)
        pairs = {(p.capability, p.specialist) for p in batch.proposals}
        self.assertEqual(pairs, {('frontend/SKILL.md', 'Frontend'), ('backend/SKILL.md', 'Backend')})
        self.assertTrue(all(p.source_revision == ('a' * 40,) for p in batch.proposals))

    def test_fresh_process_reads_committed_history_and_proposals(self):
        import subprocess, sys, os
        packet = self.approved()
        batch = self.process(self.organizer(), packet)
        script = """
import sys
from test_research import bootstrap
from alfred_research.intelligence import IntelligenceOrganizer
_, contexts, _, _, store, _ = bootstrap(sys.argv[1])
o = IntelligenceOrganizer(store, clock=lambda: 1000)
c = contexts['personal-director']
rows = o.history(c, 'personal')
assert len(rows) == 1 and rows[0].record.record_id == sys.argv[2]
assert o.proposals(c, 'personal')[0].status == 'PROPOSAL_ONLY'
assert rows[0].record.packet.digest == sys.argv[3]
print('catalog restart verified')
"""
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH='src:tests')
        completed = subprocess.run([sys.executable, '-c', script, self.temp.name, batch.record.record_id, packet.digest],
                                   env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn('catalog restart verified', completed.stdout)

    def test_generic_department_and_profile_proposals_have_no_grants(self):
        from dataclasses import replace
        from alfred_research.intelligence.service import SpecialistProfileProposal
        proposal = self.process(self.organizer(), self.approved()).proposals[0]
        generic = replace(proposal, department='Finance', specialist='proposed:accounting')
        self.assertTrue(generic.approval_required)
        profile = SpecialistProfileProposal(environment='personal', specialist_id='proposed:accounting',
                                            categories=('Finance and Accounting',))
        with self.assertRaises(ContractError):
            replace(profile, deployment_enabled=True)

    def test_concurrent_corrections_cannot_overwrite_head(self):
        organizer = self.organizer()
        original = self.process(organizer, self.approved())
        packets = (self.approved(text='React update one', request_id='one'),
                   self.approved(text='React update two', request_id='two'))
        def update(index):
            try:
                return self.process(organizer, packets[index], str(index), relation='UPDATE',
                    targets=(original.record.record_id,), expected_head=hash_content(original.record))
            except ContractError:
                return None
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(update, (0, 1)))
        self.assertEqual(sum(r is not None for r in results), 1)
        self.assertEqual(len(organizer.history(self.ctx(), 'personal')), 2)

    def test_rejected_packet_never_enters_catalog(self):
        from alfred_research.research import SyntheticModelProvider, SyntheticFixture
        task, source = self.task()
        provider = SyntheticModelProvider(test_only=True, fixtures={
            f'personal/{task.task_id}/1/personal-verifier': SyntheticFixture(verdict='REJECTED')})
        director, verifier = self.runtime(verifier_provider=provider)
        _, _, packet = self.start(task, source, director=director)
        self.assertEqual(self.review(verifier, packet).verdict, 'REJECTED')
        organizer = self.organizer()
        with self.assertRaises(ContractError):
            self.process(organizer, packet)
        self.assertEqual(organizer.history(self.ctx(), 'personal'), ())

    def validity_snapshot(self, organizer, env='personal'):
        import sqlite3
        from contextlib import closing
        from pathlib import Path
        with closing(sqlite3.connect(Path(self.temp.name) / env / 'research.sqlite3')) as db:
            audit = db.execute('SELECT * FROM audit ORDER BY seq').fetchall()
            outbox = db.execute('SELECT * FROM outbox ORDER BY id').fetchall()
        return organizer.history(self.ctx(env), env), audit, outbox

    def test_invalid_duplicate_validity_has_no_effects(self):
        organizer = self.organizer()
        packet = self.approved()
        self.process(organizer, packet, valid_until=2000)
        before = self.validity_snapshot(organizer)
        for expiration in (-1, 0, True, '2000', None, 2000.0, 2**63, 1000, 999):
            for _ in range(2):
                with self.assertRaises(ContractError):
                    self.process(organizer, packet, 'invalid', valid_until=expiration)
                self.assertEqual(self.validity_snapshot(organizer), before)

    def test_expired_initial_request_does_not_provision_catalog(self):
        from alfred_research.intelligence.service import CATALOG
        organizer = self.organizer()
        packet = self.approved()
        before = self.validity_snapshot(organizer)
        directory = organizer.journal._directory(self.ctx(), CATALOG)
        self.assertFalse(directory.exists())
        with self.assertRaises(ContractError):
            self.process(organizer, packet, valid_until=1000)
        self.assertFalse(directory.exists())
        self.assertEqual(self.validity_snapshot(organizer), before)

    def test_review_exact_validity_conflict_reproduction(self):
        from alfred_research.intelligence.service import ValidityConflict
        organizer = self.organizer()
        packet = self.approved()
        original = self.process(organizer, packet, valid_until=2000)
        before = self.validity_snapshot(organizer)
        for expiration in (1001, 3000):
            for _ in range(2):
                with self.assertRaisesRegex(ValidityConflict, 'VALIDITY_CONFLICT'):
                    self.process(organizer, packet, 'conflicting', valid_until=expiration)
                self.assertEqual(self.validity_snapshot(organizer), before)
        self.now = 1002
        self.assertEqual(organizer.status(self.ctx(), 'personal', original.record.record_id), 'CURRENT')
        self.assertEqual(original.record.valid_until, 2000)  # rejected request cannot shorten history
        print('Validity diagnostic: 2000 -> 1001 explicitly conflicted; at 1002 original unchanged; -1 denied in regression')

    def test_identical_validity_duplicate_replay_and_expiry(self):
        organizer = self.organizer()
        packet = self.approved()
        original = self.process(organizer, packet, valid_until=1001)
        duplicate = self.process(organizer, packet, 'duplicate', valid_until=1001)
        self.assertEqual(duplicate.record, original.record)
        self.assertEqual(duplicate.proposals, ())
        self.assertEqual(self.process(organizer, packet, 'duplicate', valid_until=1001), duplicate)
        self.now = 1001
        self.assertEqual(organizer.views(self.ctx(), 'personal', 'Frontend', simulated=True), ())
        self.assertEqual(self.process(organizer, packet, 'duplicate', valid_until=1001), duplicate)
        self.assertEqual(len(organizer.history(self.ctx(), 'personal')), 2)

    def test_authorized_validity_revision_preserves_provenance(self):
        organizer = self.organizer()
        packet = self.approved()
        original = self.process(organizer, packet, valid_until=2000)
        revised = self.process(organizer, packet, 'revise-validity', relation='VALIDITY_UPDATE',
            targets=(original.record.record_id,), expected_head=hash_content(original.record), valid_until=1001)
        self.assertNotEqual(revised.record.record_id, original.record.record_id)
        for field in ('packet', 'source', 'decision_id', 'review_digest', 'environment', 'exact_identity'):
            self.assertEqual(getattr(revised.record, field), getattr(original.record, field))
        self.assertFalse(revised.record.memory_eligible)
        self.assertEqual(revised.proposals, ())
        self.assertEqual(organizer.status(self.ctx(), 'personal', original.record.record_id), 'SUPERSEDED')
        replay = self.process(self.organizer(), packet, 'revise-validity', relation='VALIDITY_UPDATE',
            targets=(original.record.record_id,), expected_head=hash_content(original.record), valid_until=1001)
        self.assertEqual(replay, revised)
        duplicate = self.process(organizer, packet, 'revised-duplicate', valid_until=1001)
        self.assertEqual(duplicate.record, revised.record)
        self.now = 1002
        self.assertEqual(organizer.views(self.ctx(), 'personal', 'Frontend', simulated=True), ())
        self.assertEqual(organizer.history(self.ctx(), 'personal')[0].record, original.record)

    def test_validity_revision_authorization_and_stale_head(self):
        organizer = self.organizer()
        packet = self.approved()
        original = self.process(organizer, packet, valid_until=2000)
        for identity in ('general', 'verifier'):
            with self.assertRaises(AuthorizationError):
                organizer.process(self.ctx(identity=identity), packet.task_id, 1, packet.digest, 'forged',
                    relation='VALIDITY_UPDATE', targets=(original.record.record_id,),
                    expected_head=hash_content(original.record), valid_until=1500)
        with self.assertRaises(ContractError):
            self.process(organizer, packet, 'stale', relation='VALIDITY_UPDATE',
                targets=(original.record.record_id,), expected_head='0' * 64, valid_until=1500)
        with self.assertRaises(ContractError):
            organizer.process(self.ctx(), packet.task_id, 1, '0' * 64, 'changed-evidence',
                relation='VALIDITY_UPDATE', targets=(original.record.record_id,),
                expected_head=hash_content(original.record), valid_until=1500)

    def test_concurrent_conflicting_duplicates_have_no_effects(self):
        from alfred_research.intelligence.service import ValidityConflict
        organizer = self.organizer()
        packet = self.approved()
        self.process(organizer, packet, valid_until=2000)
        before = self.validity_snapshot(organizer)
        def conflict(index):
            try:
                self.process(self.organizer(), packet, 'conflict-' + str(index), valid_until=1001 + index)
            except ValidityConflict:
                return True
            return False
        with ThreadPoolExecutor(max_workers=4) as pool:
            self.assertTrue(all(pool.map(conflict, range(8))))
        self.assertEqual(self.validity_snapshot(organizer), before)

    def test_duplicate_validity_remains_environment_local(self):
        organizer = self.organizer()
        batches = {}
        for index, env in enumerate(ENVIRONMENTS):
            batches[env] = self.process(organizer, self.approved(env), valid_until=2000 + index)
        self.assertEqual(len({b.record.record_id for b in batches.values()}), 4)
        for env, original in batches.items():
            self.assertEqual(len(organizer.history(self.ctx(env), env)), 1)
            self.assertEqual(original.record.environment, env)
            for other, foreign in batches.items():
                if env != other:
                    with self.assertRaises(ContractError):
                        organizer.process(self.ctx(env), original.record.research_task_id, 1, original.record.packet.digest,
                            'cross-validity', relation='VALIDITY_UPDATE', targets=(foreign.record.record_id,),
                            expected_head=hash_content(foreign.record), valid_until=1500)

if __name__ == '__main__':
    unittest.main()
