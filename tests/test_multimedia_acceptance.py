"""Regressions found by the live multimedia acceptance runs (docs/MULTIMEDIA_ACCEPTANCE.md).

Network responses are explicit test doubles; no live calls.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from alfred_research.integration.desk import ResearchDesk, final_message
from alfred_research.integration.message_intake import detect
from alfred_research.local.documents import ArticleHandler, TextHandler
from alfred_research.local.pdf import PDFHandler
from alfred_research.local.sources import UnsupportedSource, extract_document, stage_upload
from alfred_research.local.platforms import InstagramHandler, YouTubeHandler
from test_multimedia_sources import PLAYER, CAPTIONS, Responses, docx, pdf, scanned_pdf, simple_pdf, stream, watch_page


class PostResponses(Responses):
    """Responses that also accept a POST body and record it."""
    def __init__(self, routes):
        super().__init__(routes)
        self.bodies = []

    def __call__(self, url, max_bytes=None, headers=None, body=None):
        self.bodies.append(body)
        return super().__call__(url, max_bytes=max_bytes, headers=headers)


def word_export_pdf():
    """Simple TrueType font whose ToUnicode CMap declares a two-byte codespace (Word export quirk)."""
    cmap = (b'/CIDInit /ProcSet findresource begin 1 begincodespacerange <0000> <FFFF> endcodespacerange\n'
            b'4 beginbfchar <20> <0020> <47> <0047> <6F> <006F> <76> <0076> endbfchar\nendcmap')
    content = b'BT /TT0 11 Tf 72 720 Td (Govern) Tj ( ) Tj (Go) Tj ET'
    cmap_full = cmap.replace(b'4 beginbfchar <20> <0020> <47> <0047> <6F> <006F> <76> <0076>',
                             b'8 beginbfchar <20> <0020> <47> <0047> <6F> <006F> <76> <0076> '
                             b'<65> <0065> <72> <0072> <6E> <006E> <73> <0073>')
    return pdf([
        b'<< /Type /Catalog /Pages 2 0 R >>',
        b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        b'<< /Type /Page /Parent 2 0 R /Contents 5 0 R /Resources << /Font << /TT0 4 0 R >> >> >>',
        b'<< /Type /Font /Subtype /TrueType /BaseFont /ABCDEF+Calibri /Encoding /WinAnsiEncoding /ToUnicode 6 0 R >>',
        stream(content), stream(cmap_full),
    ])


class PDFFontTests(unittest.TestCase):
    def test_simple_font_with_two_byte_cmap_codespace_is_decoded(self):
        result = PDFHandler().extract(word_export_pdf(), 'source.pdf')
        self.assertIn('Govern Go', result.evidence[0]['text'])
        self.assertEqual(result.evidence[0]['location'], 'pdf:page-1:char0')
        self.assertFalse(any('without extractable text' in item for item in result.limitations))

    def test_image_only_pdf_reports_no_text_layer(self):
        with self.assertRaisesRegex(UnsupportedSource, 'no text layer'):
            extract_document(scanned_pdf(), 'source.pdf')


class ArticleContainerTests(unittest.TestCase):
    PAGE = ('<html><head><title>Notes</title></head><body>'
            '<div id="sponsored-banner"><strong>Sponsored by:</strong> a vendor with an excellent product today</div>'
            '<div id="wrapper"><div id="primary"><div class="entry entryPage">' +
            ''.join('<p>Paragraph %d of the real essay discusses idempotent retries in useful detail.</p>' % n
                    for n in range(12)) +
            '</div><section><h3>Monthly briefing</h3><p>Sponsor me for $10/month and get a curated digest.</p></section>'
            '</div><div id="secondary"><p>This is the sidebar metabox with author biography text.</p></div></div>'
            '</body></html>').encode()

    def test_content_class_container_excludes_promos_and_sidebars(self):
        result = ArticleHandler().extract(self.PAGE, 'source.html')
        text = ' '.join(e['text'] for e in result.evidence)
        self.assertIn('Paragraph 11 of the real essay', text)
        for leaked in ('Sponsor me', 'Sponsored by', 'metabox'):
            self.assertNotIn(leaked, text)
        self.assertTrue(any('content container' in item for item in result.limitations))


class TextParagraphTests(unittest.TestCase):
    def test_paragraph_evidence_cites_exact_line_ranges_without_bom(self):
        data = '﻿\n\nTitle\n\nFirst paragraph line one\nline two of the first paragraph which is long enough ' \
               'to stand alone as evidence in a report about retries and backoff behaviour.' + 'x' * 250 + \
               '\n\nSecond paragraph.\n'
        result = TextHandler().extract(data.encode('utf-8'), 'source.txt')
        locations = [e['location'] for e in result.evidence]
        self.assertEqual(locations, ['text:lines-3-6:char0', 'text:lines-8-8:char0'])
        self.assertFalse(result.evidence[0]['text'].startswith('﻿'))
        self.assertEqual(result.metadata['lines'], 8)

    def test_markdown_and_transcripts_keep_their_basis(self):
        self.assertEqual(TextHandler().extract(b'# Heading\n\nBody text.\n', 'source.md').basis, 'full_text')
        vtt = TextHandler().extract(b'WEBVTT\n\n00:00:01.000 --> 00:00:04.000\nHello there.\n', 'source.vtt')
        self.assertEqual(vtt.basis, 'owner_supplied_transcript')

    def test_non_utf8_text_refused(self):
        with self.assertRaisesRegex(UnsupportedSource, 'UTF-8'):
            TextHandler().extract(b'\xff\xfe\x00bad', 'source.txt')


class YouTubePlayerFallbackTests(unittest.TestCase):
    def page(self):
        return watch_page(PLAYER).replace(b'</html>', b'<script>ytcfg.set({"INNERTUBE_API_KEY": "AIzaTestKey0123456789abcd"});</script></html>')

    def test_empty_web_captions_fall_back_to_public_player_api(self):
        android = {'playabilityStatus': {'status': 'OK'}, 'videoDetails': {'videoId': 'abcdefghijk'},
                   'captions': {'playerCaptionsTracklistRenderer': {'captionTracks': [
                       {'baseUrl': 'https://www.youtube.com/api/timedtext?v=abcdefghijk&lang=en&fmt=srv3&android=1',
                        'languageCode': 'en'}]}}}
        routes = [('https://www.youtube.com/oembed', {'title': 'Retry talk'}),
                  ('https://www.youtube.com/api/timedtext?v=abcdefghijk&lang=en&android=1', CAPTIONS),
                  ('https://www.youtube.com/api/timedtext', (b'', 'text/html')),
                  ('https://www.youtube.com/youtubei/v1/player?key=AIzaTestKey0123456789abcd', android),
                  ('https://www.youtube.com/watch', self.page())]
        responses = PostResponses(routes)
        with patch('alfred_research.local.sources.http_get', responses):
            data, name, provenance = YouTubeHandler().acquire_url('https://youtu.be/abcdefghijk')
        self.assertIn('android client', provenance['caption_source'])
        self.assertIn('https://www.youtube.com/api/timedtext?v=abcdefghijk&lang=en&android=1&fmt=json3', responses.calls)
        posted = [json.loads(b) for b in responses.bodies if b]
        self.assertEqual(posted[0]['videoId'], 'abcdefghijk')
        self.assertNotIn('Authorization', json.dumps(posted))
        result = YouTubeHandler().extract(data, name)
        self.assertEqual(result.evidence[0]['location'], 'youtube:t=00:00:00-00:01:06:char0')
        self.assertIn('not watched', result.limitations[0])

    def test_both_paths_empty_is_honestly_unsupported(self):
        routes = [('https://www.youtube.com/oembed', {'title': 'Retry talk'}),
                  ('https://www.youtube.com/api/timedtext', (b'', 'text/html')),
                  ('https://www.youtube.com/youtubei/v1/player', {'playabilityStatus': {'status': 'LOGIN_REQUIRED'}}),
                  ('https://www.youtube.com/watch', self.page())]
        with patch('alfred_research.local.sources.http_get', PostResponses(routes)):
            with self.assertRaisesRegex(UnsupportedSource, 'no caption text.*No findings were inferred from the title') as caught:
                YouTubeHandler().acquire_url('https://www.youtube.com/watch?v=abcdefghijk')
        self.assertEqual(caught.exception.metadata['title'], 'Retry talk')


class InstagramTests(unittest.TestCase):
    def test_login_wall_says_reel_was_not_watched(self):
        page = b'<html><head><meta property="og:description" content="Log in to Instagram"></head></html>'
        with self.assertRaisesRegex(UnsupportedSource, 'not watched and its caption was not read'):
            InstagramHandler().caption(page)

    def test_multiline_title_metadata_is_single_line(self):
        page = ('<html><head><meta property="og:title" content="Creator on Instagram: &quot;Line one.\n\nLine two.&quot;">'
                '<meta property="og:description" content="5 likes - creator: &quot;Line one.\n\nLine two.&quot;">'
                '</head></html>').encode()
        caption, metadata = InstagramHandler().caption(page)
        self.assertNotIn('\n', metadata['title'])
        self.assertIn('Line two', caption)


class ChatUploadTests(unittest.TestCase):
    """A Telegram upload arrives as an opaque local file plus its original file name."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.downloads = self.root / 'telegram-downloads'
        self.downloads.mkdir()
        self.attachments = self.root / 'attachments'

    def tearDown(self):
        self.temp.cleanup()

    def upload(self, data, opaque='file_7'):
        path = self.downloads / opaque
        path.write_bytes(data)
        return path

    def test_staged_uploads_run_through_intake_and_desk(self):
        cases = [(simple_pdf(), 'Retry Guidance.pdf', 'pdf:page-1'),
                 (docx(['Retries are safe only for idempotent requests.']), 'memo.docx', 'docx:paragraph-1'),
                 (b'Retries are safe only for idempotent requests, says this note.\n', 'notes.txt', 'text:lines-1-1'),
                 (b'# Retry notes\n\nRetries are safe only for idempotent requests.\n', 'notes.md', 'text:lines-1-3')]
        desk = ResearchDesk(self.root / 'work', provider='extractive', runner='inline')
        for number, (data, name, location) in enumerate(cases):
            with self.subTest(name=name):
                staged = stage_upload(self.upload(data, 'file_' + str(number)), name, self.attachments)
                self.assertEqual(Path(staged).name, name)
                self.assertEqual(Path(staged).stat().st_mode & 0o777, 0o600)
                intent = detect('', [{'path': staged, 'filename': name}], [self.attachments], dedicated=True)
                self.assertEqual(intent.sources, [staged])
                desk.accept(intent, {'project': 'research'}, 'telegram:' + str(number))
                job = desk.engine.store.get(desk.engine.store.by_request_key('telegram:' + str(number)))
                self.assertEqual(job['status'], 'completed', job.get('error'))
                source = job['artifacts']['source-1']
                self.assertEqual(source['provenance']['original_filename'], name)
                self.assertEqual(source['provenance']['origin'], 'owner_file')
                self.assertTrue(any(e['location'].startswith(location) for e in source['evidence']))
                self.assertIn('Research complete', final_message(job))

    def test_unsupported_upload_refused_before_any_job(self):
        for name in ('budget.xlsx', 'scan.png', 'slides.pptx', 'legacy.doc', 'no-extension'):
            with self.subTest(name=name), self.assertRaisesRegex(UnsupportedSource, 'not analyzed'):
                stage_upload(self.upload(b'data'), name, self.attachments)
        self.assertFalse(self.attachments.exists() and any(self.attachments.iterdir()))

    def test_renamed_or_scanned_upload_is_refused_by_content(self):
        desk = ResearchDesk(self.root / 'work', provider='extractive', runner='inline')
        for number, (data, name, reason) in enumerate([(b'\x89PNG\r\n\x1a\n' + b'0' * 40, 'photo.pdf', 'missing %PDF header'),
                                                        (scanned_pdf(), 'scan.pdf', 'no text layer')]):
            staged = stage_upload(self.upload(data, 'f' + str(number)), name, self.attachments)
            intent = detect('', [{'path': staged, 'filename': name}], [self.attachments], dedicated=True)
            desk.accept(intent, {'project': 'research'}, 'bad:' + str(number))
            job = desk.engine.store.get(desk.engine.store.by_request_key('bad:' + str(number)))
            self.assertEqual(job['status'], 'unsupported')
            self.assertNotIn('report', job['artifacts'])
            self.assertIn(reason, final_message(job))
            self.assertIn('Nothing was inferred', final_message(job))

    def test_original_filename_is_sanitized(self):
        staged = stage_upload(self.upload(b'hello world text\n'), '../../etc/pass<wd>.txt', self.attachments)
        self.assertTrue(Path(staged).resolve().is_relative_to(self.attachments.resolve()))
        self.assertEqual(Path(staged).name, 'pass_wd_.txt')
        with self.assertRaisesRegex(ValueError, 'original file name'):
            stage_upload(self.upload(b'x'), '', self.attachments)


if __name__ == '__main__':
    unittest.main()
