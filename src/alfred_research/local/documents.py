"""Document handlers: plain text, web articles and DOCX. No network, no execution."""
from html.parser import HTMLParser
import io
import re
import zipfile
from xml.etree import ElementTree

from .sources import (BINARY_MAX_BYTES, TEXT_SUFFIXES, Extraction, SourceHandler,
                      UnsupportedSource, legacy_text_extract, text_evidence)


class TextHandler(SourceHandler):
    name, kind, suffixes = 'text', 'document', TEXT_SUFFIXES

    def extract(self, data, filename):
        try:
            evidence, limitations, flags = legacy_text_extract(data, filename)
        except UnicodeDecodeError:
            raise UnsupportedSource('Text documents must be UTF-8; no findings generated.')
        basis = 'owner_supplied_transcript' if filename.lower().endswith(('.vtt', '.srt')) else 'full_text'
        if basis == 'owner_supplied_transcript':
            limitations.append('Supplied transcript text only; the original audio/video was not viewed.')
        return Extraction(evidence, limitations, flags, {}, basis)


SKIP = {'script', 'style', 'template', 'noscript', 'svg', 'nav', 'footer', 'aside', 'form', 'button',
        'select', 'iframe', 'canvas', 'dialog', 'menu'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
BLOCK = {'p', 'div', 'li', 'blockquote', 'pre', 'td', 'th', 'tr', 'section', 'article', 'main', 'table',
         'figcaption', 'dd', 'dt', 'ul', 'ol', 'header', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'body'}
HEADINGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
BOILERPLATE = {'nav', 'navbar', 'menu', 'footer', 'sidebar', 'cookie', 'cookies', 'consent', 'banner', 'share',
               'sharing', 'social', 'related', 'advert', 'advertisement', 'ads', 'promo', 'breadcrumb',
               'breadcrumbs', 'newsletter', 'subscribe', 'comments', 'popup', 'modal', 'navbox', 'catlinks',
               'printfooter', 'toc', 'skip', 'masthead', 'pagination'}
STRUCTURAL = {'html', 'body', 'main', 'article'}
META = {'author': 'author', 'article:author': 'author', 'publisher': 'publisher', 'og:site_name': 'site_name',
        'article:published_time': 'published_at', 'date': 'published_at', 'og:title': 'title',
        'description': 'description', 'og:description': 'description'}


class _Article(HTMLParser):
    """Visible block text with boilerplate regions removed; scripts are never run."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_tag, self.skip_depth = None, 0
        self.stack = []
        self.blocks, self.buffer, self.start = [], [], None
        self.metadata, self.title, self.in_title = {}, [], False
        self.removed = 0

    def boilerplate(self, tag, attrs):
        if tag in SKIP or attrs.get('hidden') is not None or attrs.get('aria-hidden') == 'true':
            return True
        if tag == 'header' and not ({'article', 'main'} & set(self.stack)):
            return True
        if attrs.get('role') in ('navigation', 'banner', 'contentinfo', 'complementary', 'dialog'):
            return True
        if tag in STRUCTURAL:
            return False
        tokens = set(re.split(r'[\s_-]+', ((attrs.get('class') or '') + ' ' + (attrs.get('id') or '')).lower()))
        return bool(tokens & BOILERPLATE)

    def flush(self):
        text = ' '.join(''.join(self.buffer).split())
        if text:
            self.blocks.append({'line': self.start, 'text': text, 'heading': bool(HEADINGS & set(self.stack)),
                                'article': 'article' in self.stack, 'main': 'main' in self.stack})
        self.buffer, self.start = [], None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if self.skip_tag:
            if tag == self.skip_tag and tag not in VOID:
                self.skip_depth += 1
            return
        if tag == 'meta':
            key = (values.get('name') or values.get('property') or '').lower()
            if key in META and values.get('content') and META[key] not in self.metadata:
                self.metadata[META[key]] = ' '.join(values['content'].split())[:2000]
        elif tag == 'link' and 'canonical' in (values.get('rel') or '').split() and values.get('href'):
            self.metadata.setdefault('canonical_url', values['href'][:2048])
        elif tag == 'title':
            self.in_title = True
        if tag in VOID:
            if tag == 'br':
                self.buffer.append(' ')
            return
        if self.boilerplate(tag, values):
            self.skip_tag, self.skip_depth = tag, 1
            if tag not in ('script', 'style', 'template', 'noscript', 'svg'):
                self.removed += 1
            return
        if tag in BLOCK:
            self.flush()
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if self.skip_tag:
            if tag == self.skip_tag:
                self.skip_depth -= 1
                if self.skip_depth == 0:
                    self.skip_tag = None
            return
        if tag == 'title':
            self.in_title = False
        if tag in self.stack:
            if tag in BLOCK:
                self.flush()
            while self.stack and self.stack.pop() != tag:
                pass

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
            return
        if self.skip_tag or 'head' in self.stack or not data.strip() and not self.buffer:
            return
        if self.start is None:
            self.start = self.getpos()[0]
        self.buffer.append(data)


def decode_html(data):
    try:
        return data.decode('utf-8'), None
    except UnicodeDecodeError:
        match = re.search(rb'charset=["\']?([A-Za-z0-9_-]+)', data[:4096])
        for codec in ([match.group(1).decode()] if match else []) + ['cp1252']:
            try:
                return data.decode(codec), 'Page decoded as ' + codec + ' (not UTF-8).'
            except (LookupError, UnicodeDecodeError):
                continue
    raise UnsupportedSource('Undecodable HTML page; no findings generated.')


def article_blocks(html):
    parser = _Article()
    parser.feed(html)
    parser.close()
    parser.flush()
    return parser


class ArticleHandler(SourceHandler):
    name, kind, suffixes = 'article', 'article', ('.html', '.htm')

    def extract(self, data, filename):
        html, note = decode_html(data)
        parser = article_blocks(html)
        limitations = ['Ordinary HTML text only; JavaScript is not run and linked resources are not fetched.']
        if note:
            limitations.append(note)
        blocks = parser.blocks
        scope = 'page'
        for key in ('article', 'main'):
            chosen = [b for b in blocks if b[key]]
            if sum(len(b['text']) for b in chosen) >= 100:
                blocks, scope = chosen, key
                break
        # Drop stray navigation residue such as single-word links, keep headings.
        blocks = [b for b in blocks if b['heading'] or len(b['text'].split()) >= 3]
        if parser.removed:
            limitations.append('Boilerplate regions removed (navigation, footers, sidebars, cookie/share widgets); '
                               'main content taken from <' + scope + '>.' if scope != 'page' else
                               'Boilerplate regions removed (navigation, footers, sidebars, cookie/share widgets).')
        if sum(len(b['text']) for b in blocks) < 100:
            # Heuristics can over-remove; fall back to every visible block rather than lose content.
            fallback = article_blocks(re.sub(r'(?is)\s(class|id|role)\s*=\s*("[^"]*"|\'[^\']*\'|\S+)', ' ', html)).blocks
            if sum(len(b['text']) for b in fallback) > sum(len(b['text']) for b in blocks):
                blocks = fallback
                limitations.append('Main-content detection found little text; all visible blocks were used.')
        counts = {}
        segments = []
        for block in blocks:
            location = 'html-line' + str(block['line'])
            counts[location] = counts.get(location, 0) + 1
            if counts[location] > 1:
                location += '-' + str(counts[location])
            segments.append((location, block['text']))
        evidence, more, flags = text_evidence('article', segments)
        metadata = dict(parser.metadata)
        title = ' '.join(''.join(parser.title).split())
        if title:
            metadata.setdefault('title', title[:500])
        return Extraction(evidence, limitations + more, flags, metadata, 'article_text')


W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
CORE = {'{http://purl.org/dc/elements/1.1/}title': 'title', '{http://purl.org/dc/elements/1.1/}creator': 'author',
        '{http://purl.org/dc/terms/}created': 'created_at', '{http://purl.org/dc/terms/}modified': 'modified_at'}
XML_LIMIT = 40_000_000


def read_xml(archive, name):
    info = archive.getinfo(name)
    if info.file_size > XML_LIMIT:
        raise UnsupportedSource('DOCX part too large to extract safely: ' + name)
    data = archive.read(info)
    if b'<!DOCTYPE' in data[:4096] or b'<!ENTITY' in data:
        raise UnsupportedSource('DOCX contains XML DTD/entities; refused for safety.')
    return ElementTree.fromstring(data)


def paragraph_text(paragraph):
    pieces = []
    for node in paragraph.iter():
        if node.tag == W + 't' and node.text:
            pieces.append(node.text)
        elif node.tag == W + 'tab':
            pieces.append('\t')
        elif node.tag in (W + 'br', W + 'cr'):
            pieces.append('\n')
    return ''.join(pieces).strip()


class DocxHandler(SourceHandler):
    name, kind, suffixes, max_bytes = 'docx', 'document', ('.docx',), BINARY_MAX_BYTES

    def extract(self, data, filename):
        try:
            archive = zipfile.ZipFile(io.BytesIO(data))
            body = read_xml(archive, 'word/document.xml').find(W + 'body')
        except (zipfile.BadZipFile, KeyError):
            raise UnsupportedSource('Not a readable DOCX package (encrypted, corrupt or legacy .doc); no findings generated.')
        except ElementTree.ParseError:
            raise UnsupportedSource('Malformed DOCX XML; no findings generated.')
        metadata = {}
        try:
            for node in read_xml(archive, 'docProps/core.xml'):
                if node.tag in CORE and node.text and node.text.strip():
                    metadata[CORE[node.tag]] = node.text.strip()[:500]
        except (KeyError, ElementTree.ParseError):
            pass
        segments, counters = [], {'paragraph': 0, 'table': 0}

        def walk(container):
            for child in container:
                if child.tag == W + 'p':
                    counters['paragraph'] += 1
                    text = paragraph_text(child)
                    if text:
                        segments.append(('paragraph-' + str(counters['paragraph']), text))
                elif child.tag == W + 'tbl':
                    counters['table'] += 1
                    for row_number, row in enumerate(child.iter(W + 'tr'), 1):
                        cells = [' '.join(paragraph_text(p) for p in cell.iter(W + 'p')).strip()
                                 for cell in row.iter(W + 'tc')]
                        if any(cells):
                            segments.append(('table-' + str(counters['table']) + '-row-' + str(row_number),
                                             ' | '.join(cells)))
                elif child.tag in (W + 'sdt', W + 'sdtContent', W + 'customXml'):
                    walk(child)

        if body is not None:
            walk(body)
        evidence, limitations, flags = text_evidence('docx', segments)
        limitations.append('DOCX body text and tables only; headers, footers, footnotes, comments, tracked '
                           'deletions and embedded images/charts were not extracted.')
        metadata['paragraphs'] = counters['paragraph']
        return Extraction(evidence, limitations, flags, metadata, 'docx_text')
