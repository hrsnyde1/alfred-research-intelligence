"""In-process capabilities issued only by trusted offline bootstrap code.

Not a remote authentication protocol. Never construct this authority from LLM data.
"""
from dataclasses import dataclass
from typing import ClassVar
from .contracts import Contract, ROLES, environment, require, text


class AuthorizationError(PermissionError):
    pass


@dataclass(frozen=True, kw_only=True)
class AuthenticatedContext(Contract):
    schema: ClassVar[str] = "authenticated_context.v1"
    environment: str
    principal: str
    role: str

    def validate(self):
        require(self.role in ROLES, 'unknown authenticated role')


class OfflineAuthority:
    def __init__(self, grants):
        self._grants = dict(grants)
        self._issued = {}
        for principal, (env, role) in self._grants.items():
            text(principal)
            environment(env)
            require(role in ROLES, 'unknown role')

    def context(self, principal):
        """Trusted test/bootstrap entrypoint, never expose as public login."""
        if principal not in self._grants:
            raise AuthorizationError('unknown principal')
        env, role = self._grants[principal]
        context = AuthenticatedContext(environment=env, principal=principal, role=role)
        self._issued[id(context)] = context
        return context

    def authorize(self, context, env=None, roles=ROLES):
        if (type(context) is not AuthenticatedContext or
                self._issued.get(id(context)) is not context or
                self._grants.get(context.principal) != (context.environment, context.role) or
                (env is not None and context.environment != env) or context.role not in roles):
            raise AuthorizationError('unissued context, wrong environment or unauthorized role')
        return context.environment
