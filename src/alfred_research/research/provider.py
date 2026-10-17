"""Minimal model port plus deterministic, explicitly test-only implementation."""
from dataclasses import dataclass
from typing import ClassVar, Protocol
from ..contracts import Contract, require, hash_content, integer
from ..tenancy import AuthorizationError
from .contracts import ResearchAssertion, ResearchDraft, VerifierProposal


class ModelProvider(Protocol):
    def research(self, invocation, source): ...
    def verify(self, invocation, source, packet): ...


@dataclass(frozen=True, kw_only=True)
class SyntheticFixture(Contract):
    schema: ClassVar[str] = 'research_synthetic_fixture.v1'
    assertions: tuple[ResearchAssertion, ...] = ()
    verdict: str = 'APPROVED'
    rationale: str = 'Synthetic fixture assessment only'
    corrections: tuple[str, ...] = ()
    unknowns: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    consumed_units: int = 1

    def validate(self):
        integer(self.consumed_units, 1)
        require(self.verdict in ('APPROVED', 'REJECTED', 'NEEDS_MORE_RESEARCH'), 'invalid test verdict')
        require(len(self.assertions) <= 8 and len(self.corrections) <= 8 and len(self.unknowns) <= 8 and
                len(self.limitations) <= 8, 'bounded synthetic fixture required')


class SyntheticModelProvider:
    def __init__(self, fixtures=None, *, test_only=False, production=False):
        if test_only is not True or production:
            raise AuthorizationError('only explicit synthetic test execution is enabled')
        self._fixtures = dict(fixtures or {})
        require(all(type(k) is str and type(v) is SyntheticFixture for k, v in self._fixtures.items()),
                'typed synthetic fixtures required')

    @property
    def configuration_digest(self):
        return hash_content({k: v.payload() for k, v in self._fixtures.items()})

    def _fixture(self, invocation, source):
        require(invocation.provider_configuration == self.configuration_digest, 'changed synthetic provider configuration')
        require(invocation.source_digest == source.digest, 'provider source mismatch')
        require(invocation.agent.model.provider == 'synthetic' and
                invocation.agent.model.model.startswith(('synthetic-', 'test-')), 'non-test model disabled')
        return self._fixtures.get(invocation.key, SyntheticFixture())

    def research(self, invocation, source):
        require(invocation.agent.role == 'researcher', 'researcher invocation required')
        fixture = self._fixture(invocation, source)
        assertions = fixture.assertions or tuple(ResearchAssertion(assertion_id='quote-' + str(i),
            statement=e.text[:4096], supporting=(e.evidence_id,)) for i, e in enumerate(source.evidence[:2]))
        return ResearchDraft(environment=invocation.environment, task_id=invocation.task_id,
            principal=invocation.agent.principal, invocation_digest=invocation.digest,
            assertions=assertions, unknowns=fixture.unknowns, limitations=fixture.limitations,
            consumed_units=fixture.consumed_units)

    def verify(self, invocation, source, packet):
        require(invocation.agent.role == 'verifier' and invocation.packet_digest == (packet.digest,),
                'exact verifier invocation required')
        fixture = self._fixture(invocation, source)
        return VerifierProposal(environment=invocation.environment, task_id=invocation.task_id,
            principal=invocation.agent.principal, invocation_digest=invocation.digest,
            verdict=fixture.verdict, rationale=fixture.rationale, corrections=fixture.corrections,
            consumed_units=fixture.consumed_units)
