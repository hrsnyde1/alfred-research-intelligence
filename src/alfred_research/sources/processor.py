"""Authorized pure source processing. No network, subprocess, storage or models."""
from dataclasses import dataclass
from threading import RLock
from urllib.parse import urlsplit, urlunsplit, urljoin
import time
import os
import stat
from ipaddress import ip_address
from pathlib import Path

from ..contracts import SourceIdentity, ResearchRequest, require, hash_content, environment
from ..tenancy import AuthorizationError
from ..budgets import EscalationRequired
from .contracts import SourceFixture, SourceResult
from .policy import ProcessingLimits, Meter, ExtractionLimit
from .adapters import (Collector, GitHubAdapter, WebsiteAdapter, DocumentAdapter,
                       PDFAdapter, YouTubeAdapter, InstagramAdapter, TikTokAdapter, XAdapter)

ADAPTERS = {'github': GitHubAdapter, 'website': WebsiteAdapter, 'article': WebsiteAdapter,
            'document': DocumentAdapter, 'pdf': PDFAdapter, 'youtube': YouTubeAdapter,
            'instagram': InstagramAdapter, 'tiktok': TikTokAdapter, 'x': XAdapter}


@dataclass(frozen=True)
class SourceGrant:
    environment: str
    principal: str
    source_digest: str
    origins: tuple[str, ...]
    local_root: tuple[str, ...]


def canonical_url(value, kind):
    """Conservative URL identity only; never rewrites IDs or follows redirects."""
    require(type(value) is str and 0 < len(value) <= 2048, 'bounded canonical URL required')
    p = urlsplit(value)
    require(p.scheme == 'https' and p.hostname and p.username is None and p.password is None and
            p.port in (None, 443) and not any(ord(c) <= 32 for c in value), 'invalid canonical URL')
    host = p.hostname.lower()
    require('\\' not in value and host.rstrip('.') != 'localhost' and
            not host.rstrip('.').endswith(('.localhost', '.local', '.internal')), 'unsafe canonical hostname')
    try:
        address = ip_address(host)
    except ValueError:
        address = None  # DNS/actual peer validation belongs to the inactive future transport.
    if address is not None:
        require(address.is_global and not address.is_multicast and not address.is_unspecified and
                not (getattr(address, 'ipv4_mapped', None) and not address.ipv4_mapped.is_global),
                'nonpublic canonical address forbidden')
    allowed = {'github': ('github.com',), 'youtube': ('youtube.com', 'www.youtube.com', 'youtu.be'),
               'instagram': ('instagram.com', 'www.instagram.com'),
               'tiktok': ('tiktok.com', 'www.tiktok.com'), 'x': ('x.com', 'www.x.com', 'twitter.com')}
    require(kind not in allowed or host in allowed[kind], 'canonical URL platform mismatch')
    authority = '[' + host + ']' if ':' in host else host
    return urlunsplit(('https', authority, p.path or '/', p.query, ''))


def html_canonical(value, source, collector):
    """Optional HTML identity must never invalidate successfully extracted text."""
    try:
        require(bool(value) and len(value) <= 2048 and '\\' not in value and
                not any(ord(c) <= 32 for c in value), 'invalid canonical reference')
        if not urlsplit(value).scheme:
            # Relative references need an independently validated submitted page URL.
            base = canonical_url(source.locator, source.kind)
            value = urljoin(base, value)
        return (canonical_url(value, source.kind),)
    except ValueError:
        collector.limit('invalid or unresolved HTML canonical identity omitted')
        return ()


class SourceProcessor:
    def __init__(self, authority, *, limits=None, clock=time.monotonic, production=False, fixture_roots=None):
        if production:
            raise AuthorizationError('production source processing disabled pending host authorization')
        self._authority = authority
        self._limits = limits if limits is not None else ProcessingLimits()
        require(type(self._limits) is ProcessingLimits, 'validated processing limits required')
        self._clock = clock
        self._fixture_roots = {}
        for env, root in (fixture_roots or {}).items():
            environment(env)
            resolved = Path(root).resolve()
            for other in self._fixture_roots.values():
                require(resolved != other and resolved not in other.parents and other not in resolved.parents,
                        'environment fixture roots must not overlap')
            self._fixture_roots[env] = resolved
        self._grants = {}
        self._lock = RLock()

    def grant(self, director, recipient, source, *, origins=('fixture',), local_root=None):
        require(type(source) is SourceIdentity, 'validated source identity required')
        self._authority.authorize(director, source.environment, ('director',))
        self._authority.authorize(recipient, source.environment)
        require(type(origins) is tuple and bool(origins) and len(set(origins)) == len(origins) and
                all(o in ('fixture', 'user_supplied') for o in origins), 'explicit offline origins required')
        root = ()
        if local_root is not None:
            require(source.kind == 'github', 'directory inspection is GitHub-fixture only')
            path = Path(local_root)
            require(not path.is_symlink() and path.is_dir(), 'authorized real fixture directory required')
            allowed = self._fixture_roots.get(source.environment)
            resolved = path.resolve()
            if allowed is None or (resolved != allowed and allowed not in resolved.parents):
                raise AuthorizationError('fixture directory outside trusted environment root')
            root = (str(resolved),)
        grant = SourceGrant(source.environment, recipient.principal, hash_content(source), origins, root)
        with self._lock:
            self._grants[id(grant)] = grant
        return grant

    def revoke(self, director, grant):
        self._authority.authorize(director, grant.environment, ('director',))
        with self._lock:
            if self._grants.get(id(grant)) is grant:
                del self._grants[id(grant)]

    def process_request(self, context, request, fixture, grant):
        require(type(request) is ResearchRequest, 'validated one-source request required')
        self._authority.authorize(context, request.environment)
        if request.requested_by != context.principal:
            raise AuthorizationError('requester must match authenticated principal')
        return self.process(context, request.sources[0], fixture, grant)

    def process(self, context, source, fixture, grant):
        require(type(source) is SourceIdentity and type(fixture) is SourceFixture, 'validated source and fixture required')
        self._authority.authorize(context, source.environment)
        # Serialize with revocation: it cannot revoke an operation half-way through.
        with self._lock:
            if (type(grant) is not SourceGrant or self._grants.get(id(grant)) is not grant or
                    grant.environment != context.environment or grant.principal != context.principal or
                    grant.source_digest != hash_content(source) or fixture.origin not in grant.origins):
                raise AuthorizationError('unissued, revoked, foreign or insufficient source permission')
            return self._process(context, source, fixture)

    def process_directory(self, context, source, grant, *, revision=''):
        """Read only an explicitly director-granted local repository fixture root.

        No checkout, Git invocation, submodule access, temp copies or writes.
        Requires POSIX no-follow/dir-fd support; no unsafe fallback on other hosts.
        """
        from .contracts import FixtureFile
        self._authority.authorize(context, source.environment)
        with self._lock:
            if (type(grant) is not SourceGrant or self._grants.get(id(grant)) is not grant or
                    grant.principal != context.principal or grant.environment != context.environment or
                    grant.source_digest != hash_content(source) or not grant.local_root or
                    'fixture' not in grant.origins):
                raise AuthorizationError('explicit local fixture permission required')
            require(hasattr(os, 'O_NOFOLLOW') and hasattr(os, 'fwalk'), 'safe directory reader unavailable')
            meter = Meter(self._limits, self._clock)
            files, total, entries = [], 0, 0
            inspection_errors = []
            def traversal_error(error):
                meter.check()
                if len(inspection_errors) >= self._limits.files:
                    raise EscalationRequired('directory traversal error limit exceeded')
                omitted = str(error.filename or '<unknown subtree>')
                if os.path.isabs(omitted):
                    try:
                        omitted = str(Path(omitted).resolve().relative_to(grant.local_root[0]))
                    except ValueError:
                        omitted = '<unresolved subtree>'
                reason = str(error.strerror or type(error).__name__)
                inspection_errors.append('repository traversal omitted ' + omitted[:512] +
                                         ': ' + type(error).__name__ +
                                         ' errno=' + str(error.errno) + ': ' + reason[:512])
            descriptor = os.open(grant.local_root[0], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                for directory, dirs, names, directory_fd in os.fwalk('.', dir_fd=descriptor, follow_symlinks=False, onerror=traversal_error):
                    meter.check()
                    for name in sorted(dirs + names):
                        entries += 1
                        if entries > self._limits.files * 2:
                            raise EscalationRequired('directory traversal budget exhausted')
                        meter.check()
                        relative = str(Path(directory) / name)
                        info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                        if stat.S_ISLNK(info.st_mode):
                            files.append(FixtureFile(relative, b'', symlink=True))
                            if name in dirs:
                                dirs.remove(name)
                        elif stat.S_ISREG(info.st_mode):
                            if info.st_size > self._limits.input_bytes - total:
                                raise EscalationRequired('local fixture input byte limit exceeded')
                            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory_fd)
                            with os.fdopen(fd, 'rb') as stream:
                                require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), 'regular fixture file required')
                                data = stream.read(self._limits.input_bytes - total + 1)
                            total += len(data)
                            if total > self._limits.input_bytes:
                                raise EscalationRequired('local fixture grew beyond byte limit')
                            files.append(FixtureFile(relative, data, executable=bool(info.st_mode & 0o111)))
                        elif not stat.S_ISDIR(info.st_mode):
                            raise AuthorizationError('special fixture files forbidden')
                        if len(files) > self._limits.files:
                            raise EscalationRequired('local fixture file limit exceeded')
            except AuthorizationError:
                raise  # Never turn a security-policy denial into partial success.
            except OSError as error:
                # Some Python versions propagate scandir/iteration failures rather
                # than invoking fwalk's callback. Stop and disclose the omission.
                traversal_error(error)
            finally:
                os.close(descriptor)
            meter.check()
            fixture = SourceFixture(files=tuple(files), revision=revision, complete=not inspection_errors)
            return self._process(context, source, fixture, meter=meter, inspection_errors=inspection_errors)

    def _process(self, context, source, fixture, *, meter=None, inspection_errors=()):
        # Reject input before hashing/parsing; bytes/file limits cover every record,
        # including unsafe and unrecognized files. No truncation of input identity.
        size = sum(len(f.data) for f in fixture.files)
        if size > self._limits.input_bytes or len(fixture.files) > self._limits.files:
            raise EscalationRequired('source input exceeds authorized extraction resources')
        meter = meter if meter is not None else Meter(self._limits, self._clock)
        collector = Collector(context.environment, fixture, meter)
        for error in inspection_errors:
            collector.limit(error)
        status = {'auth_required': 'AUTH_REQUIRED', 'inaccessible': 'INACCESSIBLE',
                  'unsupported': 'UNSUPPORTED', 'error': 'ERROR'}.get(fixture.access)
        snapshot_digest = fixture.digest
        revision = (fixture.revision,) if fixture.revision else ()
        metadata = dict(fixture.metadata)
        canonical = ()
        try:
            meter.check(max(1, size // 64))
            if 'canonical_url' in metadata and source.kind not in ('website', 'article'):
                canonical = (canonical_url(metadata['canonical_url'], source.kind),)
            if source.content_digest != snapshot_digest:
                collector.limit('submitted snapshot digest differs from observed snapshot; new verification required')
            if source.revision != fixture.revision:
                collector.limit('submitted revision differs from observed revision; no implicit task repinning')
            if not fixture.complete:
                collector.limit('supplied source snapshot declared incomplete')
            if status is None:
                status = ADAPTERS[source.kind]().extract(fixture, collector)
                for key in collector.ambiguous_metadata:
                    metadata.pop(key, None)
                for key, value in collector.metadata.items():
                    if key in metadata and metadata[key] != value:
                        metadata.pop(key)
                        collector.limit('conflicting supplied and extracted metadata omitted:' + key)
                    else:
                        metadata[key] = value
                if 'canonical_url' in metadata:
                    canonical = (html_canonical(metadata['canonical_url'], source, collector)
                                 if source.kind in ('website', 'article') else
                                 (canonical_url(metadata['canonical_url'], source.kind),))
                if status is None and not collector.evidence:
                    collector.limit('no extractable text available')
                status = status or ('ERROR' if inspection_errors and not collector.evidence else
                                    'PARTIAL' if collector.limitations else
                                    'SUPPORTED_FETCHED' if collector.evidence else 'PARTIAL')
            else:
                if 'canonical_url' in metadata and source.kind in ('website', 'article'):
                    canonical = html_canonical(metadata['canonical_url'], source, collector)
                collector.limit('access status supplied by authorized fixture; blocked bytes not extracted')
        except ExtractionLimit as exc:
            collector.limit(str(exc))
            status = 'PARTIAL' if collector.evidence else 'ERROR'
        except (ValueError, RecursionError) as exc:
            # No malformed parsed identity is returned as observed provenance.
            collector.evidence.clear()
            collector.capabilities.clear()
            meter.characters = 0
            collector.limit('malformed source: ' + type(exc).__name__)
            status = 'ERROR'
            if source.kind == 'github':
                revision = ()
        return SourceResult(environment=context.environment, submitted=source, outcome=status,
            snapshot_digest=snapshot_digest, revision=revision, canonical_identity=canonical,
            title=(metadata['title'],) if 'title' in metadata else (),
            license=(metadata['license'],) if 'license' in metadata else (),
            publisher=(metadata['publisher'],) if 'publisher' in metadata else (),
            author=(metadata['author'],) if 'author' in metadata else (),
            published_at=(metadata['published_at'],) if 'published_at' in metadata else (),
            retrieved_at=(metadata['retrieved_at'],) if 'retrieved_at' in metadata else (),
            evidence=tuple(collector.evidence), files=tuple(collector.files),
            capabilities=tuple(collector.capabilities), limitations=tuple(collector.limitations),
            flags=tuple(collector.flags), input_bytes=size, extracted_characters=meter.characters,
            work_units=meter.work, origin=fixture.origin)
