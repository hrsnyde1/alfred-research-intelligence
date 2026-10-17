# Optional Memory patch: `research_finding` kind

Adds a dedicated `research_finding` memory kind so Research line findings are labeled as research rather than as `development_lesson`.

- `focused_v1/store.py`: accepts `research_finding` in `create`, and auto-approves it for agent principals (owner decision, 2026-10-16). Every other agent kind still goes to pending review as before.
- `deploy/focused-v1/obsidian_export.py`: adds the export category `"research_finding": "Research"`. Without it the export raises "Unknown memory kind".
- Tests: the export test expects one more memory (10 instead of 9); `test_research_finding_kind.py` is new.

The patch targets the installed release `4d5ba29bd3027e74c808a8feaf1b5dadfded22f0`. Installed `store.py` sha256 `5ca002bd…cf8c` equals the local baseline it was made against.

**Validation (Mac, Python 3.14, scratch virtualenv with `cryptography`):**
- The export and research-kind tests pass (6).
- The full Memory suite shows exactly the same set of failures before and after the patch (17 failures and 3 errors, environment-related, as already described in `docs/PHASE7H_BASELINE_FAILURE_ANALYSIS.md`).

This was not run on Linux. Installing it is a Memory release (sudo, `alfred-memory-v1.service` restart, export regeneration) and needs Hayden's approval. Without this patch, configure the Research line with `"kind": "development_lesson"`, which the current Memory release already auto-approves for agents.
