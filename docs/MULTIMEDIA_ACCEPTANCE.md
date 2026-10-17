# Multimedia acceptance: Lucius Fox source acquisition (tests A–F)

Run on 2026-10-17 from branch `claude/fox-multimedia-acceptance-651330` (based on `feat/research-line`), on Hayden's Mac
(Python 3.14.3). Every test below is a **real job** run through the same interface as Fox's worker:

```bash
python3 scripts/research.py --data /Users/haydensnyder/Git/alfred-research-intelligence/data/multimedia-acceptance \
  submit <url-or-file> --question "<objective>" --provider extractive --run
```

The `extractive` provider needs no model key. Its findings are keyword-ranked verbatim quotes, so they show what was
**acquired and cited**, not how good the analysis is. Verification ran in a separate process against the pinned snapshot
for every job.

**Where the outputs are.** The job store, snapshots and reports are outside git, in
`/Users/haydensnyder/Git/alfred-research-intelligence/data/multimedia-acceptance/` (the main checkout's gitignored
`data/`). Each job has a folder `<job-id>/` holding `report.md`, the byte snapshot (`1-source.*`, `1-youtube.json`,
`1-github.json`, `1-instagram.html`) and `memory-candidate.json`. Inspect a job with
`scripts/research.py --data <dir> show|report <job-id>`. Copies of the local input files are in `inputs/`. Third-party
content is not committed. This document records hashes instead.

## Results

| Test | Source | Job | Result | Live or mocked |
|---|---|---|---|---|
| A article | simonwillison.net "Things we learned about LLMs in 2024" | `research-3250cbaadec94be6bd529f9ce69e427c` | **pass** (after fix 1) | live |
| B YouTube | 3Blue1Brown `aircAruvnKk` (creator captions) | `research-b866497390b3490bbfd137ed1e381992` | **pass** (after fix 2) | live |
| C Instagram Reel | NASA Reel `Dbn-XJhk0_-` | `research-ea6ed362e31f4c9a8099eaa98ef348f3` | **pass**, caption only | live |
| C inaccessible | non-existent Reel `DZzzzzzzzz1` | `research-096c50821288482587b58873e4d93ed9` | **pass**, honest refusal | live |
| D PDF URL | arXiv 1706.03762 "Attention Is All You Need" | `research-1526ecd16ade4bb0806ee030e667ccdf` | **pass** | live |
| D local PDF | NIST CSWP 29 (CSF 2.0), local file | `research-dfce6ea1bb9a4a87b9a61b9ae264ed65` | **pass** (after fix 3) | live |
| D image-only PDF | page 1 of CSF 2.0 rasterized (PNG→PDF with `sips`) | `research-c45efc274c974358a611fdc937f4946a` | **pass**, honest refusal | live |
| E DOCX | `Fox Acceptance Brief.docx` (own content, made with `textutil`) | `research-c03b776dd9a34ef39edd5227743dfbb4` | **pass** | live |
| E TXT | RFC 9309 plain text | `research-7f2e38ac4fa7402caff74b53065f2125` | **pass** (after fix 4) | live |
| E Markdown | copy of `docs/MULTIMEDIA_V1_SOURCES.md` | `research-fc5cb184b7a844649a7fce779ebc2590` | **pass** (after fix 4) | live |
| E unsupported | `scan.png`, `budget.xlsx` | `research-dee69590623046e8a3cbe325f1f96b66`, `research-9129841eed724291b28108f94e9d5ed2` | **pass**, refused | live |
| F GitHub | `pallets/itsdangerous` | `research-ebf1cffebaa7429095899596d0ede3da` | **pass** | live |
| Telegram upload | NIST PDF and DOCX saved as `file_41`/`file_42`, plus `budget.xlsx` | `research-4b155afe1e5845c093ebb53253013b2d`, `research-93f6afffc22c45948854708b69773eec` | **pass** | live (local files; no Telegram API) |

Mocked regression tests for each fix are in `tests/test_multimedia_acceptance.py`.

## Per test: what was actually extracted

### A. Public article
- Source: `https://simonwillison.net/2024/Dec/31/llms-in-2024/`. Snapshot SHA-256 `45af4320d5c855968697e97d4411439e79a15d4164cf945eab2f7c9cf70577c8`, 79,380 bytes. Report SHA-256 prefix `ab8389ee278ebb6c`.
- Extracted: 270 paragraph blocks of visible article text from the page's content container, plus title and author metadata. Citations look like `article:html-line101`.
- **Failure found on the first run** (`research-95b3d17c3af4448fa4e4ea86412776c1`): a "Sponsor me for $10/month" promo box became finding C1. The page has no `<article>` or `<main>`, so the whole page was used. **Fix 1:** with no `<article>`/`<main>`, take the innermost content-class container (`entry`, `post`, `content`, …) that holds at least 80% of the text such containers hold. Also treat `sponsor`, `sponsored` and `secondary` as boilerplate. On the rerun, all four findings come from the essay.
- Limitations: JavaScript is not run. The `prompt_injection_candidate:article` flag was raised (the article quotes prompts) and is shown in the report. The text is treated as data.

### B. YouTube with captions
- Source: `https://www.youtube.com/watch?v=aircAruvnKk`. Snapshot `cfbc2a57afc1277a70c3d5c3ff383c3f47fcd50f9c9991243af5a93679f203a4`, 42,407 bytes. Report prefix `a6530d4fd9dfb621`.
- Extracted: the creator-provided English caption track as 23 timed windows (`youtube:t=00:13:26-00:14:17`), plus the creator description. The description is labelled "not spoken content". Metadata: title, channel, published date, duration 1120 s.
- **Failure found on the first run** (`research-db699c60128c4a0e81412bfa2806dc57`, an honest `unsupported`): the web player's caption URLs now need a proof-of-origin token and return an empty body. **Fix 2:** when the web track is empty, ask YouTube's public player API using the Android client context (an unauthenticated POST, no credentials). Its caption URLs still serve text. `caption_source` in provenance records which path was used. If both paths return nothing, the job stays `unsupported` and says "No findings were inferred from the title".
- Limitations (stated in the report): the video was not watched, so visuals and on-screen text are not covered. Auto-generated tracks carry a misrecognition warning. The Android-client path is an undocumented YouTube behaviour and may stop working. If it does, the job degrades to the honest refusal.

### C. Instagram Reel
- Accessible: `https://www.instagram.com/reel/Dbn-XJhk0_-/` (NASA, "Lunar landers, assemble."). Snapshot `19283045083abdbcda5eb4a75835a015292e421c7f6521e16f622f0e408e8092`, 626,676 bytes. Report prefix `0c9803185654065d`.
- Extracted: **only** the public caption from page metadata (`og:description`, here the full caption with an engagement-count prefix) as one evidence item, `instagram:caption-metadata`. Evidence basis `caption_metadata_only`. The report and the Fox reply both say: "The Reel or post media was not watched or transcribed".
- Inaccessible: `https://www.instagram.com/reel/DZzzzzzzzz1/` → status `unsupported`, no report, no findings. Fox's reply (from `final_message`) reads: "Research stopped: unsupported source … Instagram returned no public caption (login wall, private or removed post), so the Reel/post was not watched and its caption was not read. … Nothing was inferred or reported as findings."
- Small fix: page titles that span several lines are collapsed to one line (they were breaking the report's Sources list). The caption is taken from `og:title` only when that field is longer than the description.
- Limitations: an unsupported job writes no `report.md`, so the refusal text lives in the job's `error` field and in Fox's reply. See the follow-ups.

### D. PDF
- URL: `https://arxiv.org/pdf/1706.03762`. Snapshot `bdfaa68d8984f0dc02beaca527b76f207d99b666d31d1da728ee0728182df697`, 2,215,244 bytes, 15 pages. Report prefix `c7ddb42f4ea726ad`. Citations look like `pdf:page-2/block-2`.
- Local file: NIST CSWP 29 (`https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf`, downloaded, then submitted as a local path). SHA-256 `3c31f46fee98cac0c4323453e5109291a213b4de7fef8c058af9bf67f717433c`, 32 pages. Report prefix `7b5a66c203483954`. Citations: `pdf:page-10`, `pdf:page-15/block-1`, `pdf:page-20/block-1`, `pdf:page-28`.
- **Failure found on the first run** (`research-aa2a196cd94d42f8a45ba53feef98503`): 17 of 32 pages were reported as "without extractable text", and there were zero findings. The PDF came from Word. Its simple TrueType fonts carry ToUnicode CMaps that declare a 2-byte codespace, so the decoder read 1-byte codes in pairs and produced nothing. **Fix 3:** simple (non-Type0) fonts always use 1-byte codes. All pages now extract.
- Image-only: `scanned-nist-csf2-page1.pdf` (SHA-256 `6d7b1a500e868e52b342982b4098c92d370b6be3a0e9288a19de7eab699a008f`) → `unsupported`: "PDF has no text layer (likely scanned or image-only; OCR is not installed); no findings generated."
- Limitations: page numbers are physical PDF page indexes, not printed page labels (CSF "page 5" is `page-10`). Spacing is reconstructed from text positioning, so small caps can split (`G OVERN`). There is no OCR. Figures and charts are not read.

### E. Documents
- DOCX: `Fox Acceptance Brief.docx`, SHA-256 `6a32533eca3db2e226d32b616e9529d15f44b2c9d091b9be089ca038ca544723`. 12 evidence items cited as `docx:paragraph-N`. `textutil` writes table cells as paragraphs, so the table rows are cited as paragraphs too. Provenance: `origin owner_file`, `path`, and (new) `original_filename`.
- TXT: RFC 9309, SHA-256 `f633915daaa15b943cae56545d333bcf3ba4d156599e4555499686d6699fb207`. Citations: `text:lines-14-23`, `text:lines-247-259`, ….
- Markdown: SHA-256 `6f69c94778384f3d2b5f7fef01bea889b7e14dbc751d526e7e9c082651944b03`. Citations: `text:lines-7-14`, ….
- **Weakness found on the first run** (`research-fb95c9c1042f4d52aaed0824de14bd46`): text files became 100-line blocks, so a citation pointed to a 100-line range, and the RFC's first quote began with a byte-order mark and blank lines. **Fix 4:** text, Markdown, CSV and VTT/SRT are now split into blank-line paragraphs, with small ones merged and long ones split. Each paragraph is cited by its exact 1-based line range, and the BOM is stripped.
- Unsupported: `.png` and `.xlsx` → `unsupported`, with the supported-format list and "Unsupported file type: .png/.xlsx". Nothing is analyzed.
- Limitations: DOCX headers, footers, footnotes, comments and images are not extracted (stated in each report). Text files must be UTF-8.

### F. GitHub repository (read-only)
- Source: `https://github.com/pallets/itsdangerous`, pinned to revision `672971d66a2ef9f85151e53283113f33d642dabd`. Snapshot `d29447916871f9ede251b07c737e458e813b017e7fa20cfbbaccb24684562692`. Report prefix `2911e8f77aa4cc3d`.
- Extracted: repository metadata (description, languages, BSD-3-Clause license, stars), the layout of all 50 paths, and the text of 24 key files: README, LICENSE, pyproject.toml, the `src/itsdangerous/*.py` modules, workflows and tests. Citations look like `github:src/itsdangerous/exc.py#L1-L80`. Flags: `declared_dependencies:pyproject.toml`, `executable_file:.devcontainer/on-create-command.sh`.
- Read-only: the GitHub REST API and raw.githubusercontent.com were called with GET only and no token. Nothing was cloned, executed or installed. The report says so.
- Tried and reverted: also ranking `CHANGES.rst` and `docs/*.rst` as key docs made the extractive findings quote the changelog instead of the code (`research-f145686a7a424e7fb1145c587e9cf013`). The handler's original ranking was kept.
- Limitations: at most 30 files and 1.5 MB per snapshot. Only `.md` files under `docs/` count as docs. The unauthenticated API rate limit is 60 requests per hour.

## Telegram-uploaded files

Fox's Telegram connector will receive uploads as an opaque local file (for example `documents/file_41`) plus the
original file name. Research picks the extractor from the file suffix and reports the file name as provenance, so
uploads go through one new helper before the existing intake:

```python
from alfred_research.local.sources import stage_upload
from alfred_research.integration.message_intake import detect

staged = stage_upload(downloaded_path, original_filename, attachments_root)    # raises UnsupportedSource for .xlsx/.png/...
intent = detect(caption_text, [{'path': staged, 'filename': original_filename}], [attachments_root], dedicated=True)
reply = desk.accept(intent, route, key)                                         # unchanged ResearchDesk / ResearchLine
```

`stage_upload` copies the bytes to `attachments_root/<sha256[:16]>/<sanitized original name>`, with mode 0600 in an
owner-only folder. It sanitizes the name (no path components) and refuses unsupported types before any job exists.
Each handler still validates the content: a PNG renamed to `.pdf` fails with "missing %PDF header". Live run:
`NIST.CSWP.29.pdf` (from `file_41`) and `Fox Acceptance Brief.docx` (from `file_42`) completed with
`provenance.original_filename` set. `budget.xlsx` was refused at staging. `research_line.py`, `desk.py` and
`message_intake.py` are unchanged. Connecting Telegram document messages to this helper is the Fox server session's
work: today `fox_connector.py` forwards text only.

## Code changes

- `local/documents.py`: article content-container selection and extra boilerplate tokens (fix 1). Paragraph and line-range text extraction (fix 4).
- `local/platforms.py`: YouTube player-API caption fallback (fix 2). Instagram single-line title, explicit "not watched" refusal wording, caption field recorded.
- `local/pdf.py`: 1-byte codes for simple fonts (fix 3).
- `local/sources.py`: `http_get(body=...)` for the one public POST (refuses redirected POSTs). `stage_upload`. `original_filename` in owner-file provenance. Removed the now-unused `legacy_text_extract`.
- Not touched: `local/workers.py`, `local/engine.py` (synthesis and report rendering), verification, `integration/research_line.py`, `integration/desk.py`.

## Follow-ups (outside this change's scope)

1. Unsupported and failed jobs write no `report.md`. The refusal lives in `error` and in Fox's reply. If a stored report is wanted for these jobs, the synthesis owner would add it in `engine.py`.
2. `final_message` labels a source by its metadata title or else its full locator. A DOCX with no core title shows the staged path, so it could fall back to `provenance.original_filename` (`desk.py`, Fox server session).
3. Wire Telegram `document` messages in `fox_connector.py` to `stage_upload` (Fox server session).
4. The extractive worker's quotes include PDF running headers ("NIST CSWP 29 … February 26, 2024"). Stripping repeated page headers would sharpen the quotes.
