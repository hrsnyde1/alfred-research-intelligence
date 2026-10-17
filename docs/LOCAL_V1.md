# Functional local Research V1

Run from the repository. No package install, Photon connection, service change, or new credentials are needed.

```sh
python3 scripts/research.py submit https://www.rfc-editor.org/rfc/rfc9110.txt \
  --question 'What does HTTP specify about idempotent methods and automatic retries?' --run
python3 scripts/research.py list
python3 scripts/research.py show JOB_ID
python3 scripts/research.py report JOB_ID
python3 scripts/research.py candidate JOB_ID
```

`submit` queues by default; `--run` executes immediately. `run JOB_ID` executes a queued job once. `--request-key` deduplicates identical submissions and rejects changed inputs. Supply `--data DIRECTORY` before the command to change the working directory. The optional installed command is `alfred-research`; `PYTHONPATH=src python3 -m alfred_research` also works.

Submit articles, documents, and questions:

```sh
python3 scripts/research.py submit article.txt --question 'What are the implications?' --run
python3 scripts/research.py submit 'Analyze this article' --text 'Actual article text here' --run
python3 scripts/research.py submit 'Compare the proposals' --source https://example.org/proposal \
  --source proposal.md --run
python3 scripts/research.py submit 'HTTP idempotent methods' --run
python3 scripts/research.py submit captions.vtt --question 'Summarize this supplied transcript' --run
```

Questions without sources use a bounded real Wikipedia public search (two results). This is limited discovery, not exhaustive primary-source research. A blocked/empty search yields `needs_sources`, with the search error preserved. Supplying relevant primary-source URLs is more reliable. At most four explicit sources plus one pasted article are accepted. Only public HTTPS URLs are fetched; redirects, certificates, addresses, body sizes, and deadlines are checked. Linked pages and JavaScript are not fetched/rendered. Raw snapshots, acquisition provenance, digest, and extraction limitations are retained.

Web articles (boilerplate-stripped HTML), PDF text layers with page citations, DOCX, UTF-8 text/Markdown/CSV, VTT/SRT transcripts, public GitHub repositories (read-only, pinned to a commit), YouTube videos whose captions are accessible, and public Instagram captions are handled by per-format `SourceHandler`s; see [MULTIMEDIA_V1_SOURCES.md](MULTIMEDIA_V1_SOURCES.md). Long text documents are processed in bounded line-range chunks. Scanned PDFs (no OCR), legacy `.doc`/Office formats, and videos without accessible captions are reported as unsupported rather than guessed. A real user-supplied transcript is supported as a document; it is never represented as video viewing or an authenticated YouTube transcript.

`--provider auto` uses the installed Codex CLI when its existing login is available; otherwise it selects the deterministic extractive worker. `--provider codex` requires that provider and fails without fabricated fallback. `--provider extractive` needs no model credentials and produces explicitly attributed quotations with keyword ranking, not semantic model research. Model execution is ephemeral and read-only, using the existing Codex authentication; source excerpts are sent to that provider. Raw provider diagnostics and credentials are not stored. Local execution metadata includes prompt/output hashes, timing, session identity and usage when supplied by the CLI; these are not Memory trust attestations.

The Director reuses existing specialty classification and assigns one worker per acquired source. Model workers select up to four findings per source from at most 40 ranked excerpts / 48,000 characters. A separate Python process re-extracts raw snapshots and checks digests, evidence identities and exact quotes. In Codex mode a separate model session checks claim entailment and recommendation support. It does not receive the original worker's reasoning. Verification establishes **source support**, not independent corroboration, source authenticity, or guaranteed real-world truth. Inferences remain labeled and excluded from Memory candidates.

Reports contain every finding's verification outcome, citations, quotations, recommendations, acquisition provenance, unknowns and limitations. Failed claims remain visible as `NOT VERIFIED`; unsupported recommendations are withheld. Any failed acquisition or rejected claim makes the job `needs_more_research`. `completed` means the local source-supported report completed; it does not mean Memory promotion, exhaustive investigation, or external factual attestation.

Working state lives in `data/research-v1/jobs.sqlite3` and per-job snapshot/report/candidate files. It is Research persistence, not a second authoritative Memory. SQLite stores request, stage history and immutable stage artifacts. Retrieval works in a fresh CLI process. No scheduler or service is required. Job execution is locked; provider calls and acquisition are bounded. Failures preserve completed stages. After a hard process kill, `recover JOB_ID` can mark an abandoned job interrupted; it refuses a still-locked running job. Submit a new job to retry rather than replaying unknown provider effects.

## Memory and Hermes boundaries

The observed installed Memory release is `/opt/alfred-obsidian-v1/releases/4d5ba29bd3027e74c808a8feaf1b5dadfded22f0`; the active service is `alfred-memory-v1.service`. Its generic `/v1/memory` actions include create/review/search but no live Research candidate/commit/promote API. `focused_v1/research_stage.py` is absent in that release. Generic create may auto-approve and must not substitute for Research promotion. The existing Phase 7G contract also requires independently trusted verification, approval, exact packet binding and currentness rules.

`AuthoritativeMemoryAdapter` validates and preserves pending source-supported candidate packets and refuses submit/promote with an explicit blocker. `promote JOB_ID` therefore returns an error and makes no external call. Pending candidates are not authorized knowledge, not Memory receipts, and not proof of persistence in Memory. Installing/authorizing the Memory-owned Research interface and attestation policy is the external blocker; no Obsidian exports or Memory databases are written.

`integration.local_research.LocalResearchEntryPoint` provides `submit`, `execute`, and `retrieve` for future authenticated Hermes tool registration. Host-issued request IDs provide idempotency. It is an in-process seam, not a network listener or an authorization boundary. Registration in Personal Hermes and production deployment remain separate approval tasks. Personal Photon, Hermes, and Memory service activation are untouched.

## Validation

```sh
python3 -m unittest discover -s tests -q
```

The local tests distinguish real owner-file processing and separate-process verification from explicitly mocked failure/model-response tests. The real public-source demonstration and its provider execution evidence are recorded separately in `LOCAL_V1_DEMONSTRATION.json`.
