"""Versioned proposed host boundaries. No installed Linux API is implied.

All executable implementations delegate to accepted offline components. Genuine
envelopes describe data only: they cannot authorize execution or promotion.
Trusted configuration is injected by test bootstrap, never reconstructed from
source, receipt or message contents. This module has no network implementation.
"""
from dataclasses import dataclass
from typing import ClassVar, Protocol
from urllib.parse import urlsplit
import re

from ..contracts import (Contract, SourceIdentity, ResearchRequest, ModelAssignment,
                         ResearchPacket, hash_content, digest, integer, require)
from ..tenancy import AuthorizationError
from ..research.journal import WorkflowJournal
from ..research.contracts import ModelInvocation, ResearchDraft, VerifierProposal, ResearchPlan
from ..research.provider import SyntheticModelProvider
from ..research.execution import execute_invocation, reconcile_execution, validate_invocation
from ..sources import SourceFixture, SourceResult
from ..memory import FakeMemoryAdapter
from ..memory.contracts import KnowledgeCandidate, MemoryCommand, MemoryReceipt, RetrievalResult
from ..workflow.contracts import Notice, FlowResult, TransportReceipt
from ..workflow.notifications import Notifications
from ..intelligence import Proposal

MARKING = 'SIMULATED / NON_PRODUCTION'


def offline_only(test_only=False, production=False):
    if test_only is not True or production is not False:
        raise AuthorizationError('production integration disabled; explicit test-only bootstrap required')


def require_production_authorization(*args, **kwargs):
    """No approval-shaped data can enable a production path at this milestone."""
    raise AuthorizationError('host authorization and production adapters are not implemented')


@dataclass(frozen=True, kw_only=True)
class GitHubReference(Contract):
    schema: ClassVar[str] = 'research_github_reference.proposed.v1'
    url: str
    commit: str

    def validate(self):
        require(re.fullmatch(r'[0-9a-f]{40}', self.commit) is not None, 'full Git commit required')
        url = urlsplit(self.url)
        require(url.scheme == 'https' and url.netloc == 'github.com' and not url.query and
                not url.fragment and re.fullmatch(r'/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+/tree/' + self.commit,
                                                url.path) is not None,
                'only explicit public GitHub tree references are supported by the harness')


@dataclass(frozen=True, kw_only=True)
class ResearchIntake(Contract):
    schema: ClassVar[str] = 'research_host_intake.proposed.v1'
    environment: str
    issuer: str
    event_id: str
    conversation_id: str
    requester: str
    recipient: str
    objective: str
    policy_ref: str
    sources: tuple[GitHubReference, ...]
    marking: str = MARKING

    def validate(self):
        require(len(self.sources) == 1, 'exactly one submitted source required')
        require(self.marking == MARKING, 'harness intake is non-production')
        require(all(len(v) <= 128 for v in (self.issuer, self.event_id, self.conversation_id,
                    self.requester, self.recipient, self.policy_ref)), 'bounded host identities required')

    @property
    def operation_id(self):
        return hash_content((self.environment, self.issuer, self.conversation_id, self.event_id))


@dataclass(frozen=True, kw_only=True)
class ConversationBinding(Contract):
    """Trusted test configuration, not a credential in a message."""
    schema: ClassVar[str] = 'research_host_binding.proposed.v1'
    environment: str
    issuer: str
    conversation_id: str
    requester: str
    recipient: str
    policy_ref: str


class IntakeMapping:
    def __init__(self, authority, bindings=(), *, test_only=False, production=False):
        offline_only(test_only, production)
        self.authority = authority
        self.bindings = {}
        for binding in bindings:
            require(type(binding) is ConversationBinding, 'typed binding required')
            key = (binding.issuer, binding.conversation_id)
            require(key not in self.bindings, 'ambiguous conversation binding')
            self.bindings[key] = binding

    def authenticate(self, context, intake):
        require(type(intake) is ResearchIntake, 'typed intake required')
        self.authority.authorize(context, intake.environment, ('director', 'researcher'))
        binding = self.bindings.get((intake.issuer, intake.conversation_id))
        if binding is None or (binding.environment, binding.requester, binding.recipient, binding.policy_ref) != (
                context.environment, context.principal, intake.recipient, intake.policy_ref) or intake.requester != context.principal:
            raise AuthorizationError('untrusted issuer/conversation/requester/environment mapping')
        return binding


@dataclass(frozen=True, kw_only=True)
class PendingAcquisition(Contract):
    schema: ClassVar[str] = 'research_pending_acquisition.proposed.v1'
    environment: str
    intake: ResearchIntake

    def validate(self):
        require(self.environment == self.intake.environment, 'pending scope mismatch')


@dataclass(frozen=True, kw_only=True)
class AcquisitionResolution(Contract):
    schema: ClassVar[str] = 'research_acquisition_resolution.proposed.v1'
    environment: str
    intake_digest: str
    outcome: str
    snapshot_digest: tuple[str, ...]
    reason: str
    marking: str = MARKING

    def validate(self):
        digest(self.intake_digest)
        require(self.outcome in ('ACQUIRED', 'FAILED', 'UNKNOWN'), 'unsupported acquisition outcome')
        require(len(self.snapshot_digest) == (1 if self.outcome == 'ACQUIRED' else 0), 'snapshot outcome mismatch')
        for value in self.snapshot_digest:
            digest(value)
        require(self.marking == MARKING, 'synthetic acquisition only')


class SourceAcquisitionPort(Protocol):
    def resolve(self, context, intake: ResearchIntake) -> AcquisitionResolution: ...
    def reconcile(self, context, intake: ResearchIntake) -> AcquisitionResolution | None: ...


class PendingSources:
    """Research-local checkpoints, not a source service or replacement queue.

    Resolution is immutable. FAILED/UNKNOWN needs an explicitly new host event;
    no automatic retry is inferred. Crash after submit resumes the same request.
    """
    def __init__(self, store, mapping, *, test_only=False, production=False, hook=None):
        offline_only(test_only, production)
        require(mapping.authority is store._authority, 'shared trusted authority required')
        self.store, self.mapping = store, mapping
        self.journal = WorkflowJournal(store._root, store._authority)
        self.hook = hook or (lambda stage: None)

    def _scope(self, requester, director, intake):
        self.mapping.authenticate(requester, intake)
        self.mapping.authority.authorize(director, intake.environment, ('director',))
        return 'acquisition-' + intake.operation_id

    def begin(self, requester, director, intake):
        namespace = self._scope(requester, director, intake)
        self.journal.provision(director, namespace)
        with self.journal.lock(director, namespace):
            return self.journal.commit(director, namespace, 'packet:pending',
                PendingAcquisition(environment=intake.environment, intake=intake))

    def reconcile(self, requester, director, intake):
        namespace = self._scope(requester, director, intake)
        prior = self.journal.load(director, namespace, 'packet:pending', PendingAcquisition)
        require(prior is not None and prior.intake == intake, 'missing/conflicting pending intake')
        return self.journal.load(director, namespace, 'packet:resolution', AcquisitionResolution)

    def resolve_fixture(self, requester, director, intake, *, fixture=None, outcome='ACQUIRED'):
        namespace = self._scope(requester, director, intake)
        require(outcome in ('ACQUIRED', 'FAILED', 'UNKNOWN'), 'invalid acquisition outcome')
        if outcome == 'ACQUIRED':
            require(type(fixture) is SourceFixture and fixture.origin == 'fixture' and
                    fixture.revision == intake.sources[0].commit and fixture.access == 'accessible' and
                    fixture.complete and bool(fixture.files), 'complete matching synthetic snapshot required')
        else:
            require(fixture is None, 'failed/ambiguous acquisition cannot contain a snapshot')
        resolution = AcquisitionResolution(environment=intake.environment, intake_digest=hash_content(intake),
            outcome=outcome, snapshot_digest=(fixture.digest,) if fixture else (), reason='Synthetic acquisition ' + outcome)
        with self.journal.lock(director, namespace):
            prior = self.journal.load(director, namespace, 'packet:pending', PendingAcquisition)
            require(prior is not None and prior.intake == intake, 'pending intake required before resolution')
            self.journal.commit(director, namespace, 'packet:resolution', resolution)
        return resolution

    def materialize(self, requester, director, intake, fixture):
        namespace = self._scope(requester, director, intake)
        with self.journal.lock(director, namespace):
            resolution = self.reconcile(requester, director, intake)
            require(resolution is not None and resolution.outcome == 'ACQUIRED', 'acquisition unresolved; no task/ACK')
            require(type(fixture) is SourceFixture and resolution.snapshot_digest == (fixture.digest,),
                    'acquired snapshot substituted')
            reference = intake.sources[0]
            request = ResearchRequest(environment=intake.environment, request_id='host-' + intake.operation_id,
                requested_by=requester.principal, objective=intake.objective,
                sources=(SourceIdentity(environment=intake.environment, source_id=intake.operation_id, kind='github',
                    locator=reference.url, revision=reference.commit, content_digest=fixture.digest),))
            self.journal.commit(director, namespace, 'packet:request', request)
            task = self.store.submit(requester, request)
            self.hook('task:effect')
            return task


@dataclass(frozen=True, kw_only=True)
class GenuineExecution(Contract):
    """Proposed untrusted wire data, NOT a validated live execution or approval."""
    schema: ClassVar[str] = 'research_genuine_execution.proposed.v1'
    environment: str
    invocation_digest: str
    issuer: str
    external_operation_id: str
    attestation_ref: str
    output_digest: str

    def validate(self):
        digest(self.invocation_digest)
        digest(self.output_digest)


class ProviderPort(Protocol):
    def research(self, context, invocation: ModelInvocation, source: SourceResult) -> ResearchDraft: ...
    def reconcile(self, context, invocation: ModelInvocation) -> ResearchDraft | None: ...


class IndependentVerifierPort(Protocol):
    def verify(self, context, invocation: ModelInvocation, source: SourceResult,
               packet: ResearchPacket) -> VerifierProposal: ...
    def reconcile(self, context, invocation: ModelInvocation) -> VerifierProposal | None: ...


class FakeExecutionPort:
    """Uses existing fixed assignments, budget ledger and model checkpoints.

    Shared execution validates the trusted plan, deadlines, task/call ceilings
    and the same reservations/checkpoints used by the Research Director.
    """
    def __init__(self, store, provider, *, clock, max_units=4, test_only=False, production=False):
        offline_only(test_only, production)
        require(type(provider) is SyntheticModelProvider, 'only existing synthetic provider accepted')
        integer(max_units, 1)
        require(max_units <= 16, 'bounded call ceiling required')
        self.store, self.provider, self.clock, self.max_units = store, provider, clock, max_units
        self.journal = WorkflowJournal(store._root, store._authority)

    def _authorize(self, context, invocation):
        self.store._authority.authorize(context, invocation.environment, ('researcher', 'verifier'))
        if invocation.agent.principal != context.principal or invocation.agent.role != context.role:
            raise AuthorizationError('assigned principal required')
        plan = self.journal.load(context, invocation.task_id, 'plan', ResearchPlan)
        if plan is None or invocation.agent not in (plan.lead, *plan.supporting, plan.verifier):
            raise AuthorizationError('principal/specialty is not delegated by the trusted Director plan')
        validate_invocation(self.store, context, plan, invocation)
        require(invocation.units <= self.max_units, 'port call ceiling exceeded')
        return plan

    def reconcile(self, context, invocation):
        plan = self._authorize(context, invocation)
        with self.journal.lock(context, invocation.task_id):
            return reconcile_execution(self.store, self.journal, context, plan, invocation)

    def _call(self, context, invocation, source, packet=None):
        plan = self._authorize(context, invocation)
        task = self.store.get_task(context, invocation.task_id)
        require(source.environment == context.environment and source.submitted == task.request.sources[0] and
                source.digest == invocation.source_digest and source.evidence and
                source.outcome in ('SUPPORTED_FETCHED', 'PARTIAL'), 'source/task mismatch or unavailable evidence')
        if packet is not None:
            require(context.role == 'verifier' and packet.researcher != context.principal and
                    packet.environment == context.environment and packet.task_id == invocation.task_id and
                    packet.packet_version == invocation.packet_version and packet.source == source.submitted and
                    invocation.packet_digest == (packet.digest,), 'independent exact-packet verifier required')
            require(self.store.get_packet(context, packet.task_id) == packet,
                    'packet is not the current durable revision')
        else:
            require(context.role == 'researcher' and not invocation.packet_digest, 'researcher invocation required')
        with self.journal.lock(context, invocation.task_id):
            return execute_invocation(self.store, self.journal, self.provider, context, plan,
                                      invocation, source, packet, self.clock, reject_late=True)

    def research(self, context, invocation, source):
        return self._call(context, invocation, source)

    def verify(self, context, invocation, source, packet):
        return self._call(context, invocation, source, packet)


class MemoryIntegrationPort(Protocol):
    def submit(self, context, candidate: KnowledgeCandidate) -> MemoryReceipt: ...
    def commit(self, context, command: MemoryCommand) -> MemoryReceipt: ...
    def promote(self, context, command: MemoryCommand) -> MemoryReceipt: ...
    def retrieve(self, context, command: MemoryCommand) -> RetrievalResult: ...
    def reconcile_receipt(self, context, receipt: MemoryReceipt) -> MemoryReceipt: ...
    def completion_snapshot(self, context, receipts: tuple[MemoryReceipt, ...]): ...


class FakeMemoryPort:
    """Delegate all authority/currentness/receipt repair to accepted fake Memory."""
    def __init__(self, adapter, *, test_only=False, production=False):
        offline_only(test_only, production)
        require(type(adapter) is FakeMemoryAdapter, 'accepted fake Memory required')
        self.adapter = adapter

    def submit(self, context, candidate): return self.adapter.submit(context, candidate)
    def commit(self, context, command): return self.adapter.commit(context, command)
    def promote(self, context, command): return self.adapter.promote(context, command)
    def retrieve(self, context, command): return self.adapter.retrieve(context, command)
    def reconcile_receipt(self, context, receipt): return self.adapter.reconcile_receipt(context, receipt)
    def completion_snapshot(self, context, receipts): return self.adapter.completion_snapshot(context, receipts)


class PhotonPort(Protocol):
    def acknowledge(self, context, notice: Notice) -> TransportReceipt: ...
    def complete(self, context, notice: Notice, result: FlowResult) -> TransportReceipt: ...
    def reconcile(self, context, notice: Notice) -> TransportReceipt | None: ...


class FakePhotonPort:
    def __init__(self, notifications, *, test_only=False, production=False):
        offline_only(test_only, production)
        require(type(notifications) is Notifications, 'accepted fake notifications required')
        self.notifications = notifications

    def acknowledge(self, context, notice):
        require(notice.kind == 'ACK', 'acknowledgment receipt is distinct from completion')
        self.notifications.store.get_task(context, notice.research_task_id)
        self.notifications.deliver(context, notice)
        return self.reconcile(context, notice)

    def complete(self, context, notice, result):
        require(notice.kind == 'FINAL', 'final notification required')
        self.notifications.deliver(context, notice, result=result)
        return self.reconcile(context, notice)

    def reconcile(self, context, notice):
        return self.notifications.transport.lookup(context, notice)


@dataclass(frozen=True, kw_only=True)
class CTOProposal(Contract):
    schema: ClassVar[str] = 'research_cto_proposal.proposed.v1'
    environment: str
    proposal: Proposal
    research_task_id: str
    packet_digest: str
    packet_version: int
    decision_id: str
    specialist_id: str
    execution_authorized: bool = False
    marking: str = MARKING

    def validate(self):
        digest(self.packet_digest)
        integer(self.packet_version, 1)
        require(self.proposal.environment == self.environment and self.proposal.department == 'Development',
                'Development proposal scope required')
        mapping = dict(zip(('Frontend', 'Backend', 'Full-Stack', 'DevOps', 'Data Engineering', 'Data Science',
                            'AI/ML', 'Integration', 'Security', 'Mobile', 'Performance'),
                           ('frontend', 'backend', 'full_stack', 'devops', 'data_engineer', 'data_scientist',
                            'ai_ml', 'integration', 'security', 'mobile', 'performance')))
        require(mapping.get(self.proposal.specialist) == self.specialist_id, 'unknown or mismatched specialist')
        require(not self.execution_authorized and self.marking == MARKING, 'proposal cannot grant execution or production approval')


class CTOProposalPort(Protocol):
    def propose(self, context, proposal: CTOProposal) -> CTOProposal: ...
    def reconcile(self, context, proposal: CTOProposal) -> CTOProposal | None: ...


class FakeCTOPort:
    """Records a local proposal only. No remote CTO acceptance is implied."""
    def __init__(self, store, *, test_only=False, production=False):
        offline_only(test_only, production)
        self.store = store
        self.journal = WorkflowJournal(store._root, store._authority)

    def _namespace(self, context, proposal):
        self.store._authority.authorize(context, proposal.environment, ('director',))
        return 'cto-proposal-' + hash_content(proposal.proposal.proposal_id)

    def propose(self, context, proposal):
        namespace = self._namespace(context, proposal)
        packet = self.store.get_packet(context, proposal.research_task_id)
        require(packet.digest == proposal.packet_digest and packet.packet_version == proposal.packet_version,
                'proposal requires current immutable packet')
        require(any(d.decision_id == proposal.decision_id and d.packet_digest == packet.digest and
                    d.verdict == 'APPROVED' for d in self.store.verification_history(context, packet.task_id)),
                'proposal requires exact independent verification')
        require(proposal.proposal.source_revision == (packet.source.revision,), 'proposal source revision mismatch')
        source = self.journal.load(context, packet.task_id, 'source:' + str(packet.packet_version), SourceResult)
        require(source is not None and source.submitted == packet.source and
                proposal.proposal.source_digest == source.digest and bool(proposal.proposal.evidence_ids) and
                set(proposal.proposal.evidence_ids) <= {e.evidence_id for e in source.evidence},
                'proposal source/evidence mismatch')
        self.journal.provision(context, namespace)
        with self.journal.lock(context, namespace):
            return self.journal.commit(context, namespace, 'packet:local-proposal', proposal)

    def reconcile(self, context, proposal):
        namespace = self._namespace(context, proposal)
        result = self.journal.load(context, namespace, 'packet:local-proposal', CTOProposal)
        require(result is None or result == proposal, 'conflicting proposal replay')
        return result
