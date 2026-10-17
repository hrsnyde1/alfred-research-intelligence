"""Proposed Memory-owned ports; no Linux API or vault mapping implied."""
from dataclasses import dataclass
from typing import ClassVar, Protocol
from ..contracts import (Contract, VerificationDecision, ENVIRONMENT_NAMES, digest, hash_content,
                         integer, require)
from ..intelligence import IntelligenceRecord

OPERATIONS = ('submit', 'commit', 'promote', 'retrieve', 'supersede', 'expire', 'delete',
              'revoke', 'request_export', 'export_status', 'sync_status', 'hq_allow', 'hq_sync', 'hq_retrieve')
MUTATIONS = ('submit', 'commit', 'promote', 'supersede', 'expire', 'delete', 'revoke')
MARKING = 'SIMULATED / NON_PRODUCTION'

@dataclass(frozen=True, kw_only=True)
class KnowledgeCandidate(Contract):
    schema: ClassVar[str] = 'memory_candidate.proposed.v1'
    environment: str
    company_name: str
    record: IntelligenceRecord
    record_version: int
    verification: VerificationDecision
    relationships: tuple[str, ...]
    related_ids: tuple[str, ...]
    idempotency_id: str
    marking: str = MARKING

    def validate(self):
        require(self.company_name == ENVIRONMENT_NAMES[self.environment], 'company identity mismatch')
        require(self.record.environment == self.verification.environment == self.environment, 'candidate environment mismatch')
        require(self.verification.verdict == 'APPROVED' and
                self.verification.packet_digest == self.record.packet.digest and
                self.verification.decision_id == self.record.decision_id and
                self.verification.verifier != self.record.packet.researcher, 'candidate verification mismatch')
        integer(self.record_version, 1)
        require(self.marking == MARKING and not self.record.memory_eligible, 'synthetic candidate only')

@dataclass(frozen=True, kw_only=True)
class MemoryCommand(Contract):
    schema: ClassVar[str] = 'memory_command.proposed.v2'
    environment: str
    record_id: str
    record_digest: str
    operation: str
    operation_id: str
    expected_sequence: int = 0
    related_ids: tuple[str, ...] = ()
    fixture_result: str = 'SUCCESS'
    export_attempt: tuple[str, ...] = ()
    export_destination: tuple[str, ...] = ()
    export_record_version: tuple[int, ...] = ()
    prerequisite_receipt: tuple[str, ...] = ()

    def validate(self):
        digest(self.record_digest)
        require(self.operation in OPERATIONS, 'unknown Memory operation')
        integer(self.expected_sequence)
        require(len(self.operation_id) <= 128, 'bounded operation identity required')
        require(self.fixture_result in ('SUCCESS', 'PARTIAL', 'FAILED'), 'unknown simulated outcome')
        bound = self.operation in ('request_export', 'export_status', 'sync_status')
        for values in (self.export_attempt, self.export_destination, self.export_record_version):
            require(len(values) == (1 if bound else 0), 'explicit export attempt/destination/version required')
        require(len(self.prerequisite_receipt) == (1 if self.operation in ('export_status', 'sync_status') else 0),
                'exact prerequisite receipt required')
        if bound:
            integer(self.export_record_version[0], 1)
        if self.prerequisite_receipt:
            digest(self.prerequisite_receipt[0])

@dataclass(frozen=True, kw_only=True)
class MemoryReceipt(Contract):
    schema: ClassVar[str] = 'memory_receipt.proposed.v2'
    environment: str
    receipt_id: str
    operation_id: str
    operation: str
    record_id: str
    record_version: int
    record_digest: str
    actor: str
    sequence: int
    observed_at: int
    outcome: str
    state: str
    detail: str
    marking: str = MARKING
    export_attempt: tuple[str, ...] = ()
    export_destination: tuple[str, ...] = ()
    prerequisite_receipt: tuple[str, ...] = ()

    def validate(self):
        require(self.operation in OPERATIONS, 'unknown receipt operation')
        require(self.outcome in ('SUCCESS', 'PARTIAL', 'FAILED'), 'unknown receipt outcome')
        require(self.state in ('ABSENT', 'CANDIDATE', 'COMMITTED', 'PROMOTED', 'RETRIEVABLE',
                'SUPERSEDED', 'EXPIRED', 'DELETED', 'REVOKED', 'EXPORT_REQUESTED', 'EXPORTED',
                'SYNCED', 'HQ_ELIGIBLE', 'HQ_SYNCED', 'HQ_TOMBSTONE'), 'unknown receipt state')
        integer(self.sequence, 1)
        integer(self.record_version, 1)
        integer(self.observed_at)
        digest(self.record_digest)
        digest(self.receipt_id)
        require(self.marking == MARKING, 'production receipt forbidden')
        bound = self.operation in ('request_export', 'export_status', 'sync_status')
        require(len(self.export_attempt) == len(self.export_destination) == (1 if bound else 0),
                'receipt export binding required')
        require(len(self.prerequisite_receipt) == (1 if self.operation in ('export_status', 'sync_status') else 0),
                'receipt prerequisite binding required')
        if self.prerequisite_receipt:
            digest(self.prerequisite_receipt[0])

@dataclass(frozen=True, kw_only=True)
class MemoryEvent(Contract):
    schema: ClassVar[str] = 'memory_simulation_event.v1'
    environment: str
    input_digest: str
    candidate: tuple[KnowledgeCandidate, ...]
    receipt: MemoryReceipt

    def validate(self):
        digest(self.input_digest)
        require(len(self.candidate) <= 1 and self.receipt.environment == self.environment and
                all(c.environment == self.environment for c in self.candidate), 'event scope mismatch')
        if self.candidate:
            candidate = self.candidate[0]
            require(self.receipt.operation == 'submit' and self.receipt.outcome == 'SUCCESS' and
                    self.receipt.record_id == candidate.record.record_id and
                    self.receipt.record_digest == hash_content(candidate.record) and
                    self.receipt.record_version == candidate.record_version, 'candidate receipt linkage mismatch')

@dataclass(frozen=True, kw_only=True)
class RetrievalResult(Contract):
    schema: ClassVar[str] = 'memory_retrieval.proposed.v1'
    environment: str
    candidate: KnowledgeCandidate
    receipt: MemoryReceipt

    def validate(self):
        require(self.candidate.environment == self.receipt.environment == self.environment and
                self.receipt.operation in ('retrieve', 'hq_retrieve') and self.receipt.outcome == 'SUCCESS',
                'fresh retrieval receipt required')
        require(self.receipt.record_digest == hash_content(self.candidate.record) and
                self.receipt.record_id == self.candidate.record.record_id and
                self.receipt.record_version == self.candidate.record_version, 'retrieval provenance mismatch')

class MemoryPort(Protocol):
    """Logical operations only. Production transport is intentionally absent."""
    def submit(self, context, candidate: KnowledgeCandidate) -> MemoryReceipt: ...
    def commit(self, context, command: MemoryCommand) -> MemoryReceipt: ...
    def promote(self, context, command: MemoryCommand) -> MemoryReceipt: ...
    def retrieve(self, context, command: MemoryCommand) -> RetrievalResult: ...
    def supersede(self, context, command: MemoryCommand) -> MemoryReceipt: ...
    def expire(self, context, command: MemoryCommand) -> MemoryReceipt: ...
    def delete(self, context, command: MemoryCommand) -> MemoryReceipt: ...
    def revoke(self, context, command: MemoryCommand) -> MemoryReceipt: ...
    def request_export(self, context, command: MemoryCommand) -> MemoryReceipt: ...
    def export_status(self, context, command: MemoryCommand) -> MemoryReceipt: ...
    def sync_status(self, context, command: MemoryCommand) -> MemoryReceipt: ...
    def hq_allow(self, context, command: MemoryCommand) -> MemoryReceipt: ...
    def hq_sync(self, context, command: MemoryCommand) -> MemoryReceipt: ...
    def hq_retrieve(self, context, command: MemoryCommand) -> RetrievalResult: ...
