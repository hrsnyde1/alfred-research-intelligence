"""Platform handlers: GitHub repositories, YouTube captions, Instagram captions.

Acquisition is read-only public HTTPS without credentials. Repository code is
never executed, installed or merged. Video content is never inferred from a
title: YouTube requires an accessible caption track and Instagram yields only
the caption text its public page exposes.
"""
import json
import re
from html.parser import HTMLParser
from pathlib import PurePosixPath
from urllib.parse import parse_qs, quote, urlencode, urlsplit

from . import sources
from .sources import Extraction, SourceHandler, UnsupportedSource, sha, text_evidence


def bundle(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, indent=1).encode()


def load_bundle(data, schema):
    try:
        value = json.loads(data)
    except ValueError:
        raise UnsupportedSource('Malformed platform snapshot')
    if not isinstance(value, dict) or value.get('schema') != schema:
        raise UnsupportedSource('Unexpected platform snapshot schema')
    return value


def host_of(url):
    return (urlsplit(url).hostname or '').lower()


# ---------------------------------------------------------------- GitHub

GITHUB_RESERVED = {'about', 'apps', 'collections', 'contact', 'customer-stories', 'enterprise', 'explore',
                   'features', 'issues', 'login', 'marketplace', 'new', 'notifications', 'orgs', 'organizations',
                   'pricing', 'pulls', 'search', 'security', 'settings', 'site', 'sponsors', 'topics', 'trending'}
NAME = re.compile(r'[A-Za-z0-9_.-]{1,100}')
DOC_NAMES = re.compile(r'(readme|license|licence|copying|contributing|changelog|security|architecture|design)(\.[a-z0-9]+)?$', re.I)
MANIFESTS = {'package.json', 'pyproject.toml', 'setup.py', 'setup.cfg', 'requirements.txt', 'pipfile', 'cargo.toml',
             'go.mod', 'pom.xml', 'build.gradle', 'build.gradle.kts', 'gemfile', 'composer.json', 'dockerfile',
             'docker-compose.yml', 'docker-compose.yaml', 'makefile', 'cmakelists.txt', 'deno.json', 'mix.exs'}
CODE = {'.py', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.go', '.rs', '.java', '.kt', '.rb', '.php', '.c',
        '.h', '.cc', '.cpp', '.hpp', '.cs', '.swift', '.scala', '.sh', '.lua', '.ex', '.exs', '.zig', '.dart'}
ENTRY = {'main', 'app', 'index', 'server', 'cli', '__main__', '__init__', 'lib', 'mod', 'core', 'api'}
VENDORED = {'node_modules', 'vendor', 'dist', 'build', 'third_party', 'third-party', '.git', 'site-packages',
            'target', 'out', 'coverage', '__pycache__'}
MAX_FILES, MAX_FILE_BYTES, MAX_TOTAL_BYTES = 30, 200_000, 1_500_000


def parse_github(url):
    parsed = urlsplit(url)
    if host_of(url) not in ('github.com', 'www.github.com'):
        return None
    parts = [p for p in parsed.path.split('/') if p]
    if len(parts) < 2 or parts[0].lower() in GITHUB_RESERVED:
        return None
    owner, repo = parts[0], parts[1][:-4] if parts[1].endswith('.git') else parts[1]
    if not (NAME.fullmatch(owner) and NAME.fullmatch(repo)):
        return None
    ref, focus = None, None
    if len(parts) >= 4 and parts[2] in ('tree', 'blob', 'commit'):
        ref = parts[3]
        if parts[2] == 'blob' and len(parts) > 4:
            focus = '/'.join(parts[4:])
    elif len(parts) > 2:
        return None  # issues, pulls, wikis etc. are not repository snapshots
    return owner, repo, ref, focus


def github_api(path, accept='application/vnd.github+json', max_bytes=sources.MAX_BYTES):
    try:
        data, _, _ = sources.http_get('https://api.github.com' + path, max_bytes=max_bytes,
                                      headers={'Accept': accept, 'X-GitHub-Api-Version': '2022-11-28'})
    except ValueError as error:
        message = str(error)
        if 'status 404' in message:
            raise UnsupportedSource('GitHub repository or revision not found, or private (no credentials are used).')
        if 'status 403' in message or 'status 429' in message:
            raise RuntimeError('GitHub API refused the request (unauthenticated rate limit or access denied); retry later.')
        raise
    return data


def priority(path):
    pure = PurePosixPath(path)
    name, depth = pure.name.lower(), len(pure.parts) - 1
    if depth == 0 and name.startswith('readme'):
        return (0, path)
    if depth == 0 and DOC_NAMES.match(name):
        return (1, path)
    if depth == 0 and name in MANIFESTS:
        return (2, path)
    if name.startswith('readme') or (pure.parts[0].lower() == 'docs' and depth <= 2 and pure.suffix.lower() == '.md'):
        return (3 + depth, path)
    if pure.suffix.lower() in CODE:
        tests = any(p.lower() in ('test', 'tests', 'spec', '__tests__', 'examples') for p in pure.parts[:-1])
        return (5 + depth + (3 if tests else 0) - (1 if pure.stem.lower() in ENTRY else 0), path)
    if name in MANIFESTS or (path.startswith('.github/workflows/') and pure.suffix in ('.yml', '.yaml')):
        return (6 + depth, path)
    return None


class GitHubHandler(SourceHandler):
    name, kind, snapshot_names = 'github', 'github', ('github.json',)

    def claims_url(self, url):
        return parse_github(url) is not None

    def acquire_url(self, url):
        owner, repo, ref, focus = parse_github(url)
        base = '/repos/' + owner + '/' + repo
        meta = json.loads(github_api(base))
        if not isinstance(meta, dict) or 'full_name' not in meta:
            raise UnsupportedSource('GitHub did not return repository metadata.')
        requested = ref or meta.get('default_branch') or 'HEAD'
        revision = github_api(base + '/commits/' + quote(requested, safe=''), accept='application/vnd.github.sha').decode().strip()
        if not re.fullmatch(r'[0-9a-f]{40}', revision):
            raise UnsupportedSource('Could not pin the repository to a commit; no findings generated.')
        tree = json.loads(github_api(base + '/git/trees/' + revision + '?recursive=1', max_bytes=10_000_000))
        languages = json.loads(github_api(base + '/languages'))
        blobs = [e for e in tree.get('tree', []) if e.get('type') == 'blob' and isinstance(e.get('path'), str)]
        candidates = []
        for entry in blobs:
            parts = entry['path'].split('/')
            if any(p.lower() in VENDORED for p in parts[:-1]) or entry['path'].endswith(('.min.js', '.map', '.lock')):
                continue
            rank = (-1, entry['path']) if focus and entry['path'] == focus else priority(entry['path'])
            if rank is not None:
                candidates.append((rank, entry))
        files, skipped, total = [], [], 0
        for _, entry in sorted(candidates, key=lambda c: c[0]):
            size = entry.get('size') or 0
            if len(files) >= MAX_FILES or total + size > MAX_TOTAL_BYTES:
                skipped.append(entry['path'] + ' (snapshot budget)')
                continue
            if size > MAX_FILE_BYTES:
                skipped.append(entry['path'] + ' (larger than 200 KB)')
                continue
            raw_url = ('https://raw.githubusercontent.com/' + owner + '/' + repo + '/' + revision + '/' +
                       quote(entry['path']))
            try:
                data, _, _ = sources.http_get(raw_url, max_bytes=MAX_FILE_BYTES)
                text = data.decode('utf-8')
                if '\0' in text:
                    raise UnicodeDecodeError('utf-8', b'', 0, 1, 'binary')
            except UnicodeDecodeError:
                skipped.append(entry['path'] + ' (binary or non-UTF-8)')
                continue
            except (ValueError, OSError) as error:
                skipped.append(entry['path'] + ' (fetch failed: ' + str(error)[:80] + ')')
                continue
            total += len(data)
            files.append({'path': entry['path'], 'mode': entry.get('mode'), 'bytes': len(data),
                          'sha256': sha(data), 'text': text})
        license_info = meta.get('license') or {}
        snapshot = {
            'schema': 'research.github-snapshot/1', 'url': url, 'requested_ref': ref, 'revision': revision,
            'repository': {'full_name': meta.get('full_name'), 'html_url': meta.get('html_url'),
                           'description': meta.get('description'), 'default_branch': meta.get('default_branch'),
                           'language': meta.get('language'), 'license': license_info.get('spdx_id'),
                           'topics': meta.get('topics') or [], 'stars': meta.get('stargazers_count'),
                           'forks': meta.get('forks_count'), 'archived': meta.get('archived'),
                           'pushed_at': meta.get('pushed_at'), 'created_at': meta.get('created_at')},
            'languages': languages if isinstance(languages, dict) else {},
            'tree': {'paths': [e['path'] for e in blobs][:20000], 'truncated': bool(tree.get('truncated')),
                     'file_count': len(blobs)},
            'files': files, 'skipped': skipped[:500],
        }
        return bundle(snapshot), 'github.json', {
            'origin': 'live_https', 'requested_url': url, 'final_url': meta.get('html_url') or url,
            'api': 'api.github.com (unauthenticated, read-only)', 'revision': revision,
            'content_type': 'application/json'}

    def extract(self, data, filename):
        snapshot = load_bundle(data, 'research.github-snapshot/1')
        repo, revision = snapshot['repository'], snapshot['revision']
        tree = snapshot['tree']
        lines = ['Repository: ' + str(repo.get('full_name')), 'Revision: ' + revision,
                 'Description: ' + str(repo.get('description') or '(none)'),
                 'Default branch: ' + str(repo.get('default_branch')),
                 'Primary language: ' + str(repo.get('language') or 'unknown'),
                 'Languages by bytes: ' + ', '.join(k + ' ' + str(v) for k, v in snapshot['languages'].items()),
                 'License (GitHub-detected): ' + str(repo.get('license') or 'none detected'),
                 'Topics: ' + (', '.join(repo.get('topics') or []) or 'none'),
                 'Stars at acquisition: ' + str(repo.get('stars')) + '; forks: ' + str(repo.get('forks')),
                 'Archived: ' + str(repo.get('archived')) + '; last push: ' + str(repo.get('pushed_at'))]
        segments = [('github-metadata', '\n'.join(lines))]
        top = {}
        for path in tree['paths']:
            head = path.split('/')[0] + ('/' if '/' in path else '')
            top[head] = top.get(head, 0) + 1
        layout = ['Repository layout at ' + revision[:12] + ' (' + str(tree['file_count']) + ' files):']
        layout += [name + (' (' + str(count) + ' files)' if name.endswith('/') else '')
                   for name, count in sorted(top.items())[:200]]
        segments.append(('tree', '\n'.join(layout)))
        flags = []
        for file in snapshot['files']:
            text_lines = file['text'].splitlines()
            start = 0
            while start < len(text_lines):
                stop, size = start, 0
                while stop < len(text_lines) and stop - start < 80 and size + len(text_lines[stop]) < 3500:
                    size += len(text_lines[stop]) + 1
                    stop += 1
                stop = max(stop, start + 1)
                segments.append((file['path'] + '#L' + str(start + 1) + '-L' + str(stop), '\n'.join(text_lines[start:stop])))
                start = stop
            name = PurePosixPath(file['path']).name.lower()
            if name in MANIFESTS:
                flags.append('declared_dependencies:' + file['path'])
            if file.get('mode') == '100755':
                flags.append('executable_file:' + file['path'])
        evidence, limitations, more = text_evidence('github', segments)
        limitations.insert(0, 'Read-only snapshot of ' + str(len(snapshot['files'])) + ' of ' + str(tree['file_count']) +
                           ' files at commit ' + revision + '. Code was not executed, dependencies were not installed, '
                           'and nothing was merged; behavior claims rest on reading source text only.')
        if tree['truncated']:
            limitations.append('GitHub truncated the file tree; the layout summary is incomplete.')
        if snapshot['skipped']:
            limitations.append(str(len(snapshot['skipped'])) + ' relevant files were not read (budget, size or binary), e.g. ' +
                               ', '.join(snapshot['skipped'][:5]) + '.')
        if not any(PurePosixPath(f['path']).name.lower().startswith(('license', 'licence', 'copying')) for f in snapshot['files']):
            flags.append('license_file_not_read')
        metadata = {'title': repo.get('full_name'), 'revision': revision, 'html_url': repo.get('html_url'),
                    'license': repo.get('license'), 'files_read': len(snapshot['files']), 'files_total': tree['file_count']}
        return Extraction(evidence, limitations, flags + more, metadata, 'repository_files')


# ---------------------------------------------------------------- YouTube

VIDEO_ID = re.compile(r'[A-Za-z0-9_-]{11}')
YOUTUBE_HOSTS = ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'music.youtube.com', 'youtu.be', 'www.youtu.be')


def youtube_id(url):
    parsed = urlsplit(url)
    host, parts = host_of(url), [p for p in parsed.path.split('/') if p]
    candidate = None
    if host in ('youtu.be', 'www.youtu.be'):
        candidate = parts[0] if parts else None
    elif parts[:1] == ['watch']:
        candidate = (parse_qs(parsed.query).get('v') or [None])[0]
    elif len(parts) >= 2 and parts[0] in ('shorts', 'embed', 'live', 'v'):
        candidate = parts[1]
    return candidate if candidate and VIDEO_ID.fullmatch(candidate) else None


def player_response(page):
    text = page.decode('utf-8', 'replace')
    match = re.search(r'ytInitialPlayerResponse\s*=\s*\{', text)
    if not match:
        return None
    try:
        value, _ = json.JSONDecoder().raw_decode(text, match.end() - 1)
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


def choose_track(tracks):
    def rank(track):
        language = (track.get('languageCode') or '').lower()
        return (track.get('kind') == 'asr', not language.startswith('en'))
    usable = [t for t in tracks if isinstance(t, dict) and isinstance(t.get('baseUrl'), str)]
    return sorted(usable, key=rank)[0] if usable else None


def clock(ms):
    seconds = int(ms // 1000)
    return '%02d:%02d:%02d' % (seconds // 3600, seconds // 60 % 60, seconds % 60)


class YouTubeHandler(SourceHandler):
    name, kind, snapshot_names = 'youtube', 'youtube', ('youtube.json',)

    def claims_url(self, url):
        return host_of(url) in YOUTUBE_HOSTS

    def acquire_url(self, url):
        video = youtube_id(url)
        if video is None:
            raise UnsupportedSource('Not a recognizable YouTube video URL. Submit a video link, or a genuine transcript '
                                    '(.vtt/.srt/.txt); video content is never inferred from metadata.')
        watch = 'https://www.youtube.com/watch?v=' + video
        metadata = {'video_id': video, 'url': watch}
        try:
            oembed, _, _ = sources.http_get('https://www.youtube.com/oembed?' + urlencode({'url': watch, 'format': 'json'}))
            info = json.loads(oembed)
            metadata.update({'title': info.get('title'), 'channel': info.get('author_name'),
                             'channel_url': info.get('author_url')})
        except (ValueError, OSError):
            pass
        page, _, provenance = sources.http_get(watch + '&hl=en', max_bytes=6_000_000,
                                               headers={'Accept-Language': 'en-US,en;q=0.8'})
        if host_of(provenance['final_url']).startswith('consent.'):
            raise UnsupportedSource('YouTube required a consent page; transcript not accessible. Submit a transcript file.', metadata)
        player = player_response(page) or {}
        details = player.get('videoDetails') or {}
        micro = (player.get('microformat') or {}).get('playerMicroformatRenderer') or {}
        metadata.update({k: v for k, v in {
            'title': details.get('title') or metadata.get('title'), 'channel': details.get('author') or metadata.get('channel'),
            'duration_seconds': int(details['lengthSeconds']) if str(details.get('lengthSeconds', '')).isdigit() else None,
            'published_at': micro.get('publishDate'), 'is_live': details.get('isLiveContent')}.items() if v is not None})
        status = (player.get('playabilityStatus') or {}).get('status')
        if status and status != 'OK':
            raise UnsupportedSource('YouTube video not playable without sign-in (' + status + '); transcript not accessible. '
                                    'Submit a transcript file. No findings were inferred from the title.', metadata)
        tracks = (((player.get('captions') or {}).get('playerCaptionsTracklistRenderer') or {}).get('captionTracks') or [])
        track = choose_track(tracks)
        if track is None:
            raise UnsupportedSource('No accessible caption track for this YouTube video; transcript not accessible. '
                                    'Submit a transcript file. No findings were inferred from the title.', metadata)
        caption_url = track['baseUrl']
        if host_of(caption_url) not in YOUTUBE_HOSTS:
            raise UnsupportedSource('Unexpected caption host; transcript not acquired.', metadata)
        raw, _, _ = sources.http_get(caption_url + '&fmt=json3', max_bytes=5_000_000)
        segments = []
        try:
            for event in json.loads(raw).get('events', []) if raw.strip() else []:
                text = ''.join(s.get('utf8', '') for s in event.get('segs') or []).replace('\n', ' ').strip()
                if text and isinstance(event.get('tStartMs'), int):
                    segments.append({'start_ms': event['tStartMs'], 'duration_ms': event.get('dDurationMs') or 0, 'text': text})
        except (ValueError, AttributeError):
            segments = []
        if not segments:
            raise UnsupportedSource('YouTube listed captions but returned no caption text to an unauthenticated client; '
                                    'transcript not accessible. Submit a transcript file.', metadata)
        snapshot = {'schema': 'research.youtube-snapshot/1', 'metadata': metadata,
                    'description': details.get('shortDescription') or '',
                    'caption_track': {'language': track.get('languageCode'), 'auto_generated': track.get('kind') == 'asr',
                                      'name': ((track.get('name') or {}).get('simpleText') or
                                               ''.join(r.get('text', '') for r in (track.get('name') or {}).get('runs', [])))},
                    'watch_page_sha256': sha(page), 'caption_response_sha256': sha(raw), 'segments': segments}
        return bundle(snapshot), 'youtube.json', {**provenance, 'requested_url': url, 'caption_source': 'youtube timedtext',
                                                  'content_type': 'application/json'}

    def extract(self, data, filename):
        snapshot = load_bundle(data, 'research.youtube-snapshot/1')
        track = snapshot['caption_track']
        windows, current, start = [], [], None
        for segment in snapshot['segments']:
            if start is None:
                start = segment['start_ms']
            current.append(segment['text'])
            if segment['start_ms'] - start >= 45000 or sum(len(x) for x in current) > 1500:
                windows.append((start, segment['start_ms'] + segment['duration_ms'], ' '.join(current)))
                current, start = [], None
        if current:
            last = snapshot['segments'][-1]
            windows.append((start, last['start_ms'] + last['duration_ms'], ' '.join(current)))
        segments = [('t=' + clock(a) + '-' + clock(b), text) for a, b, text in windows]
        if snapshot['description'].strip():
            segments.append(('creator-description', 'Creator-written description (not spoken content): ' + snapshot['description']))
        evidence, limitations, flags = text_evidence('youtube', segments)
        kind = 'auto-generated' if track['auto_generated'] else 'creator-provided'
        limitations.insert(0, 'Evidence is the ' + kind + ' caption track (' + str(track['language']) + ') and the creator '
                              'description; the video itself was not watched, so visuals and on-screen text are not covered.')
        if track['auto_generated']:
            limitations.append('Auto-generated captions can misrecognize words, names and numbers; verify quotes against the video.')
        metadata = {**snapshot['metadata'], 'caption_language': track['language'], 'captions': kind}
        return Extraction(evidence, limitations, flags, metadata,
                          'transcript_auto_generated' if track['auto_generated'] else 'transcript_creator_captions')


# ---------------------------------------------------------------- Instagram

INSTAGRAM_PATH = re.compile(r'/(?:[A-Za-z0-9_.]+/)?(reel|reels|p|tv)/([A-Za-z0-9_-]{5,64})/?$')
LOGIN_WALL = re.compile(r'log ?in|sign ?up|create an account', re.I)


class _Meta(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.values = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            values = dict(attrs)
            key = (values.get('property') or values.get('name') or '').lower()
            if key and values.get('content') and key not in self.values:
                self.values[key] = values['content']


class InstagramHandler(SourceHandler):
    name, kind, snapshot_names = 'instagram', 'instagram', ('instagram.html',)

    def claims_url(self, url):
        return host_of(url) in ('instagram.com', 'www.instagram.com', 'm.instagram.com')

    def acquire_url(self, url):
        match = INSTAGRAM_PATH.search(urlsplit(url).path)
        if not match:
            raise UnsupportedSource('Only public Instagram post/Reel links are supported; profiles, stories and '
                                    'other pages are not.')
        canonical = 'https://www.instagram.com/' + match.group(1).replace('reels', 'reel') + '/' + match.group(2) + '/'
        page, _, provenance = sources.http_get(canonical, max_bytes=4_000_000,
                                               headers={'Accept-Language': 'en-US,en;q=0.8'})
        self.caption(page)  # refuse login walls before storing a snapshot
        return page, 'instagram.html', {**provenance, 'requested_url': url}

    def caption(self, page):
        parser = _Meta()
        parser.feed(page.decode('utf-8', 'replace'))
        meta = parser.values
        metadata = {k: meta[v] for k, v in (('title', 'og:title'), ('url', 'og:url'), ('type', 'og:type')) if v in meta}
        metadata['video_listed'] = bool(meta.get('og:video') or meta.get('og:video:secure_url') or
                                        meta.get('og:type') == 'video.other')
        caption = meta.get('og:description') or meta.get('description') or ''
        if not caption.strip() or (LOGIN_WALL.search(caption) and len(caption) < 160 and '"' not in caption):
            raise UnsupportedSource('Instagram returned no public caption (login wall, private or removed post). '
                                    'Submit the caption or a transcript as text; nothing was inferred.', metadata)
        return caption, metadata

    def extract(self, data, filename):
        caption, metadata = self.caption(data)
        evidence, limitations, flags = text_evidence('instagram', [('caption-metadata', caption)])
        limitations.insert(0, 'Caption/description text from the public page metadata only. The Reel or post media '
                              'was not watched or transcribed, so spoken or on-screen claims are absent.')
        limitations.append('Instagram metadata may truncate long captions and prefixes them with engagement counts.')
        return Extraction(evidence, limitations, flags, metadata, 'caption_metadata_only')
