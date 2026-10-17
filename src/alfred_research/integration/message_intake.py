"""Decide whether an owner message is a Research request. Pure; no network or I/O.

Supported links and attachments start Research automatically. Ordinary
conversation (scheduling, operations, development, forwarding) passes through
untouched. Only the owner's own words shape the objective; fetched source text
is never consulted here, so source content cannot steer routing.
"""
from dataclasses import dataclass, field
from pathlib import Path
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from ..local.platforms import parse_github
from ..local.sources import handler_for_snapshot, handler_for_url

MAX_SOURCES = 4
URL = re.compile(r'https?://[^\s<>"\'`]+', re.I)
TRAILING = '.,;:!?)]}>\'"’”'
TRACKING = re.compile(r'^(utm_.*|fbclid|gclid|dclid|mc_cid|mc_eid|igsh|igshid|si|ref_src|ref_url|_hsenc|_hsmi|spm)$', re.I)
NON_RESEARCH_HOSTS = ('zoom.us', 'meet.google.com', 'teams.microsoft.com', 'teams.live.com', 'calendly.com',
                      'calendar.google.com', 'maps.google.com', 'maps.app.goo.gl', 'linear.app', 'atlassian.net',
                      'figma.com', 'docusign.net', 'venmo.com', 'paypal.com', 'cash.app')
RESEARCH_CUE = re.compile(
    r"\b(look(ing)? into|research|investigate|analy[sz]e|analysis|summari[sz]e|summary|fact[- ]?check|verify|"
    r"is (this|it|that) (true|legit|accurate|real|right)|what do you (think|make) of|thoughts on|check (this|it|that) out|"
    r"read (this|it)|watch (this|it)|dig into|break (this|it|that) down|tl;?dr|explain (this|it|that)|deep dive|"
    r"learn (from|about)|worth (reading|watching))\b", re.I)
OPERATIONAL_CUE = re.compile(
    r"\b(schedul\w*|reschedul\w*|meeting|calendar|invite|remind\w*|appointment|book (a|the|me)|deploy\w*|merge|"
    r"rebase|commit|push|pull request|fix|debug|build|install|restart|ticket|bug|send (this|it|that)( to)?|"
    r"forward|email (this|it)|text (this|it)|share (this|it) with|pay|invoice|order|buy|purchase|sign (this|it))\b", re.I)
RERUN_CUE = re.compile(r"\b(again|re-?research|re-?run|redo|refresh|re-?check|one more time)\b", re.I)
COMMAND = re.compile(r'^\s*(?:/research|research:|research|look into|investigate)\s+(.{3,})$', re.I | re.S)
GREETING = re.compile(r'^\s*((hey|hi|hello|ok|okay|yo)[\s,]+)?(alfred)?[\s,:;.!-]*', re.I)
DEFAULT_OBJECTIVE = {
    'youtube': 'Analyze this video\'s transcript: identify its main claims, check what the evidence supports, and summarize findings and implications.',
    'instagram': 'Analyze this post\'s caption: identify its claims, check what the evidence supports, and summarize findings.',
    'github': 'Analyze this repository: purpose, architecture, notable techniques, dependencies and risks, citing files.',
}
GENERIC_OBJECTIVE = 'Analyze this source: identify its main claims, check what the source supports, and summarize findings and implications.'


@dataclass
class ResearchIntent:
    sources: list
    objective: str
    question_only: bool = False
    rerun: bool = False
    notes: list = field(default_factory=list)


def normalize_url(raw):
    """Canonical public HTTPS locator, or None when not a usable link."""
    url = raw.rstrip(TRAILING)
    if url.count('(') < url.count(')'):
        url = url.rstrip(')')
    try:
        parts = urlsplit(url)
        host = (parts.hostname or '').lower().rstrip('.')
        port = parts.port
    except ValueError:
        return None
    if not host or '.' not in host or parts.username or parts.password or port not in (None, 80, 443):
        return None
    if re.fullmatch(r'[\d.]+|\[?[0-9a-f:]+\]?', host) or host == 'localhost' or host.endswith(('.local', '.internal', '.localhost')):
        return None
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not TRACKING.match(k)])
    return urlunsplit(('https', host, parts.path or '/', query, ''))


def research_link(url):
    host = urlsplit(url).hostname
    if any(host == h or host.endswith('.' + h) for h in NON_RESEARCH_HOSTS):
        return False
    if host in ('github.com', 'www.github.com') and parse_github(url) is None:
        return False  # pull requests, issues, actions: development workflow, not research
    return True


def objective_from(text, links, kind):
    remainder = text
    for link in links:
        remainder = remainder.replace(link, ' ')
    remainder = ' '.join(GREETING.sub('', remainder, count=1).split())
    cue_only = RESEARCH_CUE.sub('', remainder)
    if len(re.findall(r'[A-Za-z]{2,}', cue_only)) < 3 or len(remainder.split()) < 4:
        return DEFAULT_OBJECTIVE.get(kind, GENERIC_OBJECTIVE)
    return remainder[:2000]


def detect(text, attachments=(), attachment_roots=()):
    """Return a ResearchIntent, or None to leave the message to normal chat.

    ``attachments`` are host-supplied dicts with a local ``path``; they are
    accepted only beneath an explicitly configured ``attachment_roots`` entry.
    """
    if not isinstance(text, str):
        text = ''
    text = text[:20000]
    notes, sources, raw_links = [], [], []
    for match in URL.finditer(text):
        raw_links.append(match.group(0))
        url = normalize_url(match.group(0))
        if url is None:
            notes.append('Ignored unusable link: ' + match.group(0)[:200])
        elif not research_link(url):
            notes.append('Not treated as research material: ' + url)
        elif url not in sources:
            sources.append(url)
    roots = [Path(r).expanduser().resolve() for r in attachment_roots]
    for attachment in attachments or ():
        path = attachment.get('path') if isinstance(attachment, dict) else None
        name = (attachment.get('filename') or path or '') if isinstance(attachment, dict) else ''
        if not path:
            continue
        try:
            resolved = Path(path).expanduser().resolve(strict=True)
        except (OSError, RuntimeError):
            notes.append('Attachment unavailable: ' + str(name)[:200])
            continue
        if not any(resolved.is_relative_to(root) for root in roots) or not resolved.is_file():
            notes.append('Attachment outside approved attachment directories ignored: ' + str(name)[:200])
            continue
        if handler_for_snapshot('source' + resolved.suffix.lower()) is None:
            notes.append('Unsupported attachment type ignored: ' + str(name)[:200])
            continue
        if str(resolved) not in sources:
            sources.append(str(resolved))
    explicit = bool(RESEARCH_CUE.search(text))
    operational = bool(OPERATIONAL_CUE.search(URL.sub(' ', text)))
    if not sources:
        command = COMMAND.match(GREETING.sub('', text, count=1)) if not raw_links else None
        if command and not operational and not attachments:
            return ResearchIntent([], ' '.join(command.group(1).split())[:2000], question_only=True,
                                  rerun=bool(RERUN_CUE.search(text)), notes=notes)
        return None
    if operational and not explicit:
        return None
    if len(sources) > MAX_SOURCES:
        notes.append('Only the first ' + str(MAX_SOURCES) + ' sources were submitted; ' +
                     str(len(sources) - MAX_SOURCES) + ' ignored.')
        sources = sources[:MAX_SOURCES]
    first = sources[0]
    handler = handler_for_url(first) if first.startswith('https://') else handler_for_snapshot('source' + Path(first).suffix.lower())
    kind = handler.kind if handler else 'article'
    return ResearchIntent(sources, objective_from(text, raw_links, kind), rerun=bool(RERUN_CUE.search(text)), notes=notes)
