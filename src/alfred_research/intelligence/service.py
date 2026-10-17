"""Immutable environment-local catalog batches using the existing workflow journal.

The catalog is Research working state, not Memory. All views are simulated.
Classification rules are explicit lexical routing hints, never semantic equivalence.
"""
from dataclasses import dataclass
from typing import ClassVar
import time
from ..contracts import Contract, ContractError, ResearchPacket, OutboxEvent, hash_content, require, integer, digest
from ..research.journal import WorkflowJournal
from ..research.contracts import VerificationReview, PacketPreparation
from ..sources import SourceResult

SPECIALISTS = ('Frontend', 'Backend', 'Full-Stack', 'DevOps', 'Data Engineering',
               'Data Science', 'AI/ML', 'Integration', 'Security', 'Mobile', 'Performance')
RULES = dict(zip(SPECIALISTS, (
    ('react', 'ui', 'frontend'), ('api', 'backend'), ('full-stack',), ('devops', 'deployment'),
    ('pipeline', 'etl'), ('forecast', 'statistics'), ('model evaluation', 'machine learning'),
    ('connector', 'integration'), ('threat', 'security'), ('mobile', 'android', 'ios'),
    ('performance', 'latency'))))
CATEGORIES = ('Finance and Accounting', 'Taxes', 'Legal and Compliance', 'Business Operations',
              'Sales and Marketing', 'Personal Research', 'General Intelligence')
CAT_RULES = (('Taxes', ('tax',)), ('Legal and Compliance', ('legal', 'compliance')),
             ('Finance and Accounting', ('finance', 'accounting')),
             ('Business Operations', ('operations',)), ('Sales and Marketing', ('sales', 'marketing')),
             ('Personal Research', ('personal',)))
CATALOG = 'phase4-intelligence-catalog-v1'

class ValidityConflict(ContractError):
    """Duplicate content has incompatible validity; no operation committed."""

@dataclass(frozen=True, kw_only=True)
class SpecialistProfileProposal(Contract):
    """Configuration proposal, not an agent binding or permission grant."""
    schema: ClassVar[str] = 'specialist_profile_proposal.v1'
    environment: str
    specialist_id: str
    categories: tuple[str, ...]
    deployment_enabled: bool = False

    def validate(self):
        require(bool(self.categories) and not self.deployment_enabled, 'profile is proposal-only')

@dataclass(frozen=True, kw_only=True)
class Classification(Contract):
    schema: ClassVar[str] = 'intelligence_classification.v1'
    primary: str
    related_topics: tuple[str, ...]
    specialists: tuple[str, ...]
    escalation: bool

@dataclass(frozen=True, kw_only=True)
class Proposal(Contract):
    schema: ClassVar[str] = 'department_proposal.v1'
    proposal_id: str
    environment: str
    department: str
    capability: str
    specialist: str
    source_revision: tuple[str, ...]
    source_digest: str
    evidence_ids: tuple[str, ...]
    benefit: str = 'Evaluate applicability; no demonstrated production benefit'
    dependencies: tuple[str, ...] = ('Dependency and license review required',)
    risks: tuple[str, ...] = ('Untrusted source; simulated investigation',)
    required_work: tuple[str, ...] = ('Director review', 'Implementation design', 'Isolated testing')
    status: str = 'PROPOSAL_ONLY'
    approval_required: bool = True

    def validate(self):
        digest(self.source_digest)
        require(self.status == 'PROPOSAL_ONLY' and self.approval_required, 'proposal cannot grant approval')

@dataclass(frozen=True, kw_only=True)
class IntelligenceRecord(Contract):
    schema: ClassVar[str] = 'intelligence_record.v1'
    environment: str
    record_id: str
    research_task_id: str
    packet: ResearchPacket
    source: SourceResult
    decision_id: str
    review_digest: str
    classification: Classification
    exact_identity: str
    created_at: int
    valid_until: int
    access_requirements: tuple[str, ...]
    marking: str = 'NON_PRODUCTION / SIMULATED'
    memory_eligible: bool = False
    impact: str = 'HIGH: conservatively requires escalation for conflicts'

    def validate(self):
        require(self.environment == self.packet.environment == self.source.environment, 'mixed intelligence scope')
        require(self.research_task_id == self.packet.task_id and self.source.submitted == self.packet.source,
                'intelligence provenance mismatch')
        for value in (self.exact_identity, self.review_digest):
            digest(value)
        integer(self.created_at)
        integer(self.valid_until)
        require(self.valid_until > self.created_at, 'invalid validity interval')
        require(self.marking == 'NON_PRODUCTION / SIMULATED' and not self.memory_eligible,
                'production promotion disabled')

@dataclass(frozen=True, kw_only=True)
class Batch(Contract):
    schema: ClassVar[str] = 'intelligence_batch.v1'
    environment: str
    sequence: int
    operation_id: str
    input_digest: str
    record: IntelligenceRecord
    relation: str
    targets: tuple[str, ...]
    proposals: tuple[Proposal, ...]
    actor: str
    submitted_packet_digest: str
    submitted_task_id: str

    def validate(self):
        integer(self.sequence, 1)
        digest(self.input_digest)
        digest(self.submitted_packet_digest)
        require(self.relation in ('NEW', 'DUPLICATE', 'RELATED', 'CORRECTION', 'UPDATE', 'CONFLICT', 'VALIDITY_UPDATE'), 'unknown relationship')
        require(self.record.environment == self.environment and
                all(p.environment == self.environment for p in self.proposals), 'batch scope mismatch')

def classify(text, extra=()):
    import re
    lower = text.lower()
    def matches(word):
        return re.search(r'(?<!\w)' + re.escape(word) + r'(?!\w)', lower) is not None
    specialists = tuple(s for s in SPECIALISTS if any(matches(w) for w in RULES[s]))
    categories = tuple(c for c, words in CAT_RULES if any(matches(w) for w in words))
    primary = ('Development: ' + specialists[0]) if specialists else (categories[0] if categories else 'General Intelligence')
    return Classification(primary=primary, related_topics=tuple('Development: ' + s for s in specialists[1:]) + categories,
                          specialists=specialists, escalation=not bool(specialists))

class IntelligenceOrganizer:
    def __init__(self, store, *, clock=time.time, extensions=None):
        self.store, self.authority, self.clock = store, store._authority, clock
        self.journal = WorkflowJournal(store._root, self.authority)
        self.extensions = dict(extensions or {})
        for env, entries in self.extensions.items():
            from ..contracts import environment
            environment(env)
            require(type(entries) is tuple and all(type(x) is str and x.strip() for x in entries), 'invalid category configuration')

    def history(self, context, environment):
        self.authority.authorize(context, env=environment)
        rows = sorted(self.journal.records(context, CATALOG, 'packet:intelligence:', Batch), key=lambda b: b.sequence)
        require([b.sequence for b in rows] == list(range(1, len(rows) + 1)), 'catalog sequence gap')
        return tuple(rows)

    def _approved(self, context, task_id, version, packet_digest):
        packet = self.store.get_packet(context, task_id, version)
        require(packet.digest == packet_digest, 'stale packet digest')
        current = self.store.get_packet(context, task_id)
        require(current.digest == packet.digest, 'historical approval cannot authorize new content')
        decisions = self.store.verification_history(context, task_id, version)
        approved = tuple(d for d in decisions if d.packet_digest == packet.digest and d.verdict == 'APPROVED')
        require(len(approved) == 1, 'exact approved decision required')
        source = self.journal.load(context, task_id, f'source:{version}', SourceResult)
        reviews = self.journal.records(context, task_id, 'review:', VerificationReview)
        reviews = tuple(r for r in reviews if r.packet_digest == packet.digest and r.verdict == 'APPROVED')
        require(source is not None and len(reviews) == 1 and reviews[0].simulation_only,
                'Phase 3 simulated verification provenance required')
        require(reviews[0].verifier == approved[0].verifier and reviews[0].source_digest == source.digest and
                approved[0].verifier != packet.researcher, 'verification linkage mismatch')
        require('phase3.source_result.sha256:' + source.digest in packet.limitations,
                'source result changed since verification')
        return packet, source, approved[0], reviews[0]

    def process(self, context, task_id, version, packet_digest, operation_id, *, relation='NEW',
                targets=(), expected_head=None, valid_until=2**31, primary=None):
        self.authority.authorize(context, roles=('director',))
        require(type(operation_id) is str and 0 < len(operation_id) <= 128, 'bounded operation identity required')
        require(type(targets) is tuple and len(set(targets)) == len(targets), 'unique relationship targets required')
        # Validate before audited SQLite reads, catalog provisioning or duplicate
        # detection. Checkpoints are only a read-only preflight; the authoritative
        # packet/decision is still checked before any successful commit.
        integer(valid_until, 1)
        prepared = self.journal.load(context, task_id, f'packet:{version}', PacketPreparation)
        source = self.journal.load(context, task_id, f'source:{version}', SourceResult)
        require(prepared is not None and source is not None and prepared.packet.digest == packet_digest and
                prepared.source_digest == source.digest, 'packet/source preflight mismatch')
        packet = prepared.packet
        classification = classify(' '.join(e.text for e in source.evidence))
        if primary is not None:
            require(primary in CATEGORIES + tuple('Development: ' + s for s in SPECIALISTS) + self.extensions.get(context.environment, ()),
                    'unconfigured category')
            classification = Classification(primary=primary, related_topics=classification.related_topics,
                specialists=classification.specialists, escalation=classification.escalation)
        inputs = hash_content((task_id, version, packet_digest, relation, targets, expected_head, valid_until, classification.payload()))
        identity = hash_content((context.environment, packet.scope, packet.classification, source.digest,
                                 tuple((c.kind, c.statement, c.evidence_ids) for c in packet.claims), classification.payload()))
        if valid_until <= int(self.clock()):
            # An expired committed replay remains safe; an expired new request
            # must not even provision the catalog directory or lock file.
            prior = self.history(context, context.environment)
            require(any(b.operation_id == operation_id and b.input_digest == inputs for b in prior),
                    'expiration must be in the future')
        self.journal.provision(context, CATALOG)
        with self.journal.lock(context, CATALOG):
            history = self.history(context, context.environment)
            replay = tuple(b for b in history if b.operation_id == operation_id)
            if replay:
                require(replay[0].input_digest == inputs, 'operation replay changed inputs')
                self._approved(context, task_id, version, packet_digest)
                self._outbox(context, replay[0])
                return replay[0]
            require(valid_until > int(self.clock()), 'expiration must be in the future')
            require(len(history) < 500, 'offline catalog bound reached')
            unique = {b.record.record_id: b.record for b in history}
            require(set(targets) <= set(unique), 'unknown or unauthorized relationship target')
            if relation in ('CORRECTION', 'UPDATE', 'VALIDITY_UPDATE'):
                require(len(targets) == 1 and expected_head == hash_content(unique[targets[0]]), 'expected head required')
                require(self._status(unique[targets[0]], history) == 'CURRENT', 'stale update target')
            elif relation in ('RELATED', 'CONFLICT'):
                require(bool(targets), 'relationship target required')
            else:
                require(relation == 'NEW' and not targets and expected_head is None, 'invalid initial relationship')
            duplicate = next((r for r in reversed(tuple(unique.values())) if r.exact_identity == identity), None)
            if relation == 'VALIDITY_UPDATE':
                require(duplicate is not None and targets == (duplicate.record_id,),
                        'validity revision must preserve exact content and reference its latest version')
                require(valid_until != duplicate.valid_until, 'validity revision must change expiration')
            elif duplicate:
                if valid_until != duplicate.valid_until:
                    raise ValidityConflict('VALIDITY_CONFLICT: duplicate expiration differs; explicit VALIDITY_UPDATE required')
                require(relation == 'NEW', 'duplicate cannot silently supersede a finding')
                record, relation, targets, proposals = duplicate, 'DUPLICATE', (duplicate.record_id,), ()
            # Only successful, validity-consistent operations may perform audited
            # authoritative reads. Rejected validity requests have no audit/outbox effects.
            packet, source, decision, review = self._approved(context, task_id, version, packet_digest)
            if duplicate is None or relation == 'VALIDITY_UPDATE':
                record = IntelligenceRecord(environment=context.environment, record_id=hash_content((inputs, len(history) + 1)),
                    research_task_id=task_id, packet=packet, source=source, decision_id=decision.decision_id,
                    review_digest=hash_content(review), classification=classification, exact_identity=identity,
                    created_at=int(self.clock()), valid_until=valid_until,
                    access_requirements=(context.environment, packet.classification, 'authenticated specialist binding', 'simulation opt-in'))
                proposals = () if relation == 'VALIDITY_UPDATE' else self._proposals(record)
            batch = Batch(environment=context.environment, sequence=len(history) + 1, operation_id=operation_id,
                input_digest=inputs, record=record, relation=relation, targets=targets, proposals=proposals, actor=context.principal,
                submitted_packet_digest=packet.digest, submitted_task_id=task_id)
            self.journal.commit(context, CATALOG, f'packet:intelligence:{batch.sequence}', batch)
            self._outbox(context, batch)
            return batch

    def _outbox(self, context, batch):
        # Intent is durable first. Replay repairs a crash before the existing
        # SQLite outbox commit. Event ID is stable; no external delivery occurs.
        self.store.enqueue(context, OutboxEvent(environment=context.environment,
            event_id='intelligence-' + hash_content(batch), task_id=batch.submitted_task_id,
            topic='offline.intelligence.proposal', payload_digest=hash_content(batch)))

    def reconcile(self, context):
        self.authority.authorize(context, roles=('director',))
        for batch in self.history(context, context.environment):
            self._outbox(context, batch)

    def _proposals(self, record):
        result = []
        source = record.source
        capabilities = tuple((c.path, c.evidence_ids) for c in source.capabilities) or (
            ('source', tuple(e.evidence_id for e in source.evidence)),)
        for path, ids in capabilities:
            text = ' '.join(e.text for e in source.evidence if e.evidence_id in ids)
            match = classify(text)
            for specialist in match.specialists or ('Central Development CTO: classification review',):
                result.append(Proposal(environment=record.environment,
                    proposal_id=hash_content((record.record_id, path, specialist)), department='Development',
                    capability=path, specialist=specialist, source_revision=source.revision,
                    source_digest=source.digest, evidence_ids=ids,
                    risks=('Untrusted source; simulated investigation',) + source.flags + source.limitations))
        return tuple(result)

    def _status(self, record, history):
        if any(b.relation == 'CONFLICT' and (record.record_id in b.targets or b.record.record_id == record.record_id) for b in history):
            return 'DISPUTED: additional verification / authorized human escalation required'
        if any(b.relation in ('CORRECTION', 'UPDATE', 'VALIDITY_UPDATE') and record.record_id in b.targets for b in history):
            return 'SUPERSEDED'
        if self.clock() >= record.valid_until:
            return 'EXPIRED'
        return 'CURRENT'

    def views(self, context, environment, specialist, *, simulated=False):
        self.authority.authorize(context, env=environment, roles=('director',))
        require(simulated is True, 'production trusted intelligence and Memory promotion disabled')
        require(specialist in SPECIALISTS, 'unconfigured specialist')
        history = self.history(context, environment)
        records = {b.record.record_id: b.record for b in history}
        return tuple(r for r in records.values() if specialist in r.classification.specialists and self._status(r, history) == 'CURRENT')

    def proposals(self, context, environment):
        self.authority.authorize(context, env=environment, roles=('director',))
        return tuple(p for b in self.history(context, environment) for p in b.proposals)

    def status(self, context, environment, record_id):
        self.authority.authorize(context, env=environment)
        history = self.history(context, environment)
        record = next((b.record for b in history if b.record.record_id == record_id), None)
        require(record is not None, 'unknown or unauthorized intelligence record')
        return self._status(record, history)
