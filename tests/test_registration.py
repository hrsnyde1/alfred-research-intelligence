"""Independent test-ledger authorization; no production credentials or services."""
from contextlib import closing
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import sqlite3
from uuid import uuid4

import test_foundation as foundation
import test_hot_recovery as hot
from alfred_research.persistence import (RecoveryRequiredError, UnsupportedSchemaError,
                                         _initialize_new, open_database, register_database)
from alfred_research.registration import OfflineRegistrationAuthority
from alfred_research.state import ResearchStore
from alfred_research.tenancy import AuthorizationError


class RegistrationTests(foundation.FoundationFixture):
    path = hot.HotRecoveryTests.path
    raw_snapshot = hot.HotRecoveryTests.raw_snapshot
    raw_spill_crash = hot.HotRecoveryTests.raw_spill_crash
    assert_hot = hot.HotRecoveryTests.assert_hot

    def receipt_path(self, env='personal'):
        return self.path(env).with_name('research.sqlite3.identity.json')

    def receipt(self, env='personal'):
        return json.loads(self.receipt_path(env).read_text())

    def store_with(self, registrations):
        return ResearchStore(self.temp.name, self.authority, self.models,
                             budget_limits={env: 20 for env in foundation.ENVIRONMENTS},
                             registration_authority=registrations)

    def register(self, env='personal', *, context=None, replace=False):
        return register_database(self.path(env), env, registration_authority=self.registrations,
                                 context=context or self.ctx(env, 'director'), replace=replace)

    def test_forged_receipt_diagnostic_never_registered_incompatible_hot_file(self):
        self.advance('personal')
        legitimate = self.receipt('personal')
        target = self.path('gabos')
        target.parent.mkdir()
        with closing(sqlite3.connect(target)) as db:
            with db:
                db.execute('CREATE TABLE metadata (version INTEGER PRIMARY KEY, environment TEXT NOT NULL)')
                db.execute("INSERT INTO metadata VALUES (999,'gabos')")
                db.execute('CREATE TABLE audit (body TEXT NOT NULL)')
                db.execute("INSERT INTO audit VALUES ('committed synthetic data')")
        self.raw_spill_crash(target, metadata_change=True)  # Child exit 30; genuine hot journal.
        trusted_before = self.registrations.snapshot_for_tests()
        stat = target.stat()
        identity = deepcopy(legitimate['identity'])
        identity.update(environment='gabos', path=str(target.resolve()), device=stat.st_dev, inode=stat.st_ino)
        # Exact prior attack plus a fabricated new-format record with plausible public fields.
        edited = deepcopy(legitimate)
        edited['identity'] = identity
        fabricated = deepcopy(edited)
        fabricated['registration_id'] = str(uuid4())
        fabricated['registered_by'] = 'gabos-director'
        legacy = {**identity, 'receipt_version': 1}
        for forged in (legacy, edited, fabricated):
            with self.subTest(format=forged['receipt_version'], id=forged.get('registration_id')):
                self.receipt_path('gabos').write_text(json.dumps(forged, sort_keys=True))
                before = self.raw_snapshot(target)
                with self.assertRaises(RecoveryRequiredError) as raised:
                    self.store.recover(self.ctx('gabos'))
                self.assertFalse(raised.exception.recovery_attempted)
                self.assertEqual(self.raw_snapshot(target), before)
                self.assertEqual(self.registrations.snapshot_for_tests(), trusted_before)
        print('Forged-receipt diagnostic: child exit 30; legacy/edited/fabricated JSON denied; '
              'database and hot journal unchanged; no trusted registration created')

    def test_matching_receipt_without_trusted_ledger_record_is_denied(self):
        task = self.advance()
        old_receipt = self.receipt_path().read_bytes()
        self.raw_spill_crash(self.path())
        # A new authority has no independent record, even with an exact original receipt.
        changed = OfflineRegistrationAuthority(self.authority, self.temp.name, test_only=True)
        before = self.raw_snapshot(self.path())
        with self.assertRaises(RecoveryRequiredError):
            self.store_with(changed).get_task(self.ctx(), task.task_id)
        self.assertEqual(self.receipt_path().read_bytes(), old_receipt)
        self.assertEqual(self.raw_snapshot(self.path()), before)
        self.assertEqual(self.store.get_task(self.ctx(), task.task_id), task)

    def test_edited_registration_fields_are_denied_without_mutation(self):
        task = self.advance()
        original = self.receipt()
        self.raw_spill_crash(self.path())
        for field in ('authority_id', 'epoch', 'registration_id', 'registered_by'):
            edited = deepcopy(original)
            edited[field] = 'edited'
            self.receipt_path().write_text(json.dumps(edited, sort_keys=True))
            before = self.raw_snapshot(self.path())
            with self.assertRaises(RecoveryRequiredError):
                self.store.get_task(self.ctx(), task.task_id)
            self.assertEqual(self.raw_snapshot(self.path()), before)
        self.receipt_path().write_text(json.dumps(original, sort_keys=True))
        self.assertEqual(self.store.get_task(self.ctx(), task.task_id), task)

    def test_copied_or_retargeted_receipt_cannot_authorize_another_environment(self):
        self.advance('personal')
        task = self.advance('gabos')
        copied = self.receipt('personal')
        original = self.receipt('gabos')
        self.raw_spill_crash(self.path('gabos'))
        retargeted = deepcopy(copied)
        retargeted['identity'] = deepcopy(original['identity'])
        retargeted['epoch'] = original['epoch']
        for candidate in (copied, retargeted):
            self.receipt_path('gabos').write_text(json.dumps(candidate, sort_keys=True))
            before = self.raw_snapshot(self.path('gabos'))
            with self.assertRaises(RecoveryRequiredError):
                self.store.get_task(self.ctx('gabos'), task.task_id)
            self.assertEqual(self.raw_snapshot(self.path('gabos')), before)

    def test_retargeted_receipt_cannot_authorize_a_replacement_database_instance(self):
        task = self.advance()
        old = self.receipt()
        path = self.path()
        replacement = path.with_name('replacement.sqlite3')
        replacement.write_bytes(path.read_bytes())
        replacement.replace(path)  # The database is clean here; no journal is manipulated.
        self.raw_spill_crash(path)
        old['identity']['device'] = path.stat().st_dev
        old['identity']['inode'] = path.stat().st_ino
        self.receipt_path().write_text(json.dumps(old, sort_keys=True))
        before = self.raw_snapshot(path)
        with self.assertRaises(RecoveryRequiredError):
            self.store.get_task(self.ctx(), task.task_id)
        self.assertEqual(self.raw_snapshot(path), before)

    def test_revocation_blocks_replay_and_survives_current_trusted_test_snapshot(self):
        task = self.advance()
        original = self.receipt_path().read_bytes()
        self.registrations.revoke(self.ctx(role='director'), self.receipt()['registration_id'])
        restored = OfflineRegistrationAuthority.from_test_snapshot(
            self.authority, self.temp.name, self.registrations.snapshot_for_tests(), test_only=True)
        self.raw_spill_crash(self.path())
        before = self.raw_snapshot(self.path())
        for store in (self.store, self.store_with(restored)):
            self.receipt_path().write_bytes(original)
            with self.assertRaises(RecoveryRequiredError):
                store.get_task(self.ctx(), task.task_id)
            self.assertEqual(self.raw_snapshot(self.path()), before)

    def test_missing_trust_provider_fails_closed_before_recovery(self):
        task = self.advance()
        self.raw_spill_crash(self.path())
        before = self.raw_snapshot(self.path())
        with self.assertRaises(RecoveryRequiredError):
            self.store_with(None).get_task(self.ctx(), task.task_id)
        with self.assertRaises(RecoveryRequiredError):
            open_database(self.path(), 'personal')
        self.assertEqual(self.raw_snapshot(self.path()), before)

    def test_epoch_rotation_is_scoped_and_old_receipts_are_rejected(self):
        personal = self.advance('personal')
        gabos = self.advance('gabos')
        self.registrations.rotate(self.ctx('personal', 'director'))
        self.assertEqual(self.store.get_task(self.ctx('gabos'), gabos.task_id), gabos)
        self.raw_spill_crash(self.path())
        before = self.raw_snapshot(self.path())
        with self.assertRaises(RecoveryRequiredError):
            self.store.get_task(self.ctx(), personal.task_id)
        self.assertEqual(self.raw_snapshot(self.path()), before)

    def test_existing_clean_database_is_not_automatically_registered(self):
        _initialize_new(self.path(), 'personal')  # Synthetic legacy file, no ledger registration.
        before = self.raw_snapshot(self.path())
        trusted_before = self.registrations.snapshot_for_tests()
        with self.assertRaises(RecoveryRequiredError):
            self.store.recover(self.ctx())
        self.assertEqual(self.raw_snapshot(self.path()), before)
        self.assertEqual(self.registrations.snapshot_for_tests(), trusted_before)
        with self.assertRaises(AuthorizationError):
            self.register(context=self.ctx())
        self.assertEqual(self.raw_snapshot(self.path()), before)
        main_before = self.path().read_bytes()
        self.register()  # A genuine issued director context plus full schema validation.
        self.assertEqual(self.path().read_bytes(), main_before)
        self.assertEqual(self.store.recover(self.ctx()), ())

    def test_registration_and_replacement_require_issued_director_context(self):
        self.advance()
        before = self.raw_snapshot(self.path())
        trusted_before = self.registrations.snapshot_for_tests()
        for ctx in (self.ctx(), replace(self.ctx(), role='director'), self.ctx('gabos', 'director')):
            with self.assertRaises(AuthorizationError):
                self.register(context=ctx, replace=True)
        self.assertEqual(self.raw_snapshot(self.path()), before)
        self.assertEqual(self.registrations.snapshot_for_tests(), trusted_before)

    def test_director_replacement_invalidates_previous_receipt_replay(self):
        task = self.advance()
        old = self.receipt_path().read_bytes()
        old_id = self.receipt()['registration_id']
        new_id = self.register(replace=True)
        self.assertNotEqual(new_id, old_id)
        current = self.receipt_path().read_bytes()
        self.raw_spill_crash(self.path())
        self.receipt_path().write_bytes(old)
        before = self.raw_snapshot(self.path())
        with self.assertRaises(RecoveryRequiredError):
            self.store.get_task(self.ctx(), task.task_id)
        self.assertEqual(self.raw_snapshot(self.path()), before)
        self.receipt_path().write_bytes(current)
        self.assertEqual(self.store.get_task(self.ctx(), task.task_id), task)

    def test_unknown_hot_file_cannot_be_registered_even_by_director(self):
        self.advance()
        self.raw_spill_crash(self.path())
        before = self.raw_snapshot(self.path())
        trusted_before = self.registrations.snapshot_for_tests()
        with self.assertRaises(sqlite3.OperationalError) as raised:
            self.register(replace=True)
        self.assertEqual(raised.exception.sqlite_errorname, 'SQLITE_READONLY_ROLLBACK')
        self.assertEqual(self.raw_snapshot(self.path()), before)
        self.assertEqual(self.registrations.snapshot_for_tests(), trusted_before)

    def test_unsupported_schema_registration_has_no_effect(self):
        path = self.path()
        path.parent.mkdir()
        with closing(sqlite3.connect(path)) as db:
            with db:
                db.execute('CREATE TABLE metadata (version INTEGER PRIMARY KEY)')
                db.execute('INSERT INTO metadata VALUES (1)')
        before = self.raw_snapshot(path)
        trusted_before = self.registrations.snapshot_for_tests()
        with self.assertRaises(UnsupportedSchemaError):
            self.register()
        self.assertEqual(self.raw_snapshot(path), before)
        self.assertEqual(self.registrations.snapshot_for_tests(), trusted_before)

    def test_registration_scope_and_revocation_cannot_cross_companies(self):
        self.advance('personal')
        self.advance('gabos')
        original = self.registrations.snapshot_for_tests()
        with self.assertRaises(AuthorizationError):
            self.registrations.revoke(self.ctx('gabos', 'director'), self.receipt('personal')['registration_id'])
        self.assertEqual(self.registrations.snapshot_for_tests(), original)
        outside = Path(self.temp.name) / 'arbitrary.sqlite3'
        with self.assertRaises(AuthorizationError):
            register_database(outside, 'personal', registration_authority=self.registrations,
                              context=self.ctx(role='director'))
        self.assertFalse(outside.exists())

    def test_test_authority_cannot_be_used_as_production_authorization(self):
        with self.assertRaises(AuthorizationError):
            OfflineRegistrationAuthority(self.authority, self.temp.name)
        with self.assertRaises(AuthorizationError):
            ResearchStore(self.temp.name, self.authority, self.models, budget_limits={'personal': 20},
                          registration_authority=self.registrations, production=True)
        for operation in (open_database, register_database):
            with self.assertRaises(RecoveryRequiredError):
                operation(self.path(), 'personal', registration_authority=self.registrations,
                          context=self.ctx(role='director'), production=True)
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])

    def test_director_provisioning_is_idempotent_all_environments(self):
        for env in foundation.ENVIRONMENTS:
            self.provision(env)
            record = self.receipt(env)
            self.assertEqual(record['registered_by'], env + '-director')
            before = self.raw_snapshot(self.path(env))
            ledger = self.registrations.snapshot_for_tests()
            self.provision(env)
            self.assertEqual(self.raw_snapshot(self.path(env)), before)
            self.assertEqual(self.registrations.snapshot_for_tests(), ledger)
            task = self.store.submit(self.ctx(env), foundation.request(env))
            self.assertEqual(self.store.get_task(self.ctx(env), task.task_id), task)

    def test_non_directors_cannot_provision_missing_databases(self):
        before = self.registrations.snapshot_for_tests()
        for env in foundation.ENVIRONMENTS:
            for role in ('researcher', 'verifier'):
                with self.subTest(env=env, role=role):
                    with self.assertRaises(AuthorizationError):
                        open_database(self.path(env), env, registration_authority=self.registrations,
                                      context=self.ctx(env, role))
                    with self.assertRaises(AuthorizationError):
                        self.store.get_task(self.ctx(env, role), 'missing-task')
                    self.assertEqual(list(Path(self.temp.name).iterdir()), [])
                    self.assertEqual(self.registrations.snapshot_for_tests(), before)

    def test_forged_environment_cannot_provision(self):
        before = self.registrations.snapshot_for_tests()
        for env in foundation.ENVIRONMENTS:
            for other in foundation.ENVIRONMENTS:
                if env == other:
                    continue
                forged = replace(foundation.request(other), requested_by=self.ctx(env).principal)
                with self.assertRaises(AuthorizationError):
                    self.store.submit(self.ctx(env), forged)
                with self.assertRaises(AuthorizationError):
                    open_database(self.path(other), other, registration_authority=self.registrations,
                                  context=self.ctx(env, 'director'))
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])
        self.assertEqual(self.registrations.snapshot_for_tests(), before)

    def test_concurrent_unauthorized_provisioning_has_no_effects(self):
        from concurrent.futures import ThreadPoolExecutor
        before = self.registrations.snapshot_for_tests()
        def attempt(pair):
            env, role = pair
            try:
                open_database(self.path(env), env, registration_authority=self.registrations,
                              context=self.ctx(env, role))
            except AuthorizationError:
                return 'denied'
            return 'unexpected success'
        attempts = [(env, role) for env in foundation.ENVIRONMENTS
                    for role in ('researcher', 'verifier')] * 4
        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(list(pool.map(attempt, attempts)), ['denied'] * len(attempts))
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])
        self.assertEqual(self.registrations.snapshot_for_tests(), before)

    def test_fabricated_registration_cannot_bypass_director_boundary(self):
        before = self.registrations.snapshot_for_tests()
        for env in foundation.ENVIRONMENTS:
            identity = {'path': str(self.path(env)), 'environment': env,
                        'device': 1, 'inode': 1, 'schema_version': 2, 'manifest_digest': 'a' * 64}
            for ctx in (self.ctx(env), self.ctx(env, 'verifier'),
                        replace(self.ctx(env), role='director')):
                for register in (self.registrations.register, self.registrations._register_new):
                    with self.assertRaises(AuthorizationError):
                        register(ctx, identity)
        self.assertEqual(self.registrations.snapshot_for_tests(), before)
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])
