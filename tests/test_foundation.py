"""Offline acceptance tests: synthetic principals/data, temporary SQLite only."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from alfred_research.contracts import *
from alfred_research.tenancy import AuthenticatedContext, AuthorizationError, OfflineAuthority
from alfred_research.budgets import EscalationRequired, ModelConfiguration
from alfred_research.state import ResearchStore
from alfred_research.registration import OfflineRegistrationAuthority
from alfred_research.verification import validate_decision


def source(env='personal'):
    return SourceIdentity(source_id='s1', environment=env, kind='github', locator='fixture://synthetic',
                          revision='synthetic-commit-1', content_digest='a' * 64)


def request(env, request_id='r1'):
    return ResearchRequest(request_id=request_id, environment=env, requested_by=env + '-researcher',
                           objective='Analyze synthetic fixture only', sources=(source(env),))


def packet(env, task_id='t1'):
    return ResearchPacket(packet_id='p1', task_id=task_id, environment=env, scope=env,
                          classification='internal', researcher=env + '-researcher',
                          researcher_model='synthetic-researcher', researcher_provider='synthetic', packet_version=1, source=source(env),
                          claims=(Claim(claim_id='c1', environment=env, statement='Synthetic claim',
                                        evidence_ids=('e1',)),),
                          evidence=(Evidence(evidence_id='e1', environment=env, source_id='s1',
                                             location='fixture:line1', content_digest='b' * 64),))


class FoundationFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.network = patch.object(socket, 'socket', side_effect=AssertionError('network forbidden'))
        self.network.start()
        self.addCleanup(self.network.stop)
        self.authority = OfflineAuthority({f'{env}-{role}': (env, role)
                                           for env in ENVIRONMENTS for role in ROLES})
        self.contexts = {(env, role): self.authority.context(f'{env}-{role}')
                         for env in ENVIRONMENTS for role in ROLES}
        self.assignments = tuple(ModelAssignment(environment=env, specialist=role,
                                                 provider='synthetic', model='synthetic-' + role,
                                                 price_units=2)
                                 for env in ENVIRONMENTS for role in ROLES)
        self.models = ModelConfiguration(self.assignments)
        self.registrations = OfflineRegistrationAuthority(self.authority, self.temp.name, test_only=True)
        self.store = self.reopen()

    def reopen(self):
        return ResearchStore(self.temp.name, self.authority, self.models,
                             budget_limits={env: 20 for env in ENVIRONMENTS}, registration_authority=self.registrations)

    def ctx(self, env='personal', role='researcher'):
        return self.contexts[env, role]

    def provision(self, env='personal'):
        from contextlib import closing
        from alfred_research.persistence import open_database
        with closing(open_database(Path(self.temp.name) / env / 'research.sqlite3', env,
                                   registration_authority=self.registrations,
                                   context=self.ctx(env, 'director'))):
            pass

    def advance(self, env='personal'):
        self.provision(env)
        task = self.store.submit(self.ctx(env), request(env))
        for before, after in [('received', 'collecting'), ('collecting', 'researching')]:
            task = self.store.transition(self.ctx(env), task.task_id, before, after)
        return task

    def decision(self, p, verdict='APPROVED'):
        return VerificationDecision(decision_id='d1', environment=p.environment,
                                    packet_digest=p.digest, verifier=p.environment + '-verifier',
                                    verifier_model='synthetic-verifier', verifier_provider='synthetic', verdict=verdict, rationale='Fixture check')


class FoundationTests(FoundationFixture):
    def setUp(self):
        super().setUp()
        # This negative test intentionally verifies a completely untouched root.
        if self._testMethodName != 'test_forged_and_foreign_authority_contexts':
            for env in ENVIRONMENTS:
                self.provision(env)

    def test_valid_durable_request_all_environments(self):
        for env in ENVIRONMENTS:
            with self.subTest(env=env):
                task = self.store.submit(self.ctx(env), request(env))
                self.assertEqual(self.reopen().get_task(self.ctx(env), task.task_id), task)
                self.assertTrue((Path(self.temp.name) / env / 'research.sqlite3').exists())

    def test_duplicate_request_one_effect_all_environments(self):
        for env in ENVIRONMENTS:
            task = self.store.submit(self.ctx(env), request(env))
            self.assertEqual(self.store.submit(self.ctx(env), request(env)), task)
            events = self.store.audit_history(self.ctx(env))
            self.assertEqual(sum(e.operation == 'task.created' for e in events), 1)

    def test_concurrent_duplicate_requests(self):
        # Initialize schema before competing transactions.
        self.store.recover(self.ctx())
        with ThreadPoolExecutor(max_workers=4) as pool:
            tasks = list(pool.map(lambda _: self.reopen().submit(self.ctx(), request('personal')), range(12)))
        self.assertEqual(len({t.task_id for t in tasks}), 1)

    def test_conflicting_idempotency_key(self):
        self.store.submit(self.ctx(), request('personal'))
        with self.assertRaises(ContractError):
            self.store.submit(self.ctx(), replace(request('personal'), objective='changed'))

    def test_unknown_environment(self):
        with self.assertRaises(ContractError):
            request('unknown')

    def test_forged_and_foreign_authority_contexts(self):
        forged = replace(self.ctx(), environment='fintra')
        other = OfflineAuthority({'personal-researcher': ('personal', 'researcher')})
        for ctx in (forged, replace(self.ctx()), other.context('personal-researcher')):
            with self.assertRaises(AuthorizationError):
                self.store.recover(ctx)
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])

    def test_forged_request_identity(self):
        with self.assertRaises(AuthorizationError):
            self.store.submit(self.ctx(), request('fintra'))
        with self.assertRaises(AuthorizationError):
            self.store.submit(self.ctx(), replace(request('personal'), requested_by='attacker'))

    def test_cross_environment_read_write_denied(self):
        for owner in ENVIRONMENTS:
            task = self.store.submit(self.ctx(owner), request(owner))
            for attacker in ENVIRONMENTS:
                if attacker == owner:
                    continue
                with self.assertRaises(AuthorizationError):
                    self.store.get_task(self.ctx(attacker), task.task_id)
                with self.assertRaises(AuthorizationError):
                    self.store.transition(self.ctx(attacker), task.task_id, 'received', 'collecting')
            self.assertEqual(self.store.get_task(self.ctx(owner), task.task_id).state, 'received')

    def test_invalid_and_duplicate_transitions_are_atomic(self):
        task = self.store.submit(self.ctx(), request('personal'))
        for target in ('approved', 'unknown'):
            with self.assertRaises(ContractError):
                self.store.transition(self.ctx(), task.task_id, 'received', target)
        task = self.store.transition(self.ctx(), task.task_id, 'received', 'collecting')
        with self.assertRaises(ContractError):
            self.store.transition(self.ctx(), task.task_id, 'received', 'collecting')
        self.assertEqual(self.store.get_task(self.ctx(), task.task_id), task)

    def test_retry_bound_and_recovery_idempotence(self):
        for env in ENVIRONMENTS:
            task = self.advance(env)
            for attempt in range(3):
                self.store.retry(self.ctx(env), task.task_id, 'retry-' + str(attempt))
            with self.assertRaises(EscalationRequired):
                self.store.retry(self.ctx(env), task.task_id, 'exhausted')
            first = self.reopen().recover(self.ctx(env))
            self.assertEqual(self.reopen().recover(self.ctx(env)), first)
            self.assertEqual(first[0].retries, 3)

    def test_process_crash_preserves_commit_and_rolls_back_uncommitted(self):
        # Parent commits through the authorized store; child crashes during deletion.
        committed = self.store.submit(self.ctx(), replace(request('personal'), request_id='crash'))
        code = '''
import os, sys, socket, json
def blocked(*args, **kwargs):
    raise AssertionError('network forbidden')
socket.socket = blocked
sys.path.insert(0, sys.argv[2])
from alfred_research.tenancy import OfflineAuthority
from alfred_research.budgets import ModelConfiguration
from alfred_research.state import ResearchStore
from alfred_research.registration import OfflineRegistrationAuthority
from alfred_research.contracts import ResearchRequest, SourceIdentity
a = OfflineAuthority({'test': ('personal','researcher')})
c = a.context('test')
registrations = OfflineRegistrationAuthority.from_test_snapshot(a,sys.argv[1],json.loads(sys.stdin.read()),test_only=True)
s = ResearchStore(sys.argv[1],a,ModelConfiguration(),budget_limits={'personal':20},registration_authority=registrations)
t = s.get_task(c,sys.argv[3])
with s._transaction(c) as db:
    db.execute('DELETE FROM tasks')
    os._exit(23)
'''
        result = subprocess.run([sys.executable, '-c', code, self.temp.name,
                                 str(Path(__file__).resolve().parents[1] / 'src'), committed.task_id],
                                input=json.dumps(self.registrations.snapshot_for_tests()), text=True, check=False)
        self.assertEqual(result.returncode, 23)
        tasks = self.reopen().recover(self.ctx())
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].request.request_id, 'crash')
        self.assertEqual(tasks[0].state, 'received')

    def test_audit_failure_rolls_back_task_creation(self):
        with patch.object(self.store, '_audit', side_effect=RuntimeError('simulated crash')):
            with self.assertRaises(RuntimeError):
                self.store.submit(self.ctx(), request('personal'))
        self.assertEqual(self.store.recover(self.ctx()), ())

    def test_outbox_restart_duplicate_and_delivery(self):
        for env in ENVIRONMENTS:
            task = self.store.submit(self.ctx(env), request(env))
            event = OutboxEvent(event_id='o1', environment=env, task_id=task.task_id,
                                topic='future.delivery', payload_digest='d' * 64)
            self.store.enqueue(self.ctx(env), event)
            self.assertEqual(self.reopen().outbox(self.ctx(env)), (event,))
            self.assertEqual(self.store.enqueue(self.ctx(env), event), event)
            delivered = self.store.record_delivery(self.ctx(env, 'director'), 'o1', delivered=True)
            self.assertEqual(self.store.record_delivery(self.ctx(env, 'director'), 'o1', delivered=True), delivered)
            with self.assertRaises(ContractError):
                self.store.enqueue(self.ctx(env), replace(event, topic='changed'))

    def test_outbox_bounded_failures(self):
        task = self.store.submit(self.ctx(), request('personal'))
        event = OutboxEvent(event_id='o', environment='personal', task_id=task.task_id,
                            topic='fake', payload_digest='d' * 64)
        self.store.enqueue(self.ctx(), event)
        for _ in range(3):
            last = self.store.record_delivery(self.ctx(role='director'), 'o', delivered=False)
        self.assertEqual(last.state, 'exhausted')
        with self.assertRaises(ContractError):
            self.store.record_delivery(self.ctx(role='director'), 'o', delivered=False)

    def test_packet_roundtrip_and_determinism(self):
        for env in ENVIRONMENTS:
            p = packet(env)
            encoded = p.payload()
            decoded = ResearchPacket.from_payload(json.loads(canonical(encoded)))
            self.assertEqual(decoded, p)
            self.assertEqual(decoded.digest, p.digest)
            self.assertEqual(canonical({'a': 1, 'b': 2}), canonical({'b': 2, 'a': 1}))

    def test_all_approved_content_changes_digest(self):
        p = packet('gabos')
        changes = [replace(p, claims=(replace(p.claims[0], statement='new'),)),
                   replace(p, evidence=(replace(p.evidence[0], content_digest='f' * 64),)),
                   replace(p, evidence=(replace(p.evidence[0], location='line2'),)),
                   replace(p, source=replace(p.source, revision='new-commit')),
                   replace(p, classification='confidential'),
                   replace(p, limitations=('new limit',)),
                   replace(p, packet_version=2), packet('fintra')]
        for changed in changes:
            self.assertNotEqual(p.digest, changed.digest)
        payload = p.payload()
        payload['version'] = 2
        self.assertNotEqual(hash_content(payload), p.digest)

    def test_verification_independence_and_stale_decision(self):
        for env in ENVIRONMENTS:
            task = self.advance(env)
            p = packet(env, task.task_id)
            self.store.put_packet(self.ctx(env), p)
            decision = self.decision(p)
            with self.assertRaises(AuthorizationError):
                self.store.verify(self.ctx(env), task.task_id,
                                  replace(decision, verifier=env + '-researcher'))
            # Explicit same-principal check, even when verifier has the correct role.
            same = replace(p, researcher=env + '-verifier')
            with self.assertRaises(AuthorizationError):
                validate_decision(self.authority, self.ctx(env, 'verifier'), same,
                                  replace(decision, packet_digest=same.digest))
            p2 = replace(p, packet_version=2, claims=(replace(p.claims[0], statement='updated'),))
            self.store.put_packet(self.ctx(env), p2)
            with self.assertRaises(ContractError):
                self.store.verify(self.ctx(env, 'verifier'), task.task_id, decision)
            approved = replace(decision, packet_digest=p2.digest)
            result = self.store.verify(self.ctx(env, 'verifier'), task.task_id, approved)
            self.assertEqual(result.state, 'approved')
            self.assertEqual(self.store.verify(self.ctx(env, 'verifier'), task.task_id, approved), result)
            with self.assertRaises(ContractError):
                self.store.put_packet(self.ctx(env), replace(p2, packet_version=3))

    def test_verification_wrong_tenant_and_principal(self):
        p = packet('gabos')
        for ctx, decision in [(self.ctx('fintra', 'verifier'), self.decision(p)),
                              (self.ctx('gabos', 'verifier'), replace(self.decision(p), verifier='fake'))]:
            with self.assertRaises(AuthorizationError):
                validate_decision(self.authority, ctx, p, decision)

    def test_rejected_and_more_research_outcomes(self):
        for env, verdict in [('personal', 'REJECTED'), ('gabos', 'NEEDS_MORE_RESEARCH')]:
            task = self.advance(env)
            p = packet(env, task.task_id)
            self.store.put_packet(self.ctx(env), p)
            result = self.store.verify(self.ctx(env, 'verifier'), task.task_id, self.decision(p, verdict))
            self.assertEqual(result.state, verdict.lower())

    def test_budget_exhaustion_isolated_and_durable(self):
        for env in ENVIRONMENTS:
            self.store.reserve(self.ctx(env), 'b1', 'researcher', 'synthetic', 'synthetic-researcher', 10)
            with self.assertRaises(EscalationRequired):
                self.reopen().reserve(self.ctx(env), 'b2', 'researcher', 'synthetic', 'synthetic-researcher', 1)
            self.reopen().settle(self.ctx(env), 'b1', 20)
            with self.assertRaises(EscalationRequired):
                self.reopen().reserve(self.ctx(env), 'b3', 'researcher', 'synthetic', 'synthetic-researcher', 1)

    def test_budget_cancel_reconcile_and_duplicate(self):
        first = self.store.reserve(self.ctx(), 'b1', 'researcher', 'synthetic', 'synthetic-researcher', 10)
        self.assertEqual(self.store.reserve(self.ctx(), 'b1', 'researcher', 'synthetic', 'synthetic-researcher', 10), first)
        with self.assertRaises(EscalationRequired):
            self.store.settle(self.ctx(), 'b1', 21)
        self.store.settle(self.ctx(), 'b1', 4)
        self.store.reserve(self.ctx(), 'b2', 'researcher', 'synthetic', 'synthetic-researcher', 8)
        self.store.settle(self.ctx(), 'b2', 0, cancel=True)
        self.store.reserve(self.ctx(), 'b3', 'researcher', 'synthetic', 'synthetic-researcher', 8)
        with self.assertRaises(ContractError):
            self.store.settle(self.ctx(), 'b1', 0, cancel=True)

    def test_budget_cross_environment_and_principal_denied(self):
        self.store.reserve(self.ctx('gabos'), 'b1', 'researcher', 'synthetic', 'synthetic-researcher', 2)
        with self.assertRaises(ContractError):
            self.store.settle(self.ctx('fintra'), 'b1', 0)
        with self.assertRaises(AuthorizationError):
            self.store.settle(self.ctx('gabos', 'director'), 'b1', 0)

    def test_budget_concurrent_reservations_cannot_overspend(self):
        self.store.recover(self.ctx())
        def reserve(i):
            try:
                self.reopen().reserve(self.ctx(), str(i), 'researcher', 'synthetic', 'synthetic-researcher', 6)
                return True
            except EscalationRequired:
                return False
        with ThreadPoolExecutor(max_workers=4) as pool:
            self.assertEqual(sum(pool.map(reserve, range(4))), 1)

    def test_model_substitution_and_missing_configuration(self):
        for provider, model in [('other', 'synthetic-researcher'), ('synthetic', 'other')]:
            with self.assertRaises(EscalationRequired):
                self.store.reserve(self.ctx(), 'b', 'researcher', provider, model, 1)
        config = ModelConfiguration(production=True)
        with self.assertRaises(EscalationRequired):
            config.resolve('personal', 'researcher', 'synthetic', 'synthetic-researcher')
        with self.assertRaises(EscalationRequired):
            ModelConfiguration(self.assignments, production=True)
        approved = ModelConfiguration((replace(self.assignments[0], approved=True),), production=True)
        with self.assertRaises(EscalationRequired):
            approved.resolve('personal', 'director', 'synthetic', 'synthetic-director')
        with self.assertRaises(ContractError):
            ModelConfiguration((self.assignments[0], self.assignments[0]))

    def test_budget_policy_change_denied(self):
        self.store.reserve(self.ctx(), 'b', 'researcher', 'synthetic', 'synthetic-researcher', 1)
        changed = ResearchStore(self.temp.name, self.authority, self.models, budget_limits={'personal': 200}, registration_authority=self.registrations)
        with self.assertRaises(ContractError):
            changed.reserve(self.ctx(), 'b2', 'researcher', 'synthetic', 'synthetic-researcher', 1)

    def test_audit_environment_and_operation(self):
        for env in ENVIRONMENTS:
            self.advance(env)
            events = self.store.audit_history(self.ctx(env))
            self.assertTrue(all(e.environment == env and e.principal == env + '-researcher' for e in events))
            self.assertEqual(len({e.event_id for e in events}), len(events))
            self.assertIn('task.created', [e.operation for e in events])
            self.assertIn('task.transition.researching', [e.operation for e in events])

    def test_malformed_and_ambiguous_contracts(self):
        for sources in ((), (source(), source()), [source()]):
            with self.assertRaises(ContractError):
                replace(request('personal'), sources=sources)
        for changes in ({'version': 2}, {'max_retries': True}, {'max_retries': -1}, {'objective': ''}):
            with self.assertRaises(ContractError):
                replace(request('personal'), **changes)
        for value in ('x', 'A' * 64):
            with self.assertRaises(ContractError):
                replace(source(), content_digest=value)
        for changes in ({'scope': 'fintra'}, {'evidence': ()},
                        {'claims': (replace(packet('personal').claims[0], environment='fintra'),)}):
            with self.assertRaises(ContractError):
                replace(packet('personal'), **changes)
        with self.assertRaises(ContractError):
            replace(request('personal'), sources=(source('fintra'),))
        with self.assertRaises(ContractError):
            ResearchRequest.from_json('{"schema":"request.v1","schema":"request.v1"}')
        self.assertEqual(ResearchRequest.from_json(canonical(request('personal')).decode()), request('personal'))
        raw = request('personal').payload()
        for change in ({**raw, 'unknown': 1}, {**raw, 'schema': 'request.v2'}):
            with self.assertRaises(ContractError):
                ResearchRequest.from_payload(change)
        with self.assertRaises(ContractError):
            canonical({'bad': float('nan')})

    def test_rework_cannot_bypass_retry_budget(self):
        task = self.advance()
        p = packet('personal', task.task_id)
        for iteration in range(4):
            p = replace(p, packet_version=iteration + 1)
            self.store.put_packet(self.ctx(), p)
            decision = replace(self.decision(p, 'NEEDS_MORE_RESEARCH'), decision_id=str(iteration))
            self.store.verify(self.ctx(role='verifier'), task.task_id, decision)
        with self.assertRaises(EscalationRequired):
            self.store.put_packet(self.ctx(), replace(p, packet_version=5))
        with self.assertRaises(EscalationRequired):
            self.store.transition(self.ctx(), task.task_id, 'needs_more_research', 'researching')
        self.assertEqual(self.store.get_task(self.ctx(), task.task_id).retries, 3)

    def test_recorded_model_substitution_rejected(self):
        task = self.advance()
        p = packet('personal', task.task_id)
        with self.assertRaises(EscalationRequired):
            self.store.put_packet(self.ctx(), replace(p, researcher_model='other'))
        self.store.put_packet(self.ctx(), p)
        with self.assertRaises(EscalationRequired):
            self.store.verify(self.ctx(role='verifier'), task.task_id,
                              replace(self.decision(p), verifier_provider='other'))
        self.assertEqual(self.store.get_task(self.ctx(), task.task_id).state, 'awaiting_verification')

    def test_model_role_escalation_rejected(self):
        with self.assertRaises(EscalationRequired):
            self.store.reserve(self.ctx(), 'b', 'verifier', 'synthetic', 'synthetic-verifier', 1)

    def test_no_network_access(self):
        with self.assertRaisesRegex(AssertionError, 'network forbidden'):
            socket.socket()
        self.assertEqual(self.store.submit(self.ctx(), request('personal')).state, 'received')


if __name__ == '__main__':
    unittest.main()
