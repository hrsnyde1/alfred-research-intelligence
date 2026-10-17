"""Durable test transcript, not a Memory implementation or production adapter.

Only synthetic Research records are accepted. The existing Research journal and
outbox hold bounded test operation/receipt fixtures; no vault or network exists.
"""
from dataclasses import replace
from contextlib import contextmanager
from ..contracts import ENVIRONMENTS, ENVIRONMENT_NAMES, OutboxEvent, hash_content, require, ContractError
from ..tenancy import AuthorizationError
from ..persistence import PersistenceError
from ..research.journal import WorkflowJournal
from .contracts import (KnowledgeCandidate, MemoryCommand, MemoryReceipt, MemoryEvent,
                        RetrievalResult, MUTATIONS)
from .access import TestMemoryAccess
from ..intelligence.service import CATALOG

NAMESPACE = 'phase5-memory-test-transcript-v1'

class DeliveryAmbiguous(TimeoutError):
    """Test transport lost response; reconcile by stable operation identity."""

class FakeMemoryAdapter:
    def __init__(self, organizer, access, service_contexts, *, test_only=False, production=False):
        if test_only is not True or production or type(access) is not TestMemoryAccess:
            raise AuthorizationError('only explicitly test-only Memory simulation is implemented')
        self.organizer, self.store = organizer, organizer.store
        self.authority, self.clock = organizer.authority, organizer.clock
        require(access.authority is self.authority, 'unrelated authorization authority')
        self.access = access
        self.services = dict(service_contexts)
        require(set(self.services) == set(ENVIRONMENTS), 'four isolated service contexts required')
        for env, context in self.services.items():
            self.authority.authorize(context, env=env, roles=('director',))
        self.journal = WorkflowJournal(self.store._root, self.authority)

    def _history(self, context):
        rows = sorted(self.journal.records(context, NAMESPACE, 'packet:memory:', MemoryEvent),
                      key=lambda e: e.receipt.sequence)
        require([e.receipt.sequence for e in rows] == list(range(1, len(rows) + 1)), 'Memory transcript sequence gap')
        return tuple(rows)

    def history(self, context, environment):
        self.authority.authorize(context, env=environment, roles=('director',))
        return self._history(context)

    def candidate(self, context, record_id, idempotency_id):
        self.authority.authorize(context, roles=('director',))
        rows = self.organizer.history(context, context.environment)
        batch = next((b for b in rows if b.record.record_id == record_id), None)
        require(batch is not None, 'unknown intelligence record in authorized environment')
        record = batch.record
        require(self.organizer.status(context, context.environment, record_id) == 'CURRENT', 'noncurrent intelligence denied')
        _, _, decision, _ = self.organizer._approved(context, record.research_task_id,
                                                   record.packet.packet_version, record.packet.digest)
        return KnowledgeCandidate(environment=context.environment, company_name=ENVIRONMENT_NAMES[context.environment],
            record=record, record_version=batch.sequence, verification=decision,
            relationships=(batch.relation,), related_ids=batch.targets, idempotency_id=idempotency_id)

    def _live(self, service, candidate):
        actual = self.candidate(service, candidate.record.record_id, candidate.idempotency_id)
        require(actual == candidate, 'candidate provenance/verification differs from authoritative Research state')

    @staticmethod
    def _candidate(rows, record_id):
        found = tuple(e.candidate[0] for e in rows if e.candidate and e.candidate[0].record.record_id == record_id)
        require(len(found) == 1, 'record not submitted in authorized environment')
        return found[0]

    @staticmethod
    def _state(rows, record_id):
        mutations = tuple(e.receipt for e in rows if e.receipt.record_id == record_id and
                          e.receipt.operation in MUTATIONS and e.receipt.outcome == 'SUCCESS')
        return (mutations[-1].state, mutations[-1].sequence) if mutations else ('ABSENT', 0)

    @staticmethod
    def _last(rows, record_id, operation):
        return next((e.receipt for e in reversed(rows) if e.receipt.record_id == record_id and
                     e.receipt.operation == operation), None)

    def submit(self, context, candidate, *, timeout_after_commit=False):
        require(type(candidate) is KnowledgeCandidate, 'validated candidate required')
        command = MemoryCommand(environment=candidate.environment, record_id=candidate.record.record_id,
            record_digest=hash_content(candidate.record), operation='submit', operation_id=candidate.idempotency_id)
        return self._perform(context, command, candidate=candidate, timeout_after_commit=timeout_after_commit)

    def _export_binding(self, rows, context, command, candidate, state):
        """Check current authorized attempt before replay, not just before new writes."""
        require(state == 'PROMOTED', 'promoted knowledge required for export/Sync')
        require(command.export_record_version == (candidate.record_version,) and
                command.export_destination == ('test-obsidian:' + candidate.environment,),
                'wrong export version or test destination')
        if command.operation == 'request_export':
            require(command.export_attempt == (command.operation_id,), 'request must establish its own attempt identity')
            return
        request = self._last(rows, command.record_id, 'request_export')
        require(request is not None and request.outcome == 'SUCCESS' and request.state == 'EXPORT_REQUESTED',
                'successful export request required')
        require(request.export_attempt == command.export_attempt and request.export_destination == command.export_destination and
                request.record_version == candidate.record_version and request.record_digest == command.record_digest and
                request.actor == context.principal, 'stale or unauthorized export attempt')
        prerequisite = request
        if command.operation == 'sync_status':
            prerequisite = self._last(rows, command.record_id, 'export_status')
            require(prerequisite is not None and prerequisite.outcome == 'SUCCESS' and prerequisite.state == 'EXPORTED' and
                    prerequisite.export_attempt == command.export_attempt and
                    prerequisite.export_destination == command.export_destination and
                    prerequisite.prerequisite_receipt == (request.receipt_id,) and
                    prerequisite.record_version == candidate.record_version and prerequisite.record_digest == command.record_digest,
                    'matching successful EXPORTED receipt required before Sync')
        require(command.prerequisite_receipt == (prerequisite.receipt_id,), 'wrong prerequisite receipt')
        latest = self._last(rows, command.record_id, command.operation)
        if latest is not None and latest.export_attempt == command.export_attempt:
            require(latest.outcome == 'SUCCESS', 'failed/partial attempt requires a new authorized export request')
            replay = next((e.receipt for e in rows if e.receipt.operation_id == command.operation_id), None)
            require(replay is None or replay.sequence == latest.sequence, 'stale export/Sync completion replay')

    def _perform(self, context, command, *, candidate=None, timeout_after_commit=False):
        require(type(command) is MemoryCommand and type(timeout_after_commit) is bool, 'validated command/test fault required')
        env, operation = command.environment, command.operation
        if operation == 'hq_retrieve':
            self.access.owner(context, env)
        else:
            self.authority.authorize(context, env=env,
                roles=('director', 'researcher', 'verifier') if operation == 'retrieve' else ('director',))
        service = self.services[env]
        # Research evolution and simulated delivery use a consistent lock order.
        # Revocation, retrieval and HQ synchronization share this per-tenant lock.
        with self.organizer.journal.lock(service, CATALOG):
            self.journal.provision(service, NAMESPACE)
            with self.journal.lock(service, NAMESPACE):
                rows = self._history(service)
                state, current_sequence = self._state(rows, command.record_id)
                if operation == 'submit':
                    require(candidate is not None, 'candidate required')
                    self._live(service, candidate)
                    if state != 'ABSENT':
                        previous = self._candidate(rows, command.record_id)
                        require(replace(candidate, idempotency_id=previous.idempotency_id) == previous,
                                'conflicting candidate submission')
                else:
                    candidate = self._candidate(rows, command.record_id)
                require(command.record_digest == hash_content(candidate.record), 'stale record digest')
                if operation in ('request_export', 'export_status', 'sync_status'):
                    self._export_binding(rows, context, command, candidate, state)
                    self._live(service, candidate)
                if operation in ('retrieve', 'hq_retrieve'):
                    require(state == 'PROMOTED', 'commit is not promotion; revoked/deleted knowledge denied')
                    self._live(service, candidate)
                    if operation == 'retrieve':
                        self.access.specialist(context, candidate.record)
                    else:
                        self.access.owner(context, env, candidate.record.packet.classification)
                        allow = self._last(rows, command.record_id, 'hq_allow')
                        synced = self._last(rows, command.record_id, 'hq_sync')
                        require(allow is not None and allow.outcome == 'SUCCESS' and synced is not None and
                                synced.outcome == 'SUCCESS' and synced.state == 'HQ_SYNCED', 'eligible successful HQ sync required')
                input_digest = hash_content((command.payload(), candidate.payload() if operation == 'submit' else None,
                                             context.principal))
                replay = next((e for e in rows if e.receipt.operation_id == command.operation_id), None)
                if replay:
                    require(replay.input_digest == input_digest, 'operation identity reused with changed input/actor')
                    require(operation not in ('retrieve', 'hq_retrieve'), 'fresh retrieval requires a new operation identity')
                    self._outbox(service, replay, candidate)
                    return replay.receipt
                require(len(rows) < 500, 'test transcript capacity exhausted')
                outcome, detail, next_state = command.fixture_result, 'test adapter only; no external delivery', state
                if operation in ('retrieve', 'hq_retrieve'):
                    next_state = 'RETRIEVABLE'
                if operation in MUTATIONS:
                    if operation == 'submit':
                        next_state = 'CANDIDATE' if state == 'ABSENT' else state
                    else:
                        require(command.expected_sequence == current_sequence, 'stale lifecycle revision')
                        if operation in ('commit', 'promote'):
                            self._live(service, candidate)
                            require(state == ('CANDIDATE' if operation == 'commit' else 'COMMITTED'), 'out-of-order lifecycle operation')
                            next_state = 'COMMITTED' if operation == 'commit' else 'PROMOTED'
                        elif operation == 'supersede':
                            require(state in ('COMMITTED', 'PROMOTED') and len(command.related_ids) == 1,
                                    'one authorized promoted replacement required')
                            replacement = self._candidate(rows, command.related_ids[0])
                            require(self._state(rows, replacement.record.record_id)[0] == 'PROMOTED', 'replacement not promoted')
                            self._live(service, replacement)
                            require(command.record_id in replacement.related_ids and
                                    set(replacement.relationships).intersection(('UPDATE', 'CORRECTION', 'VALIDITY_UPDATE')),
                                    'replacement lacks verified Research supersession relationship')
                            next_state = 'SUPERSEDED'
                        else:
                            require(state not in ('ABSENT', 'DELETED', 'REVOKED', 'SUPERSEDED', 'EXPIRED'), 'terminal lifecycle state')
                            if operation == 'expire':
                                require(self.clock() >= candidate.record.valid_until, 'cannot expire before validity boundary')
                            next_state = {'delete': 'DELETED', 'revoke': 'REVOKED', 'expire': 'EXPIRED'}[operation]
                elif operation in ('request_export', 'export_status', 'sync_status', 'hq_allow'):
                    require(state == 'PROMOTED', 'promoted knowledge required')
                    self._live(service, candidate)
                    if operation == 'hq_allow':
                        require(env != 'personal', 'company-specific HQ partitions only')
                    next_state = {'request_export': 'EXPORT_REQUESTED', 'export_status': 'EXPORTED',
                                  'sync_status': 'SYNCED', 'hq_allow': 'HQ_ELIGIBLE'}[operation]
                elif operation == 'hq_sync':
                    require(env != 'personal', 'company-specific HQ partition required')
                    allow = self._last(rows, command.record_id, 'hq_allow')
                    try:
                        self._live(service, candidate)
                        live = state == 'PROMOTED' and allow is not None and allow.outcome == 'SUCCESS'
                    except (ValueError, AuthorizationError):
                        live = False
                    if live:
                        next_state = 'HQ_SYNCED'
                    else:
                        next_state, detail = 'HQ_TOMBSTONE', 'ineligible/noncurrent/revoked/deleted; no current HQ copy'
                if outcome != 'SUCCESS':
                    next_state = state  # failure/partial receipt never advances lifecycle or HQ state
                receipt = MemoryReceipt(environment=env, receipt_id=hash_content((env, command.operation_id, input_digest)),
                    operation_id=command.operation_id, operation=operation, record_id=command.record_id,
                    record_version=candidate.record_version, record_digest=command.record_digest, actor=context.principal,
                    sequence=len(rows) + 1, observed_at=int(self.clock()), outcome=outcome, state=next_state, detail=detail,
                    export_attempt=command.export_attempt, export_destination=command.export_destination,
                    prerequisite_receipt=command.prerequisite_receipt)
                event = MemoryEvent(environment=env, input_digest=input_digest,
                    candidate=(candidate,) if operation == 'submit' and state == 'ABSENT' and outcome == 'SUCCESS' else (), receipt=receipt)
                self.journal.commit(service, NAMESPACE, f'packet:memory:{receipt.sequence}', event)
                if timeout_after_commit:
                    raise DeliveryAmbiguous('SIMULATED response lost after durable transcript commit; delivery not confirmed')
                self._outbox(service, event, candidate)
                if operation in ('retrieve', 'hq_retrieve'):
                    require(outcome == 'SUCCESS', 'failed retrieval has no knowledge result')
                    return RetrievalResult(environment=env, candidate=candidate, receipt=receipt)
                return receipt

    def _outbox(self, service, event, candidate):
        if event.receipt.operation in ('retrieve', 'hq_retrieve'):
            return
        self.store.enqueue(service, OutboxEvent(environment=service.environment,
            event_id='memory-test-' + event.receipt.receipt_id, task_id=candidate.record.research_task_id,
            topic='offline.memory.' + event.receipt.operation, payload_digest=hash_content(event)))

    def reconcile_receipt(self, context, receipt):
        """Validate an exact historical receipt and repair its original outbox intent.

        Historical success is not current export/Sync authorization. No new
        operation or success receipt is created by this reconciliation port.
        """
        self.authority.authorize(context, env=receipt.environment, roles=('director',))
        require(type(receipt) is MemoryReceipt and receipt.actor == context.principal,
                'receipt actor mismatch')
        with self.organizer.journal.lock(context, CATALOG):
            with self.journal.lock(context, NAMESPACE):
                return self._reconcile_receipt(context, receipt, self._history(context))

    def _reconcile_receipt(self, context, receipt, rows):
        require(receipt.environment == context.environment and
                (receipt.actor == context.principal or receipt.operation == 'retrieve'), 'receipt actor/scope mismatch')
        event = next((e for e in rows if e.receipt.receipt_id == receipt.receipt_id), None)
        require(event is not None and event.receipt == receipt, 'unknown or altered receipt')
        candidate = self._candidate(rows, receipt.record_id)
        require(receipt.record_digest == hash_content(candidate.record) and
                receipt.record_version == candidate.record_version, 'receipt identity mismatch')
        if receipt.outcome == 'SUCCESS' and receipt.operation in ('promote', 'retrieve', 'hq_sync'):
            require(self._state(rows, receipt.record_id)[0] == 'PROMOTED', 'promotion no longer current')
            self._live(context, candidate)
            if receipt.operation == 'retrieve':
                reader = next((grant[0] for grant in self.access.specialists.values()
                               if grant[0].principal == receipt.actor), None)
                self.access.specialist(reader, candidate.record)
            if receipt.operation == 'hq_sync':
                allow = self._last(rows, receipt.record_id, 'hq_allow')
                require(allow is not None and allow.outcome == 'SUCCESS' and
                        self._last(rows, receipt.record_id, 'hq_sync') == receipt and
                        receipt.state == 'HQ_SYNCED', 'HQ delivery no longer current')
        if receipt.outcome == 'SUCCESS' and receipt.operation in ('export_status', 'sync_status'):
            command = MemoryCommand(environment=receipt.environment, record_id=receipt.record_id,
                record_digest=receipt.record_digest, operation=receipt.operation,
                operation_id=receipt.operation_id, export_attempt=receipt.export_attempt,
                export_destination=receipt.export_destination,
                export_record_version=(receipt.record_version,),
                prerequisite_receipt=receipt.prerequisite_receipt)
            self._export_binding(rows, context, command, candidate,
                                 self._state(rows, receipt.record_id)[0])
            self._live(context, candidate)
        self._outbox(context, event, candidate)
        if receipt.operation not in ('retrieve', 'hq_retrieve'):
            expected = OutboxEvent(environment=context.environment,
                event_id='memory-test-' + receipt.receipt_id,
                task_id=candidate.record.research_task_id,
                topic='offline.memory.' + receipt.operation, payload_digest=hash_content(event))
            actual = next((e for e in self.store.outbox(context) if e.event_id == expected.event_id), None)
            require(actual is not None and replace(actual, state=expected.state,
                    attempts=expected.attempts) == expected, 'Memory outbox reconciliation incomplete')
        return receipt

    @contextmanager
    def completion_snapshot(self, context, receipts):
        """Hold currentness locks through FINAL preparation/delivery in the fake.

        Revalidate existing receipts only; never repeat a model, promotion or read.
        Excluded historical receipts remain in the original immutable transcript.
        """
        self.authority.authorize(context, roles=('director',))
        with self.organizer.journal.lock(context, CATALOG):
            with self.journal.lock(context, NAMESPACE):
                rows = self._history(context)
                valid = []
                for receipt in receipts:
                    try:
                        valid.append(self._reconcile_receipt(context, receipt, rows))
                    except (ContractError, AuthorizationError, DeliveryAmbiguous, PersistenceError):
                        pass  # Cannot use unresolved evidence for a current success claim.
                yield tuple(valid)

    def reconcile(self, context):
        self.authority.authorize(context, roles=('director',))
        with self.journal.lock(context, NAMESPACE):
            rows = self._history(context)
            for event in rows:
                candidate = self._candidate(rows, event.receipt.record_id)
                self._outbox(context, event, candidate)
        return tuple(e.receipt for e in rows)

    def _operation(self, name, context, command, **fault):
        require(command.operation == name, 'wrong operation port')
        return self._perform(context, command, **fault)

    def commit(self, context, command, **fault): return self._operation('commit', context, command, **fault)
    def promote(self, context, command, **fault): return self._operation('promote', context, command, **fault)
    def retrieve(self, context, command): return self._operation('retrieve', context, command)
    def supersede(self, context, command): return self._operation('supersede', context, command)
    def expire(self, context, command): return self._operation('expire', context, command)
    def delete(self, context, command): return self._operation('delete', context, command)
    def revoke(self, context, command): return self._operation('revoke', context, command)
    def request_export(self, context, command, **fault): return self._operation('request_export', context, command, **fault)
    def export_status(self, context, command): return self._operation('export_status', context, command)
    def sync_status(self, context, command): return self._operation('sync_status', context, command)
    def hq_allow(self, context, command): return self._operation('hq_allow', context, command)
    def hq_sync(self, context, command, **fault): return self._operation('hq_sync', context, command, **fault)
    def hq_retrieve(self, context, command): return self._operation('hq_retrieve', context, command)
