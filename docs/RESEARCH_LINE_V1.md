# Research line V1: text a link, grow Alfred's Memory

2026-10-16. **Built and tested locally; not installed or activated.** This change made no server writes, credential handling, Photon session, live message or Memory write. Owner decision (Hayden, 2026-10-16): Research V1 runs on the **dedicated Research Photon line (+1 415 225-0168)**, not the Personal Alfred conversation, and verified findings are **published to Alfred's Memory as auto-approved**, overriding the earlier "research approval ≠ Memory promotion" rule. Personal Alfred integration (`integration/hermes_research.py`) is parked for a later release.

## Flow

```
owner iMessage → Research line (+1 415 225-0168)
  → alfred-research-photon.service  (Node; authenticates the Research Photon project, accepts only the bound
                                      conversation + sender, stores each text durably as a pending record)
  → alfred-research-line.service    (Python; same service account; polls pending records)
       detect → acknowledgement → ResearchEngine (acquire, workers, separate verifier, cited report)
       → MemoryServicePublisher → POST 127.0.0.1:<port>/v1/memory  create(kind, task research-line)
       → final cited summary
  → outbox/ → connector sends each reply once → owner iMessage
Alfred (Hermes memory plugin) → Memory search → approved research findings
```

## Components

| Path | What |
|---|---|
| `src/alfred_research/integration/research_line.py`, `scripts/research_line.py` | Worker. Polls `research.connector.pending/1` records in arrival order and re-checks the exact line/space/sender binding (the shared line is refused). Commands: `help`, `status [job]`. Plain questions of 3+ words become question research. Every link is researched (no operational-wording filter on this line). The acknowledgement is queued before the job starts, and final replies are keyed `final:<message>` so restart retries never double-send. |
| `src/alfred_research/integration/desk.py` | Shared desk (also used by the parked Personal adapter): intake, dedupe (24 h; "again" re-runs), background execution, Memory publication, delivery, restart `resume()`. |
| `src/alfred_research/local/memory.py` `MemoryServicePublisher` | Loopback-only (`http://127.0.0.1:PORT/v1/memory`). Reads the token from a private file and never logs it. Creates one record per independently verified source statement. `source_message_id = research:<job>:<claim>` makes publishing idempotent. Records `review_state` exactly as Memory reports it and never claims approval Memory didn't return. |
| `staging/research-photon-line-v1/` | Long-running connector: the installed connector/ledger code plus `outbox.mjs` (sequence-ordered, at-most-once; uncertain sends go to `outbox/unknown/` for reconciliation and are never resent), no 5-minute session cap, `Restart=on-failure`, ledger cap 50,000. Also contains both proposed units and config templates. |
| `staging/memory-research-finding-kind-v1/` | Optional Memory patch adding a `research_finding` kind (see its README). |

Each Memory record looks like this:

```
Research finding: <verified statement>
Source: <title> - <url> (<location e.g. pdf:page-3>), retrieved <time>.
Verification: exact quotation checked against the saved source; not independently corroborated.
Research job <id>, claim <C#>.
```

## Validation

- Python: `python3 -W ignore::ResourceWarning -m unittest discover -s tests -p 'test_*.py'` → **422 passed** (410 earlier + 12 in `tests/test_research_line.py`).
- Node 24: `node --test tests/connector.test.mjs tests/outbox.test.mjs` in `staging/research-photon-line-v1` → **23 passed** (17 existing connector tests + 6 outbox tests).
- **Real Memory code check** (installed-identical `store.py`, temporary database, Research agent principal):
  - `development_lesson` → approved, and Alfred's search returns it;
  - `personal_fact` → pending;
  - `research_finding` → HTTP 400 until the optional patch is installed.
- **Local end-to-end rehearsal.** The staged connector code (fake SDK) stored the text "Hey, look into this https://en.wikipedia.org/wiki/Idempotence". The worker researched the live page and published 4 approved findings to the real Memory code, and Alfred-principal search returned them. The outbox pump delivered the acknowledgement, then the cited summary ending "Memory: 4 finding(s) saved to Alfred's Memory as approved; Alfred can now use them."

This was not tested with the real Photon SDK, the real line, or the live Memory service.

## Decisions and blockers for Hayden

1. **Model provider (decided 2026-10-16: Memory publishing stays OFF until a real provider is configured; provider choice pending).**
   - The config template ships with `memory.enabled: false`. Findings stay as local candidates, and replies say "not published to Alfred's Memory".
   - Even with Memory switched on, the desk publishes only jobs whose workers used a model provider (`plan.mode == "codex"`). Extractive-mode jobs are recorded as `skipped`, which also covers `provider: auto` falling back to extractive. Only an explicit `memory.allow_extractive: true` overrides this.
   - Hayden will choose the provider next. Options: a Codex CLI login for the service account, or another provider credential that he provisions.
2. **Memory kind.** Either `development_lesson` (works today, shows under "Lessons" in Obsidian) or install the `research_finding` patch (a Memory release).
3. **Line mode is unverified** (`RESEARCH_PHOTON_ACCOUNT_CAPABILITY_DECISION.md`). The connector refuses the shared line. Whether the project issues a dedicated line for +1 415 225-0168 is only knowable by authenticating, which is your step.

## Owner steps (not performed; each needs your approval)

1. **Binding values (nonsecret).** The Research line phone label, the conversation space ID and your sender ID on that line. The staged discovery tool (`staging/research-imessage-discovery-v1`) or the first transport test can reveal them.
2. **Memory principal.** On the server, as the Memory owner, provision an **agent** principal `research-line` with a fresh token, and assign it task `research-line`. Use `MemoryStore.provision` / `assign` with the Alfred token; never paste tokens into chat. Write the token to `/etc/alfred-research-line/credentials/memory-token` (root, 0600).
3. **Photon credentials.** Write the Research project ID and secret to `/etc/alfred-research-photon/credentials/research-project-id` and `research-project-secret` (root, 0600). They never pass through Research tooling.
4. **Install.**
   - Copy `staging/research-photon-line-v1/{connector,research-project,outbox,main}.mjs` to `/opt/alfred-research-photon/v1/` and that folder's `alfred-research-photon.service` to `/etc/systemd/system/`.
   - Copy the repo's `src/` and `scripts/` to `/opt/alfred-research-line/v1/`, and `alfred-research-line.service` to `/etc/systemd/system/`.
   - Fill `policy.template.json` → `/etc/alfred-research-photon/policy.json` (root:alfredresearchphoton 0640) and `line-config.template.json` → `/etc/alfred-research-line/config.json` (root:alfredresearchphoton 0640), still with `enabled: false`.
   - Run `sudo systemctl daemon-reload`.
5. **Enable.** Set `enabled: true` in both configs, then `sudo systemctl start alfred-research-photon.service alfred-research-line.service`. Check health with `main.mjs health …` and `python3 scripts/research_line.py check /etc/alfred-research-line/config.json`. **No restart of Personal Photon, Hermes or Memory is needed** (unless you choose the Memory kind patch).
6. **Acceptance test.** From your phone, text the line:
   - "help" → usage reply;
   - "https://www.rfc-editor.org/rfc/rfc9110.html" → "On it…", then a cited summary with a Memory line;
   - then ask Personal Alfred about HTTP idempotent retries → Alfred should cite the stored research finding;
   - the same link again → "Already researched".
7. **Rollback.** `sudo systemctl stop alfred-research-line.service alfred-research-photon.service` and set `enabled: false`. Published memories are ordinary Memory rows (task `research-line`): remove them with Memory's existing forget/delete tools if wanted. Research state stays in `/var/lib/alfred-research-line`.
