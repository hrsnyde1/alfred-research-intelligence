"""Non-executing fixture adapters. All source instructions remain evidence data."""
from html.parser import HTMLParser
from hashlib import sha256
import json
import re
from datetime import datetime

from ..contracts import require, ContractError
from .contracts import SourceEvidence, FileRecord, Capability, safe_path
from .policy import ExtractionLimit


class Collector:
    def __init__(self, environment, fixture, meter):
        self.environment, self.fixture, self.meter = environment, fixture, meter
        self.evidence, self.files, self.capabilities = [], [], []
        self.flags, self.limitations = [], []
        self.metadata, self.ambiguous_metadata = {}, set()

    def observe_metadata(self, key, value):
        if not value or len(value) > 2048:
            return
        if key == 'published_at':
            try:
                parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
                if parsed.tzinfo is None:
                    raise ValueError('timezone missing')
            except ValueError:
                self.limit('invalid HTML publication date omitted')
                return
        if key in self.ambiguous_metadata:
            return
        if key in self.metadata and self.metadata[key] != value:
            del self.metadata[key]
            self.ambiguous_metadata.add(key)
            self.limit('ambiguous HTML metadata omitted:' + key)
        else:
            self.metadata[key] = value

    def flag(self, flag):
        if flag not in self.flags:
            self.flags.append(flag)

    def limit(self, message):
        if message not in self.limitations:
            self.limitations.append(message)

    def add(self, file, text, location):
        # Never obey instructions. Detection is advisory, not a sanitizer/security proof.
        if re.search(r'ignore.{0,40}(instructions|previous)|system\s*prompt|exfiltrat|override.{0,30}(policy|rules)',
                     text, re.I):
            self.flag('prompt_injection_candidate:' + file.path)
        for offset in range(0, len(text), 4000):
            self.meter.check()
            room = self.meter.limits.characters - self.meter.characters
            if room <= 0 or self.meter.segments >= self.meter.limits.segments:
                self.limit('extraction output limit reached')
                return
            chunk = text[offset:offset + min(4000, room)]
            if not chunk.strip():
                continue
            evidence_id = 'e-' + sha256((file.path + '\0' + location + '\0' + str(offset)).encode()).hexdigest()[:24]
            self.evidence.append(SourceEvidence(environment=self.environment, evidence_id=evidence_id,
                location=file.path + ':' + location + ':char' + str(offset), text=chunk,
                file_digest=file.digest, origin=self.fixture.origin))
            self.meter.characters += len(chunk)
            self.meter.segments += 1
            if len(chunk) < min(4000, len(text) - offset):
                self.limit('extraction output limit reached')
                return

    def inventory(self, file):
        self.meter.check()
        if not safe_path(file.path):
            self.flag('unsafe_path:' + file.path)
            self.limit('unsafe file records omitted')
            return False
        if file.symlink:
            self.flag('symlink:' + file.path)
            self.limit('symlink contents not inspected')
            return False
        self.files.append(FileRecord(path=file.path, content_digest=file.digest, size=len(file.data)))
        return True

    def decode(self, file):
        self.meter.check(max(1, len(file.data) // 64))
        try:
            value = file.data.decode('utf-8')
            if '\0' in value:
                self.limit('binary content not extracted:' + file.path)
                return None
            return value
        except UnicodeDecodeError:
            self.limit('non-UTF8 content not extracted:' + file.path)
            return None

    def lines(self, file, value):
        for number, line in enumerate(value.splitlines(), 1):
            self.meter.check()
            if line.strip():
                self.add(file, line, 'line' + str(number))
            if self.meter.characters >= self.meter.limits.characters or self.meter.segments >= self.meter.limits.segments:
                self.limit('extraction output limit reached')
                break


class GitHubAdapter:
    def extract(self, fixture, collector):
        if fixture.revision and re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', fixture.revision) is None:
            raise ContractError('repository revision must be a full lowercase hex commit')
        if not fixture.revision:
            collector.limit('repository commit unavailable; snapshot digest is the only pin')
        licenses = []
        for file in sorted(fixture.files, key=lambda f: f.path):
            if not collector.inventory(file):
                continue
            name = file.path.rsplit('/', 1)[-1]
            lower = name.lower()
            if lower.startswith(('license', 'copying')):
                licenses.append(file.path)
            if name == '.gitmodules':
                collector.flag('submodule_dependencies:' + file.path)
            script = file.executable or lower.endswith(('.py', '.sh', '.js', '.mjs', '.ps1', '.bat'))
            if script or '/hooks/' in '/' + file.path:
                collector.flag('executable_or_hook:' + file.path)
            relevant = (lower.startswith(('readme', 'license', 'copying')) or name == 'SKILL.md' or
                        lower.endswith(('.json', '.yaml', '.yml', '.toml', '.txt')) or script or name == '.gitmodules')
            if not relevant:
                collector.limit('unrecognized repository file not extracted:' + file.path)
                continue
            value = collector.decode(file)
            if value is None:
                continue
            if re.search(r'https?://|curl\b|wget\b|requests\.|fetch\(', value, re.I):
                collector.flag('network_requirement_candidate:' + file.path)
            if re.search(r'api[_ -]?key|secret|token|password|credential|os\.environ|process\.env', value, re.I):
                collector.flag('secret_requirement_candidate:' + file.path)
            if lower in ('requirements.txt', 'package.json', 'pyproject.toml', 'pipfile'):
                collector.flag('declared_dependencies:' + file.path)
                collector.flag('runtime_compatibility_unverified:' + file.path)
            capability_manifest = False
            if lower.endswith('.json'):
                try:
                    def unique(pairs):
                        obj = {}
                        for key, item in pairs:
                            require(key not in obj, 'duplicate manifest key')
                            obj[key] = item
                        return obj
                    manifest = json.loads(value, object_pairs_hook=unique,
                                          parse_constant=lambda v: require(False, 'invalid constant'))
                    require(type(manifest) is dict, 'manifest object required')
                    capability_manifest = (lower in ('skill.json', 'plugin.json') and
                                           type(manifest.get('name')) is str and bool(manifest['name'].strip()))
                    if lower in ('skill.json', 'plugin.json'):
                        require(capability_manifest, 'manifest name required')
                    if manifest.get('scripts') or manifest.get('hooks'):
                        collector.flag('executable_or_hook:' + file.path)
                    if manifest.get('engines') or manifest.get('runtime'):
                        collector.flag('runtime_compatibility_unverified:' + file.path)
                        if re.search(r'unknown|unsupported|999', json.dumps(manifest), re.I):
                            collector.flag('unsupported_runtime_candidate:' + file.path)
                except (ValueError, RecursionError) as exc:
                    collector.flag('malformed_manifest:' + file.path)
                    collector.limit('JSON manifest not validated:' + file.path)
            if lower.endswith(('.yaml', '.yml')):
                # No YAML dependency: retain exact lines, never evaluate tags/anchors.
                collector.flag('yaml_semantics_unvalidated:' + file.path)
                collector.limit('YAML retained as text; structure not parsed:' + file.path)
            start = len(collector.evidence)
            collector.lines(file, value)
            if name == 'SKILL.md' or capability_manifest:
                refs = tuple(e.evidence_id for e in collector.evidence[start:])
                if refs:
                    collector.capabilities.append(Capability(path=file.path, evidence_ids=refs))
                else:
                    collector.limit('capability text unavailable:' + file.path)
        if not licenses:
            collector.flag('missing_license')
        elif len(licenses) > 1:
            collector.flag('ambiguous_license')
        else:
            collector.flag('license_terms_require_review:' + licenses[0])


class _HTMLText(HTMLParser):
    def __init__(self, file, collector):
        super().__init__(convert_charrefs=True)
        self.file, self.collector = file, collector
        self.hidden = []

    def handle_starttag(self, tag, attrs):
        self.collector.meter.check()
        if tag in ('script', 'style', 'template', 'noscript'):
            self.hidden.append(tag)
        if not self.hidden:
            values = dict(attrs)
            if tag == 'meta':
                key = values.get('name', values.get('property', ''))
                fields = {'author': 'author', 'publisher': 'publisher', 'og:site_name': 'publisher',
                          'article:published_time': 'published_at', 'date': 'published_at', 'og:title': 'title'}
                if key in fields:
                    self.collector.observe_metadata(fields[key], values.get('content', ''))
            if tag == 'link' and 'canonical' in (values.get('rel') or '').split():
                self.collector.observe_metadata('canonical_url', values.get('href', ''))

    def handle_endtag(self, tag):
        self.collector.meter.check()
        if self.hidden and self.hidden[-1] == tag:
            self.hidden.pop()

    def handle_data(self, data):
        self.collector.meter.check()
        if not self.hidden and data.strip():
            line, column = self.getpos()
            self.collector.add(self.file, data.strip(), f'html-line{line}-column{column}')


class WebsiteAdapter:
    def extract(self, fixture, collector):
        for file in sorted(fixture.files, key=lambda f: f.path):
            if not collector.inventory(file):
                continue
            if not file.path.lower().endswith(('.html', '.htm')):
                collector.limit('unsupported website fixture format:' + file.path)
                continue
            value = collector.decode(file)
            if value is not None:
                parser = _HTMLText(file, collector)
                # Chunk feed bounds callbacks and deadline checks.
                for start in range(0, len(value), 4096):
                    collector.meter.check()
                    parser.feed(value[start:start + 4096])
                parser.close()
        collector.limit('ordinary HTML text only; no JS/rendering or linked resource fetching')


class DocumentAdapter:
    def extract(self, fixture, collector):
        for file in sorted(fixture.files, key=lambda f: f.path):
            if not collector.inventory(file):
                continue
            if not file.path.lower().endswith(('.txt', '.md', '.csv', '.vtt', '.srt')):
                collector.limit('unsupported document format:' + file.path)
                continue
            value = collector.decode(file)
            if value is not None:
                collector.lines(file, value)


class PDFAdapter:
    """Explicit unsupported parser boundary; no PDF decoding or fake page citations."""
    def extract(self, fixture, collector):
        for file in fixture.files:
            collector.inventory(file)
        collector.limit('PDF parser not configured/verified; no pages extracted')
        return 'UNSUPPORTED'


class MediaAdapter:
    names = ()
    def extract(self, fixture, collector):
        for file in sorted(fixture.files, key=lambda f: f.path):
            if not collector.inventory(file):
                continue
            if file.path not in self.names:
                collector.limit('media bytes/unsupported fixture not decoded:' + file.path)
                continue
            value = collector.decode(file)
            if value is not None:
                collector.lines(file, value)
        collector.limit('fixture/user-supplied text only; no live platform retrieval or media viewing')
        if not collector.evidence:
            collector.limit('metadata-only or unavailable transcript; no content invented')


class YouTubeAdapter(MediaAdapter):
    names = ('transcript.txt', 'captions.vtt', 'captions.srt')


class InstagramAdapter(MediaAdapter):
    names = ('post.txt', 'transcript.txt', 'captions.vtt')


class TikTokAdapter(MediaAdapter):
    names = ('post.txt', 'transcript.txt', 'captions.vtt')


class XAdapter(MediaAdapter):
    names = ('post.txt', 'thread.txt')
