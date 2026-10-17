"""Phase 3 offline Research workforce; all providers and verdicts are simulated."""
from .contracts import ResearchAgent, ResearchPolicy, ResearchAssertion, SPECIALTIES, SIMULATION
from .provider import ModelProvider, SyntheticModelProvider, SyntheticFixture
from .workflow import AgentRoster, ResearchDirector, IndependentVerificationAgent

__all__ = ['ResearchAgent', 'ResearchPolicy', 'ResearchAssertion', 'SPECIALTIES', 'SIMULATION',
           'ModelProvider', 'SyntheticModelProvider', 'SyntheticFixture', 'AgentRoster',
           'ResearchDirector', 'IndependentVerificationAgent']
