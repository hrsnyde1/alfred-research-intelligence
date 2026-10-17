"""Exact-content, tenant and independent-principal decision checks."""
from .contracts import ResearchPacket, VerificationDecision, require
from .tenancy import AuthorizationError


def validate_decision(authority, context, packet, decision):
    require(type(packet) is ResearchPacket and type(decision) is VerificationDecision,
            'validated packet and decision required')
    authority.authorize(context, packet.environment, roles=('verifier',))
    if decision.environment != packet.environment or decision.verifier != context.principal:
        raise AuthorizationError('verification environment or principal mismatch')
    if packet.researcher == context.principal:
        raise AuthorizationError('self verification forbidden')
    require(packet.digest == decision.packet_digest, 'stale packet decision')
    return decision.verdict
