"""Independent source discovery for claim verification. Never invents sources.

Search providers return candidate URLs only; a URL becomes evidence only after
its bytes are retrieved, pinned to a snapshot and extracted by the existing
source handlers. Search snippets are never evidence. Retrieved text is
untrusted data: instruction-like sentences are flagged and excluded from
matching, and nothing in a page is ever executed or followed.

Providers that need no new paid account: Wikipedia (MediaWiki public API) and a
pluggable ``WebSearch`` interface whose default is ``NoWebSearch``.
"""
from dataclasses import asdict, dataclass, field
import json
import re
import time
from pathlib import Path
from urllib.parse import quote, unquote, urlencode, urlsplit

from .sources import extract_document, fetch, http_get, sha

WIKIPEDIA_PUBLISHER = 'Wikipedia (Wikimedia Foundation)'
MAX_SOURCES_PER_CLAIM = 3
MAX_RETRIEVALS = 12

# Same advisory patterns as sources.adapters.Collector, extended for verifier-directed text.
INJECTION = re.compile(
    r'ignore.{0,40}(instructions|previous)|disregard.{0,40}(instructions|previous|above)|system\s*prompt|'
    r'exfiltrat|override.{0,30}(policy|rules)|you are (now )?(an? )?(ai|assistant|language model|chatgpt|claude)|'
    r'(mark|classify|label|rate|treat)\s.{0,60}\b(as\s)?(corroborated|verified|supported|uncontradicted)\b|'
    r'\b(assistant|system|developer)\s*:', re.I)

# Official records and research repositories; everything else is secondary.
PRIMARY_SUFFIXES = ('.gov', '.mil', '.int', '.gov.uk', '.gov.au', '.gc.ca', '.europa.eu')
PRIMARY_HOSTS = ('doi.org', 'arxiv.org', 'ncbi.nlm.nih.gov', 'un.org', 'who.int', 'iso.org', 'ietf.org',
                 'rfc-editor.org', 'w3.org', 'federalregister.gov', 'legislation.gov.uk')
SECOND_LEVEL = {'co', 'com', 'org', 'net', 'gov', 'ac', 'edu'}


@dataclass(frozen=True)
class SearchHit:
    url: str
    title: str = ''
    provider: str = ''


# Wikimedia API etiquette: identify the client and keep requests serial and spaced.
WIKIMEDIA_USER_AGENT = 'Alfred-Research/1.0 (personal research assistant; https://github.com/hrsnyde1)'
WIKIMEDIA_INTERVAL = 1.0
_last_wikimedia = [0.0]


def wikimedia_fetch(url, *, allow_json=False):
    """``sources.fetch``-shaped JSON GET for the Wikimedia API with an identifying User-Agent."""
    wait = _last_wikimedia[0] + WIKIMEDIA_INTERVAL - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    try:
        data, media, provenance = http_get(url, headers={'User-Agent': WIKIMEDIA_USER_AGENT, 'Accept': 'application/json'})
    finally:
        _last_wikimedia[0] = time.monotonic()
    if media != 'application/json':
        raise ValueError('Wikimedia API returned ' + (media or 'unknown') + ', not JSON')
    return data, 'response.json', provenance


class SearchProvider:
    """``search(query, limit)`` returns ``SearchHit`` candidates (URLs, never evidence)."""
    name = 'none'

    def search(self, query, limit):
        raise NotImplementedError


class NoWebSearch(SearchProvider):
    """Default web search: no provider configured, so no web results (stated, not hidden)."""
    name = 'web-search:none-configured'

    def search(self, query, limit):
        return []


class WikipediaSearch(SearchProvider):
    name = 'wikipedia'

    def __init__(self, fetcher=None):
        self.fetcher = fetcher or wikimedia_fetch

    def search(self, query, limit):
        url = 'https://en.wikipedia.org/w/api.php?' + urlencode(
            {'action': 'query', 'list': 'search', 'srsearch': query, 'srlimit': limit, 'format': 'json'})
        data, _, _ = self.fetcher(url, allow_json=True)
        rows = json.loads(data).get('query', {}).get('search', [])
        return [SearchHit('https://en.wikipedia.org/wiki/' + quote(row['title'].replace(' ', '_'), safe=''),
                          row['title'], self.name) for row in rows[:limit] if isinstance(row.get('title'), str)]


def wikipedia_title(url):
    p = urlsplit(url)
    if p.hostname == 'en.wikipedia.org' and p.path.startswith('/wiki/'):
        return unquote(p.path[len('/wiki/'):]).replace('_', ' ')
    return None


def publisher_key(url):
    """Registrable domain used for independence grouping (www/mobile prefixes collapse)."""
    host = (urlsplit(url).hostname or '').lower().rstrip('.')
    labels = host.split('.')
    if len(labels) >= 3 and labels[-2] in SECOND_LEVEL and len(labels[-1]) == 2:
        return '.'.join(labels[-3:])
    return '.'.join(labels[-2:])


def source_role(url, provider):
    host = (urlsplit(url).hostname or '').lower()
    if provider == 'wikipedia' or publisher_key(url) == 'wikipedia.org':
        return 'secondary', 'Encyclopedia (tertiary compilation of other sources); counted as secondary'
    if host.endswith(PRIMARY_SUFFIXES) or any(host == h or host.endswith('.' + h) for h in PRIMARY_HOSTS):
        return 'primary', 'Official record or research repository domain'
    return 'secondary', 'Publisher not identified as an official record or research repository'


@dataclass
class DiscoveredSource:
    """One discovered candidate. ``status`` is ``retrieved`` or ``unreachable``; never assumed."""
    discovery_id: str
    url: str
    provider: str
    query: str
    status: str
    publisher: str = ''
    publisher_key: str = ''
    title: str = ''
    retrieved_at: str = ''
    role: str = ''
    role_basis: str = ''
    final_url: str = ''
    snapshot: str = ''
    sha256: str = ''
    error: str = ''
    flags: list = field(default_factory=list)
    independent: bool = True
    independence_group: str = ''
    independence_reason: str = ''
    sentences: list = field(default_factory=list)   # [(location, sentence)] clean of flagged text

    def payload(self):
        value = asdict(self)
        value.pop('sentences')
        return value


SENTENCE = re.compile(r'(?<=[.!?])\s+(?=["\'“(\[]?[A-Z0-9])|\n\s*\n|\n(?==)')


def sentences(evidence):
    """Split extracted evidence into exact sentences, dropping instruction-like ones."""
    rows, flagged = [], 0
    for item in evidence:
        for number, sentence in enumerate(SENTENCE.split(item['text'])):
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
            if INJECTION.search(sentence):
                flagged += 1
                continue
            rows.append((item['location'] + ':s' + str(number), sentence))
    return rows, flagged


class Discovery:
    """Finds and retrieves candidate independent sources for a claim query."""

    def __init__(self, providers=None, fetcher=None, directory=None, clock=None):
        self.fetcher = fetcher or fetch
        self.wikimedia = fetcher or wikimedia_fetch
        self.providers = list(providers) if providers is not None else [WikipediaSearch(self.wikimedia), NoWebSearch()]
        self.directory = Path(directory) if directory else None
        self.clock = clock or (lambda: time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
        self.sources, self.by_url, self.search_errors = [], {}, []

    def find(self, query, limit=MAX_SOURCES_PER_CLAIM):
        """Returns (sources, complete) where ``complete`` means every provider answered."""
        found, complete = [], True
        for provider in self.providers:
            try:
                hits = provider.search(query, limit)
            except Exception as error:
                complete = False
                self.search_errors.append({'provider': provider.name, 'query': query,
                                           'error': type(error).__name__ + ': ' + str(error)[:300]})
                continue
            for hit in hits[:limit]:
                if not isinstance(hit, SearchHit) or not hit.url.startswith('https://'):
                    continue
                source = self.retrieve(hit.url, hit.provider or provider.name, query)
                if source is not None and source not in found:
                    found.append(source)
        return found, complete

    def retrieve(self, url, provider, query):
        if url in self.by_url:
            return self.by_url[url]
        if len(self.sources) >= MAX_RETRIEVALS:
            return None
        source = DiscoveredSource('D' + str(len(self.sources) + 1), url, provider, query, 'unreachable',
                                  publisher_key=publisher_key(url))
        source.role, source.role_basis = source_role(url, provider)
        self.sources.append(source)
        self.by_url[url] = source
        try:
            title = wikipedia_title(url) if provider == 'wikipedia' else None
            if title:
                # Plain-text extract of the same article; the citation URL stays the article URL.
                api = 'https://en.wikipedia.org/w/api.php?' + urlencode(
                    {'action': 'query', 'prop': 'extracts', 'explaintext': 1, 'redirects': 1,
                     'titles': title, 'format': 'json', 'formatversion': 2})
                raw, _, provenance = self.wikimedia(api, allow_json=True)
                pages = json.loads(raw).get('query', {}).get('pages', [])
                if not pages or pages[0].get('missing') or not pages[0].get('extract'):
                    raise ValueError('Wikipedia article has no retrievable text')
                data, filename = pages[0]['extract'].encode(), 'source.txt'
                source.title, source.publisher = pages[0].get('title', title), WIKIPEDIA_PUBLISHER
                source.final_url = 'https://en.wikipedia.org/wiki/' + quote(source.title.replace(' ', '_'), safe='')
            else:
                data, filename, provenance = self.fetcher(url)
                source.final_url = provenance.get('final_url', url)
            result = extract_document(data, filename)
            source.retrieved_at = self.clock()
            source.sha256 = sha(data)
            source.publisher_key = publisher_key(source.final_url or url)
            source.title = source.title or result.metadata.get('title', '')
            source.publisher = (source.publisher or result.metadata.get('publisher') or
                                result.metadata.get('site_name') or source.publisher_key)
            source.sentences, flagged = sentences(result.evidence)
            source.flags = list(dict.fromkeys(result.flags))
            if flagged:
                source.flags.append('instruction_like_text_excluded:' + str(flagged))
            if self.directory:
                self.directory.mkdir(mode=0o700, exist_ok=True)
                snapshot = self.directory / (source.discovery_id + '-' + filename)
                snapshot.write_bytes(data)
                snapshot.chmod(0o600)
                source.snapshot = str(snapshot)
            source.status = 'retrieved'
        except Exception as error:
            source.error = type(error).__name__ + ': ' + str(error)[:300]
        return source
