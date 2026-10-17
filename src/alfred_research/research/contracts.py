"""Research-only workflow contracts; all Phase 3 execution is simulated."""
from dataclasses import dataclass
from typing import ClassVar
from ..contracts import (Contract, ModelAssignment, ResearchPacket, require, integer,
                         digest, hash_content)

SPECIALTIES = ('technology_code', 'finance_tax', 'legal_compliance', 'business_market', 'general')
SIMULATION = 'SIMULATED research/verification only; not real-world factual verification'


@dataclass(frozen=True, kw_only=True)
class ResearchAgent(Contract):
    schema: ClassVar[str] = 'research_agent.v1'
    environment: str
    principal: str
    role: str
    specialty: str
    model: ModelAssignment

    def validate(self):
        require(self.role in ('director', 'researcher', 'verifier'), 'invalid agent role')
        require(self.specialty in SPECIALTIES, 'invalid logical specialty')
        require(len(self.principal) <= 128, 'bounded agent identity required')
        require(self.model.environment == self.environment and self.model.specialist == self.role,
                'fixed role/model scope mismatch')
        require(self.model.approved, 'explicit test model approval required')


@dataclass(frozen=True, kw_only=True)
class ResearchPolicy(Contract):
    schema: ClassVar[str] = 'research_policy.v1'
    deadline: int
    max_task_cost: int
    max_call_units: int = 4

    def validate(self):
        integer(self.deadline, 1)
        integer(self.max_task_cost, 1)
        integer(self.max_call_units, 1)
        require(self.max_call_units <= 16, 'call authorization exceeds offline ceiling')


@dataclass(frozen=True, kw_only=True)
class ResearchPlan(Contract):
    schema: ClassVar[str] = 'research_plan.v1'
    environment: str
    task_id: str
    director: ResearchAgent
    lead: ResearchAgent
    supporting: tuple[ResearchAgent, ...]
    support_reasons: tuple[str, ...]
    verifier: ResearchAgent
    policy: ResearchPolicy
    provider_configuration: str

    def validate(self):
        require(self.director.role == 'director' and self.lead.role == 'researcher' and
                self.verifier.role == 'verifier', 'plan role mismatch')
        agents = (self.director, self.lead, *self.supporting, self.verifier)
        require(all(a.environment == self.environment for a in agents), 'mixed plan environments')
        require(len(self.supporting) <= 2 and len(self.supporting) == len(self.support_reasons),
                'bounded justified support required')
        require(all(a.role == 'researcher' for a in self.supporting), 'support role mismatch')
        require(len({a.principal for a in agents}) == len(agents), 'independent plan principals required')
        digest(self.provider_configuration)


@dataclass(frozen=True, kw_only=True)
class ResearchAssertion(Contract):
    schema: ClassVar[str] = 'research_assertion.v1'
    assertion_id: str
    statement: str
    supporting: tuple[str, ...]
    contradicting: tuple[str, ...] = ()
    kind: str = 'finding'

    def validate(self):
        require(len(self.assertion_id) <= 128 and len(self.statement) <= 4096, 'bounded assertion required')
        require(self.kind in ('finding', 'inference', 'forecast', 'unknown'), 'invalid assertion kind')
        require(bool(self.supporting) and len(self.supporting) <= 16 and len(self.contradicting) <= 16,
                'bounded supporting evidence required')
        require(len(set(self.supporting)) == len(self.supporting) and
                len(set(self.contradicting)) == len(self.contradicting), 'duplicate evidence citation')
        require(all(len(i) <= 128 for i in (*self.supporting, *self.contradicting)), 'bounded citation required')


@dataclass(frozen=True, kw_only=True)
class ModelInvocation(Contract):
    schema: ClassVar[str] = 'research_model_invocation.v1'
    environment: str
    task_id: str
    packet_version: int
    agent: ResearchAgent
    source_digest: str
    packet_digest: tuple[str, ...]
    deadline: int
    units: int
    provider_configuration: str

    def validate(self):
        require(self.agent.environment == self.environment, 'model invocation scope mismatch')
        integer(self.packet_version, 1)
        integer(self.deadline, 1)
        integer(self.units, 1)
        require(self.units <= 16 and len(self.packet_digest) <= 1, 'bounded invocation required')
        digest(self.source_digest)
        digest(self.provider_configuration)
        for value in self.packet_digest:
            digest(value)

    @property
    def digest(self):
        return hash_content(self)

    @property
    def key(self):
        return f'{self.environment}/{self.task_id}/{self.packet_version}/{self.agent.principal}'


@dataclass(frozen=True, kw_only=True)
class ResearchDraft(Contract):
    schema: ClassVar[str] = 'research_draft.v1'
    environment: str
    task_id: str
    principal: str
    invocation_digest: str
    assertions: tuple[ResearchAssertion, ...]
    unknowns: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    consumed_units: int = 1
    simulation_only: bool = True

    def validate(self):
        digest(self.invocation_digest)
        require(self.simulation_only is True, 'real provider execution disabled')
        require(0 < len(self.assertions) <= 8 and len({a.assertion_id for a in self.assertions}) == len(self.assertions),
                'bounded unique assertions required')
        require(len(self.unknowns) <= 8 and len(self.limitations) <= 8 and
                all(len(v) <= 512 for v in (*self.unknowns, *self.limitations)), 'bounded draft notes required')
        integer(self.consumed_units, 1)


@dataclass(frozen=True, kw_only=True)
class VerifierProposal(Contract):
    schema: ClassVar[str] = 'simulated_verifier_proposal.v1'
    environment: str
    task_id: str
    principal: str
    invocation_digest: str
    verdict: str
    rationale: str
    corrections: tuple[str, ...] = ()
    consumed_units: int = 1
    simulation_only: bool = True

    def validate(self):
        digest(self.invocation_digest)
        require(self.verdict in ('APPROVED', 'REJECTED', 'NEEDS_MORE_RESEARCH'), 'invalid simulated verdict')
        require(self.simulation_only is True, 'real verifier execution disabled')
        require(len(self.rationale) <= 512 and len(self.corrections) <= 8 and
                all(len(v) <= 512 for v in self.corrections), 'bounded verification notes required')
        integer(self.consumed_units, 1)


@dataclass(frozen=True, kw_only=True)
class ClaimTrace(Contract):
    schema: ClassVar[str] = 'research_claim_trace.v1'
    claim_id: str
    contributor: str
    supporting: tuple[str, ...]
    contradicting: tuple[str, ...]


@dataclass(frozen=True, kw_only=True)
class PacketPreparation(Contract):
    schema: ClassVar[str] = 'research_packet_preparation.v1'
    environment: str
    task_id: str
    packet: ResearchPacket
    source_digest: str
    traces: tuple[ClaimTrace, ...]

    def validate(self):
        digest(self.source_digest)
        require(self.packet.environment == self.environment and self.packet.task_id == self.task_id,
                'packet preparation scope mismatch')
        require(tuple(t.claim_id for t in self.traces) == tuple(c.claim_id for c in self.packet.claims),
                'every claim requires one ordered trace')


@dataclass(frozen=True, kw_only=True)
class ClaimAssessment(Contract):
    schema: ClassVar[str] = 'research_claim_assessment.v1'
    claim_id: str
    verdict: str
    rationale: str

    def validate(self):
        require(self.verdict in ('APPROVED', 'REJECTED', 'NEEDS_MORE_RESEARCH'), 'invalid claim assessment')


@dataclass(frozen=True, kw_only=True)
class VerificationReview(Contract):
    schema: ClassVar[str] = 'research_verification_review.v1'
    environment: str
    task_id: str
    packet_version: int
    packet_digest: str
    source_digest: str
    verifier: str
    verdict: str
    assessments: tuple[ClaimAssessment, ...]
    corrections: tuple[str, ...]
    limitations: tuple[str, ...]
    simulation_only: bool = True

    def validate(self):
        integer(self.packet_version, 1)
        digest(self.packet_digest)
        digest(self.source_digest)
        require(self.simulation_only is True and bool(self.assessments), 'simulated per-claim review required')
        require(self.verdict in ('APPROVED', 'REJECTED', 'NEEDS_MORE_RESEARCH'), 'invalid review verdict')
        require(len({a.claim_id for a in self.assessments}) == len(self.assessments), 'duplicate claim assessment')

    @property
    def digest(self):
        return hash_content(self)
