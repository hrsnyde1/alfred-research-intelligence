"""Regression tests for the independent Phase 1 readiness review findings."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from dataclasses import replace
from pathlib import Path
import sqlite3
import json
import subprocess
import sys
from unittest.mock import patch

import test_foundation as foundation
from alfred_research.contracts import ContractError, ENVIRONMENTS, OutboxEvent, canonical
from alfred_research.budgets import EscalationRequired
from alfred_research.persistence import (PersistenceError, SCHEMA_VERSION,
                                         UnsupportedSchemaError, open_database)
from alfred_research.state import ResearchStore
from alfred_research.registration import OfflineRegistrationAuthority
from alfred_research.tenancy import AuthorizationError


class CorrectionTests(foundation.FoundationFixture):
    def db_path(self, env='personal', root=None):
        return Path(root or self.temp.name) / env / 'research.sqlite3'

    def counts(self, env='personal'):
        with closing(sqlite3.connect(self.db_path(env))) as db:
            return {name: db.execute('SELECT count(*) FROM ' + name).fetchone()[0]
                    for name in ('retry_operations', 'packets', 'decisions', 'audit', 'outbox')}

    def snapshot(self, path):
        with closing(sqlite3.connect(path)) as db:
            return (path.read_bytes(), tuple(db.iterdump()),
                    tuple(db.execute('SELECT * FROM sqlite_master ORDER BY type,name')),
                    db.execute('PRAGMA schema_version').fetchone(),
                    db.execute('PRAGMA user_version').fetchone(),
                    db.execute('PRAGMA application_id').fetchone())

    def test_packet_history_and_exact_verdict_links_survive_restart(self):
        for env in ENVIRONMENTS:
            with self.subTest(env=env):
                task = self.advance(env)
                p1 = foundation.packet(env, task.task_id)
                self.store.put_packet(self.ctx(env), p1)
                d1 = self.decision(p1, 'NEEDS_MORE_RESEARCH')
                self.store.verify(self.ctx(env, 'verifier'), task.task_id, d1)
                p2 = replace(p1, packet_version=2, claims=(replace(p1.claims[0], statement='Revised fixture'),))
                self.store.put_packet(self.ctx(env), p2)
                restarted = self.reopen()
                self.assertEqual(restarted.packet_history(self.ctx(env), task.task_id), (p1, p2))
                self.assertEqual(restarted.get_packet(self.ctx(env), task.task_id), p2)
                self.assertEqual(restarted.get_packet(self.ctx(env), task.task_id, 1), p1)
                self.assertEqual(restarted.verification_history(self.ctx(env), task.task_id, 1), (d1,))
                self.assertEqual(restarted.verification_history(self.ctx(env), task.task_id, 2), ())
                with self.assertRaises(ContractError):
                    restarted.verify(self.ctx(env, 'verifier'), task.task_id, d1)
                d2 = replace(self.decision(p2), decision_id='d2')
                restarted.verify(self.ctx(env, 'verifier'), task.task_id, d2)
                self.assertEqual(self.reopen().verification_history(self.ctx(env), task.task_id), (d1, d2))
                self.assertEqual(self.reopen().get_packet(self.ctx(env), task.task_id, 1).digest, d1.packet_digest)
                with closing(sqlite3.connect(self.db_path(env))) as db:
                    rows = db.execute('SELECT task_id,packet_version,environment,digest,body FROM packets ORDER BY packet_version').fetchall()
                self.assertEqual(rows, [(task.task_id, p.packet_version, env, p.digest, canonical(p).decode())
                                        for p in (p1, p2)])

    def test_packet_replays_do_not_change_head_state_or_audit(self):
        task = self.advance()
        p1 = foundation.packet('personal', task.task_id)
        self.store.put_packet(self.ctx(), p1)
        p2 = replace(p1, packet_version=2, limitations=('revision',))
        self.store.put_packet(self.ctx(), p2)
        self.store.verify(self.ctx(role='verifier'), task.task_id, self.decision(p2))
        before = self.counts()
        self.assertEqual(self.store.put_packet(self.ctx(), p1), p1.digest)
        self.assertEqual(self.store.put_packet(self.ctx(), p2), p2.digest)
        self.assertEqual(self.counts(), before)
        self.assertEqual(self.store.get_packet(self.ctx(), task.task_id), p2)
        self.assertEqual(self.store.get_task(self.ctx(), task.task_id).state, 'approved')
        with self.assertRaises(ContractError):
            self.store.put_packet(self.ctx(), replace(p2, packet_version=3))

    def test_concurrent_duplicate_packet_revision_has_one_effect(self):
        task = self.advance()
        p = foundation.packet('personal', task.task_id)
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: self.reopen().put_packet(self.ctx(), p), range(12)))
        self.assertEqual(results, [p.digest] * 12)
        self.assertEqual(self.counts()['packets'], 1)
        recorded = [e for e in self.store.audit_history(self.ctx()) if e.operation == 'packet.recorded']
        self.assertEqual(len(recorded), 1)

    def test_concurrent_conflicting_and_stale_revisions_rejected(self):
        task = self.advance()
        p = foundation.packet('personal', task.task_id)
        self.store.put_packet(self.ctx(), p)
        candidates = [replace(p, packet_version=2, limitations=(label,)) for label in ('first', 'second')]
        def write(candidate):
            try:
                return self.reopen().put_packet(self.ctx(), candidate)
            except ContractError:
                return 'conflict'
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(write, candidates))
        self.assertEqual(results.count('conflict'), 1)
        winner = self.store.get_packet(self.ctx(), task.task_id)
        self.assertIn(winner, candidates)
        self.assertEqual(len(self.store.packet_history(self.ctx(), task.task_id)), 2)
        for stale in (replace(p, limitations=('overwriting v1',)), replace(p, packet_version=4)):
            with self.assertRaises(ContractError):
                self.store.put_packet(self.ctx(), stale)
        self.assertEqual(self.store.get_packet(self.ctx(), task.task_id), winner)

    def test_packet_and_verdict_storage_are_immutable(self):
        task = self.advance()
        p = foundation.packet('personal', task.task_id)
        self.store.put_packet(self.ctx(), p)
        self.store.verify(self.ctx(role='verifier'), task.task_id, self.decision(p))
        for table in ('packets', 'decisions'):
            for statement in ('UPDATE ' + table + " SET body='changed'", 'DELETE FROM ' + table):
                with self.assertRaises(PersistenceError):
                    with self.store._transaction(self.ctx()) as db:
                        db.execute(statement)
        self.assertEqual(self.store.get_packet(self.ctx(), task.task_id), p)
        self.assertEqual(self.store.verification_history(self.ctx(), task.task_id), (self.decision(p),))

    def test_verdict_foreign_key_requires_exact_revision_digest_and_environment(self):
        task = self.advance()
        p1 = foundation.packet('personal', task.task_id)
        p2 = replace(p1, packet_version=2)
        self.store.put_packet(self.ctx(), p1)
        self.store.put_packet(self.ctx(), p2)
        decision = self.decision(p1)
        # Each digest exists, but it must belong to the stated revision/tenant.
        for version, digest_value, env in ((2, p1.digest, 'personal'), (1, p1.digest, 'fintra')):
            with self.assertRaises(PersistenceError):
                with self.store._transaction(self.ctx(role='verifier')) as db:
                    db.execute('INSERT INTO decisions VALUES (?,?,?,?,?,?)',
                               ('bad-link', task.task_id, version, digest_value, env,
                                canonical(decision).decode()))
        self.assertEqual(self.store.verification_history(self.ctx(), task.task_id), ())

    def test_packet_revision_and_head_rollback_together(self):
        task = self.advance()
        p1 = foundation.packet('personal', task.task_id)
        self.store.put_packet(self.ctx(), p1)
        with patch.object(self.store, '_audit', side_effect=RuntimeError('transaction interrupted')):
            with self.assertRaises(RuntimeError):
                self.store.put_packet(self.ctx(), replace(p1, packet_version=2))
        self.assertEqual(self.reopen().packet_history(self.ctx(), task.task_id), (p1,))
        self.assertEqual(self.store.get_packet(self.ctx(), task.task_id), p1)

    def incompatible(self, variant):
        root = Path(self.temp.name) / variant
        path = self.db_path(root=root)
        path.parent.mkdir(parents=True)
        with closing(sqlite3.connect(path)) as db:
            with db:
                if variant == 'old_v1':
                    db.execute('CREATE TABLE metadata (version INTEGER PRIMARY KEY)')
                    db.execute('INSERT INTO metadata VALUES (1)')
                elif variant != 'missing_metadata':
                    db.execute('CREATE TABLE metadata (version INTEGER PRIMARY KEY, environment TEXT NOT NULL)')
                    db.execute('INSERT INTO metadata VALUES (?,?)',
                               (SCHEMA_VERSION if variant == 'malformed_v2' else 999, 'personal'))
                db.execute('CREATE TABLE private_fixture (id INTEGER PRIMARY KEY, value TEXT)')
                db.execute("INSERT INTO private_fixture VALUES (1,'preserve me')")
                db.execute('CREATE INDEX fixture_index ON private_fixture(value)')
                db.execute('CREATE VIEW fixture_view AS SELECT value FROM private_fixture')
                db.execute("CREATE TRIGGER fixture_trigger BEFORE DELETE ON private_fixture BEGIN SELECT RAISE(ABORT,'preserve'); END")
                db.execute('PRAGMA user_version=47')
                db.execute('PRAGMA application_id=42')
        return path, ResearchStore(root, self.authority, self.models, budget_limits={'personal': 20},
                                  registration_authority=OfflineRegistrationAuthority(self.authority, root, test_only=True))

    def test_unsupported_schemas_rejected_without_any_database_mutation(self):
        for variant in ('old_v1', 'future_version', 'missing_metadata', 'malformed_v2'):
            with self.subTest(variant=variant):
                path, store = self.incompatible(variant)
                before = self.snapshot(path)
                for _ in range(2):
                    with self.assertRaises(UnsupportedSchemaError):
                        store.recover(self.ctx())
                    self.assertEqual(self.snapshot(path), before)
                self.assertEqual({p.name for p in path.parent.iterdir()}, {'research.sqlite3'})

    def test_existing_empty_or_corrupt_file_is_never_initialized(self):
        for env, content in (('personal', b''), ('gabos', b'not a SQLite database')):
            path = self.db_path(env)
            path.parent.mkdir(parents=True)
            path.write_bytes(content)
            with self.assertRaises(PersistenceError):
                self.store.recover(self.ctx(env))
            self.assertEqual(path.read_bytes(), content)
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_compatible_schema_open_preserves_every_existing_row(self):
        task = self.advance()
        p = foundation.packet('personal', task.task_id)
        self.store.put_packet(self.ctx(), p)
        self.store.reserve(self.ctx(), 'b1', 'researcher', 'synthetic', 'synthetic-researcher', 2)
        before = self.snapshot(self.db_path())
        with closing(open_database(self.db_path(), 'personal', registration_authority=self.registrations, context=self.ctx())) as db:
            self.assertEqual(db.execute('SELECT version,environment FROM metadata').fetchall(), [(2, 'personal')])
        self.assertEqual(self.snapshot(self.db_path()), before)
        self.assertEqual(self.reopen().get_packet(self.ctx(), task.task_id), p)

    def test_cold_concurrent_initialization_is_safe(self):
        self.assertFalse(self.db_path().exists())
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda _: self.provision(), range(12)))
            tasks = list(pool.map(lambda _: self.reopen().submit(self.ctx(), foundation.request('personal')), range(12)))
        self.assertEqual(len({t.task_id for t in tasks}), 1)
        self.assertEqual({p.name for p in self.db_path().parent.iterdir()},
                         {'research.sqlite3', 'research.sqlite3.identity.json'})

    def test_database_tenant_mismatch_is_nonmutating(self):
        self.advance('personal')
        target = self.db_path('fintra')
        target.parent.mkdir()
        target.write_bytes(self.db_path().read_bytes())
        before = self.snapshot(target)
        with self.assertRaises(UnsupportedSchemaError):
            self.store.recover(self.ctx('fintra'))
        self.assertEqual(self.snapshot(target), before)

    def test_retry_sequential_replay_returns_original_result_without_effects(self):
        for env in ENVIRONMENTS:
            task = self.advance(env)
            event = OutboxEvent(event_id='o', environment=env, task_id=task.task_id,
                                topic='fixture', payload_digest='a' * 64)
            self.store.enqueue(self.ctx(env), event)
            result1 = self.store.retry(self.ctx(env), task.task_id, 'retry1')
            before = self.counts(env)
            self.assertEqual(self.reopen().retry(self.ctx(env), task.task_id, 'retry1'), result1)
            self.assertEqual(self.counts(env), before)
            result2 = self.store.retry(self.ctx(env), task.task_id, 'retry2')
            self.assertEqual(result2.retries, 2)
            self.assertEqual(self.store.retry(self.ctx(env), task.task_id, 'retry1'), result1)
            self.assertEqual(self.store.get_task(self.ctx(env), task.task_id).retries, 2)
            operation = self.reopen().get_retry(self.ctx(env), task.task_id, 'retry1')
            self.assertEqual(operation.result, result1)
            self.assertEqual(operation.environment, env)
            self.assertEqual(self.store.outbox(self.ctx(env)), (event,))
            self.store.transition(self.ctx(env), task.task_id, 'researching', 'cancelled')
            self.assertEqual(self.store.retry(self.ctx(env), task.task_id, 'retry1'), result1)
            self.assertEqual(self.store.get_task(self.ctx(env), task.task_id).state, 'cancelled')

    def test_retry_concurrent_replay_has_one_counter_and_audit_effect(self):
        task = self.advance()
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: self.reopen().retry(self.ctx(), task.task_id, 'retry1'), range(16)))
        self.assertEqual({r.retries for r in results}, {1})
        self.assertEqual(self.counts()['retry_operations'], 1)
        self.assertEqual(self.store.get_task(self.ctx(), task.task_id).retries, 1)
        events = self.store.audit_history(self.ctx())
        self.assertEqual(sum(e.operation == 'task.retry' for e in events), 1)
        self.assertEqual(self.counts()['outbox'], 0)

    def test_retry_identity_conflicts_and_exhaustion_fail_closed(self):
        task = self.advance()
        first = self.store.retry(self.ctx(), task.task_id, 'retry1')
        for retry_id in ('retry2', 'retry3'):
            self.store.retry(self.ctx(), task.task_id, retry_id)
        before = self.counts()
        self.assertEqual(self.reopen().retry(self.ctx(), task.task_id, 'retry1'), first)
        with self.assertRaises(EscalationRequired):
            self.store.retry(self.ctx(), task.task_id, 'retry4')
        with self.assertRaises(ContractError):
            self.store.retry(self.ctx(role='director'), task.task_id, 'retry1')
        self.assertEqual(self.counts(), before)
        other = self.store.submit(self.ctx(), foundation.request('personal', 'other'))
        self.store.transition(self.ctx(), other.task_id, 'received', 'collecting')
        with self.assertRaises(ContractError):
            self.store.retry(self.ctx(), other.task_id, 'retry1')
        self.assertEqual(self.store.get_task(self.ctx(), other.task_id).retries, 0)
        with self.assertRaises(TypeError):
            self.store.retry(self.ctx(), task.task_id)
        with self.assertRaises(ContractError):
            self.store.retry(self.ctx(), task.task_id, '')

    def test_retry_failure_rolls_back_identity_counter_and_audit(self):
        task = self.advance()
        before = self.counts()
        with patch.object(self.store, '_audit', side_effect=RuntimeError('interrupted')):
            with self.assertRaises(RuntimeError):
                self.store.retry(self.ctx(), task.task_id, 'retry1')
        self.assertEqual(self.counts(), before)
        self.assertEqual(self.store.get_task(self.ctx(), task.task_id).retries, 0)
        self.assertEqual(self.store.retry(self.ctx(), task.task_id, 'retry1').retries, 1)

    def retry_crash(self, committed):
        task = self.advance()
        code = '''
import os, sys, socket, json
def blocked(*args, **kwargs):
    raise AssertionError('network forbidden')
socket.socket = blocked
sys.path.insert(0, sys.argv[3])
from alfred_research.tenancy import OfflineAuthority
from alfred_research.budgets import ModelConfiguration
from alfred_research.state import ResearchStore
from alfred_research.registration import OfflineRegistrationAuthority
a = OfflineAuthority({'personal-researcher': ('personal','researcher')})
c = a.context('personal-researcher')
registrations = OfflineRegistrationAuthority.from_test_snapshot(a,sys.argv[1],json.loads(sys.stdin.read()),test_only=True)
s = ResearchStore(sys.argv[1], a, ModelConfiguration(), budget_limits={'personal':20},registration_authority=registrations)
if sys.argv[4] == 'uncommitted':
    original = s._audit
    def crash(*args):
        original(*args)
        os._exit(25)
    s._audit = crash
s.retry(c, sys.argv[2], 'retry1')
os._exit(24)
'''
        result = subprocess.run([sys.executable, '-c', code, self.temp.name, task.task_id,
                                 str(Path(__file__).resolve().parents[1] / 'src'),
                                 'committed' if committed else 'uncommitted'],
                                input=json.dumps(self.registrations.snapshot_for_tests()), text=True, check=False)
        self.assertEqual(result.returncode, 24 if committed else 25)
        self.assertEqual(self.reopen().get_task(self.ctx(), task.task_id).retries, 1 if committed else 0)
        self.assertEqual(self.reopen().retry(self.ctx(), task.task_id, 'retry1').retries, 1)
        events = self.store.audit_history(self.ctx())
        self.assertEqual(sum(e.operation == 'task.retry' for e in events), 1)
        self.assertEqual(self.counts()['retry_operations'], 1)
        self.assertEqual(self.counts()['outbox'], 0)

    def test_committed_retry_crash_then_replay_has_one_effect(self):
        self.retry_crash(True)

    def test_uncommitted_retry_crash_then_replay_has_one_effect(self):
        self.retry_crash(False)

    def test_valid_requester_with_forged_environment_rejected_by_scope(self):
        for authenticated in ENVIRONMENTS:
            for claimed in ENVIRONMENTS:
                if authenticated == claimed:
                    continue
                forged = replace(foundation.request(claimed), requested_by=self.ctx(authenticated).principal)
                self.assertEqual(forged.requested_by, self.ctx(authenticated).principal)
                with self.assertRaisesRegex(AuthorizationError, 'environment'):
                    self.store.submit(self.ctx(authenticated), forged)
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])

    def test_all_state_operations_enforce_cross_environment_boundaries(self):
        fixtures = {}
        for env in ENVIRONMENTS:
            task = self.advance(env)
            self.store.retry(self.ctx(env), task.task_id, env + '-retry')
            p1 = foundation.packet(env, task.task_id)
            self.store.put_packet(self.ctx(env), p1)
            d1 = self.decision(p1, 'NEEDS_MORE_RESEARCH')
            self.store.verify(self.ctx(env, 'verifier'), task.task_id, d1)
            p2 = replace(p1, packet_version=2)
            self.store.put_packet(self.ctx(env), p2)
            event = OutboxEvent(event_id=env + '-outbox', environment=env, task_id=task.task_id,
                                topic=env + '-private', payload_digest=p2.digest)
            self.store.enqueue(self.ctx(env), event)
            self.store.reserve(self.ctx(env), env + '-budget', 'researcher', 'synthetic', 'synthetic-researcher', 1)
            fixtures[env] = (task, p1, p2, d1, event)
        for owner in ENVIRONMENTS:
            task, p1, p2, d1, event = fixtures[owner]
            for attacker in ENVIRONMENTS:
                if attacker == owner:
                    continue
                with self.subTest(owner=owner, attacker=attacker):
                    ctx = self.ctx(attacker)
                    before = self.snapshot(self.db_path(owner))
                    denied = (
                        lambda: self.store.get_task(ctx, task.task_id),
                        lambda: self.store.transition(ctx, task.task_id, 'awaiting_verification', 'failed'),
                        lambda: self.store.retry(ctx, task.task_id, owner + '-retry'),
                        lambda: self.store.get_retry(ctx, task.task_id, owner + '-retry'),
                        lambda: self.store.get_packet(ctx, task.task_id),
                        lambda: self.store.get_packet(ctx, task.task_id, 1),
                        lambda: self.store.packet_history(ctx, task.task_id),
                        lambda: self.store.verification_history(ctx, task.task_id),
                        lambda: self.store.verification_history(ctx, task.task_id, 1),
                        lambda: self.store.put_packet(ctx, replace(p2, researcher=ctx.principal)),
                        lambda: self.store.verify(self.ctx(attacker, 'verifier'), task.task_id,
                                                  replace(d1, verifier=attacker + '-verifier')),
                        lambda: self.store.enqueue(ctx, event),
                    )
                    for operation in denied:
                        with self.assertRaises(AuthorizationError):
                            operation()
                    # A rewritten payload cannot make a foreign task ID local.
                    rewritten = replace(p2, environment=attacker, scope=attacker,
                                        researcher=ctx.principal, source=foundation.source(attacker),
                                        claims=tuple(replace(c, environment=attacker) for c in p2.claims),
                                        evidence=tuple(replace(e, environment=attacker) for e in p2.evidence))
                    with self.assertRaises(AuthorizationError):
                        self.store.put_packet(ctx, rewritten)
                    with self.assertRaises(AuthorizationError):
                        self.store.verify(self.ctx(attacker, 'verifier'), task.task_id,
                                          replace(d1, environment=attacker, verifier=attacker + '-verifier'))
                    with self.assertRaises(AuthorizationError):
                        self.store.enqueue(ctx, replace(event, environment=attacker))
                    with self.assertRaises(ContractError):
                        self.store.record_delivery(self.ctx(attacker, 'director'), event.event_id, delivered=True)
                    with self.assertRaises(ContractError):
                        self.store.settle(ctx, owner + '-budget', 0, cancel=True)
                    with self.assertRaises(EscalationRequired):
                        self.store.reserve(ctx, 'invalid-model', 'researcher', 'synthetic', owner + '-private-model', 1)
                    self.assertTrue(all(e.environment == attacker for e in self.store.audit_history(ctx)))
                    own_outbox = self.store.outbox(ctx)
                    self.assertEqual(len(own_outbox), 1)
                    self.assertEqual(own_outbox[0].environment, attacker)
                    self.assertNotIn(event, own_outbox)
                    self.assertTrue(all(t.environment == attacker for t in self.store.recover(ctx)))
                    # The same reservation ID in another namespace affects only that ledger.
                    own_reservation = self.store.reserve(ctx, owner + '-budget', 'researcher',
                                                         'synthetic', 'synthetic-researcher', 1)
                    self.assertEqual(own_reservation.environment, attacker)
                    self.assertEqual(self.snapshot(self.db_path(owner)), before)
