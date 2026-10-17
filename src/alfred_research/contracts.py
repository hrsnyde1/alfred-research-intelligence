"""Immutable internal contracts, deliberately unrelated to Linux API schemas."""
from dataclasses import dataclass, fields, is_dataclass
from hashlib import sha256
import json
import re
from typing import ClassVar, get_args, get_origin, get_type_hints


class ContractError(ValueError):
    pass


ENVIRONMENTS = ("personal", "gabos", "fintra", "sc_products")
ENVIRONMENT_NAMES = dict(zip(ENVIRONMENTS, (
    "Personal Alfred", "Gabos Holdings Inc.", "Fintra AI", "SC Products Group")))
ROLES = ("director", "researcher", "verifier")
STATES = ("received", "collecting", "researching", "awaiting_verification",
          "approved", "rejected", "needs_more_research", "failed", "cancelled")


def require(condition, message):
    if not condition:
        raise ContractError(message)


def text(value):
    require(type(value) is str and bool(value.strip()) and len(value) <= 16384,
            "expected bounded nonempty text")


def integer(value, minimum=0):
    require(type(value) is int and minimum <= value <= 2**63 - 1,
            "expected bounded integer")


def environment(value):
    require(value in ENVIRONMENTS, "unknown environment")


def digest(value):
    require(type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None,
            "invalid SHA-256 digest")


def _typed(value, annotation):
    if get_origin(annotation) is tuple:
        require(type(value) is tuple, "immutable tuple required")
        args = get_args(annotation)
        require(len(value) <= 10000, "collection too large")
        for item in value:
            _typed(item, args[0])
    else:
        require(type(value) is annotation, f"expected {annotation.__name__}")


@dataclass(frozen=True)
class Contract:
    schema: ClassVar[str] = "contract.v1"
    version: int = 1

    def __post_init__(self):
        hints = get_type_hints(type(self))
        for field in fields(self):
            _typed(getattr(self, field.name), hints[field.name])
        require(self.version == 1, "unsupported schema version")
        if hasattr(self, 'environment'):
            environment(self.environment)
        for field in fields(self):
            value = getattr(self, field.name)
            if type(value) is str:
                text(value)
        self.validate()

    def validate(self):
        pass

    def payload(self):
        def encode(value):
            if is_dataclass(value):
                return {"schema": value.schema, **{
                    f.name: encode(getattr(value, f.name)) for f in fields(value)}}
            if isinstance(value, tuple):
                return [encode(v) for v in value]
            return value
        return encode(self)

    @classmethod
    def from_json(cls, value):
        require(type(value) is str and len(value) <= 2_000_000, "bounded JSON text required")
        def unique(pairs):
            result = {}
            for key, item in pairs:
                require(key not in result, "duplicate JSON key")
                result[key] = item
            return result
        def invalid_constant(value):
            raise ContractError("nonfinite JSON value")
        try:
            payload = json.loads(value, object_pairs_hook=unique, parse_constant=invalid_constant)
        except (json.JSONDecodeError, RecursionError) as exc:
            raise ContractError("malformed JSON") from exc
        return cls.from_payload(payload)

    @classmethod
    def from_payload(cls, payload):
        require(type(payload) is dict, "object required")
        require(set(payload) == {"schema", *(f.name for f in fields(cls))},
                "missing or unknown fields")
        require(payload['schema'] == cls.schema, "unsupported schema")
        hints = get_type_hints(cls)
        def decode(value, annotation):
            if get_origin(annotation) is tuple:
                require(type(value) is list, "array required")
                return tuple(decode(v, get_args(annotation)[0]) for v in value)
            if isinstance(annotation, type) and issubclass(annotation, Contract):
                return annotation.from_payload(value)
            return value
        return cls(**{f.name: decode(payload[f.name], hints[f.name]) for f in fields(cls)})


def canonical(value):
    """UTF-8, sorted keys, compact JSON; ordered arrays; no floats/NaN."""
    if isinstance(value, Contract):
        value = value.payload()
    def check(v):
        if type(v) is dict:
            require(all(type(k) is str for k in v), "string keys required")
            for item in v.values():
                check(item)
        elif type(v) in (list, tuple):
            for item in v:
                check(item)
        else:
            require(type(v) in (str, int, bool, type(None)), "noncanonical value")
    check(value)
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def hash_content(value):
    return sha256(canonical(value)).hexdigest()


@dataclass(frozen=True, kw_only=True)
class SourceIdentity(Contract):
    schema: ClassVar[str] = "source.v1"
    source_id: str
    environment: str
    kind: str
    locator: str
    revision: str
    content_digest: str

    def validate(self):
        require(self.kind in ('github', 'website', 'article', 'pdf', 'document',
                              'youtube', 'instagram', 'tiktok', 'x'), "unsupported source")
        digest(self.content_digest)


@dataclass(frozen=True, kw_only=True)
class ResearchRequest(Contract):
    schema: ClassVar[str] = "request.v1"
    request_id: str
    environment: str
    requested_by: str
    objective: str
    sources: tuple[SourceIdentity, ...]
    max_retries: int = 3

    def validate(self):
        require(len(self.sources) == 1, "exactly one submitted source required")
        require(self.sources[0].environment == self.environment, "source environment mismatch")
        integer(self.max_retries)
        require(self.max_retries <= 10, "retry limit exceeds authorization")


@dataclass(frozen=True, kw_only=True)
class DurableTask(Contract):
    schema: ClassVar[str] = "task.v1"
    task_id: str
    environment: str
    request: ResearchRequest
    state: str
    retries: int = 0

    def validate(self):
        require(self.state in STATES, "unknown task state")
        require(self.request.environment == self.environment, "task scope mismatch")
        integer(self.retries)
        require(self.retries <= self.request.max_retries, "retry bound exceeded")


@dataclass(frozen=True, kw_only=True)
class Evidence(Contract):
    schema: ClassVar[str] = "evidence.v1"
    evidence_id: str
    environment: str
    source_id: str
    location: str
    content_digest: str

    def validate(self):
        digest(self.content_digest)


@dataclass(frozen=True, kw_only=True)
class Claim(Contract):
    schema: ClassVar[str] = "claim.v1"
    claim_id: str
    environment: str
    statement: str
    evidence_ids: tuple[str, ...]
    kind: str = "finding"

    def validate(self):
        require(self.kind in ('finding', 'inference', 'forecast', 'unknown'), "unknown claim kind")
        require(bool(self.evidence_ids) and len(set(self.evidence_ids)) == len(self.evidence_ids),
                "unique evidence references required")
        for item in self.evidence_ids:
            text(item)


@dataclass(frozen=True, kw_only=True)
class ResearchPacket(Contract):
    schema: ClassVar[str] = "packet.v1"
    packet_id: str
    task_id: str
    environment: str
    scope: str
    classification: str
    researcher: str
    researcher_model: str
    researcher_provider: str
    packet_version: int
    source: SourceIdentity
    claims: tuple[Claim, ...]
    evidence: tuple[Evidence, ...]
    limitations: tuple[str, ...] = ()

    def validate(self):
        require(self.scope == self.environment, "scope must match environment")
        require(self.source.environment == self.environment, "source environment mismatch")
        require(self.classification in ('public', 'internal', 'confidential'), "unknown classification")
        integer(self.packet_version, 1)
        require(bool(self.claims) and bool(self.evidence), "claims and evidence required")
        for records, key in ((self.claims, 'claim_id'), (self.evidence, 'evidence_id')):
            require(len({getattr(r, key) for r in records}) == len(records), "duplicate record identity")
            require(all(r.environment == self.environment for r in records), "mixed environments")
        ids = {e.evidence_id for e in self.evidence}
        require(all(set(c.evidence_ids) <= ids for c in self.claims), "dangling evidence")
        require(all(e.source_id == self.source.source_id for e in self.evidence), "unknown evidence source")
        for item in self.limitations:
            text(item)

    @property
    def digest(self):
        return hash_content(self)


@dataclass(frozen=True, kw_only=True)
class VerificationDecision(Contract):
    schema: ClassVar[str] = "verification.v1"
    decision_id: str
    environment: str
    packet_digest: str
    verifier: str
    verifier_model: str
    verifier_provider: str
    verdict: str
    rationale: str

    def validate(self):
        digest(self.packet_digest)
        require(self.verdict in ('APPROVED', 'REJECTED', 'NEEDS_MORE_RESEARCH'), "unknown verdict")


@dataclass(frozen=True, kw_only=True)
class ModelAssignment(Contract):
    schema: ClassVar[str] = "model_assignment.v1"
    environment: str
    specialist: str
    provider: str
    model: str
    price_units: int
    approved: bool = False

    def validate(self):
        integer(self.price_units, 1)
        require(self.specialist in ROLES + ('general', 'code', 'finance_tax', 'business_legal'),
                "unsupported Research specialist")


@dataclass(frozen=True, kw_only=True)
class SpecialistAssignment(Contract):
    schema: ClassVar[str] = "specialist_assignment.v1"
    environment: str
    task_id: str
    principal: str
    role: str
    model: ModelAssignment

    def validate(self):
        require(self.role in ROLES, "unknown role")
        require(self.model.environment == self.environment, "model scope mismatch")
        require(self.model.specialist == self.role, "role model assignment mismatch")


@dataclass(frozen=True, kw_only=True)
class BudgetReservation(Contract):
    schema: ClassVar[str] = "budget_reservation.v1"
    reservation_id: str
    environment: str
    principal: str
    assignment: ModelAssignment
    reserved: int
    consumed: int = 0
    state: str = "reserved"

    def validate(self):
        integer(self.reserved, 1)
        integer(self.consumed)
        require(self.consumed <= self.reserved, "consumption exceeds reservation")
        require(self.assignment.environment == self.environment, "budget scope mismatch")
        require(self.state in ('reserved', 'settled', 'cancelled'), "unknown reservation state")
        require(self.state != 'cancelled' or self.consumed == 0, "cancelled spend")


@dataclass(frozen=True, kw_only=True)
class AuditEvent(Contract):
    schema: ClassVar[str] = "audit.v1"
    event_id: str
    environment: str
    principal: str
    operation: str
    subject_id: str


@dataclass(frozen=True, kw_only=True)
class OutboxEvent(Contract):
    schema: ClassVar[str] = "outbox.v1"
    event_id: str
    environment: str
    task_id: str
    topic: str
    payload_digest: str
    state: str = "pending"
    attempts: int = 0

    def validate(self):
        digest(self.payload_digest)
        require(self.state in ('pending', 'delivered', 'exhausted'), "unknown outbox state")
        integer(self.attempts)
        require(self.attempts <= 3, "outbox retry bound")


@dataclass(frozen=True, kw_only=True)
class RetryOperation(Contract):
    schema: ClassVar[str] = "retry_operation.v1"
    retry_id: str
    task_id: str
    environment: str
    principal: str
    result: DurableTask

    def validate(self):
        require(self.result.environment == self.environment and self.result.task_id == self.task_id,
                "retry result scope mismatch")
        require(self.result.retries > 0, "retry result must consume an allowance")
