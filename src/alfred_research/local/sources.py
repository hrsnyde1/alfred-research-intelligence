"""Source handlers: live acquisition plus deterministic extraction of pinned bytes.

Each supported source family is one ``SourceHandler``. Acquisition stores an
immutable byte snapshot and its provenance. Extraction must depend only on the
snapshot bytes and snapshot name, because the independent verifier re-extracts
the same snapshot in a separate process before any claim is accepted.
"""
from dataclasses import dataclass, field
import hashlib
import http.client
import json
import socket
import ssl
import time
from pathlib import Path
from urllib.parse import quote, urlencode, urljoin, urlsplit

from ..sources.adapters import Collector
from ..sources.contracts import SourceFixture, FixtureFile
from ..sources.policy import FutureNetworkPolicy, Meter, ProcessingLimits

MAX_BYTES = 1_000_000
BINARY_MAX_BYTES = 20_000_000   # PDF/DOCX snapshots
MAX_EXTRACTED_CHARACTERS = 1_500_000
TEXT_SUFFIXES = ('.txt', '.md', '.csv', '.vtt', '.srt')


class UnsupportedSource(ValueError):
    """Honest refusal; metadata records what was observed without analyzing it."""
    def __init__(self, message, metadata=None):
        super().__init__(message)
        self.metadata = dict(metadata or {})


@dataclass
class Extraction:
    evidence: list
    limitations: list = field(default_factory=list)
    flags: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    # What the evidence actually is (e.g. full_text, pdf_text_layer,
    # caption_metadata_only); reports state it so nothing is overclaimed.
    basis: str = 'full_text'


class SourceHandler:
    """One source family. Subclasses override only what they support.

    ``claims_url`` selects a platform handler before generic HTTPS fetching;
    ``acquire_url`` returns ``(bytes, snapshot_name, provenance)``; ``extract``
    turns a snapshot into evidence without network or execution.
    """
    name = 'generic'
    kind = 'document'            # source kind used for Director specialty routing
    snapshot_names = ()          # exact snapshot names owned by this handler
    suffixes = ()                # owner-file and fetched-file suffixes it extracts
    max_bytes = MAX_BYTES

    def claims_url(self, url):
        return False

    def acquire_url(self, url):
        raise UnsupportedSource(self.name + ' does not acquire URLs')

    def extract(self, data, filename):
        raise NotImplementedError


def handlers():
    """Ordered registry: URL-claiming platform handlers first, then documents."""
    from .documents import ArticleHandler, DocxHandler, TextHandler
    from .pdf import PDFHandler
    from .platforms import GitHubHandler, InstagramHandler, YouTubeHandler
    return (YouTubeHandler(), InstagramHandler(), GitHubHandler(),
            PDFHandler(), DocxHandler(), ArticleHandler(), TextHandler())


def handler_for_url(url):
    return next((h for h in handlers() if h.claims_url(url)), None)


def handler_for_snapshot(filename):
    name = Path(filename).name.lower()
    registry = handlers()
    exact = next((h for h in registry if name in h.snapshot_names), None)
    if exact:
        return exact
    suffix = Path(name).suffix
    return next((h for h in registry if suffix in h.suffixes), None)


def supported_formats():
    return ('Supported: web articles (HTML), PDF text layer, DOCX, UTF-8 text/Markdown/CSV, VTT/SRT '
            'transcripts, public GitHub repositories, YouTube videos with accessible captions, and '
            'public Instagram post/Reel captions.')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def text_evidence(label, segments, *, chars=60000, count=200):
    """Bounded evidence from ordered ``(location, text)`` segments.

    Reuses the existing Collector (bounds, prompt-injection flags, stable IDs).
    Locations must be unique within ``label``; they are cited in reports.
    """
    evidence, limitations, flags = [], [], []
    part, size, total = [], 0, 0
    seen = set()

    def flush():
        if not part:
            return
        data = '\n'.join(text for _, text in part).encode()
        file = FixtureFile(label, data[:1_000_000])
        collector = Collector('personal', SourceFixture(files=(file,), origin='user_supplied'),
                              Meter(ProcessingLimits(characters=128000, segments=256, milliseconds=10000)))
        collector.inventory(file)
        for location, text in part:
            collector.add(file, text, location)
        evidence.extend(e.payload() for e in collector.evidence)
        limitations.extend(collector.limitations)
        flags.extend(collector.flags)

    for location, text in segments:
        text = text.strip()
        if not text:
            continue
        if location in seen:
            raise ValueError('Duplicate evidence location: ' + location)
        seen.add(location)
        if total + len(text) > MAX_EXTRACTED_CHARACTERS:
            limitations.append('Extraction stopped at ' + str(MAX_EXTRACTED_CHARACTERS) +
                               ' characters; later content (from ' + location + ') was not analyzed.')
            break
        if part and (len(part) >= count or size + len(text) > chars):
            flush()
            part, size = [], 0
        part.append((location, text))
        size += len(text)
        total += len(text)
    flush()
    return evidence, list(dict.fromkeys(limitations)), list(dict.fromkeys(flags))


def extract_document(data, filename):
    handler = handler_for_snapshot(filename)
    if handler is None:
        raise UnsupportedSource(supported_formats() + ' Legacy .doc, PowerPoint, spreadsheets and images are not.')
    result = handler.extract(data, filename)
    if not result.evidence:
        raise UnsupportedSource('No extractable text; no research findings generated.', result.metadata)
    result.limitations = list(dict.fromkeys(result.limitations))
    result.flags = list(dict.fromkeys(result.flags))
    result.metadata.setdefault('handler', handler.name)
    return result


def extract(data, filename):
    """Compatibility wrapper used by the verifier: (evidence, limitations, flags)."""
    result = extract_document(data, filename)
    return result.evidence, result.limitations, result.flags


def legacy_text_extract(data, filename):
    """Original line-range text extraction, retained unchanged for text formats."""
    suffix = Path(filename).suffix.lower()
    evidence, limitations, flags = [], [], []
    # Preserve all lines of long standards/articles rather than silently
    # researching only the table of contents under the legacy 128-line cap.
    text = data.decode('utf-8')
    parts, pending, start = [], [], 1
    for number, line in enumerate(text.splitlines(keepends=True), 1):
        if pending and (len(pending) >= 100 or len(''.join(pending)) + len(line) > 60000):
            parts.append((f'lines-{start}-{number-1}' + suffix, ''.join(pending).encode()))
            pending, start = [], number
        pending.append(line)
    if pending:
        parts.append((f'lines-{start}-{start+len(pending)-1}' + suffix, ''.join(pending).encode()))
    for part_name, part_data in parts:
        file = FixtureFile(part_name, part_data)
        snapshot = SourceFixture(files=(file,), origin='user_supplied')
        collector = Collector('personal', snapshot, Meter(ProcessingLimits(characters=128000, segments=256)))
        # Keep wrapped prose together for entailment review. Collector is
        # the existing bounded text/evidence implementation used by all
        # legacy adapters; locations retain original line-range + offset.
        collector.inventory(file)
        collector.add(file, part_data.decode('utf-8'), 'text')
        evidence.extend(e.payload() for e in collector.evidence)
        limitations.extend(collector.limitations)
        flags.extend(collector.flags)
    return evidence, list(dict.fromkeys(limitations)), list(dict.fromkeys(flags))


class PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host, address, timeout):
        context = ssl.create_default_context()
        # python.org macOS installs can lack their optional CA symlink. Trust
        # the OS bundle when present, retaining hostname and chain validation.
        if not ssl.get_default_verify_paths().cafile and Path('/etc/ssl/cert.pem').is_file():
            context.load_verify_locations('/etc/ssl/cert.pem')
        super().__init__(host, timeout=timeout, context=context)
        self.address = address

    def connect(self):
        raw = socket.create_connection((self.address, 443), self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except BaseException:
            raw.close()
            raise


def http_get(url, *, max_bytes=MAX_BYTES, headers=None):
    """Public HTTPS GET with pinned addresses, validated redirects and bounds.

    Returns ``(bytes, media_type, provenance)``. Never sends credentials.
    """
    policy = FutureNetworkPolicy()
    deadline = time.monotonic() + 45
    chain = []
    request_headers = {'User-Agent': 'Alfred-Research/1.0', 'Accept-Encoding': 'identity'}
    request_headers.update(headers or {})
    for hop in range(4):
        p = urlsplit(url)
        # Validate syntax before DNS, then pin the connection to a validated IP.
        policy.validate(url, ('8.8.8.8',))
        addresses = tuple(dict.fromkeys(x[4][0] for x in socket.getaddrinfo(p.hostname, 443, type=socket.SOCK_STREAM)))
        policy.validate(url, addresses)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('Source acquisition deadline exceeded')
        connection = PinnedHTTPS(p.hostname, addresses[0], min(15, remaining))
        try:
            connection.request('GET', (p.path or '/') + ('?' + p.query if p.query else ''), headers=request_headers)
            response = connection.getresponse()
            chain.append({'url': url, 'status': response.status})
            if response.status in (301, 302, 303, 307, 308):
                if hop >= 3 or not response.getheader('Location'):
                    raise ValueError('Redirect limit or missing redirect target')
                url = urljoin(url, response.getheader('Location'))
                continue
            if response.status != 200:
                raise ValueError('Source HTTP status ' + str(response.status))
            if response.getheader('Content-Encoding', 'identity') != 'identity':
                raise UnsupportedSource('Compressed response not supported')
            data = bytearray()
            while True:
                if time.monotonic() >= deadline:
                    raise TimeoutError('Source acquisition deadline exceeded')
                chunk = response.read(min(65536, max_bytes + 1 - len(data)))
                if not chunk:
                    break
                data.extend(chunk)
                if len(data) > max_bytes:
                    raise ValueError('Source exceeds ' + str(max_bytes // 1_000_000) + ' MB limit')
            media = response.getheader('Content-Type', '').split(';')[0].strip().lower()
            return bytes(data), media, {'origin': 'live_https', 'requested_url': chain[0]['url'],
                                        'final_url': url, 'redirects': chain, 'content_type': media}
        finally:
            connection.close()
    raise ValueError('Redirect limit')


DOCX_MEDIA = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'


def fetch(url, *, allow_json=False):
    """Generic URL acquisition; the snapshot name selects the extracting handler."""
    path = urlsplit(url).path.lower()
    data, media, provenance = http_get(url, max_bytes=BINARY_MAX_BYTES)
    if media in ('application/pdf', 'application/x-pdf') or (path.endswith('.pdf') and data.startswith(b'%PDF-')):
        filename = 'source.pdf'
    elif media == DOCX_MEDIA or (path.endswith('.docx') and data.startswith(b'PK')):
        filename = 'source.docx'
    elif len(data) > MAX_BYTES:
        raise ValueError('Source exceeds 1 MB limit')
    elif allow_json and media == 'application/json':
        filename = 'response.json'
    elif media in ('text/html', 'application/xhtml+xml'):
        filename = 'source.html'
    elif media.startswith('text/') or path.endswith(TEXT_SUFFIXES):
        filename = 'source.txt'
    else:
        raise UnsupportedSource('Unsupported response format: ' + (media or 'unknown') + '. ' + supported_formats())
    return data, filename, provenance


def discover(question):
    """Small real public search fallback; no fabricated sources or citations."""
    query = urlencode({'action': 'query', 'list': 'search', 'srsearch': question,
                       'srlimit': 2, 'format': 'json'})
    data, _, _ = fetch('https://en.wikipedia.org/w/api.php?' + query, allow_json=True)
    result = json.loads(data)
    rows = result.get('query', {}).get('search', [])
    return ['https://en.wikipedia.org/wiki/' + quote(row['title'].replace(' ', '_'), safe='')
            for row in rows[:2] if isinstance(row.get('title'), str)]


def acquire(locator, destination, index):
    if locator.startswith(('https://', 'http://')):
        handler = handler_for_url(locator)
        if handler is not None:
            data, filename, provenance = handler.acquire_url(locator)
        else:
            data, filename, provenance = fetch(locator)
    else:
        path = Path(locator).expanduser().resolve(strict=True)
        if not path.is_file():
            raise ValueError('Source must be a regular file')
        filename = 'source' + path.suffix.lower()
        handler = handler_for_snapshot(filename)
        if handler is None:
            raise UnsupportedSource(supported_formats() + ' Unsupported file type: ' + (path.suffix or 'none') + '.')
        if path.stat().st_size > handler.max_bytes:
            raise ValueError('Source must be at most ' + str(handler.max_bytes // 1_000_000) + ' MB')
        data = path.read_bytes()
        provenance = {'origin': 'owner_file', 'path': str(path)}
    result = extract_document(data, filename)
    snapshot = destination / (str(index) + '-' + filename)
    snapshot.write_bytes(data)
    snapshot.chmod(0o600)
    source_id = 'S' + str(index)
    for e in result.evidence:
        e['evidence_id'] = source_id + ':' + e['evidence_id']
    handler = handler_for_snapshot(filename)
    return {'source_id': source_id, 'locator': locator, 'snapshot': str(snapshot),
            'filename': filename, 'sha256': sha(data), 'bytes': len(data),
            'acquired_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'provenance': provenance, 'handler': handler.name, 'kind': handler.kind,
            'content_basis': result.basis, 'metadata': result.metadata,
            'evidence': result.evidence, 'limitations': result.limitations, 'flags': result.flags}
