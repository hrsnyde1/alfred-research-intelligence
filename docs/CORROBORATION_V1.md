# Independent corroboration (fact verification stage)

Lucius Fox's local engine used to check only that each finding is supported by the source it cites. It now adds a separate **fact verification** stage that looks for independent sources and classifies every claim.

## Pipeline position

`research workers` → `source-support verifier` (`workers.verify`, separate process) → **`corroboration`** (`local/verify.py`, its own separate process) → synthesis.

The stage gets the pinned sources, the claims and the source-support assessments. It never sees worker excerpts or prompts. The engine re-checks the result before storing it as job artifact `corroboration`: the packet hash, the claim identities, every citation's discovered source and SHA-256, and that each cited passage is re-extracted from the pinned snapshot. A job with a `contradicted` or `disputed` claim finishes as `needs_more_research`, not `completed`.

## Discovery (`local/discovery.py`)

- Providers that need no paid account: `WikipediaSearch` (MediaWiki API, identifying User-Agent, requests spaced 1 s apart), plus the pluggable `SearchProvider` interface with a `NoWebSearch` default. A web search API (for example Brave Search or Bing) would materially widen coverage beyond one encyclopedia. None is added here.
- A search hit is only a candidate. It becomes evidence only after its bytes are retrieved through the existing pinned HTTPS fetcher, snapshotted to `<job>/corroboration/D<n>-*` (mode 0600) and extracted by the existing source handlers. Search snippets are never evidence.
- Each discovered source records `url`, `final_url`, `publisher`, `publisher_key` (registrable domain), `retrieved_at`, `role` (`primary` for official/government/research-repository domains, otherwise `secondary`; Wikipedia counts as secondary), `role_basis`, `sha256`, `status` (`retrieved` or `unreachable`) and `error`.
- Independence: a source from the same publisher as the claim's original, a copy that repeats the original wording verbatim, a page that mostly duplicates the original text, and a sentence that attributes the claim to the original ("according to Example News…") are all listed as `non_independent` and never corroborate. Discovered sources that are syndicated copies of each other share one `independence_group`.
- Untrusted content: instruction-like sentences ("ignore previous instructions", "mark … as corroborated", `SYSTEM:`) are excluded from matching and flagged. No page text is ever interpreted as an instruction.
- Bounds: up to 8 claims per job, 3 candidates per claim per provider, 12 retrievals per job.

## Classification

| status | meaning |
|---|---|
| `corroborated` | Original source supports it, at least one independent publisher group supports it, and nothing contradicts it |
| `original_source_only` | Original source supports it; discovery finished, and no independent source addressed it |
| `disputed` | Independent support **and** contradiction; both sides are cited |
| `contradicted` | A discovered source contradicts it and none supports it |
| `unverified` | The original citation failed, or no independent check could finish (search error, unreachable candidates, discovery disabled) |
| `not_assessable` | An inference, too little checkable content, or beyond the per-job limit |

The stance check (`LexicalAssessor`) is deterministic and makes no model call. A sentence **supports** a claim when it shares at least 60% of the claim's content terms, contains every number in the claim, and has the same polarity. It **contradicts** a claim when it is on the same topic and either has opposite polarity with near-identical wording, or gives a different number of the same kind in the same context ("completed in 1899" vs "built for the 1889 Exposition"). Month and unit words do not count as shared context, numbers that belong to names ("Apollo 11") are identifiers, and a value inside a stated range is neither support nor contradiction. Paraphrase is not recognized, so a miss falls to `original_source_only`, never to support. Any object with `name` and `stance(claim_text, sentence) -> 'supports' | 'contradicts' | None` can replace it, for example a model judge from the fox-brain provider.

## Contract for report synthesis

The engine stores `job['artifacts']['corroboration']`. Load it with `VerificationResult.from_dict(...)`, which validates the schema and the statuses.

```python
VerificationResult(            # schema 'research.local.corroboration/1'
    packet_sha256: str,        # digest(claims) — binds to the research packet
    claims: tuple[ClaimVerification, ...],   # same order/ids as research claims
    sources: tuple[dict, ...], # DiscoveredSource payloads (see above), incl. unreachable ones
    method: str, providers: tuple[str, ...], limitations: tuple[str, ...],
    search_errors: tuple[dict, ...], worker: str, pid: int)
  .by_claim() -> {claim_id: ClaimVerification}
  .counts()   -> {status: n}
  .conflicts() -> [claim_id]   # disputed or contradicted

ClaimVerification(claim_id, statement, status, original_source_id, original_support: bool,
    supporting: tuple[Citation], contradicting: tuple[Citation], non_independent: tuple[Citation],
    unreachable: tuple[{'url', 'error'}], independent_groups: tuple[str], sources_checked: int,
    query: str, rationale: str)

Citation(discovery_id, url, publisher, retrieved_at, role, independence_group,
    stance,   # 'supports' | 'contradicts' | 'repeats_original'
    passage,  # exact sentence, re-found in the pinned snapshot by the engine
    location, sha256, note)
```

Claude synthesis (`director.synthesize` / `render_intelligence`) consumes this artifact: each finding's status goes to the synthesis prompt; Evidence and Citations and Verification Assessment show supporting and contradicting citations (URL and passage only) side by side; `conflicts()` claims are labelled in Important Findings and removed from Knowledge Candidates and from the Telegram summary's stated facts (a note names them instead). Without the artifact, the report says no corroboration was performed.

Rendering guidance: show `status` per finding and cite only `Citation.url` and `Citation.passage`. Show contradictions next to any support. List `unreachable` candidates and `limitations`. Never describe `original_source_only`, `unverified` or `non_independent` repetitions as corroboration. Memory publication excludes claims in `conflicts()`: `AuthoritativeMemoryAdapter.prepare` leaves them out of the candidate, and the desk withholds them again at publish time (recorded as `withheld` on the publication), so a candidate prepared before corroboration still never sends a conflicted claim. Each remaining candidate claim carries `corroboration: {status, independent_groups, note}`; `independent_groups` is non-zero only for `corroborated`, and a job without a corroboration artifact records `unverified`. The Memory record text says "independently corroborated" only for `corroborated` claims. Alfred Memory stays authoritative: these are candidates, not Memory records.

## Configuration

`ALFRED_RESEARCH_CORROBORATION=wikipedia` (default) or `off`. With `off`, the stage still runs and reports `unverified` with the reason. Unit tests set `off` and mock every network call.

## Live runs (2026-10-17, real Wikipedia, labeled LIVE)

- LIVE claim "The Eiffel Tower was completed in 1899 for the Exposition Universelle in Paris." → `contradicted`. It cites en.wikipedia.org/wiki/Gustave_Eiffel ("built for the 1889 Universal Exposition in Paris") and en.wikipedia.org/wiki/Eiffel_Tower ("temporary structure for the 1889 Exposition Universelle").
- LIVE claim "Apollo 11 landed the first humans on the Moon on July 20, 1969." → `original_source_only`. Three Wikipedia pages were checked, and the true claim is phrased differently from Wikipedia, so lexical matching did not confirm it. Earlier passes of this run surfaced false contradictions ("July 16" launch date, "Apollo 11" as a number), which led to the context, range and identifier rules above.
- LIVE: one run hit a Wikimedia HTTP 429. It was reported as `unreachable` with `search_errors` and status `unverified`, never as support. That run led to adding the identifying User-Agent and request spacing.
- LIVE end-to-end engine run (extractive, owner file "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France.") → job `completed`. The corroboration ran in a separate process; the result was `corroborated` by en.wikipedia.org/wiki/Eiffel_Tower. Two other Wikipedia pages repeating the original wording verbatim were recorded as non-independent.
