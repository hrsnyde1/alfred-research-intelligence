"""Fact verification stage: independent corroboration of research claims.

Runs after, and separately from, the research workers and the source-support
verifier (``workers.verify``), in its own process. For each checkable claim it
discovers other sources (``discovery.Discovery``), checks whether each one is
independent of the claim's original source, and classifies the claim.

Contract consumed by report synthesis: ``VerificationResult`` (schema
``research.local.corroboration/1``), stored as job artifact ``corroboration``.

Rules: every citation names a retrieved, pinned discovered source and an exact
passage re-extractable from its snapshot (no invented URLs); contradictions are
kept beside support, never collapsed; same-publisher, syndicated or attributed
copies of the original are listed as non-independent and never corroborate;
discovered text is data and never instructions.
"""
from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from .discovery import Discovery, NoWebSearch, publisher_key
from .sources import extract_document, sha
from .workers import digest

SCHEMA = 'research.local.corroboration/1'
STATUSES = ('corroborated', 'original_source_only', 'disputed', 'contradicted', 'unverified', 'not_assessable')
MODES = ('wikipedia', 'off')
MAX_CLAIMS = 8

STOP = set('''the and for are was were has have had that this with from which their there they them than then
into onto upon also been being its it's his her hers our ours your yours who whom whose what when where why how
can could would should will shall may might must does did doing done not only more most such some any each other
about after before over under between during while because since until very just than these those said says
source states state stated'''.split())
NEGATION = re.compile(r"\b(not|no|never|none|neither|nor|cannot|without|false|untrue|denied|denies|deny|refuted|disproved)\b|n't\b", re.I)
NUMBER = re.compile(r'\d+(?:[.,]\d+)*')
ATTRIBUTION = r'(according to|reported by|reports? (?:from|by)|as reported (?:by|in)|citing|cited by|via|said|says|told)'


def stem(word):
    for suffix in ('ing', 'ed', 'es', 's'):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[:-len(suffix)]
    return word


def terms(text):
    return {stem(w) for w in re.findall(r"[a-z][a-z'\-]{2,}", text.lower()) if w not in STOP}


def numbers(text):
    return {n.replace(',', '') for n in NUMBER.findall(text)}


def claim_text(claim):
    statement = claim['statement']
    return statement[len('The source states: '):] if statement.startswith('The source states: ') else statement


RANGE = re.compile(r'(\d+)\s*(?:[\u2013\u2014-]|to|through)\s*(\d+)')


# Calendar and unit words do not establish that two numbers describe the same fact.
GENERIC_ANCHORS = {stem(w) for w in '''january february march april may june july august september october november
december year years month months day days week weeks hour hours minute minutes second seconds utc gmt percent
about around approximately nearly over under'''.split()}


def number_context(text):
    """Each measured number (not name parts) with the content terms within three tokens of it."""
    tokens = re.findall(r"\d+(?:[.,]\d+)*|[A-Za-z][A-Za-z'\-]*", text)
    rows = []
    for index, token in enumerate(tokens):
        if token[0].isdigit():
            previous = tokens[index - 1] if index else ''
            if previous[:1].isupper() and stem(previous.lower()) not in GENERIC_ANCHORS:
                continue   # part of a name ("Apollo 11"): a different value names a different thing
            nearby = tokens[max(0, index - 3):index] + tokens[index + 1:index + 4]
            rows.append((token.replace(',', ''), {stem(w.lower()) for w in nearby
                                                  if not w[0].isdigit() and len(w) > 2 and w.lower() not in STOP} - GENERIC_ANCHORS))
    return rows


def year_like(value):
    return len(value) == 4 and value.isdigit() and 1000 <= int(value) <= 2199


def in_range(value, text):
    try:
        number = float(value)
    except ValueError:
        return False
    return any(float(a) <= number <= float(b) for a, b in RANGE.findall(text))


class LexicalAssessor:
    """Deterministic stance check of one sentence against a claim; no model call.

    Supports: most claim terms present, every claim number present, same polarity.
    Contradicts: same topic, and either opposite polarity with near-identical
    wording, or a different number of the same kind in the same context as the
    claim's number (e.g. "completed in 1899" vs "completed in 1889").
    Paraphrase is not recognized; a miss falls to original_source_only, never to support.
    """
    name = 'deterministic-lexical-stance'

    def stance(self, claim, sentence):
        claim_terms, sentence_terms = terms(claim), terms(sentence)
        if len(claim_terms) < 3:
            return None
        shared = claim_terms & sentence_terms
        ratio = len(shared) / len(claim_terms)
        if len(shared) < 3 or ratio < 0.6:
            return None
        if bool(NEGATION.search(claim)) != bool(NEGATION.search(sentence)):
            return 'contradicts' if ratio >= 0.75 else None
        claim_numbers, sentence_numbers = numbers(claim), numbers(sentence)
        missing = claim_numbers - sentence_numbers
        if not missing:
            return 'supports'
        if any(in_range(value, sentence) for value in missing):
            return None   # inside a stated range: neither confirmed nor contradicted
        theirs = [(v, near) for v, near in number_context(sentence) if v not in claim_numbers]
        for value, near in number_context(claim):
            if value in missing and any(year_like(value) == year_like(other) and near & around
                                        for other, around in theirs):
                return 'contradicts'
        return None


@dataclass(frozen=True)
class Citation:
    discovery_id: str
    url: str
    publisher: str
    retrieved_at: str
    role: str                 # primary | secondary
    independence_group: str
    stance: str               # supports | contradicts | repeats_original
    passage: str              # exact sentence re-extractable from the pinned snapshot
    location: str
    sha256: str
    note: str = ''


@dataclass(frozen=True)
class ClaimVerification:
    claim_id: str
    statement: str
    status: str               # one of STATUSES
    original_source_id: str
    original_support: bool    # result of the separate source-support verifier
    supporting: tuple = ()          # independent Citations, stance supports
    contradicting: tuple = ()       # Citations, stance contradicts (any publisher; kept, never collapsed)
    non_independent: tuple = ()     # same publisher / syndicated / attributed repeats; never corroboration
    unreachable: tuple = ()         # {'url', 'error'} candidates that could not be retrieved
    independent_groups: tuple = ()  # distinct publisher groups among supporting
    sources_checked: int = 0        # retrieved discovered sources examined for this claim
    query: str = ''
    rationale: str = ''


@dataclass(frozen=True)
class VerificationResult:
    packet_sha256: str
    claims: tuple
    sources: tuple            # DiscoveredSource payloads (url, publisher, retrieved_at, role, status, ...)
    method: str
    providers: tuple
    limitations: tuple = ()
    search_errors: tuple = ()
    worker: str = 'independent-corroboration-worker'
    pid: int = 0
    schema: str = SCHEMA

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, value):
        if not isinstance(value, dict) or value.get('schema') != SCHEMA:
            raise ValueError('Corroboration result with schema ' + SCHEMA + ' required')
        claims = []
        for row in value['claims']:
            if row['status'] not in STATUSES:
                raise ValueError('Unknown verification status: ' + str(row['status']))
            cited = {k: tuple(Citation(**c) for c in row[k]) for k in ('supporting', 'contradicting', 'non_independent')}
            claims.append(ClaimVerification(**{**row, **cited, 'unreachable': tuple(row['unreachable']),
                                               'independent_groups': tuple(row['independent_groups'])}))
        lists = {k: tuple(value[k]) for k in ('sources', 'providers', 'limitations', 'search_errors')}
        scalars = {k: value[k] for k in ('packet_sha256', 'method', 'worker', 'pid', 'schema')}
        return cls(claims=tuple(claims), **lists, **scalars)

    def by_claim(self):
        return {c.claim_id: c for c in self.claims}

    def counts(self):
        return {status: sum(c.status == status for c in self.claims) for status in STATUSES}

    def conflicts(self):
        return [c.claim_id for c in self.claims if c.status in ('disputed', 'contradicted')]


def shingles(text, size=8):
    words = re.findall(r'\w+', text.lower())
    return {' '.join(words[i:i + size]) for i in range(0, max(0, len(words) - size + 1))}


def normalized(text):
    return ' '.join(re.findall(r'\w+', text.lower()))


def build_query(text):
    """Short search query: named terms and numbers first, then distinctive words."""
    words = re.findall(r"[A-Za-z][A-Za-z'\-]+|\d+(?:[.,]\d+)*", text)
    named = [w for w in words if w[0].isupper() or w[0].isdigit()]
    rest = sorted((w for w in words if w.lower() not in STOP and len(w) > 3 and w not in named), key=len, reverse=True)
    return ' '.join(list(dict.fromkeys(named + rest))[:8])


class Original:
    """What the claim's own source looks like, for independence checks."""

    def __init__(self, source):
        provenance = source.get('provenance', {})
        url = provenance.get('final_url') or (source['locator'] if source['locator'].startswith('https://') else '')
        self.source_id = source['source_id']
        self.key = publisher_key(url) if url else 'owner-file:' + source['source_id']
        metadata = source.get('metadata', {})
        names = [self.key.split('.')[0]] + [metadata.get(k, '') for k in ('publisher', 'site_name', 'author', 'channel')]
        self.names = [n for n in dict.fromkeys(n.strip() for n in names if n) if len(n) >= 4 and not n.startswith('owner-file')]
        self.text = normalized(' '.join(e['text'] for e in source.get('evidence', []))[:400000])
        self.shingles = shingles(self.text)

    def dependence(self, discovered, quote):
        """Reason the discovered source is not independent of this original, or ''."""
        if discovered.publisher_key == self.key:
            return 'same publisher as original source ' + self.source_id + ' (' + self.key + ')'
        page = normalized(' '.join(s for _, s in discovered.sentences))
        quote = normalized(quote)
        if len(quote) >= 60 and quote in page:
            return 'repeats the original source wording verbatim (copy or syndication)'
        theirs = shingles(page)
        if theirs and self.shingles and len(theirs & self.shingles) / len(theirs) >= 0.5:
            return 'most of its text duplicates original source ' + self.source_id + ' (syndicated copy)'
        return ''

    def attributed(self, sentence):
        return any(re.search(ATTRIBUTION + r'\W+(?:\w+\W+){0,4}?' + re.escape(name), sentence, re.I) for name in self.names)


def group_discovered(sources):
    """Independence groups across discovered sources: same publisher, or syndicated copies of each other."""
    groups = []
    for source in sources:
        if source.status != 'retrieved' or source.independence_group:
            continue
        source.independence_group = source.publisher_key
        mine = shingles(' '.join(s for _, s in source.sentences))
        for earlier, earlier_shingles in groups:
            if mine and len(mine & earlier_shingles) / len(mine) >= 0.5:
                source.independence_group = earlier.independence_group
                source.independence_reason = 'syndicated copy of ' + earlier.discovery_id
                break
        groups.append((source, mine))


def citation(source, location, passage, stance, note=''):
    return Citation(source.discovery_id, source.final_url or source.url, source.publisher, source.retrieved_at,
                    source.role, source.independence_group, stance, passage, location, source.sha256, note)


def classify(original_support, supporting, contradicting, checked, state):
    """``state``: complete | incomplete (search failed / candidates unreachable) | disabled."""
    if contradicting and supporting:
        return 'disputed', 'Independent sources both support and contradict the claim; both sides are cited.'
    if contradicting:
        return 'contradicted', 'Discovered evidence contradicts the claim and no independent source supports it.'
    if not original_support:
        return 'unverified', 'The cited original source did not support the claim, and no contradiction was found.'
    if supporting:
        groups = len({c.independence_group for c in supporting})
        return 'corroborated', 'Supported by the original source and ' + str(groups) + ' independent publisher group(s).'
    if state == 'disabled':
        return 'unverified', 'Independent discovery is disabled; only the original source was checked.'
    if state == 'incomplete':
        return 'unverified', 'No independent check completed: search failed or candidate sources were unreachable.'
    if checked:
        return 'original_source_only', ('Supported by its original source; ' + str(checked) +
                                        ' independent source(s) checked did not address it.')
    return 'original_source_only', 'Supported by its original source; discovery found no independent source addressing it.'


def corroborate(payload, discovery=None, assessor=None):
    """Classify every claim. ``payload``: sources, claims, support (source-support assessments), mode, directory."""
    mode = payload.get('mode', 'wikipedia')
    if mode not in MODES:
        raise ValueError('Corroboration mode must be one of ' + ', '.join(MODES))
    enabled = mode != 'off'
    if discovery is None:
        discovery = Discovery(providers=None if enabled else [NoWebSearch()], directory=payload.get('directory'))
    assessor = assessor or LexicalAssessor()
    sources = {s['source_id']: s for s in payload['sources']}
    originals = {key: Original(value) for key, value in sources.items()}
    support = {a['claim_id']: a['supported'] is True for a in payload['support']}
    results, limitations = [], []
    claims = payload['claims']
    if len(claims) > MAX_CLAIMS:
        limitations.append('Corroboration checked the first ' + str(MAX_CLAIMS) + ' claims; later claims are not_assessable.')
    for index, claim in enumerate(claims):
        text = claim_text(claim)
        base = dict(claim_id=claim['claim_id'], statement=claim['statement'], original_source_id=claim['source_id'],
                    original_support=support.get(claim['claim_id'], False))
        if index >= MAX_CLAIMS:
            results.append(ClaimVerification(status='not_assessable', rationale='Beyond the per-job corroboration limit.', **base))
            continue
        if claim.get('kind') != 'source_statement':
            results.append(ClaimVerification(status='not_assessable', rationale='Inference, not a factual statement to corroborate.', **base))
            continue
        if len(terms(text)) < 3:
            results.append(ClaimVerification(status='not_assessable', rationale='Too little checkable content to search for.', **base))
            continue
        query = build_query(text)
        found, complete = discovery.find(query)
        group_discovered(discovery.sources)
        original = originals[claim['source_id']]
        supporting, contradicting, dependent, unreachable, checked = [], [], [], [], 0
        for source in found:
            if source.status != 'retrieved':
                unreachable.append({'url': source.url, 'error': source.error})
                continue
            reason = original.dependence(source, claim['quote'])
            checked += 0 if reason else 1
            hits = {'supports': [], 'contradicts': []}
            for location, sentence in source.sentences:
                stance = assessor.stance(text, sentence)
                if stance and len(hits[stance]) < 2:
                    hits[stance].append((location, sentence))
            for location, sentence in hits['contradicts']:
                contradicting.append(citation(source, location, sentence, 'contradicts', reason))
            for location, sentence in hits['supports']:
                if reason:
                    dependent.append(citation(source, location, sentence, 'supports', reason))
                elif original.attributed(sentence):
                    dependent.append(citation(source, location, sentence, 'repeats_original',
                                              'attributes the claim to the original source; repetition is not corroboration'))
                else:
                    supporting.append(citation(source, location, sentence, 'supports'))
        state = 'disabled' if not enabled else 'incomplete' if not complete or (unreachable and not checked) else 'complete'
        status, why = classify(base['original_support'], supporting, contradicting, checked, state)
        if unreachable:
            why += ' ' + str(len(unreachable)) + ' candidate source(s) unreachable.'
        if dependent:
            why += ' ' + str(len(dependent)) + ' non-independent repetition(s) not counted.'
        results.append(ClaimVerification(status=status, supporting=tuple(supporting), contradicting=tuple(contradicting),
                                         non_independent=tuple(dependent), unreachable=tuple(unreachable),
                                         independent_groups=tuple(dict.fromkeys(c.independence_group for c in supporting)),
                                         sources_checked=checked, query=query, rationale=why.strip(), **base))
    limitations += ['Lexical stance matching: paraphrased support is not recognized (falls to original_source_only), '
                    'and support from a page that itself cites the original cannot be detected unless it names the original.',
                    'Wikipedia is a tertiary compilation; it is counted as one secondary publisher group.']
    if not enabled:
        limitations.append('Independent discovery disabled (ALFRED_RESEARCH_CORROBORATION=off).')
    if any(isinstance(p, NoWebSearch) for p in discovery.providers):
        limitations.append('No web search provider configured; discovery used ' +
                           (', '.join(p.name for p in discovery.providers if not isinstance(p, NoWebSearch)) or 'no provider') + ' only.')
    return VerificationResult(digest(claims), tuple(results), tuple(s.payload() for s in discovery.sources),
                              assessor.name, tuple(p.name for p in discovery.providers), tuple(limitations),
                              tuple(discovery.search_errors), pid=os.getpid())


def check(result, claims):
    """Engine-side binding check: packet, statuses, and every citation re-found in its pinned snapshot."""
    if not isinstance(result, VerificationResult):
        result = VerificationResult.from_dict(result)
    if result.packet_sha256 != digest(claims):
        raise ValueError('Corroboration packet differs from research claims')
    if [c.claim_id for c in result.claims] != [c['claim_id'] for c in claims]:
        raise ValueError('Corroboration omitted, duplicated, or invented claim identities')
    sources = {s['discovery_id']: s for s in result.sources}
    texts = {}
    for row in result.claims:
        for item in row.supporting + row.contradicting + row.non_independent:
            source = sources.get(item.discovery_id)
            if not source or source['status'] != 'retrieved' or item.url != (source['final_url'] or source['url']) \
                    or item.sha256 != source['sha256']:
                raise ValueError('Citation does not name a retrieved discovered source: ' + item.url)
            if item.discovery_id not in texts:
                data = Path(source['snapshot']).read_bytes()
                if sha(data) != source['sha256']:
                    raise ValueError('Discovered snapshot changed after retrieval')
                texts[item.discovery_id] = [e['text'] for e in extract_document(data, Path(source['snapshot']).name.split('-', 1)[1]).evidence]
            if not any(item.passage in text for text in texts[item.discovery_id]):
                raise ValueError('Cited passage not found in discovered snapshot ' + item.discovery_id)
    return result


def run_stage(sources, claims, support, directory, mode=None, timeout=420):
    """Engine hook: separate process; returns a checked ``VerificationResult``."""
    mode = mode or os.environ.get('ALFRED_RESEARCH_CORROBORATION', 'wikipedia')
    payload = {'sources': sources, 'claims': claims, 'support': support, 'mode': mode, 'directory': str(directory)}
    environment = os.environ.copy()
    environment['PYTHONPATH'] = str(Path(__file__).resolve().parents[2]) + os.pathsep + environment.get('PYTHONPATH', '')
    result = subprocess.run([sys.executable, '-m', 'alfred_research.local.verify'], input=json.dumps(payload),
                            text=True, capture_output=True, env=environment, timeout=timeout)
    if result.returncode:
        raise RuntimeError('Corroboration stage failed; no verification result accepted. ' + result.stdout[:400])
    value = check(json.loads(result.stdout), claims)
    if value.pid == os.getpid():
        raise ValueError('Corroboration must run in a separate process')
    return value


if __name__ == '__main__':
    try:
        print(json.dumps(corroborate(json.load(sys.stdin)).to_dict(), ensure_ascii=False))
    except Exception as error:
        print(json.dumps({'error': type(error).__name__ + ': ' + str(error)[:300]}))
        sys.exit(1)
