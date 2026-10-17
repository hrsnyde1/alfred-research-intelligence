"""Personal-only Hermes attachment library; no listener, transport or live trust.

The trusted host must authenticate an event BEFORE calling this seam. The only
issuer implemented here is an explicit offline capability fixture, not Photon
JSON authentication. Production and genuine acquisition remain fail-closed.
"""
from dataclasses import dataclass
from types import MappingProxyType
from typing import ClassVar

from ..contracts import Contract, canonical, digest, hash_content, require
from ..tenancy import AuthorizationError, OfflineAuthority
from ..research.journal import WorkflowJournal
from .canary_contracts import (MARKING, GitHubReference, ResearchIntake,
    ConversationBinding, IntakeMapping, PendingSources, PendingAcquisition,
    offline_only)

INDEX = 'hermes-personal-intake-v1'


def identity(value):
    require(type(value) is str and 0 < len(value) <= 128 and value == value.strip()
            and not any(ord(c) < 32 or c in '*?' for c in value),
            'exact bounded host identity required; no wildcards or fallback')


@dataclass(frozen=True, kw_only=True)
class ObservedHermesEvent(Contract):
    """Normalized data, not authentication. Only an issued instance is accepted."""
    schema: ClassVar[str] = 'research_hermes_event.offline.v1'
    issuer: str
    host_principal: str
    platform: str
    profile: str
    recipient: str
    conversation_id: str
    sender_id: str
    event_id: str
    message_text: str
    message_digest: str
    objective: str
    sources: tuple[GitHubReference, ...]
    marking: str = MARKING

    def validate(self):
        for value in (self.issuer, self.host_principal, self.platform, self.profile, self.recipient,
                      self.conversation_id, self.sender_id, self.event_id):
            identity(value)
        require(self.platform == 'photon', 'only existing Photon/Hermes seam supported')
        digest(self.message_digest)
        require(self.message_digest == hash_content(self.message_text), 'message digest mismatch')
        require(len(self.sources) == 1, 'exactly one submitted source required')
        require(self.marking == MARKING, 'offline observation only')
        require(len(canonical(self)) <= 65536, 'intake event oversized')

    @property
    def route_key(self):
        return (self.issuer, self.platform, self.profile, self.recipient, self.conversation_id)


class OfflineHermesAuthentication:
    """Trusted synthetic host bootstrap only, never a callable login endpoint.

    Authenticity is issued object identity plus a separately injected current
    host capability. A copied/deserialized event has no authority. No keys,
    credentials, network sockets or production host authentication are provided.
    """
    def __init__(self, authority, issuers, *, test_only=False, production=False):
        offline_only(test_only, production)
        require(type(authority) is OfflineAuthority, 'offline host authority required')
        require(bool(issuers), 'host issuer authorization absent')
        self.authority = authority
        self.issuers = MappingProxyType(dict(issuers))
        self._issued = {}
        self._events = {}
        for issuer in self.issuers:
            identity(issuer)
            self.check_issuer(issuer)

    def check_issuer(self, issuer):
        context = self.issuers.get(issuer)
        if context is None:
            raise AuthorizationError('unknown authenticated host issuer')
        self.authority.authorize(context, 'personal', ('director',))
        return context

    def observe(self, host_context, **fields):
        """Test host attests exact normalized metadata AND interpreted submission.

        Never expose this bootstrap method to a message/model. A future Hermes
        binding must independently authenticate sender and receiving identity.
        """
        context = self.check_issuer(fields.get('issuer'))
        if host_context is not context:
            raise AuthorizationError('unissued host observation capability')
        event = ObservedHermesEvent(host_principal=context.principal,
            message_digest=hash_content(fields['message_text']), **fields)
        fingerprint = hash_content(event)
        if fingerprint in self._events:
            return self._events[fingerprint]
        require(len(self._issued) < 256, 'offline host observation bound exceeded')
        self._issued[id(event)] = event
        self._events[fingerprint] = event
        return event

    def authenticate(self, event):
        if type(event) is not ObservedHermesEvent or self._issued.get(id(event)) is not event:
            raise AuthorizationError('event was not authenticated by the configured host')
        self.check_issuer(event.issuer)
        return event


@dataclass(frozen=True, kw_only=True)
class HermesResearchRoute(Contract):
    """Future company schema support is data only; this adapter accepts Personal."""
    schema: ClassVar[str] = 'research_hermes_route.v1'
    environment: str
    issuer: str
    platform: str
    profile: str
    recipient: str
    conversation_id: str
    sender_id: str
    requester: str
    policy_ref: str
    route_ref: str

    def validate(self):
        for value in (self.issuer, self.platform, self.profile, self.recipient,
                      self.conversation_id, self.sender_id, self.requester,
                      self.policy_ref, self.route_ref):
            identity(value)
        require(self.platform == 'photon', 'unsupported platform route')

    @property
    def route_key(self):
        return (self.issuer, self.platform, self.profile, self.recipient, self.conversation_id)

    @property
    def pending_issuer(self):
        # Carry profile/receiver/platform in the existing canary dedupe scope.
        return 'hermes-' + hash_content(self.route_key)


@dataclass(frozen=True, kw_only=True)
class HermesResearchEnvelope(Contract):
    schema: ClassVar[str] = 'research_hermes_intake.v1'
    environment: str
    event: ObservedHermesEvent
    route: HermesResearchRoute

    def validate(self):
        require(self.environment == self.route.environment == 'personal', 'Personal intake only')
        require(self.event.route_key == self.route.route_key and
                self.event.sender_id == self.route.sender_id, 'event/route identity mismatch')

    @property
    def operation_id(self):
        # Sender/objective/source are payload, NOT dedupe keys. Changing them for
        # the same scoped platform event cannot create another legitimate task.
        return hash_content((self.schema, self.environment, *self.event.route_key, self.event.event_id))

    def pending_intake(self):
        return ResearchIntake(environment=self.environment, issuer=self.route.pending_issuer,
            event_id=self.event.event_id, conversation_id=self.event.conversation_id,
            requester=self.route.requester, recipient=self.route.recipient,
            objective=self.event.objective, policy_ref=self.route.policy_ref,
            sources=self.event.sources)


@dataclass(frozen=True, kw_only=True)
class IntakeAcknowledgment(Contract):
    """Stable local acknowledgment data; never a send/delivery/final receipt."""
    schema: ClassVar[str] = 'research_hermes_intake_ack.offline.v1'
    environment: str
    operation_id: str
    envelope_digest: str
    pending_digest: str
    status: str = 'INTAKE_ACCEPTED'
    acquisition_status_at_acceptance: str = 'PENDING_ACQUISITION'
    research_complete: bool = False
    production_trusted: bool = False
    marking: str = MARKING

    def validate(self):
        for value in (self.operation_id, self.envelope_digest, self.pending_digest):
            digest(value)
        require(self.environment == 'personal' and self.status == 'INTAKE_ACCEPTED' and
                self.acquisition_status_at_acceptance == 'PENDING_ACQUISITION', 'invalid intake ACK')
        require(not self.research_complete and not self.production_trusted and self.marking == MARKING,
                'intake ACK is never research completion or production trust')


class PersonalHermesIntake:
    """One bounded index composed with existing pending acquisition/task contracts.

    All writes are Research-local immutable WorkflowJournal checkpoints. The
    host owns message dispatch and any outbound ACK/retry. No Memory is called.
    """
    def __init__(self, store, director, host_authentication=None, routes=(), requesters=None,
                 *, test_only=False, production=False, hook=None):
        offline_only(test_only, production)
        if type(host_authentication) is not OfflineHermesAuthentication or not routes:
            raise AuthorizationError('host authentication and exact Personal routes required')
        self.store, self.director, self.host = store, director, host_authentication
        store._authority.authorize(director, 'personal', ('director',))
        self.requesters = MappingProxyType(dict(requesters or {}))
        bindings, approved = [], {}
        for route in routes:
            require(type(route) is HermesResearchRoute and route.environment == 'personal',
                    'company Research is unconfigured and disabled')
            require(route.route_key not in approved, 'ambiguous host conversation mapping')
            self.host.check_issuer(route.issuer)
            context = self.requesters.get(route.requester)
            store._authority.authorize(context, 'personal', ('director', 'researcher'))
            require(context.principal == route.requester, 'requester capability mapping mismatch')
            approved[route.route_key] = route
            bindings.append(ConversationBinding(environment='personal', issuer=route.pending_issuer,
                conversation_id=route.conversation_id, requester=route.requester,
                recipient=route.recipient, policy_ref=route.policy_ref))
        self.routes = MappingProxyType(approved)
        mapping = IntakeMapping(store._authority, bindings, test_only=True)
        self.pending = PendingSources(store, mapping, test_only=True, hook=hook)
        self.journal = WorkflowJournal(store._root, store._authority)
        self.hook = hook or (lambda stage: None)
        self.journal.provision(director, INDEX)

    def _current(self, envelope):
        self.store._authority.authorize(self.director, 'personal', ('director',))
        if self.host.check_issuer(envelope.event.issuer).principal != envelope.event.host_principal:
            raise AuthorizationError('original host issuer principal changed')
        if self.routes.get(envelope.event.route_key) != envelope.route:
            raise AuthorizationError('route absent, changed or revoked')
        requester = self.requesters.get(envelope.route.requester)
        self.store._authority.authorize(requester, envelope.environment, ('director', 'researcher'))
        return requester

    def _begin(self, envelope):
        requester = self._current(envelope)
        pending = self.pending.begin(requester, self.director, envelope.pending_intake())
        self.hook('pending:committed')
        return IntakeAcknowledgment(environment='personal', operation_id=envelope.operation_id,
            envelope_digest=hash_content(envelope), pending_digest=hash_content(pending))

    def accept(self, authenticated_event):
        event = self.host.authenticate(authenticated_event)
        route = self.routes.get(event.route_key)
        if route is None or route.sender_id != event.sender_id:
            raise AuthorizationError('unknown receiving conversation or authenticated sender')
        envelope = HermesResearchEnvelope(environment='personal', event=event, route=route)
        self._current(envelope)
        with self.journal.lock(self.director, INDEX):
            key = 'packet:envelope:' + envelope.operation_id
            prior = self.journal.load(self.director, INDEX, key, HermesResearchEnvelope)
            require(prior is None or prior == envelope, 'platform event reused with changed payload')
            if prior is None:
                require(len(self.journal.records(self.director, INDEX, 'packet:envelope:',
                                                HermesResearchEnvelope)) < 128, 'pending intake bound exceeded')
            self.journal.commit(self.director, INDEX, key, envelope)
            self.hook('envelope:committed')
            return self._begin(envelope)

    def recover(self, director):
        """Replay durable acceptance only, with CURRENT issuer/routes/grants.

        Never reacquire a URL, execute Research, send a message or claim a final.
        Stored event data does not become a newly authenticated live host event.
        """
        self.store._authority.authorize(director, 'personal', ('director',))
        with self.journal.lock(director, INDEX):
            return tuple(self._begin(e) for e in self.journal.records(director, INDEX,
                'packet:envelope:', HermesResearchEnvelope))

    def materialize_fixture_for_test(self, director, operation_id, fixture):
        """Explicit offline-only exercise of existing acquisition/task dedupe.

        A fixture snapshot never represents an authenticated live acquisition.
        """
        digest(operation_id)
        self.store._authority.authorize(director, 'personal', ('director',))
        with self.journal.lock(director, INDEX):
            envelope = self.journal.load(director, INDEX, 'packet:envelope:' + operation_id,
                                         HermesResearchEnvelope)
            require(envelope is not None, 'no accepted intake')
            requester = self._current(envelope)
            intake = envelope.pending_intake()
            self.pending.resolve_fixture(requester, director, intake, fixture=fixture)
            return self.pending.materialize(requester, director, intake, fixture)

    def materialize_genuine_acquisition(self, *args, **kwargs):
        raise AuthorizationError('authenticated live acquisition authority/contract not configured')
