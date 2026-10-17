"""Offline project attachment model. No SDK, secrets, sockets or live issuer.

Trusted fixture bootstrap issues observations; serialized metadata is never trust.
Pending ACKs precede task creation, so task-based FINAL notifications stay outside
this seam. The existing intake journal and reconcile-before-effect pattern apply.
"""
from dataclasses import dataclass
from types import MappingProxyType
from typing import ClassVar

from ..contracts import Contract, hash_content, require
from ..tenancy import AuthorizationError
from .canary_contracts import MARKING, offline_only
from .hermes_intake import identity, PersonalHermesIntake


@dataclass(frozen=True, kw_only=True)
class ProjectBinding(Contract):
    schema: ClassVar[str] = 'photon_project_binding.offline.v1'
    project: str
    line: str
    conversation: str
    sender: str
    profile: str
    credential_ref: str
    role: str

    def validate(self):
        for value in (self.project, self.line, self.conversation, self.sender,
                      self.profile, self.credential_ref):
            identity(value)
        require(self.role in ('personal', 'research'), 'unknown project role')

    @property
    def scope(self):
        return (self.project, self.line, self.conversation)

    @property
    def issuer(self):
        return 'photon-project-' + hash_content(self.scope)


@dataclass(frozen=True, kw_only=True)
class ProjectObservation(Contract):
    schema: ClassVar[str] = 'photon_project_observation.offline.v1'
    binding: ProjectBinding
    event_id: str
    text: str
    objective: str
    sources: tuple

    def validate(self):
        identity(self.event_id)
        require(type(self.binding) is ProjectBinding, 'binding required')
        require(type(self.text) is str and len(self.text.encode()) <= 65536, 'bounded text required')

    @property
    def key(self):
        return hash_content((self.schema, *self.binding.scope, self.event_id))


@dataclass(frozen=True, kw_only=True)
class ProjectSend(Contract):
    schema: ClassVar[str] = 'photon_project_ack.offline.v1'
    binding: ProjectBinding
    event_key: str
    operation_id: str
    text: str
    environment: str = 'personal'
    marking: str = MARKING

    def validate(self):
        from ..contracts import digest
        require(type(self.binding) is ProjectBinding, 'binding required')
        digest(self.event_key); digest(self.operation_id)
        require(self.environment == 'personal' and self.marking == MARKING and self.text ==
                'SIMULATED: Research intake accepted; source acquisition pending. Research is not complete.',
                'only synthetic acceptance ACK supported')


class FakeProjectConnection:
    """Independent fixture credential reference and durable simulated acceptance.

    lookup None is authoritative absence ONLY in this fake. Live unknown outcomes
    must not be translated to None. Credentials are never resolved here.
    """
    def __init__(self, binding, journal, director, *, test_only=False, production=False, hook=None):
        offline_only(test_only, production)
        require(type(binding) is ProjectBinding, 'exact binding required')
        self.binding, self.journal, self.director = binding, journal, director
        self.hook = hook or (lambda stage: None)
        self._issued = {}

    def observe(self, *, sender, line, conversation, event_id, text, objective='', sources=()):
        # Trusted synthetic provider boundary, never an exposed payload API.
        if (sender, line, conversation) != (self.binding.sender, self.binding.line, self.binding.conversation):
            raise AuthorizationError('provider identity does not match approved binding')
        event = ProjectObservation(binding=self.binding, event_id=event_id,
            text=text, objective=objective, sources=tuple(sources))
        self._issued[id(event)] = event
        return event

    def authenticate(self, event):
        if type(event) is not ProjectObservation or self._issued.get(id(event)) is not event:
            raise AuthorizationError('unissued project observation')
        if event.binding != self.binding:
            raise AuthorizationError('project binding mismatch')
        return event

    def _namespace(self, send):
        require(send.binding == self.binding, 'cross-project send denied')
        return 'project-send-' + hash_content((self.binding.scope, send.operation_id))

    def reconcile(self, send):
        ns = self._namespace(send)
        prior = self.journal.load(self.director, ns, 'packet:accepted', ProjectSend)
        require(prior is None or prior == send, 'send operation payload conflict')
        return prior

    def send(self, send):
        ns = self._namespace(send)
        self.journal.provision(self.director, ns)
        with self.journal.lock(self.director, ns):
            prior = self.reconcile(send)
            if prior is not None:
                return prior
            self.journal.commit(self.director, ns, 'packet:accepted', send)
            self.hook('accepted')
            return send  # Simulated acceptance, never recipient delivery.


@dataclass(frozen=True)
class DispatchResult:
    status: str
    profile: str
    acknowledgment: object = None


class ProjectAttachment:
    """One existing orchestrator seam; Personal remains its original callback.

    Exact fake types are deliberate production locks. No arbitrary transport or
    credential resolver can turn this offline model into a live connector.
    """
    def __init__(self, connections, intake, host_context, personal_handler, *,
                 research_enabled=False, test_only=False, production=False):
        offline_only(test_only, production)
        require(type(intake) is PersonalHermesIntake, 'existing pending intake required')
        require(type(research_enabled) is bool, 'explicit enable state required')
        require(len(connections) == 2 and all(type(c) is FakeProjectConnection for c in connections),
                'two independently scoped fake connections required')
        bindings = [c.binding for c in connections]
        require({b.role for b in bindings} == {'personal', 'research'} and
                len({b.project for b in bindings}) == 2 and
                len({b.credential_ref for b in bindings}) == 2,
                'projects and credential references must be distinct')
        self.connections = MappingProxyType({c.binding.project: c for c in connections})
        self.intake, self.host_context = intake, host_context
        self.personal_handler = personal_handler
        self.research_enabled = research_enabled
        research = next(b for b in bindings if b.role == 'research')
        routes = list(intake.routes.values())
        require(len(routes) == 1 and routes[0].issuer == research.issuer and
                (routes[0].recipient, routes[0].conversation_id, routes[0].sender_id, routes[0].profile) ==
                (research.line, research.conversation, research.sender, research.profile),
                'intake route must exactly bind Research connection')

    def dispatch(self, connection, event):
        if self.connections.get(connection.binding.project) is not connection:
            raise AuthorizationError('unconfigured connection capability')
        event = connection.authenticate(event)
        binding = connection.binding
        if binding.role == 'personal':
            return self.personal_handler(event)  # No Research rewriting or retry owner.
        if not self.research_enabled:
            return DispatchResult('UNAVAILABLE', binding.profile)
        try:
            observed = self.intake.host.observe(self.host_context, issuer=binding.issuer,
                platform='photon', profile=binding.profile, recipient=binding.line,
                conversation_id=binding.conversation, sender_id=binding.sender,
                event_id=event.event_id, message_text=event.text, objective=event.objective,
                sources=event.sources)
            ack = self.intake.accept(observed)
            return DispatchResult('INTAKE_ACCEPTED', binding.profile, ack)
        except Exception:
            # Terminal outcome, never delegation to the ordinary Personal agent.
            return DispatchResult('UNAVAILABLE', binding.profile)

    def acknowledge(self, connection, event):
        # Reauthenticate and reauthorize rather than accept caller-supplied From
        # metadata or an acknowledgment copied from another project.
        if connection.binding.role != 'research':
            raise AuthorizationError('Research ACK cannot use Personal connection')
        result = self.dispatch(connection, event)
        if result.status != 'INTAKE_ACCEPTED':
            raise AuthorizationError('Research intake unavailable')
        send = ProjectSend(binding=connection.binding, event_key=event.key,
            operation_id=result.acknowledgment.operation_id,
            text='SIMULATED: Research intake accepted; source acquisition pending. Research is not complete.')
        prior = connection.reconcile(send)  # Lookup failure propagates; no resend.
        return prior if prior is not None else connection.send(send)
