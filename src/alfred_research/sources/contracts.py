"""Internal source snapshots/results v1; never host API or provider receipts."""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import PurePosixPath
from typing import ClassVar
from datetime import datetime
import re

from ..contracts import Contract, SourceIdentity, digest, require, hash_content

OUTCOMES = ('SUPPORTED_FETCHED', 'PARTIAL', 'AUTH_REQUIRED', 'INACCESSIBLE', 'UNSUPPORTED', 'ERROR')
KINDS = ('github', 'website', 'article', 'pdf', 'document', 'youtube', 'instagram', 'tiktok', 'x')
METADATA = ('canonical_url', 'publisher', 'author', 'published_at', 'retrieved_at', 'title', 'license')


def safe_path(path):
    return (type(path) is str and 0 < len(path) <= 512 and
            not any(ord(c) < 32 for c in path) and '\\' not in path and
            ':' not in path and not path.startswith('/') and
            all(p not in ('', '.', '..') for p in path.split('/')) and
            str(PurePosixPath(path)) == path)


@dataclass(frozen=True)
class FixtureFile:
    """Bytes are untrusted data. symlink records are never dereferenced."""
    path: str
    data: bytes
    symlink: bool = False
    executable: bool = False

    def __post_init__(self):
        require(type(self.path) is str and 0 < len(self.path) <= 512, 'bounded file path required')
        require(type(self.data) is bytes and len(self.data) <= 1_000_000, 'bounded bytes required')
        try:
            self.path.encode('utf-8')
        except UnicodeError as exc:
            raise ValueError('invalid Unicode fixture path') from exc
        require(type(self.symlink) is bool and type(self.executable) is bool, 'boolean file flags required')

    @property
    def digest(self):
        return sha256(self.data).hexdigest()


@dataclass(frozen=True)
class SourceFixture:
    """Authorized fixture or user-supplied snapshot, not a live fetch assertion."""
    files: tuple[FixtureFile, ...] = ()
    metadata: tuple[tuple[str, str], ...] = ()
    revision: str = ''
    access: str = 'accessible'
    origin: str = 'fixture'
    complete: bool = True

    def __post_init__(self):
        require(type(self.files) is tuple and len(self.files) <= 256 and
                all(type(f) is FixtureFile for f in self.files), 'bounded immutable files required')
        require(len({f.path for f in self.files}) == len(self.files), 'duplicate file paths')
        require(type(self.metadata) is tuple and len(self.metadata) <= len(METADATA), 'bounded metadata required')
        keys = []
        for pair in self.metadata:
            require(type(pair) is tuple and len(pair) == 2, 'metadata pair required')
            key, value = pair
            require(key in METADATA and type(value) is str and 0 < len(value.strip()) <= 2048,
                    'unknown or malformed metadata')
            try:
                value.encode('utf-8')
            except UnicodeError as exc:
                raise ValueError('invalid Unicode metadata') from exc
            keys.append(key)
            if key.endswith('_at'):
                try:
                    date = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    require(date.tzinfo is not None, 'timezone required')
                except ValueError as exc:
                    raise ValueError('invalid source date') from exc
        require(len(set(keys)) == len(keys), 'duplicate metadata')
        require(type(self.revision) is str and len(self.revision) <= 128, 'bounded revision required')
        require(type(self.access) is str and self.access in ('accessible', 'auth_required', 'inaccessible', 'unsupported', 'error'), 'invalid access outcome')
        require(type(self.origin) is str and self.origin in ('fixture', 'user_supplied'), 'no live retrieval origin in Phase 2')
        require(type(self.complete) is bool, 'boolean completeness required')

    @property
    def digest(self):
        return hash_content({'files': sorted([{'path': f.path, 'digest': f.digest,
                                'symlink': f.symlink, 'executable': f.executable} for f in self.files],
                                             key=lambda f: f['path']),
                             'metadata': sorted(self.metadata), 'revision': self.revision,
                             'access': self.access, 'origin': self.origin, 'complete': self.complete})


@dataclass(frozen=True, kw_only=True)
class SourceEvidence(Contract):
    schema: ClassVar[str] = 'source_evidence.v1'
    environment: str
    evidence_id: str
    location: str
    text: str
    file_digest: str
    origin: str

    def validate(self):
        digest(self.file_digest)
        require(self.origin in ('fixture', 'user_supplied'), 'unsupported evidence origin')


@dataclass(frozen=True, kw_only=True)
class FileRecord(Contract):
    schema: ClassVar[str] = 'source_file.v1'
    path: str
    content_digest: str
    size: int

    def validate(self):
        from ..contracts import integer
        require(safe_path(self.path), 'unsafe inventory path')
        digest(self.content_digest)
        integer(self.size)


@dataclass(frozen=True, kw_only=True)
class Capability(Contract):
    schema: ClassVar[str] = 'source_capability.v1'
    path: str
    evidence_ids: tuple[str, ...]

    def validate(self):
        require(safe_path(self.path), 'unsafe capability path')
        require(bool(self.evidence_ids), 'capability evidence required')


@dataclass(frozen=True, kw_only=True)
class SourceResult(Contract):
    schema: ClassVar[str] = 'source_result.v1'
    environment: str
    submitted: SourceIdentity
    outcome: str
    snapshot_digest: str
    revision: tuple[str, ...]
    canonical_identity: tuple[str, ...]
    title: tuple[str, ...]
    license: tuple[str, ...]
    publisher: tuple[str, ...]
    author: tuple[str, ...]
    published_at: tuple[str, ...]
    retrieved_at: tuple[str, ...]
    evidence: tuple[SourceEvidence, ...]
    files: tuple[FileRecord, ...]
    capabilities: tuple[Capability, ...]
    limitations: tuple[str, ...]
    flags: tuple[str, ...]
    input_bytes: int
    extracted_characters: int
    work_units: int
    origin: str

    def validate(self):
        from ..contracts import integer
        require(self.submitted.environment == self.environment, 'result source scope mismatch')
        require(self.outcome in OUTCOMES, 'unknown extraction outcome')
        digest(self.snapshot_digest)
        for field in ('revision', 'canonical_identity', 'title', 'license', 'publisher', 'author', 'published_at', 'retrieved_at'):
            require(len(getattr(self, field)) <= 1, 'ambiguous optional source field')
        for field in ('input_bytes', 'extracted_characters', 'work_units'):
            integer(getattr(self, field))
        require(self.origin in ('fixture', 'user_supplied'), 'unsupported result origin')
        if self.submitted.kind == 'github' and self.revision:
            require(re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', self.revision[0]) is not None,
                    'invalid observed repository commit')
        for values in (self.published_at, self.retrieved_at):
            if values:
                parsed = datetime.fromisoformat(values[0].replace('Z', '+00:00'))
                require(parsed.tzinfo is not None, 'source result date must include timezone')
        ids = {e.evidence_id for e in self.evidence}
        require(len(ids) == len(self.evidence) and all(e.environment == self.environment for e in self.evidence),
                'mixed/duplicate evidence')
        require(len({f.path for f in self.files}) == len(self.files), 'duplicate inventory')
        inventory = {f.path: f.content_digest for f in self.files}
        require(all(inventory.get(e.location.split(':', 1)[0]) == e.file_digest and e.origin == self.origin
                    for e in self.evidence), 'evidence provenance does not match inventory')
        require(len({c.path for c in self.capabilities}) == len(self.capabilities) and
                all(c.path in inventory for c in self.capabilities), 'invalid capability inventory')
        require(all(set(c.evidence_ids) <= ids for c in self.capabilities), 'dangling capability evidence')
        require(self.extracted_characters == sum(len(e.text) for e in self.evidence), 'extraction accounting mismatch')
        if self.outcome == 'SUPPORTED_FETCHED':
            require(bool(self.evidence), 'successful extraction requires content')
        if self.outcome in ('AUTH_REQUIRED', 'INACCESSIBLE', 'UNSUPPORTED', 'ERROR'):
            require(not self.evidence, 'blocked outcome cannot claim extracted content')

    @property
    def digest(self):
        return hash_content(self)
