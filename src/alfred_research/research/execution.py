"""Shared offline invocation validation/accounting. No production execution.

Callers hold the existing task journal lock for execution/reconciliation. The
reservation ID deliberately preserves the accepted Director convention.
"""
from dataclasses import dataclass
from hashlib import sha256
from typing import ClassVar

from ..contracts import Contract, digest, hash_content, require
from ..tenancy import AuthorizationError
from ..budgets import EscalationRequired
from .contracts import ModelInvocation, ResearchDraft, VerifierProposal


@dataclass(frozen=True, kw_only=True)
class RejectedExecution(Contract):
    schema: ClassVar[str] = 'research_rejected_execution.v1'
    environment: str
    task_id: str
    principal: str
    invocation_digest: str
    reason: str

    def validate(self):
        digest(self.invocation_digest)


def reservation_id(invocation):
    key = f'{invocation.packet_version}:{invocation.agent.principal}'
    return 'research-' + sha256((invocation.task_id + ':' + key).encode()).hexdigest()


def validate_invocation(store, context, plan, invocation):
    require(type(invocation) is ModelInvocation, 'typed invocation required')
    store._authority.authorize(context, plan.environment, ('researcher', 'verifier'))
    if invocation.agent.principal != context.principal or invocation.agent.role != context.role:
        raise AuthorizationError('assigned invocation principal required')
    if invocation.agent not in (plan.lead, *plan.supporting, plan.verifier):
        raise AuthorizationError('invocation agent is not delegated by the Director')
    require(invocation.environment == plan.environment and invocation.task_id == plan.task_id,
            'invocation plan scope mismatch')
    require(invocation.deadline == plan.policy.deadline and invocation.units <= plan.policy.max_call_units,
            'invocation cannot change trusted deadline or call ceiling')
    fixed = store._models.resolve(context.environment, context.role,
                                  invocation.agent.model.provider, invocation.agent.model.model)
    require(fixed == invocation.agent.model, 'invocation model/price/approval mismatch')
    if context.role == 'researcher':
        require(invocation.provider_configuration == plan.provider_configuration,
                'research provider configuration differs from trusted plan')
    task = store.get_task(context, plan.task_id)
    require(invocation.packet_version <= task.request.max_retries + 1,
            'invocation revision exceeds retry authorization')


def validate_response(invocation, response):
    expected = ResearchDraft if invocation.agent.role == 'researcher' else VerifierProposal
    require(type(response) is expected and response.simulation_only is True and
            response.environment == invocation.environment and response.task_id == invocation.task_id and
            response.principal == invocation.agent.principal and response.invocation_digest == invocation.digest and
            response.consumed_units <= invocation.units,
            'invalid or substituted synthetic provider response')
    # The digest binds the complete assigned model/provider/price/approval as
    # well as source, packet, role, principal and limits. Output schemas do not
    # contain an independent model field that could supersede this assignment.
    return response


def reconcile_execution(store, journal, context, plan, invocation):
    """Recover a validated output and its existing reservation; never execute."""
    validate_invocation(store, context, plan, invocation)
    key = f'{invocation.packet_version}:{context.principal}'
    prior = journal.load(context, plan.task_id, 'intent:' + key, ModelInvocation)
    require(prior is None or prior == invocation, 'conflicting model operation replay')
    cls = ResearchDraft if context.role == 'researcher' else VerifierProposal
    response = journal.load(context, plan.task_id, 'output:' + key, cls)
    require(response is None or prior is not None, 'model output lacks authorized invocation intent')
    if response is not None:
        validate_response(invocation, response)
        # Never create a new reservation to legitimize an orphaned output.
        store.settle(context, reservation_id(invocation),
                     response.consumed_units * invocation.agent.model.price_units)
    return response


def execute_invocation(store, journal, provider, context, plan, invocation, source, packet, clock,
                       *, reject_late=False):
    """Shared by Director and harness; caller already holds task lock."""
    validate_invocation(store, context, plan, invocation)
    require(invocation.provider_configuration == provider.configuration_digest,
            'provider configuration substitution')
    key = f'{invocation.packet_version}:{context.principal}'
    response = reconcile_execution(store, journal, context, plan, invocation)
    if response is not None:
        return response  # Existing authorized work may reconcile after expiry.
    if clock() >= plan.policy.deadline:
        raise EscalationRequired('trusted research deadline exhausted; no new model call')
    prior = journal.load(context, plan.task_id, 'intent:' + key, ModelInvocation)
    if prior is None:
        intents = journal.records(context, plan.task_id, 'intent:', ModelInvocation)
        committed = sum(i.units * i.agent.model.price_units for i in intents)
        if committed + invocation.units * invocation.agent.model.price_units > plan.policy.max_task_cost:
            raise EscalationRequired('task research budget exhausted; Director escalation required')
        journal.commit(context, plan.task_id, 'intent:' + key, invocation)
    reservation = store.reserve(context, reservation_id(invocation), context.role,
        invocation.agent.model.provider, invocation.agent.model.model, invocation.units)
    require(reservation.state == 'reserved', 'settled/cancelled reservation lacks successful output; reconciliation required')
    if clock() >= plan.policy.deadline:
        raise EscalationRequired('trusted research deadline exhausted before execution')
    try:
        response = (provider.research(invocation, source) if packet is None else
                    provider.verify(invocation, source, packet))
        validate_response(invocation, response)
        if reject_late:
            require(clock() < plan.policy.deadline, 'provider returned after deadline; reservation held')
    except Exception:
        failure = RejectedExecution(environment=invocation.environment, task_id=invocation.task_id,
            principal=context.principal, invocation_digest=invocation.digest,
            reason='Provider response rejected or execution failed; no successful output; reservation held')
        journal.commit(context, plan.task_id, 'output:rejected:' + hash_content(failure), failure)
        raise
    journal.commit(context, plan.task_id, 'output:' + key, response)
    store.settle(context, reservation_id(invocation), response.consumed_units * invocation.agent.model.price_units)
    return response
