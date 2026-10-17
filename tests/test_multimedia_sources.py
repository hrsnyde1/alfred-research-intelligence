"""Multimedia source handlers. Network responses are explicit test doubles; no live calls."""
import io
import json
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
os.environ.setdefault('ALFRED_RESEARCH_CORROBORATION', 'off')  # engine runs in unit tests never reach the network
from alfred_research.local.engine import ResearchEngine
from alfred_research.local.sources import (acquire, extract, extract_document, handler_for_snapshot,
                                           handler_for_url, UnsupportedSource)
from alfred_research.local.platforms import parse_github, youtube_id


def pdf(objects, root=1, trailer_extra=b''):
    """Minimal PDF writer: objects is a list of bytes bodies numbered from 1."""
    out = bytearray(b'%PDF-1.7\n%\xe2\xe3\xcf\xd3\n')
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += str(number).encode() + b' 0 obj\n' + body + b'\nendobj\n'
    xref = len(out)
    out += b'xref\n0 ' + str(len(objects) + 1).encode() + b'\n0000000000 65535 f \n'
    out += b''.join(b'%010d 00000 n \n' % o for o in offsets)
    out += (b'trailer\n<< /Size ' + str(len(objects) + 1).encode() + b' /Root ' + str(root).encode() + b' 0 R ' +
            trailer_extra + b'>>\nstartxref\n' + str(xref).encode() + b'\n%%EOF\n')
    return bytes(out)


def stream(content, extra=b'', compress=True):
    data = zlib.compress(content) if compress else content
    return (b'<< /Length ' + str(len(data)).encode() + (b' /Filter /FlateDecode' if compress else b'') + extra +
            b' >>\nstream\n' + data + b'\nendstream')


def simple_pdf():
    page1 = b'BT /F1 12 Tf 72 720 Td (Page one says retries are safe for idempotent methods.) Tj ET'
    page2 = b'BT /F1 12 Tf 72 720 Td [(Page two ) -250 (explains the) -300 (\\(caveats\\).)] TJ 0 -14 Td (Second line here.) Tj ET'
    return pdf([
        b'<< /Type /Catalog /Pages 2 0 R >>',
        b'<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 /Resources << /Font << /F1 5 0 R >> >> >>',
        b'<< /Type /Page /Parent 2 0 R /Contents 6 0 R >>',
        b'<< /Type /Page /Parent 2 0 R /Contents 7 0 R >>',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>',
        stream(page1), stream(page2),
        b'<< /Title (Retry Guidance) /Author (Test Author) >>',
    ], trailer_extra=b'/Info 8 0 R ')


def cid_pdf_with_object_stream():
    cmap = (b'/CIDInit /ProcSet findresource begin 1 begincodespacerange <0000> <FFFF> endcodespacerange\n'
            b'2 beginbfchar <0001> <0048> <0002> <0069> endbfchar\n'
            b'1 beginbfrange <0010> <0012> <0041> endbfrange\nendcmap')
    content = b'BT /F1 10 Tf 50 700 Td <000100020010001100120001> Tj ET'
    inner = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
             b'<< /Type /Page /Parent 2 0 R /Contents 6 0 R /Resources << /Font << /F1 4 0 R >> >> >>',
             b'<< /Type /Font /Subtype /Type0 /BaseFont /Fake /Encoding /Identity-H /ToUnicode 5 0 R >>']
    header, body = [], b''
    for number, item in enumerate(inner, 1):
        header.append(b'%d %d' % (number, len(body)))
        body += item + b'\n'
    head = b' '.join(header) + b'\n'
    objstm = stream(head + body, b' /Type /ObjStm /N 4 /First ' + str(len(head)).encode())
    # Object numbers 1-4 live inside object 7 (the object stream).
    return pdf([b'null', b'null', b'null', b'null', stream(cmap), stream(content), objstm])


def scanned_pdf():
    return pdf([
        b'<< /Type /Catalog /Pages 2 0 R >>',
        b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        b'<< /Type /Page /Parent 2 0 R /Contents 4 0 R /Resources << /XObject << /Im1 5 0 R >> >> >>',
        stream(b'q 612 0 0 792 0 0 cm /Im1 Do Q'),
        stream(b'\xff\xd8\xff' * 20, b' /Subtype /Image /Width 1 /Height 1', compress=False),
    ])


def docx(paragraphs, table=None, core=True, doctype=False):
    w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    body = ''.join('<w:p><w:r><w:t xml:space="preserve">' + p + '</w:t></w:r></w:p>' for p in paragraphs)
    if table:
        body += '<w:tbl>' + ''.join('<w:tr>' + ''.join('<w:tc><w:p><w:r><w:t>' + c + '</w:t></w:r></w:p></w:tc>' for c in row)
                                    + '</w:tr>' for row in table) + '</w:tbl>'
    document = ('<!DOCTYPE x [<!ENTITY a "b">]>' if doctype else '') + \
        '<w:document xmlns:w="' + w + '"><w:body>' + body + '</w:body></w:document>'
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        archive.writestr('word/document.xml', document)
        if core:
            archive.writestr('docProps/core.xml', '<cp:coreProperties xmlns:cp="x" xmlns:dc="http://purl.org/dc/elements/1.1/">'
                                                  '<dc:title>Quarterly memo</dc:title><dc:creator>Owner</dc:creator></cp:coreProperties>')
    return buffer.getvalue()


ARTICLE_HTML = b'''<html><head><title>Idempotency explained</title>
<meta name="author" content="A. Writer"><meta property="article:published_time" content="2026-01-02T03:04:05Z">
<link rel="canonical" href="https://example.org/idempotency"></head><body class="has-sidebar">
<nav><a>Home</a> <a>Subscribe to our newsletter today</a></nav>
<div class="cookie-banner">We use cookies to improve your experience on this site.</div>
<article><h1>Idempotency</h1><p>An idempotent request can be repeated with the same intended effect on the server.</p>
<p>Clients may therefore retry such requests automatically after a connection failure occurs.</p>
<div class="share-tools">Share this article on social media platforms now</div></article>
<aside>Related: ten unrelated stories you might enjoy reading later.</aside>
<footer>Copyright notice and legal boilerplate for the entire website.</footer></body></html>'''


class Responses:
    """Routes http_get calls to canned bodies; unknown URLs fail loudly."""
    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def __call__(self, url, max_bytes=None, headers=None):
        self.calls.append(url)
        for prefix, body in self.routes:
            if url.startswith(prefix):
                if isinstance(body, Exception):
                    raise body
                media = 'application/json'
                if isinstance(body, tuple):
                    body, media = body
                data = body if isinstance(body, bytes) else json.dumps(body).encode()
                return data, media, {'origin': 'live_https', 'requested_url': url, 'final_url': url,
                                                  'redirects': [{'url': url, 'status': 200}], 'content_type': 'x'}
        raise AssertionError('unexpected network call ' + url)


SHA = 'a' * 40
GITHUB = [
    ('https://api.github.com/repos/octo/tool/commits/', SHA.encode()),
    ('https://api.github.com/repos/octo/tool/git/trees/', {'truncated': False, 'tree': [
        {'path': 'README.md', 'type': 'blob', 'size': 60, 'mode': '100644'},
        {'path': 'LICENSE', 'type': 'blob', 'size': 20, 'mode': '100644'},
        {'path': 'pyproject.toml', 'type': 'blob', 'size': 30, 'mode': '100644'},
        {'path': 'src/tool/__main__.py', 'type': 'blob', 'size': 50, 'mode': '100755'},
        {'path': 'node_modules/x/index.js', 'type': 'blob', 'size': 10, 'mode': '100644'},
        {'path': 'assets/logo.png', 'type': 'blob', 'size': 10, 'mode': '100644'}]}),
    ('https://api.github.com/repos/octo/tool/languages', {'Python': 1234}),
    ('https://api.github.com/repos/octo/tool', {'full_name': 'octo/tool', 'html_url': 'https://github.com/octo/tool',
                                               'description': 'A tiny retry helper', 'default_branch': 'main',
                                               'language': 'Python', 'license': {'spdx_id': 'MIT'}, 'topics': ['http'],
                                               'stargazers_count': 5, 'forks_count': 1, 'archived': False}),
    ('https://raw.githubusercontent.com/octo/tool/' + SHA + '/README.md',
     b'# Tool\nTool retries idempotent HTTP requests with exponential backoff.\n'),
    ('https://raw.githubusercontent.com/octo/tool/' + SHA + '/LICENSE', b'MIT License text\n'),
    ('https://raw.githubusercontent.com/octo/tool/' + SHA + '/pyproject.toml', b'[project]\nname = "tool"\n'),
    ('https://raw.githubusercontent.com/octo/tool/' + SHA + '/src/tool/__main__.py',
     b'import os\nos.system("rm -rf /")  # never executed by Research\n'),
]


def watch_page(player):
    return b'<html><script>var ytInitialPlayerResponse = ' + json.dumps(player).encode() + b';var x=1;</script></html>'


PLAYER = {'playabilityStatus': {'status': 'OK'},
          'videoDetails': {'title': 'Retry talk', 'author': 'Channel', 'lengthSeconds': '120',
                           'shortDescription': 'Slides linked below.'},
          'microformat': {'playerMicroformatRenderer': {'publishDate': '2026-01-01'}},
          'captions': {'playerCaptionsTracklistRenderer': {'captionTracks': [
              {'baseUrl': 'https://www.youtube.com/api/timedtext?v=abcdefghijk&lang=de', 'languageCode': 'de', 'kind': 'asr'},
              {'baseUrl': 'https://www.youtube.com/api/timedtext?v=abcdefghijk&lang=en', 'languageCode': 'en',
               'name': {'simpleText': 'English'}}]}}}
CAPTIONS = {'events': [{'tStartMs': 0, 'dDurationMs': 4000, 'segs': [{'utf8': 'Welcome to the talk about retries.'}]},
                       {'tStartMs': 61000, 'dDurationMs': 5000, 'segs': [{'utf8': 'Only idempotent requests should be retried automatically.'}]}]}
YOUTUBE = [('https://www.youtube.com/oembed', {'title': 'Retry talk', 'author_name': 'Channel'}),
           ('https://www.youtube.com/api/timedtext?v=abcdefghijk&lang=en', CAPTIONS),
           ('https://www.youtube.com/watch', watch_page(PLAYER))]

REEL = b'''<html><head><meta property="og:title" content="Creator on Instagram">
<meta property="og:description" content="1,234 likes, 56 comments - creator on January 1, 2026: &quot;Three habits that doubled my sleep quality.&quot;">
<meta property="og:type" content="video.other"><meta property="og:url" content="https://www.instagram.com/reel/ABCdef123/"></head></html>'''
LOGIN = b'<html><head><meta property="og:description" content="Create an account or log in to Instagram"></head></html>'


class HandlerRegistryTests(unittest.TestCase):
    def test_url_and_snapshot_dispatch(self):
        cases = {'https://youtu.be/abcdefghijk': 'youtube', 'https://www.youtube.com/shorts/abcdefghijk': 'youtube',
                 'https://www.instagram.com/reel/ABCdef123/': 'instagram', 'https://github.com/octo/tool': 'github',
                 'https://github.com/octo/tool/tree/v1.2': 'github'}
        for url, name in cases.items():
            with self.subTest(url=url):
                self.assertEqual(handler_for_url(url).name, name)
        for url in ('https://example.org/a.pdf', 'https://github.com/features', 'https://github.com/octo/tool/issues/4'):
            self.assertIsNone(handler_for_url(url))
        for filename, name in (('source.pdf', 'pdf'), ('source.docx', 'docx'), ('source.html', 'article'),
                               ('source.vtt', 'text'), ('github.json', 'github'), ('youtube.json', 'youtube'),
                               ('instagram.html', 'instagram')):
            self.assertEqual(handler_for_snapshot(filename).name, name)
        self.assertIsNone(handler_for_snapshot('source.json'))
        self.assertIsNone(handler_for_snapshot('source.doc'))

    def test_url_parsers(self):
        self.assertEqual(parse_github('https://github.com/octo/tool.git'), ('octo', 'tool', None, None))
        self.assertEqual(parse_github('https://github.com/octo/tool/blob/main/src/a.py'), ('octo', 'tool', 'main', 'src/a.py'))
        self.assertEqual(youtube_id('https://www.youtube.com/watch?v=abcdefghijk&t=30'), 'abcdefghijk')
        self.assertIsNone(youtube_id('https://www.youtube.com/watch?v=short'))


class ArticleTests(unittest.TestCase):
    def test_boilerplate_removed_and_metadata_kept(self):
        result = extract_document(ARTICLE_HTML, 'source.html')
        text = ' '.join(e['text'] for e in result.evidence)
        self.assertIn('same intended effect', text)
        self.assertIn('retry such requests', text)
        for noise in ('newsletter', 'cookies', 'social media', 'unrelated stories', 'Copyright'):
            self.assertNotIn(noise, text)
        self.assertEqual(result.metadata['author'], 'A. Writer')
        self.assertEqual(result.metadata['title'], 'Idempotency explained')
        self.assertEqual(result.metadata['canonical_url'], 'https://example.org/idempotency')
        self.assertEqual(result.basis, 'article_text')
        self.assertTrue(all(':html-line' in e['location'] for e in result.evidence))

    def test_overaggressive_cleanup_falls_back_to_visible_text(self):
        page = (b'<html><body><div class="content-sidebar"><p>' + b'Primary finding sentence repeated for length. ' * 10 +
                b'</p></div></body></html>')
        result = extract_document(page, 'source.html')
        self.assertIn('Primary finding', result.evidence[0]['text'])
        self.assertTrue(any('all visible blocks' in x for x in result.limitations))

    def test_scripts_never_become_evidence(self):
        evidence, _, _ = extract(b'<p>This is an actual visible finding.</p><script>Fabricated hidden claim.</script>', 'source.html')
        self.assertNotIn('Fabricated', json.dumps(evidence))


class PDFTests(unittest.TestCase):
    def test_page_references_metadata_and_tj_spacing(self):
        result = extract_document(simple_pdf(), 'source.pdf')
        by_location = {e['location']: e['text'] for e in result.evidence}
        self.assertIn('Page one says retries are safe', by_location['pdf:page-1:char0'])
        self.assertIn('Page two explains the (caveats).\nSecond line here.', by_location['pdf:page-2:char0'])
        self.assertEqual(result.metadata['title'], 'Retry Guidance')
        self.assertEqual(result.metadata['pages'], 2)
        self.assertEqual(result.basis, 'pdf_text_layer')
        self.assertIn('no OCR', result.limitations[0])

    def test_object_stream_and_tounicode_cmap(self):
        result = extract_document(cid_pdf_with_object_stream(), 'source.pdf')
        self.assertEqual(result.evidence[0]['text'], 'HiABCH')

    def test_scanned_pdf_is_unsupported_not_guessed(self):
        with self.assertRaisesRegex(UnsupportedSource, 'scanned'):
            extract_document(scanned_pdf(), 'source.pdf')

    def test_encrypted_and_invalid_pdf_unsupported(self):
        with self.assertRaisesRegex(UnsupportedSource, 'Encrypted'):
            extract_document(pdf([b'<< /Type /Catalog >>'], trailer_extra=b'/Encrypt << /Filter /Standard >> '), 'source.pdf')
        with self.assertRaises(UnsupportedSource):
            extract_document(b'%PDF-not-a-working-parser', 'source.pdf')


class DocxTests(unittest.TestCase):
    def test_paragraphs_tables_and_core_metadata(self):
        result = extract_document(docx(['First paragraph states the policy.', 'Second paragraph adds detail.'],
                                       table=[['Metric', 'Value'], ['Retries', '3']]), 'source.docx')
        by_location = {e['location']: e['text'] for e in result.evidence}
        self.assertEqual(by_location['docx:paragraph-2:char0'], 'Second paragraph adds detail.')
        self.assertEqual(by_location['docx:table-1-row-2:char0'], 'Retries | 3')
        self.assertEqual(result.metadata['title'], 'Quarterly memo')
        self.assertTrue(any('footnotes' in x for x in result.limitations))

    def test_unsafe_or_legacy_documents_refused(self):
        with self.assertRaisesRegex(UnsupportedSource, 'DTD'):
            extract_document(docx(['x'], doctype=True), 'source.docx')
        with self.assertRaisesRegex(UnsupportedSource, 'legacy'):
            extract_document(b'\xd0\xcf\x11\xe0 legacy word file', 'source.docx')
        with self.assertRaisesRegex(UnsupportedSource, 'Unsupported file type'):
            with tempfile.NamedTemporaryFile(suffix='.doc') as file:
                acquire(file.name, Path(tempfile.gettempdir()), 1)


class PlatformTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_github_snapshot_is_pinned_read_only_and_cited(self):
        responses = Responses(GITHUB)
        with patch('alfred_research.local.sources.http_get', responses):
            source = acquire('https://github.com/octo/tool', self.root, 1)
        self.assertEqual(source['metadata']['revision'], SHA)
        self.assertEqual(source['content_basis'], 'repository_files')
        locations = [e['location'] for e in source['evidence']]
        self.assertIn('github:README.md#L1-L2:char0', locations)
        self.assertIn('github:github-metadata:char0', locations)
        self.assertFalse(any('node_modules' in u or 'logo.png' in u for u in responses.calls))
        self.assertTrue(all(SHA in u for u in responses.calls if 'raw.githubusercontent.com' in u))
        self.assertIn('declared_dependencies:pyproject.toml', source['flags'])
        self.assertIn('executable_file:src/tool/__main__.py', source['flags'])
        self.assertIn('not executed', source['limitations'][0])
        # Re-extraction from the pinned snapshot (what the verifier does) needs no network.
        evidence, _, _ = extract(Path(source['snapshot']).read_bytes(), source['filename'])
        self.assertEqual(len(evidence), len(source['evidence']))

    def test_github_private_or_missing_repository(self):
        with patch('alfred_research.local.sources.http_get', Responses([('https://api.github.com', ValueError('Source HTTP status 404'))])):
            with self.assertRaisesRegex(UnsupportedSource, 'not found'):
                acquire('https://github.com/octo/missing', self.root, 1)

    def test_youtube_transcript_with_timestamps(self):
        with patch('alfred_research.local.sources.http_get', Responses(YOUTUBE)):
            source = acquire('https://youtu.be/abcdefghijk', self.root, 1)
        self.assertEqual(source['content_basis'], 'transcript_creator_captions')
        self.assertEqual(source['metadata']['title'], 'Retry talk')
        by_location = {e['location']: e['text'] for e in source['evidence']}
        self.assertIn('Only idempotent requests', by_location['youtube:t=00:00:00-00:01:06:char0'])
        self.assertTrue(by_location['youtube:creator-description:char0'].startswith('Creator-written description'))
        self.assertIn('not watched', source['limitations'][0])

    def test_youtube_without_captions_never_uses_title(self):
        player = dict(PLAYER, captions={})
        routes = [YOUTUBE[0], ('https://www.youtube.com/watch', watch_page(player))]
        with patch('alfred_research.local.sources.http_get', Responses(routes)):
            with self.assertRaisesRegex(UnsupportedSource, 'transcript not accessible') as caught:
                acquire('https://www.youtube.com/watch?v=abcdefghijk', self.root, 1)
        self.assertEqual(caught.exception.metadata['title'], 'Retry talk')
        self.assertEqual(list(self.root.iterdir()), [])

    def test_youtube_empty_caption_body_and_sign_in_required(self):
        empty = [YOUTUBE[0], ('https://www.youtube.com/api/timedtext', b''), YOUTUBE[2]]
        with patch('alfred_research.local.sources.http_get', Responses(empty)):
            with self.assertRaisesRegex(UnsupportedSource, 'no caption text'):
                acquire('https://youtu.be/abcdefghijk', self.root, 1)
        login = [YOUTUBE[0], ('https://www.youtube.com/watch', watch_page({'playabilityStatus': {'status': 'LOGIN_REQUIRED'}}))]
        with patch('alfred_research.local.sources.http_get', Responses(login)):
            with self.assertRaisesRegex(UnsupportedSource, 'LOGIN_REQUIRED'):
                acquire('https://youtu.be/abcdefghijk', self.root, 1)

    def test_instagram_caption_only_and_login_wall(self):
        with patch('alfred_research.local.sources.http_get', Responses([('https://www.instagram.com/reel/ABCdef123/', REEL)])):
            source = acquire('https://www.instagram.com/reels/ABCdef123/?igsh=x', self.root, 1)
        self.assertEqual(source['content_basis'], 'caption_metadata_only')
        self.assertIn('Three habits', source['evidence'][0]['text'])
        self.assertTrue(source['metadata']['video_listed'])
        self.assertIn('not watched', source['limitations'][0])
        with patch('alfred_research.local.sources.http_get', Responses([('https://www.instagram.com/', LOGIN)])):
            with self.assertRaisesRegex(UnsupportedSource, 'no public caption'):
                acquire('https://www.instagram.com/p/ABCdef123/', self.root, 2)
        with self.assertRaisesRegex(UnsupportedSource, 'post/Reel'):
            acquire('https://www.instagram.com/someprofile/', self.root, 3)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.engine = ResearchEngine(self.root / 'state')

    def tearDown(self):
        self.temp.cleanup()

    def run_job(self, locator, question='Explain retries'):
        return self.engine.run(self.engine.submit(question, [locator], provider='extractive'))

    def test_pdf_and_docx_jobs_complete_with_verified_citations(self):
        for name, data, marker in (('guide.pdf', simple_pdf(), 'pdf:page-'), ('memo.docx', docx(['Retries happen three times for idempotent calls.']), 'docx:paragraph-1')):
            with self.subTest(name=name):
                path = self.root / name
                path.write_bytes(data)
                job = self.run_job(str(path))
                self.assertEqual(job['status'], 'completed')
                report = Path(job['report_path']).read_text()
                self.assertIn(marker, report)
                self.assertIn('evidence basis', report)
                self.assertTrue(all(a['supported'] for a in job['artifacts']['verification']['assessments']))

    def test_platform_job_verifies_in_separate_process_without_network(self):
        with patch('alfred_research.local.sources.http_get', Responses(YOUTUBE)):
            job = self.run_job('https://youtu.be/abcdefghijk')
        self.assertEqual(job['status'], 'completed')
        report = Path(job['report_path']).read_text()
        self.assertIn('transcript_creator_captions', report)
        self.assertIn('title Retry talk', report)

    def test_inaccessible_video_is_unsupported_with_observed_metadata(self):
        routes = [YOUTUBE[0], ('https://www.youtube.com/watch', watch_page(dict(PLAYER, captions={})))]
        with patch('alfred_research.local.sources.http_get', Responses(routes)):
            job = self.run_job('https://youtu.be/abcdefghijk')
        self.assertEqual(job['status'], 'unsupported')
        self.assertNotIn('report', job['artifacts'])
        failure = job['artifacts']['acquisition-failures'][0]
        self.assertEqual(failure['metadata']['title'], 'Retry talk')

    def test_scanned_pdf_job_is_unsupported(self):
        path = self.root / 'scan.pdf'
        path.write_bytes(scanned_pdf())
        job = self.run_job(str(path))
        self.assertEqual(job['status'], 'unsupported')
        self.assertNotIn('memory-candidate', job['artifacts'])


if __name__ == '__main__':
    unittest.main()
