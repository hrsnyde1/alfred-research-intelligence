"""Live acquisition with immutable byte snapshots; reuse existing pure extractors."""
import hashlib
import http.client
import json
import socket
import ssl
import time
from pathlib import Path
from urllib.parse import quote, urlencode, urljoin, urlsplit

from ..sources.adapters import Collector, WebsiteAdapter, DocumentAdapter
from ..sources.contracts import SourceFixture, FixtureFile
from ..sources.policy import FutureNetworkPolicy, Meter, ProcessingLimits

MAX_BYTES = 1_000_000


class UnsupportedSource(ValueError):
    pass


def sha(data):
    return hashlib.sha256(data).hexdigest()


def extract(data, filename):
    """A fetched snapshot is passed as user-supplied bytes, never relabeled a fixture.

    Live acquisition provenance is held separately from these legacy extraction
    contracts, which intentionally have no live-provider origin.
    """
    suffix = Path(filename).suffix.lower()
    if suffix not in ('.html', '.htm', '.txt', '.md', '.csv', '.vtt', '.srt'):
        raise UnsupportedSource('Supported documents: UTF-8 text, Markdown, HTML, CSV, VTT, SRT. PDF/Office extraction is not installed.')
    evidence, limitations, flags = [], [], []
    if suffix in ('.html', '.htm'):
        parts = [(filename, data)]
    else:
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
        if suffix in ('.html', '.htm'):
            WebsiteAdapter().extract(snapshot, collector)
        else:
            # Keep wrapped prose together for entailment review. Collector is
            # the existing bounded text/evidence implementation used by all
            # legacy adapters; locations retain original line-range + offset.
            collector.inventory(file)
            collector.add(file, part_data.decode('utf-8'), 'text')
        evidence.extend(e.payload() for e in collector.evidence)
        limitations.extend(collector.limitations)
        flags.extend(collector.flags)
    if not evidence:
        raise UnsupportedSource('No extractable UTF-8 text; no research findings generated.')
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


def fetch(url, *, allow_json=False):
    policy = FutureNetworkPolicy()
    deadline = time.monotonic() + 45
    chain = []
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
            connection.request('GET', (p.path or '/') + ('?' + p.query if p.query else ''),
                               headers={'User-Agent': 'Alfred-Research/1.0', 'Accept-Encoding': 'identity'})
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
                chunk = response.read(min(16384, MAX_BYTES + 1 - len(data)))
                if not chunk:
                    break
                data.extend(chunk)
                if len(data) > MAX_BYTES:
                    raise ValueError('Source exceeds 1 MB limit')
            media = response.getheader('Content-Type', '').split(';')[0].lower()
            if allow_json and media == 'application/json':
                filename = 'response.json'
            elif media in ('text/html', 'application/xhtml+xml'):
                filename = 'source.html'
            elif media.startswith('text/') or p.path.lower().endswith(('.txt', '.md', '.csv', '.vtt', '.srt')):
                filename = 'source.txt'
            else:
                raise UnsupportedSource('Unsupported response format: ' + (media or 'unknown'))
            return bytes(data), filename, {'origin': 'live_https', 'requested_url': chain[0]['url'],
                                          'final_url': url, 'redirects': chain, 'content_type': media}
        finally:
            connection.close()
    raise ValueError('Redirect limit')


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
        host = (urlsplit(locator).hostname or '').lower()
        if host in ('youtube.com', 'www.youtube.com', 'youtu.be'):
            raise UnsupportedSource('YouTube retrieval is not installed. Submit a genuine downloaded transcript (.vtt/.srt/.txt); video content is not inferred from metadata.')
        data, filename, provenance = fetch(locator)
    else:
        path = Path(locator).expanduser().resolve(strict=True)
        if not path.is_file() or path.stat().st_size > MAX_BYTES:
            raise ValueError('Source must be a regular file of at most 1 MB')
        data = path.read_bytes()
        filename = 'source' + path.suffix.lower()
        provenance = {'origin': 'owner_file', 'path': str(path)}
    evidence, limitations, flags = extract(data, filename)
    snapshot = destination / (str(index) + '-' + filename)
    snapshot.write_bytes(data)
    snapshot.chmod(0o600)
    source_id = 'S' + str(index)
    for e in evidence:
        e['evidence_id'] = source_id + ':' + e['evidence_id']
    return {'source_id': source_id, 'locator': locator, 'snapshot': str(snapshot),
            'filename': filename, 'sha256': sha(data), 'bytes': len(data),
            'acquired_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'provenance': provenance, 'evidence': evidence, 'limitations': limitations, 'flags': flags}
