"""Transactional Research-local metadata, not a Memory store or orchestrator."""
from contextlib import contextmanager
from contextvars import ContextVar
import time
from dataclasses import replace
import json
from pathlib import Path
import sqlite3
from uuid import uuid4

from .contracts import (AuditEvent, BudgetReservation, DurableTask, OutboxEvent,
                        ResearchPacket, ResearchRequest, VerificationDecision,
                        RetryOperation, canonical, environment, hash_content, integer, require, text)
from .budgets import EscalationRequired
from .tenancy import AuthorizationError
from .verification import validate_decision
from .persistence import PersistenceError, open_database, validate_schema


TRANSITIONS = {
    'received': {'collecting', 'cancelled', 'failed'},
    'collecting': {'researching', 'cancelled', 'failed'},
    'researching': {'awaiting_verification', 'cancelled', 'failed'},
    'awaiting_verification': {'cancelled', 'failed'},
    'needs_more_research': {'researching', 'cancelled', 'failed'},
    'approved': set(), 'rejected': set(), 'failed': set(), 'cancelled': set(),
}


def _dump(record):
    return canonical(record).decode('utf-8')


def _load(cls, value):
    return cls.from_payload(json.loads(value))


class ResearchStore:
    def __init__(self, root, authority, models, *, budget_limits, registration_authority=None, production=False):
        if production or models.production:
            raise AuthorizationError('production persistence authorization disabled pending Linux integration')
        self._registration_authority = registration_authority
        self._root = Path(root)
        self._authority = authority
        self._models = models
        self._limits = dict(budget_limits)
        self._commit_bound = ContextVar('research_commit_deadline', default=None)
        for env, limit in self._limits.items():
            environment(env)
            integer(limit, 1)

    @contextmanager
    def bounded_commit(self, context, deadline, *, clock=time.time):
        """Optional caller deadline guard; does not change unbounded existing APIs.

        Checked again after SQLite locking and immediately before logical commit.
        No deadline aborts SQLite's required journal recovery or guesses refunds.
        """
        self._authority.authorize(context)
        integer(deadline, 1)
        token = self._commit_bound.set((context, deadline, clock))
        try:
            self._check_commit_bound(context)
            yield
        finally:
            self._commit_bound.reset(token)

    def _check_commit_bound(self, context):
        bound = self._commit_bound.get()
        if bound is not None:
            expected, deadline, clock = bound
            if expected is not context:
                raise AuthorizationError('transaction deadline context mismatch')
            if clock() >= deadline:
                raise EscalationRequired('research transaction deadline exhausted; commit refused')

    @contextmanager
    def _transaction(self, context, *, env=None, roles=('director', 'researcher', 'verifier')):
        tenant = self._authority.authorize(context, env, roles)
        self._check_commit_bound(context)
        connection = None
        try:
            connection = open_database(self._root / tenant / 'research.sqlite3', tenant,
                                       registration_authority=self._registration_authority, context=context)
            connection.execute('BEGIN IMMEDIATE')
            # Recheck under the write lock, before any application writes.
            validate_schema(connection, tenant)
            self._check_commit_bound(context)
            yield connection
            self._check_commit_bound(context)
            connection.commit()
        except AuthorizationError:
            if connection is not None:
                connection.rollback()
            raise
        except (sqlite3.Error, OSError) as exc:
            if connection is not None:
                connection.rollback()
            raise PersistenceError('Research-local SQLite operation failed: ' + str(exc)) from exc
        except BaseException:
            if connection is not None:
                connection.rollback()
            raise
        finally:
            if connection is not None:
                connection.close()

    def _audit(self, db, context, operation, subject):
        record = AuditEvent(event_id=str(uuid4()), environment=context.environment,
                            principal=context.principal, operation=operation, subject_id=subject)
        db.execute('INSERT INTO audit(body) VALUES (?)', (_dump(record),))

    def _task(self, db, context, task_id):
        text(task_id)
        row = db.execute('SELECT body FROM tasks WHERE id=?', (task_id,)).fetchone()
        if row is None:
            raise AuthorizationError('task not available in authorized environment')
        task = _load(DurableTask, row[0])
        self._authority.authorize(context, task.environment)
        return task

    def _save_task(self, db, task):
        db.execute('UPDATE tasks SET body=? WHERE id=?', (_dump(task), task.task_id))

    def submit(self, context, request):
        require(type(request) is ResearchRequest, 'validated request required')
        if request.requested_by != context.principal:
            raise AuthorizationError('requester must match authenticated principal')
        with self._transaction(context, env=request.environment, roles=('director', 'researcher')) as db:
            row = db.execute('SELECT request_hash, body FROM tasks WHERE request_id=?',
                             (request.request_id,)).fetchone()
            if row:
                require(row[0] == hash_content(request), 'idempotency key reused with changed request')
                return _load(DurableTask, row[1])
            task = DurableTask(task_id=str(uuid4()), environment=context.environment,
                               request=request, state='received')
            db.execute('INSERT INTO tasks VALUES (?,?,?,?)',
                       (task.task_id, request.request_id, hash_content(request), _dump(task)))
            self._audit(db, context, 'task.created', task.task_id)
            return task

    def get_task(self, context, task_id):
        with self._transaction(context) as db:
            task = self._task(db, context, task_id)
            self._audit(db, context, 'task.read', task_id)
            return task

    def transition(self, context, task_id, expected, target):
        with self._transaction(context, roles=('director', 'researcher')) as db:
            task = self._task(db, context, task_id)
            require(task.state == expected, 'stale transition')
            require(target in TRANSITIONS[task.state], 'invalid transition')
            if task.state == 'needs_more_research' and target == 'researching':
                if task.retries >= task.request.max_retries:
                    raise EscalationRequired('rework retry budget exhausted')
                task = replace(task, retries=task.retries + 1)
            task = replace(task, state=target)
            self._save_task(db, task)
            self._audit(db, context, 'task.transition.' + target, task_id)
            return task

    def retry(self, context, task_id, retry_id):
        """Replay returns the originally committed result, not a new retry.

        retry_id is required and stable across transport retries. It is unique
        per environment and bound to task and requesting principal.
        """
        text(retry_id)
        with self._transaction(context, roles=('director', 'researcher')) as db:
            task = self._task(db, context, task_id)
            row = db.execute('SELECT body FROM retry_operations WHERE id=?', (retry_id,)).fetchone()
            if row:
                operation = _load(RetryOperation, row[0])
                self._authority.authorize(context, operation.environment)
                require(operation.task_id == task_id and operation.principal == context.principal,
                        'retry identity reused for another task or principal')
                return operation.result
            require(task.state in ('collecting', 'researching', 'needs_more_research'),
                    'task not retryable')
            if task.retries >= task.request.max_retries:
                raise EscalationRequired('retry budget exhausted')
            task = replace(task, retries=task.retries + 1)
            operation = RetryOperation(retry_id=retry_id, task_id=task_id,
                                       environment=context.environment,
                                       principal=context.principal, result=task)
            self._save_task(db, task)
            db.execute('INSERT INTO retry_operations VALUES (?,?,?,?,?)',
                       (retry_id, task_id, context.environment, context.principal, _dump(operation)))
            self._audit(db, context, 'task.retry', task_id)
            return task

    def get_retry(self, context, task_id, retry_id):
        text(retry_id)
        with self._transaction(context) as db:
            self._task(db, context, task_id)
            row = db.execute('SELECT body FROM retry_operations WHERE id=? AND task_id=?',
                             (retry_id, task_id)).fetchone()
            if row is None:
                raise AuthorizationError('retry not available in authorized environment')
            operation = _load(RetryOperation, row[0])
            self._authority.authorize(context, operation.environment)
            self._audit(db, context, 'retry.read', retry_id)
            return operation

    def recover(self, context):
        """Return resumable durable work; no implicit transition or retry spending."""
        with self._transaction(context, roles=('director', 'researcher')) as db:
            tasks = tuple(_load(DurableTask, row[0]) for row in db.execute('SELECT body FROM tasks ORDER BY id'))
            require(all(t.environment == context.environment for t in tasks), 'corrupt task environment')
            self._audit(db, context, 'tasks.recovery_scan', context.environment)
            return tuple(t for t in tasks if t.state not in ('approved', 'rejected', 'failed', 'cancelled'))

    def _packet(self, db, context, task_id, packet_version=None):
        if packet_version is None:
            row = db.execute('SELECT packet_version FROM packet_heads WHERE task_id=?',
                             (task_id,)).fetchone()
            if row is None:
                raise AuthorizationError('packet not available in authorized environment')
            packet_version = row[0]
        integer(packet_version, 1)
        row = db.execute('SELECT environment,digest,body FROM packets WHERE task_id=? AND packet_version=?',
                         (task_id, packet_version)).fetchone()
        if row is None:
            raise AuthorizationError('packet revision not available in authorized environment')
        self._authority.authorize(context, row[0])
        packet = _load(ResearchPacket, row[2])
        require(packet.environment == row[0] and packet.task_id == task_id and
                packet.packet_version == packet_version and packet.digest == row[1],
                'stored packet integrity mismatch')
        return packet

    def get_packet(self, context, task_id, packet_version=None):
        """Read current content, or an immutable historical revision."""
        with self._transaction(context) as db:
            self._task(db, context, task_id)
            packet = self._packet(db, context, task_id, packet_version)
            self._audit(db, context, 'packet.read', task_id)
            return packet

    def packet_history(self, context, task_id):
        with self._transaction(context) as db:
            self._task(db, context, task_id)
            versions = db.execute('SELECT packet_version FROM packets WHERE task_id=? ORDER BY packet_version',
                                  (task_id,)).fetchall()
            packets = tuple(self._packet(db, context, task_id, row[0]) for row in versions)
            self._audit(db, context, 'packet.history', task_id)
            return packets

    def put_packet(self, context, packet):
        require(type(packet) is ResearchPacket, 'validated packet required')
        if packet.researcher != context.principal:
            raise AuthorizationError('researcher must match authenticated principal')
        with self._transaction(context, env=packet.environment, roles=('researcher',)) as db:
            self._models.resolve(context.environment, 'researcher',
                                 packet.researcher_provider, packet.researcher_model)
            task = self._task(db, context, packet.task_id)
            require(packet.source == task.request.sources[0], 'source does not match task')
            row = db.execute('SELECT body FROM packets WHERE task_id=? AND packet_version=?',
                             (task.task_id, packet.packet_version)).fetchone()
            if row:
                require(_load(ResearchPacket, row[0]) == packet, 'conflicting immutable packet revision')
                # A historical replay must not move the head or invalidate a verdict.
                return self._packet(db, context, task.task_id, packet.packet_version).digest
            require(task.state in ('researching', 'awaiting_verification', 'needs_more_research'),
                    'packet cannot change in this state')
            row = db.execute('SELECT packet_version FROM packet_heads WHERE task_id=?', (task.task_id,)).fetchone()
            previous_version = row[0] if row else 0
            if previous_version:
                previous = self._packet(db, context, task.task_id, previous_version)
                require(previous.packet_id == packet.packet_id, 'packet identity changed')
            require(packet.packet_version == previous_version + 1, 'stale or skipped packet revision')
            if task.state == 'needs_more_research':
                if task.retries >= task.request.max_retries:
                    raise EscalationRequired('rework retry budget exhausted')
                task = replace(task, retries=task.retries + 1)
            db.execute('INSERT INTO packets VALUES (?,?,?,?,?,?)',
                       (task.task_id, packet.packet_version, packet.packet_id,
                        context.environment, packet.digest, _dump(packet)))
            if previous_version:
                updated = db.execute('UPDATE packet_heads SET packet_version=? WHERE task_id=? AND packet_version=?',
                                     (packet.packet_version, task.task_id, previous_version))
                require(updated.rowcount == 1, 'concurrent packet head conflict')
            else:
                db.execute('INSERT INTO packet_heads VALUES (?,?)', (task.task_id, packet.packet_version))
            self._save_task(db, replace(task, state='awaiting_verification'))
            self._audit(db, context, 'packet.recorded', packet.packet_id)
            return packet.digest

    def verification_history(self, context, task_id, packet_version=None):
        with self._transaction(context) as db:
            self._task(db, context, task_id)
            if packet_version is not None:
                self._packet(db, context, task_id, packet_version)
            rows = db.execute('SELECT packet_version,digest,environment,body FROM decisions WHERE task_id=? ORDER BY packet_version,id',
                              (task_id,)).fetchall()
            decisions = []
            for version, digest_value, tenant, body in rows:
                self._authority.authorize(context, tenant)
                decision = _load(VerificationDecision, body)
                packet = self._packet(db, context, task_id, version)
                require(decision.environment == tenant and decision.packet_digest == digest_value == packet.digest,
                        'stored verification linkage mismatch')
                if packet_version is None or version == packet_version:
                    decisions.append(decision)
            self._audit(db, context, 'verification.history', task_id)
            return tuple(decisions)

    def verify(self, context, task_id, decision):
        require(type(decision) is VerificationDecision, 'validated decision required')
        if decision.verifier != context.principal:
            raise AuthorizationError('verifier identity mismatch')
        with self._transaction(context, env=decision.environment, roles=('verifier',)) as db:
            task = self._task(db, context, task_id)
            packet = self._packet(db, context, task_id)
            validate_decision(self._authority, context, packet, decision)
            self._models.resolve(context.environment, 'verifier',
                                 decision.verifier_provider, decision.verifier_model)
            row = db.execute('SELECT body FROM decisions WHERE id=?', (decision.decision_id,)).fetchone()
            if row:
                require(_load(VerificationDecision, row[0]) == decision, 'decision id conflict')
                return task
            require(task.state == 'awaiting_verification', 'task not awaiting verification')
            db.execute('INSERT INTO decisions VALUES (?,?,?,?,?,?)',
                       (decision.decision_id, task_id, packet.packet_version,
                        packet.digest, context.environment, _dump(decision)))
            task = replace(task, state=decision.verdict.lower())
            self._save_task(db, task)
            self._audit(db, context, 'verification.' + decision.verdict, task_id)
            return task

    def enqueue(self, context, event):
        require(type(event) is OutboxEvent, 'validated outbox event required')
        require(event.state == 'pending' and event.attempts == 0, 'new event must be pending')
        with self._transaction(context, env=event.environment, roles=('director', 'researcher')) as db:
            self._task(db, context, event.task_id)
            row = db.execute('SELECT body FROM outbox WHERE id=?', (event.event_id,)).fetchone()
            if row:
                previous = _load(OutboxEvent, row[0])
                require(replace(previous, state='pending', attempts=0) == event, 'event id conflict')
                return previous
            db.execute('INSERT INTO outbox VALUES (?,?)', (event.event_id, _dump(event)))
            self._audit(db, context, 'outbox.enqueued', event.event_id)
            return event

    def outbox(self, context):
        with self._transaction(context) as db:
            events = tuple(_load(OutboxEvent, row[0]) for row in db.execute('SELECT body FROM outbox ORDER BY id'))
            require(all(e.environment == context.environment for e in events), 'outbox scope mismatch')
            self._audit(db, context, 'outbox.read', context.environment)
            return events

    def record_delivery(self, context, event_id, *, delivered):
        require(type(delivered) is bool, 'boolean delivery outcome required')
        with self._transaction(context, roles=('director',)) as db:
            row = db.execute('SELECT body FROM outbox WHERE id=?', (event_id,)).fetchone()
            require(row is not None, 'unknown outbox event')
            event = _load(OutboxEvent, row[0])
            self._authority.authorize(context, event.environment)
            if event.state == 'delivered' and delivered:
                return event
            require(event.state == 'pending', 'outbox event no longer pending')
            attempts = event.attempts + 1
            event = replace(event, attempts=attempts,
                            state='delivered' if delivered else ('exhausted' if attempts == 3 else 'pending'))
            db.execute('UPDATE outbox SET body=? WHERE id=?', (_dump(event), event_id))
            self._audit(db, context, 'outbox.' + event.state, event_id)
            return event

    def audit_history(self, context):
        with self._transaction(context) as db:
            self._audit(db, context, 'audit.read', context.environment)
            records = tuple(_load(AuditEvent, row[0]) for row in db.execute('SELECT body FROM audit ORDER BY seq'))
            require(all(e.environment == context.environment for e in records), 'audit scope mismatch')
            return records

    def _budget_policy(self, db, context):
        limit = self._limits.get(context.environment)
        if limit is None:
            raise EscalationRequired('missing environment budget authorization')
        row = db.execute('SELECT ceiling FROM budget_policy WHERE id=1').fetchone()
        if row:
            require(row[0] == limit, 'budget ceiling changes need explicit migration approval')
        else:
            db.execute('INSERT INTO budget_policy VALUES (1,?)', (limit,))
        return limit

    def reserve(self, context, reservation_id, specialist, provider, model, units):
        integer(units, 1)
        text(reservation_id)
        self._authority.authorize(context, roles=('director', 'researcher', 'verifier'))
        allowed = {'director': ('director',), 'verifier': ('verifier',),
                   'researcher': ('researcher', 'general', 'code', 'finance_tax', 'business_legal')}
        if specialist not in allowed[context.role]:
            raise EscalationRequired('specialist assignment exceeds principal role')
        assignment = self._models.resolve(context.environment, specialist, provider, model)
        amount = units * assignment.price_units
        integer(amount, 1)
        with self._transaction(context) as db:
            limit = self._budget_policy(db, context)
            reservations = tuple(_load(BudgetReservation, row[0]) for row in db.execute('SELECT body FROM reservations'))
            candidate = BudgetReservation(reservation_id=reservation_id, environment=context.environment,
                                          principal=context.principal, assignment=assignment, reserved=amount)
            for r in reservations:
                require(r.environment == context.environment, 'reservation scope mismatch')
                if r.reservation_id == reservation_id:
                    require(replace(r, state='reserved', consumed=0) == candidate, 'reservation id conflict')
                    return r
            used = sum(r.reserved if r.state == 'reserved' else r.consumed for r in reservations)
            if amount > limit - used:
                raise EscalationRequired('environment budget exhausted; escalation required')
            db.execute('INSERT INTO reservations VALUES (?,?)', (reservation_id, _dump(candidate)))
            self._audit(db, context, 'budget.reserved', reservation_id)
            return candidate

    def settle(self, context, reservation_id, consumed, *, cancel=False):
        integer(consumed)
        require(type(cancel) is bool, 'boolean cancel required')
        with self._transaction(context) as db:
            row = db.execute('SELECT body FROM reservations WHERE id=?', (reservation_id,)).fetchone()
            require(row is not None, 'unknown reservation')
            reservation = _load(BudgetReservation, row[0])
            self._authority.authorize(context, reservation.environment)
            if reservation.principal != context.principal:
                raise AuthorizationError('reservation belongs to another principal')
            if consumed > reservation.reserved or (cancel and consumed):
                raise EscalationRequired('consumption exceeds authorization or invalid cancellation')
            updated = replace(reservation, consumed=consumed, state='cancelled' if cancel else 'settled')
            if reservation.state != 'reserved':
                require(reservation == updated, 'reservation already reconciled')
                return reservation
            db.execute('UPDATE reservations SET body=? WHERE id=?', (_dump(updated), reservation_id))
            self._audit(db, context, 'budget.' + updated.state, reservation_id)
            return updated
