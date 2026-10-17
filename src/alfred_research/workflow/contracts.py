"""Phase 6 offline orchestration envelopes, never host messaging contracts."""
from dataclasses import dataclass
from typing import ClassVar
from ..contracts import Contract, SourceIdentity, ResearchRequest, digest, integer, require, hash_content
from ..sources import SourceFixture, FixtureFile
from ..research import ResearchPolicy
from ..memory import MemoryReceipt
from ..intelligence import Proposal

MARKING = 'SIMULATED / NON_PRODUCTION'

@dataclass(frozen=True, kw_only=True)
class Conversation(Contract):
    schema: ClassVar[str] = 'research_conversation.test.v1'
    environment: str
    conversation_id: str
    label: str
    requester: str
    recipient: str
    source_kinds: tuple[str, ...]

@dataclass(frozen=True, kw_only=True)
class ResearchMessage(Contract):
    schema: ClassVar[str] = 'research_message.test.v1'
    environment: str
    conversation_id: str
    message_id: str
    requester: str
    objective: str
    sources: tuple[SourceIdentity, ...]

    def validate(self):
        require(len(self.sources) == 1 and self.sources[0].environment == self.environment, 'one same-environment source required')
        require(len(self.message_id) <= 128, 'bounded message identity required')

@dataclass(frozen=True, kw_only=True)
class FlowOptions(Contract):
    schema: ClassVar[str] = 'research_flow_options.test.v1'
    policy: ResearchPolicy
    valid_until: int
    max_retries: int = 2
    hq_eligible: bool = False
    export_selected: bool = False
    memory_outcomes: tuple[str, ...] = ()

    def validate(self):
        integer(self.valid_until, 1)
        integer(self.max_retries)
        require(self.max_retries <= 10, 'bounded retries required')
        allowed = ('commit', 'promote', 'hq_sync', 'request_export', 'export_status', 'sync_status')
        require(len(set(self.memory_outcomes)) == len(self.memory_outcomes), 'duplicate fake outcome')
        for item in self.memory_outcomes:
            require(item.count(':') == 1 and item.split(':')[0] in allowed and
                    item.split(':')[1] in ('FAILED', 'PARTIAL'), 'invalid test-only failure configuration')

    def outcome(self, operation):
        return dict(item.split(':') for item in self.memory_outcomes).get(operation, 'SUCCESS')

@dataclass(frozen=True, kw_only=True)
class FixtureBlob(Contract):
    schema: ClassVar[str] = 'research_fixture_blob.test.v1'
    path: str
    chunks: tuple[str, ...]
    symlink: bool
    executable: bool

@dataclass(frozen=True, kw_only=True)
class MetadataPair(Contract):
    schema: ClassVar[str] = 'research_fixture_metadata.test.v1'
    name: str
    value: str

@dataclass(frozen=True, kw_only=True)
class FixtureSnapshot(Contract):
    schema: ClassVar[str] = 'research_fixture_snapshot.test.v1'
    files: tuple[FixtureBlob, ...]
    metadata: tuple[MetadataPair, ...]
    revision: tuple[str, ...]
    access: str
    origin: str
    complete: bool

    @classmethod
    def capture(cls, fixture):
        require(type(fixture) is SourceFixture and len(fixture.files) <= 64 and
                sum(len(f.data) for f in fixture.files) <= 128000, 'offline intake snapshot limit exceeded')
        return cls(files=tuple(FixtureBlob(path=f.path,
            chunks=tuple(f.data.hex()[i:i+8192] for i in range(0, len(f.data)*2, 8192)),
            symlink=f.symlink, executable=f.executable) for f in fixture.files),
            metadata=tuple(MetadataPair(name=k, value=v) for k, v in fixture.metadata),
            revision=(fixture.revision,) if fixture.revision else (), access=fixture.access,
            origin=fixture.origin, complete=fixture.complete)

    def restore(self):
        require(len(self.files) <= 64 and len(self.revision) <= 1 and
                sum(sum(len(c) for c in f.chunks) for f in self.files) <= 256000, 'bounded fixture snapshot required')
        return SourceFixture(files=tuple(FixtureFile(f.path, bytes.fromhex(''.join(f.chunks)),
            f.symlink, f.executable) for f in self.files), metadata=tuple((m.name,m.value) for m in self.metadata),
            revision=self.revision[0] if self.revision else '', access=self.access, origin=self.origin, complete=self.complete)

@dataclass(frozen=True, kw_only=True)
class Intake(Contract):
    schema: ClassVar[str] = 'research_flow_intake.test.v1'
    environment: str
    message: ResearchMessage
    fixture: FixtureSnapshot
    options: FlowOptions
    configuration_digest: str
    request: ResearchRequest

    def validate(self):
        require(self.environment == self.message.environment == self.request.environment, 'intake scope mismatch')
        require(self.request.sources == self.message.sources and self.request.requested_by == self.message.requester,
                'intake requester/source mismatch')
        digest(self.configuration_digest)

@dataclass(frozen=True, kw_only=True)
class Stage(Contract):
    schema: ClassVar[str] = 'research_flow_stage.test.v1'
    environment: str
    research_task_id: str
    name: str
    reference: str

@dataclass(frozen=True, kw_only=True)
class FlowResult(Contract):
    schema: ClassVar[str] = 'research_flow_result.test.v1'
    environment: str
    research_task_id: str
    conversation_id: str
    requester: str
    outcome: str
    steps: tuple[str, ...]
    receipts: tuple[MemoryReceipt, ...]
    record_id: tuple[str, ...]
    proposals: tuple[Proposal, ...]
    reason: str = 'NONE'
    marking: str = MARKING

    def validate(self):
        require(self.outcome in ('COMPLETED', 'PARTIAL', 'BLOCKED', 'REJECTED', 'NEEDS_MORE_RESEARCH'), 'unknown workflow outcome')
        require(self.reason in ('NONE','SOURCE_UNAVAILABLE','RESOURCE_LIMIT','AUTHORIZATION','VALIDATION','INCOMPLETE'), 'unknown failure reason')
        require(self.marking == MARKING and len(self.record_id) <= 1 and
                all(r.environment == self.environment for r in self.receipts) and
                all(p.environment == self.environment for p in self.proposals), 'result scope/simulation mismatch')

@dataclass(frozen=True, kw_only=True)
class Notice(Contract):
    schema: ClassVar[str] = 'research_notice.test.v1'
    environment: str
    research_task_id: str
    conversation_id: str
    recipient: str
    kind: str
    message: str
    receipt_refs: tuple[str, ...] = ()

    def validate(self):
        require(self.kind in ('ACK', 'FINAL') and len(self.message) <= 240 and
                self.message.startswith('SIMULATED:'), 'short explicitly simulated notice required')

    @property
    def notification_id(self):
        return hash_content((self.environment,self.research_task_id,self.conversation_id,self.recipient,self.kind))

@dataclass(frozen=True, kw_only=True)
class NoticeState(Contract):
    schema: ClassVar[str] = 'research_notice_state.test.v1'
    environment: str
    notification_id: str
    state: str
    attempt: int

    def validate(self):
        digest(self.notification_id)
        require(self.state in ('PREPARED','SENDING','UNKNOWN','ACCEPTED','DELIVERED','FAILED'), 'unknown notice state')
        integer(self.attempt)
        require(self.attempt <= 3, 'notice retry bound exceeded')

@dataclass(frozen=True, kw_only=True)
class TransportReceipt(Contract):
    schema: ClassVar[str] = 'research_transport_receipt.test.v1'
    environment: str
    notification_id: str
    notice_digest: str
    conversation_id: str
    recipient: str
    state: str
    marking: str = MARKING

    def validate(self):
        digest(self.notification_id); digest(self.notice_digest)
        require(self.state in ('ACCEPTED','DELIVERED') and self.marking == MARKING, 'fake transport receipt required')
