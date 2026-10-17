# Personal Alfred → Research adapter (Milestones 3–4)

2026-10-16. **Prepared and tested locally; not registered, installed or activated.** No Hermes, Photon, Memory or server change was made. Nothing here has been tested end to end over iMessage.

Target flow: owner texts Personal Alfred "Hey Alfred, look into this. <link>" → Hermes' existing `post_gateway_admission` hook → adapter acknowledges → the existing persistent Research engine runs in the background → a message-friendly result returns to the same conversation → verified findings stay as pending Memory candidates.

## Components

| File | Role |
|---|---|
| `integration/message_intake.py` | `detect(text, attachments, attachment_roots)` returns a `ResearchIntent` or `None`. Pure function; never reads source content. |
| `integration/hermes_research.py` | `HermesResearchAdapter.on_post_gateway_admission(payload)`, background execution, delivery, restart `resume()`, `research status`, and `register(ctx, config)`. |
| `local/store.py` | Adds `by_request_key` and `find_recent` lookups on the existing jobs table. No schema change and no new database. |

The older offline canary seam (`integration/hermes_intake.py`, GitHub-commit-only) is unchanged.

## Message intake rules (Milestone 3)

- **Research automatically:** any message from the owner containing a supported link or approved attachment. This covers articles, PDF, DOCX, GitHub repositories, YouTube and Instagram, using the Milestone 2 handlers. Explicit cues such as "look into", "fact-check", "summarize" or "what do you think of" always count.
- **Leave to normal chat:**
  - messages with no link;
  - links to meeting, calendar, maps, payment and dev-tool hosts (Zoom, Meet, Teams, Calendly, Linear, Figma, Atlassian, …);
  - GitHub pull requests, issues and actions;
  - messages whose wording is operational ("schedule", "deploy", "send this to", "fix", "pay", …) unless an explicit research cue is also present.
- **Question research:** only in command form ("Research: <topic>", "/research …", "look into <topic>") with no operational wording. It uses the existing discovery fallback.
- **URL normalization:**
  - https only, lowercase host, no fragment;
  - tracking parameters removed (`utm_*`, `fbclid`, `igsh`, `si`, …);
  - trailing punctuation trimmed;
  - private, IP-literal and credentialed URLs rejected;
  - at most 4 sources, and the owner is told about extras.
- **Attachments:** accepted only beneath configured `attachment_roots`, and only for supported types. Everything else is ignored with a note.
- **Objective:** taken from the owner's own words, with links and greeting removed. A bare link or "look into this" gets a per-kind default objective. Fetched content never changes routing, objective or destination; prompt-injection text in a source is flagged as data.

## Hermes adapter behavior (Milestone 4)

- **Disabled by default.** `register()` calls `ctx.register_hook("post_gateway_admission", …)` only when `config["enabled"] is True`.
- **Owner-only.** It acts only for exact `(platform, chat_id, user_id)` owner tuples. Wildcards are refused, and `user_id == chat_id` is refused because Photon falls back to the space ID when the sender is missing. Any other sender, chat or platform returns `None`, so ordinary Hermes handling continues.
- **Personal only.** Every job's route artifact is stamped `environment: personal`. Research gains no other department or company access.
- **Idempotent.**
  - The request key is a hash of (platform, chat_id, message_id): a replayed host event returns the same job and acknowledgement.
  - The same link and objective from a new message within 24 hours replies "Already researched (job …)" without a new job. This doesn't apply if the earlier job failed or was unsupported.
  - Words like "again", "redo" or "re-research" force a new job.
  - An event without a `message_id` is not taken over.
- **Acknowledge, then work.** The hook returns `{"action": "handled", "reply": "On it: researching … (job …)"}` at once. A background thread (at most 2 concurrent) runs the existing engine.
- **Honest failures.** If intake fails, the owner gets "I couldn't start research … Nothing was researched" instead of the turn falling through to an ungrounded chat answer. Failed and unsupported results say "Nothing was inferred".
- **Result message.** The delivered summary contains:
  - the objective;
  - each source's title and evidence basis;
  - the count of findings that are source-supported but not independently corroborated;
  - up to 4 findings with citations such as `[pdf:page-3]` or `[article:html-line120]`;
  - the main limitation;
  - Memory status (pending, not promoted);
  - the job ID.
  "research status [job]" retrieves the result or recent jobs.
- **Delivery recording.** The result goes through a host-supplied `deliver(route, text)` callable. The outcome is recorded as `handed_to_host`, `failed` or `not_configured`; host acceptance is never claimed as receipt. Without a `deliver` function, the acknowledgement points the owner to `research status`.
- **Restart.** `resume()` (run from `register`) does three things:
  - runs jobs still waiting in the queue;
  - marks abandoned in-progress jobs `interrupted` and retries each once as a new linked job (`retry_of`);
  - delivers results whose delivery was never recorded.
  State is the existing `jobs.sqlite3`.
- **Owner-facing states:** accepted, running, completed, partially completed, failed, unsupported source, needs sources, interrupted.

## Assumed host contract (verify before installation)

From the Phase 7B audit and `PERSONAL_RESEARCH_ROUTE_CONTRACT.md`:
- the `post_gateway_admission` callback receives `session_key`, `platform`, `source` (`source.to_dict()`: `platform`, `chat_id`, `user_id`, `profile`, …), `message_id` and the full normalized `text`;
- returning `{action: handled, reply}` consumes the turn.

This was not re-verified against current Hermes source in this change: the server config home was not inspected. Attachment field names (`attachments`/`media` with a local `path`) are assumptions; attachments are ignored unless roots are configured.

Known host limits from the audit, not solved here:
- busy-session and slash-command lanes run before this hook, so a message sent while Alfred is mid-turn may skip Research;
- the hook fails open: if the plugin errors or times out, the message reaches normal chat;
- the source dictionary is not cryptographic sender authentication.

For the Personal conversation this is acceptable degradation: the worst case is a normal chat reply instead of Research. It is **not** acceptable for a reserved Research-only conversation; see `RESEARCH_HERMES_FAIL_CLOSED_ROUTE.md`.

## Owner approvals and steps to go live (not performed)

1. **Confirm identity values.** Provide the exact Personal Photon `chat_id` and non-fallback `user_id` for the owner (nonsecret, redacted evidence of the active route).
2. **Find the delivery function.** Identify Hermes' existing delivery call for proactive messages to a conversation (for example the Photon adapter `send(chat_id, text)` behind Hermes' delivery obligation). Bind it as `deliver(route, text)`. Without it, results are available only via `research status`.
3. **Install.** Install this package on the server in a Research-owned location (proposal: `/opt/alfred-research/v1/`). Set the working directory to a Research-owned path, not Memory and not Obsidian.
4. **Add the plugin.** Add the Hermes plugin entry in the Personal profile calling `register(ctx, {...})` with `enabled: false` first. Then set `enabled: true` in an approved window. Hermes profile hooks are cached: this needs an approved `alfred-hermes.service` restart or a verified supported reload. **No Photon restart is required.**
5. **Acceptance test.**
   - The owner texts "Hey Alfred, look into this. https://www.rfc-editor.org/rfc/rfc9110.html".
   - Expect an "On it" acknowledgement and then a cited summary.
   - A non-link message ("what's on my calendar?") must get a normal Alfred reply.
   - A second identical link the same day must reply "Already researched".
6. **Rollback.** Set `enabled: false` (or remove the plugin entry) and restart Hermes. Research state stays in its own directory.

Steps 1, 2 and 4–6 change production behavior and need Hayden's explicit approval.

## Validation

`python3 -W ignore::ResourceWarning -m unittest discover -s tests -p 'test_*.py'`: **410 passed** (390 earlier plus 20 in `tests/test_hermes_research.py`). The tests cover:
- detection and pass-through cases;
- normalization;
- attachment roots;
- owner, fallback and non-owner identity handling;
- disabled default;
- acknowledgement, execution and delivery;
- replay and dedupe, including the window and failed-job retry;
- unsupported video;
- intake error;
- source prompt injection;
- status command;
- missing or failing delivery;
- restart resume;
- threaded acknowledgement;
- `register()` gating.

Local live run (simulated host payload, real HTTPS, extractive provider): "What does HTTP say about retrying idempotent requests? https://www.rfc-editor.org/rfc/rfc9110.html" produced an acknowledgement and then a completed job with 4 source-supported findings citing `article:html-line…`. "Can you schedule lunch with Sam on Friday?" passed through. The YouTube link was reported as unsupported with no inference. Extractive mode ranks passages by keywords. The configured Codex provider (`--provider auto`) gives more relevant findings, but it sends source excerpts to that provider.
