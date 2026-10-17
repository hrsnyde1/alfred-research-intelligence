"""PDF text-layer extraction with page references, standard library only.

Deliberately partial: classic objects and compressed object streams, Flate,
LZW, ASCIIHex and ASCII85 filters, ToUnicode CMaps and simple font encodings.
There is no OCR. Image-only (scanned) pages and undecodable fonts are reported
as limitations; text is never guessed.
"""
import base64
import re
import zlib

from .sources import BINARY_MAX_BYTES, Extraction, SourceHandler, UnsupportedSource, text_evidence

WHITESPACE = b' \t\r\n\f\x00'
DELIMITERS = b'()<>[]{}/%'
NUMBER = re.compile(rb'[+-]?(?:\d+\.?\d*|\.\d+)')
OBJECT = re.compile(rb'(\d+)\s+(\d+)\s+obj\b')
MAX_DECODED = 60_000_000
MAX_PAGES = 1000


class PDFError(ValueError):
    pass


class Name(str):
    pass


class Keyword(bytes):
    pass


class Ref(tuple):
    pass


class Stream:
    def __init__(self, dictionary, raw):
        self.dict, self.raw = dictionary, raw


def skip_space(data, pos):
    while pos < len(data):
        c = data[pos]
        if c in WHITESPACE:
            pos += 1
        elif c == 0x25:  # % comment
            end = data.find(b'\n', pos)
            pos = len(data) if end < 0 else end + 1
        else:
            break
    return pos


def literal_string(data, pos):
    out, depth = bytearray(), 1
    pos += 1
    escapes = {ord('n'): b'\n', ord('r'): b'\r', ord('t'): b'\t', ord('b'): b'\b', ord('f'): b'\f'}
    while pos < len(data):
        c = data[pos]
        if c == 0x5C:  # backslash
            pos += 1
            if pos >= len(data):
                break
            e = data[pos]
            if e in escapes:
                out += escapes[e]
            elif 0x30 <= e <= 0x37:
                digits = data[pos:pos + 3]
                n = 1
                while n < len(digits) and 0x30 <= digits[n] <= 0x37:
                    n += 1
                out.append(int(digits[:n], 8) & 0xFF)
                pos += n - 1
            elif e == 0x0D:
                if data[pos + 1:pos + 2] == b'\n':
                    pos += 1
            elif e != 0x0A:
                out.append(e)
            pos += 1
            continue
        if c == 0x28:
            depth += 1
        elif c == 0x29:
            depth -= 1
            if depth == 0:
                return bytes(out), pos + 1
        out.append(c)
        pos += 1
    raise PDFError('unterminated string')


def token(data, pos):
    """Next (token, position). Tokens: numbers, Name, bytes, Keyword, or structural markers."""
    pos = skip_space(data, pos)
    if pos >= len(data):
        return None, pos
    c = data[pos:pos + 1]
    if c == b'(':
        return literal_string(data, pos)
    if data.startswith(b'<<', pos):
        return Keyword(b'<<'), pos + 2
    if data.startswith(b'>>', pos):
        return Keyword(b'>>'), pos + 2
    if c == b'<':
        end = data.find(b'>', pos)
        if end < 0:
            raise PDFError('unterminated hex string')
        digits = re.sub(rb'[^0-9A-Fa-f]', b'', data[pos + 1:end])
        if len(digits) % 2:
            digits += b'0'
        return bytes.fromhex(digits.decode()), end + 1
    if c in (b'[', b']', b'{', b'}'):
        return Keyword(c), pos + 1
    if c == b'/':
        end = pos + 1
        while end < len(data) and data[end] not in WHITESPACE and data[end] not in DELIMITERS:
            end += 1
        raw = re.sub(rb'#([0-9A-Fa-f]{2})', lambda m: bytes([int(m.group(1), 16)]), data[pos + 1:end])
        return Name(raw.decode('latin-1')), end
    end = pos
    while end < len(data) and data[end] not in WHITESPACE and data[end] not in DELIMITERS:
        end += 1
    if end == pos:
        return Keyword(c), pos + 1
    word = data[pos:end]
    if NUMBER.fullmatch(word):
        return (float(word) if b'.' in word else int(word)), end
    return Keyword(word), end


def value(data, pos, depth=0):
    if depth > 64:
        raise PDFError('nesting too deep')
    item, pos = token(data, pos)
    if isinstance(item, Keyword):
        if item == b'<<':
            result = {}
            while True:
                key, after = token(data, pos)
                if key is None:
                    raise PDFError('unterminated dictionary')
                if key == Keyword(b'>>'):
                    return result, after
                if not isinstance(key, Name):
                    pos = after
                    continue
                result[str(key)], pos = value(data, after, depth + 1)
        if item == b'[':
            result = []
            while True:
                peek, after = token(data, pos)
                if peek is None:
                    raise PDFError('unterminated array')
                if peek == Keyword(b']'):
                    return result, after
                element, pos = value(data, pos, depth + 1)
                result.append(element)
        if item in (b'true', b'false'):
            return item == b'true', pos
        if item == b'null':
            return None, pos
    if isinstance(item, int) and not isinstance(item, bool):
        second, after = token(data, pos)
        if isinstance(second, int):
            third, after2 = token(data, after)
            if third == Keyword(b'R'):
                return Ref((item, second)), after2
    return item, pos


def lzw(data):
    table = [bytes([i]) for i in range(256)] + [b'', b'']
    out, bits, buffer, width, previous = bytearray(), 0, 0, 9, None
    for byte in data:
        buffer = (buffer << 8) | byte
        bits += 8
        while bits >= width:
            bits -= width
            code = (buffer >> bits) & ((1 << width) - 1)
            if code == 256:
                table, width, previous = table[:258], 9, None
                continue
            if code == 257:
                return bytes(out)
            if code < len(table):
                entry = table[code]
                if previous is not None:
                    table.append(previous + entry[:1])
            elif previous is not None:
                entry = previous + previous[:1]
                table.append(entry)
            else:
                raise PDFError('bad LZW stream')
            out += entry
            if len(out) > MAX_DECODED:
                raise PDFError('decoded stream too large')
            previous = entry
            if len(table) + 1 >= (1 << width) and width < 12:
                width += 1
    return bytes(out)


def decode_stream(stream, resolve):
    filters = resolve(stream.dict.get('Filter'))
    filters = filters if isinstance(filters, list) else ([filters] if filters else [])
    data = stream.raw
    for name in filters:
        name = resolve(name)
        if name in ('FlateDecode', 'Fl'):
            inflater = zlib.decompressobj()
            try:
                data = inflater.decompress(data, MAX_DECODED)
            except zlib.error:
                raise PDFError('corrupt Flate stream')
            if inflater.unconsumed_tail:
                raise PDFError('decoded stream too large')
        elif name in ('LZWDecode', 'LZW'):
            data = lzw(data)
        elif name in ('ASCIIHexDecode', 'AHx'):
            digits = re.sub(rb'[^0-9A-Fa-f]', b'', data.split(b'>')[0])
            data = bytes.fromhex((digits + b'0' * (len(digits) % 2)).decode())
        elif name in ('ASCII85Decode', 'A85'):
            body = re.sub(rb'\s', b'', data)
            body = body[2:] if body.startswith(b'<~') else body
            body = body.split(b'~>')[0]
            data = base64.a85decode(body)
        else:
            return None  # image codecs and unsupported filters carry no text
    return data


class Document:
    def __init__(self, data):
        if not data.startswith(b'%PDF-'):
            raise UnsupportedSource('Not a PDF file (missing %PDF header); no findings generated.')
        if re.search(rb'/Encrypt\s*(?:\d+\s+\d+\s+R|<<)', data):
            raise UnsupportedSource('Encrypted PDF; decryption is not supported, so no findings were generated.')
        self.data, self.objects = data, {}
        entries, pos = [], 0
        while True:
            match = OBJECT.search(data, pos)
            if not match:
                break
            try:
                item, end = value(data, match.end())
                after = skip_space(data, end)
                if isinstance(item, dict) and data.startswith(b'stream', after):
                    start = after + 6
                    start += 2 if data.startswith(b'\r\n', start) else (1 if data[start:start + 1] in (b'\n', b'\r') else 0)
                    length = item.get('Length')
                    stop = start + length if isinstance(length, int) else -1
                    if not (isinstance(length, int) and data.startswith(b'endstream', skip_space(data, stop))):
                        stop = data.find(b'endstream', start)
                        if stop < 0:
                            raise PDFError('unterminated stream')
                        raw = data[start:stop].rstrip(b'\r\n')
                    else:
                        raw = data[start:stop]
                    item, end = Stream(item, raw), data.find(b'endstream', stop) + 9
                entries.append((match.start(), 0, int(match.group(1)), item))
                pos = max(end, match.end())
            except (PDFError, ValueError, IndexError, RecursionError):
                pos = match.end()
        # Objects inside compressed object streams take their container's position.
        for position, _, _, item in list(entries):
            if isinstance(item, Stream) and item.dict.get('Type') == 'ObjStm':
                try:
                    body = decode_stream(item, self.resolve_direct)
                    first, count = int(item.dict['First']), int(item.dict['N'])
                    header, cursor = [], 0
                    for _ in range(2 * count):
                        number, cursor = token(body, cursor)
                        header.append(number)
                    for index in range(count):
                        number, offset = header[2 * index], header[2 * index + 1]
                        inner, _ = value(body, first + offset)
                        entries.append((position, index + 1, number, inner))
                except (PDFError, ValueError, KeyError, TypeError, IndexError, RecursionError):
                    continue
        for _, _, number, item in sorted(entries, key=lambda e: (e[0], e[1])):
            self.objects[number] = item

    def resolve_direct(self, item):
        return item

    def resolve(self, item, depth=0):
        while isinstance(item, Ref) and depth < 32:
            item, depth = self.objects.get(item[0]), depth + 1
        return item

    def trailer_ref(self, key):
        matches = re.findall(rb'/' + key + rb'\s+(\d+)\s+\d+\s+R', self.data)
        return self.resolve(Ref((int(matches[-1]), 0))) if matches else None

    def pages(self):
        found, seen = [], set()

        def walk(node, resources, depth):
            node = self.resolve(node)
            if not isinstance(node, dict) or id(node) in seen or depth > 64 or len(found) >= MAX_PAGES:
                return
            seen.add(id(node))
            resources = self.resolve(node.get('Resources')) or resources
            kids = self.resolve(node.get('Kids'))
            if isinstance(kids, list):
                for kid in kids:
                    walk(kid, resources, depth + 1)
            elif node.get('Type') == 'Page' or 'Contents' in node:
                found.append((node, resources or {}))

        catalog = self.trailer_ref(b'Root')
        if not isinstance(catalog, dict):
            catalog = next((o for o in self.objects.values() if isinstance(o, dict) and o.get('Type') == 'Catalog'), None)
        if isinstance(catalog, dict):
            walk(catalog.get('Pages'), {}, 0)
        if not found:
            found = [(o, self.resolve(o.get('Resources')) or {}) for o in self.objects.values()
                     if isinstance(o, dict) and o.get('Type') == 'Page'][:MAX_PAGES]
        return found

    def info(self):
        info = self.trailer_ref(b'Info')
        metadata = {}
        if isinstance(info, dict):
            for key, field in (('Title', 'title'), ('Author', 'author'), ('Subject', 'subject'),
                               ('CreationDate', 'created_at')):
                text = self.resolve(info.get(key))
                if isinstance(text, bytes):
                    decoded = pdf_string(text).strip()
                    if decoded:
                        metadata[field] = decoded[:500]
        return metadata


def pdf_string(raw):
    if raw.startswith(b'\xfe\xff'):
        return raw[2:].decode('utf-16-be', 'replace')
    return raw.decode('latin-1')


GLYPHS = {'space': ' ', 'period': '.', 'comma': ',', 'hyphen': '-', 'colon': ':', 'semicolon': ';',
          'quoteright': '’', 'quoteleft': '‘', 'quotedblleft': '“', 'quotedblright': '”',
          'endash': '–', 'emdash': '—', 'fi': 'fi', 'fl': 'fl', 'ff': 'ff', 'parenleft': '(',
          'parenright': ')', 'slash': '/', 'question': '?', 'exclam': '!', 'quotesingle': "'", 'bullet': '•',
          'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5', 'six': '6',
          'seven': '7', 'eight': '8', 'nine': '9', 'percent': '%', 'ampersand': '&', 'dollar': '$'}


class Font:
    def __init__(self, font, document):
        resolve = document.resolve
        self.cmap, self.width, self.codec, self.differences = {}, 1, 'cp1252', {}
        self.undecodable = False
        subtype = resolve(font.get('Subtype'))
        encoding = resolve(font.get('Encoding'))
        unicode_map = resolve(font.get('ToUnicode'))
        if subtype == 'Type0':
            self.width = 2
        if isinstance(unicode_map, Stream):
            try:
                self.parse_cmap(decode_stream(unicode_map, resolve) or b'')
            except (PDFError, ValueError):
                self.cmap = {}
        if subtype != 'Type0':
            # Simple fonts always use one-byte codes, even when their ToUnicode
            # CMap declares a two-byte codespace (common in Word exports).
            self.width = 1
        if isinstance(encoding, dict):
            base = resolve(encoding.get('BaseEncoding'))
            code = None
            for item in resolve(encoding.get('Differences')) or []:
                if isinstance(item, int):
                    code = item
                elif isinstance(item, Name) and code is not None:
                    glyph = GLYPHS.get(item) or (item if len(item) == 1 else None)
                    if item.startswith('uni') and len(item) == 7:
                        try:
                            glyph = chr(int(item[3:], 16))
                        except ValueError:
                            pass
                    if glyph:
                        self.differences[code] = glyph
                    code += 1
            encoding = base
        if encoding == 'MacRomanEncoding':
            self.codec = 'mac_roman'
        if subtype == 'Type0' and not self.cmap:
            self.undecodable = True  # CID glyph codes without ToUnicode cannot be mapped honestly

    def parse_cmap(self, text):
        space = re.search(rb'begincodespacerange\s*<([0-9A-Fa-f]+)>', text)
        if space:
            self.width = max(1, len(space.group(1)) // 2)
        for block in re.findall(rb'beginbfchar(.*?)endbfchar', text, re.S):
            for source, target in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]*)>', block):
                self.cmap[int(source, 16)] = utf16(target)
        for block in re.findall(rb'beginbfrange(.*?)endbfrange', text, re.S):
            for low, high, target in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(<[0-9A-Fa-f]*>|\[[^\]]*\])', block):
                low, high = int(low, 16), int(high, 16)
                if high < low or high - low > 65535:
                    continue
                if target.startswith(b'['):
                    for offset, item in enumerate(re.findall(rb'<([0-9A-Fa-f]*)>', target)):
                        self.cmap[low + offset] = utf16(item)
                else:
                    digits = target[1:-1]
                    base = int(digits or b'0', 16)
                    size = max(2, len(digits) // 2)
                    for offset in range(high - low + 1):
                        self.cmap[low + offset] = (base + offset).to_bytes(size, 'big').decode('utf-16-be', 'replace')

    def decode(self, raw):
        if self.undecodable:
            return None
        if self.cmap:
            out = []
            for index in range(0, len(raw) - self.width + 1, self.width):
                code = int.from_bytes(raw[index:index + self.width], 'big')
                if code in self.cmap:
                    out.append(self.cmap[code])
                elif self.width == 1:
                    out.append(self.differences.get(code) or bytes([code]).decode(self.codec, 'replace'))
            return ''.join(out)
        return ''.join(self.differences.get(b) or bytes([b]).decode(self.codec, 'replace') for b in raw)


def utf16(digits):
    try:
        return bytes.fromhex(digits.decode()).decode('utf-16-be', 'replace') if digits else ''
    except ValueError:
        return ''


class PageReader:
    def __init__(self, document):
        self.document, self.fonts, self.undecodable = document, {}, 0

    def font(self, resources, name):
        fonts = self.document.resolve((resources or {}).get('Font')) or {}
        reference = fonts.get(str(name)) if isinstance(fonts, dict) else None
        font = self.document.resolve(reference)
        if not isinstance(font, dict):
            return None
        key = reference[0] if isinstance(reference, Ref) else id(font)
        if key not in self.fonts:
            self.fonts[key] = Font(font, self.document)
        return self.fonts[key]

    def content(self, page):
        contents = self.document.resolve(page.get('Contents'))
        streams = contents if isinstance(contents, list) else [contents]
        chunks = []
        for item in streams:
            stream = self.document.resolve(item)
            if isinstance(stream, Stream):
                decoded = decode_stream(stream, self.document.resolve)
                if decoded:
                    chunks.append(decoded)
        return b'\n'.join(chunks)

    def text(self, data, resources, depth=0):
        out, operands, font, pos, last_y = [], [], None, 0, None

        def show(raw):
            if not isinstance(raw, bytes):
                return
            if font is None:
                out.append(raw.decode('latin-1'))
                return
            decoded = font.decode(raw)
            if decoded is None:
                self.undecodable += 1
            else:
                out.append(decoded)

        def newline():
            if out and not out[-1].endswith('\n'):
                out.append('\n')

        while True:
            start = pos
            try:
                item, pos = token(data, pos)
            except PDFError:
                break
            if item is None:
                break
            if item == Keyword(b'[') or item == Keyword(b'<<'):
                try:
                    item, pos = value(data, start)
                except PDFError:
                    break
                operands.append(item)
                continue
            if not isinstance(item, Keyword):
                operands.append(item)
                continue
            op = bytes(item)
            if op == b'BI':
                match = re.compile(rb'\sEI(?=[\s]|$)').search(data, data.find(b'ID', pos) + 2)
                pos = match.end() if match else len(data)
            elif op == b'Tf' and len(operands) >= 2:
                font = self.font(resources, operands[-2])
            elif op == b'Tj' and operands:
                show(operands[-1])
            elif op in (b"'", b'"') and operands:
                newline()
                show(operands[-1])
            elif op == b'TJ' and operands and isinstance(operands[-1], list):
                for element in operands[-1]:
                    if isinstance(element, bytes):
                        show(element)
                    elif isinstance(element, (int, float)) and element < -180 and out and not out[-1].endswith((' ', '\n')):
                        out.append(' ')
            elif op in (b'Td', b'TD') and len(operands) >= 2:
                tx, ty = operands[-2], operands[-1]
                if isinstance(ty, (int, float)) and abs(ty) > 0.01:
                    newline()
                elif isinstance(tx, (int, float)) and tx > 0 and out and not out[-1].endswith((' ', '\n')):
                    out.append(' ')
            elif op == b'Tm' and len(operands) >= 6:
                if last_y is not None and operands[-1] != last_y:
                    newline()
                elif out and not out[-1].endswith((' ', '\n')):
                    out.append(' ')
                last_y = operands[-1]
            elif op in (b'T*', b'ET'):
                newline()
            elif op == b'Do' and operands and depth < 3:
                xobjects = self.document.resolve((resources or {}).get('XObject')) or {}
                form = self.document.resolve(xobjects.get(str(operands[-1]))) if isinstance(xobjects, dict) else None
                if isinstance(form, Stream) and form.dict.get('Subtype') == 'Form':
                    body = decode_stream(form, self.document.resolve)
                    if body:
                        inner = self.document.resolve(form.dict.get('Resources')) or resources
                        newline()
                        out.append(self.text(body, inner, depth + 1))
                        newline()
            operands = []
        return ''.join(out)


def clean(text):
    lines = [' '.join(line.split()) for line in text.replace('\r', '\n').split('\n')]
    return '\n'.join(line for line in lines if line)


def readable(text):
    if not text:
        return False
    good = sum(1 for c in text if c.isalnum() or c.isspace() or c in '.,;:!?\'"()-–—%$&/@#*+=[]{}<>’‘“”•…')
    return good / len(text) >= 0.85


def ranges(numbers):
    spans, start, previous = [], None, None
    for n in numbers:
        if start is None:
            start = previous = n
        elif n == previous + 1:
            previous = n
        else:
            spans.append((start, previous))
            start = previous = n
    if start is not None:
        spans.append((start, previous))
    return ', '.join(str(a) if a == b else str(a) + '-' + str(b) for a, b in spans)


class PDFHandler(SourceHandler):
    name, kind, suffixes, max_bytes = 'pdf', 'pdf', ('.pdf',), BINARY_MAX_BYTES

    def extract(self, data, filename):
        document = Document(data)
        pages = document.pages()
        if not pages:
            raise UnsupportedSource('No PDF pages could be parsed; no findings generated.')
        reader = PageReader(document)
        segments, empty, garbled = [], [], []
        for number, (page, resources) in enumerate(pages, 1):
            try:
                text = clean(reader.text(reader.content(page), resources))
            except (PDFError, ValueError, KeyError, TypeError, RecursionError):
                text = ''
            if not text.replace('\n', '').strip():
                empty.append(number)
                continue
            if not readable(text):
                garbled.append(number)
                continue
            # Paragraph-sized blocks keep quotes intact; every location names its page.
            block, blocks = [], []
            for line in text.split('\n'):
                if block and sum(len(x) for x in block) + len(line) > 1500:
                    blocks.append('\n'.join(block))
                    block = []
                block.append(line)
            blocks.append('\n'.join(block))
            for index, value in enumerate(blocks, 1):
                segments.append(('page-' + str(number) + ('' if len(blocks) == 1 else '/block-' + str(index)), value))
        metadata = {**document.info(), 'pages': len(pages)}
        if not segments:
            reason = ('no text layer (likely scanned or image-only; OCR is not installed)' if empty and not garbled
                      else 'text layer uses fonts that cannot be decoded reliably')
            raise UnsupportedSource('PDF has ' + reason + '; no findings generated.', metadata)
        evidence, limitations, flags = text_evidence('pdf', segments)
        limitations.insert(0, 'PDF text layer only: no OCR; figures, charts, images and scanned pages are not read. '
                              'Reading order and spacing are reconstructed and may differ from the visual layout.')
        if empty:
            limitations.append('Pages without extractable text (possibly scanned/image-only): ' + ranges(empty) + '.')
        if garbled or reader.undecodable:
            limitations.append('Text with undecodable fonts was omitted' +
                               (' (pages ' + ranges(garbled) + ')' if garbled else '') + '.')
        if len(pages) >= MAX_PAGES:
            limitations.append('Only the first ' + str(MAX_PAGES) + ' pages were processed.')
        return Extraction(evidence, limitations, flags, metadata, 'pdf_text_layer')
