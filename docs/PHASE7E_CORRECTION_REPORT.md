# Phase 7E — Targeted execution corrections

## Result and changed files

**305 tests passed: all 283 existing tests plus 22 new regressions; zero failures/errors.** Only the three reviewed execution defects were corrected. Production remains disabled. No live Linux integration, external provider call, Memory write, Photon message, dependency installation, service, commit, push or deployment occurred.

Modified:

- `src/alfred_research/integration/canary_contracts.py`
- `src/alfred_research/research/workflow.py`
- `docs/PHASE7E_IMPLEMENTATION_REPORT.md`

Created:

- `src/alfred_research/research/execution.py`
- `tests/test_execution_corrections.py`
- `docs/PHASE7E_CORRECTION_REPORT.md`

Existing test files, budgets.py, state/persistence schemas, model/packet contracts and dependency configuration were not changed. No new infrastructure or migration was introduced. The shared helper is internal offline execution logic, not another coordinator or provider.

## Confirmed root causes and corrections

| Defect | Before editing: independently repeated observation | Correction |
|---|---|---|
| A — response substitution | Provider returned a valid ResearchDraft with invocation_digest `f` repeated 64 times. FakeExecutionPort checkpointed/returned it; later reconcile rejected it. Its response check covered consumption only. | `validate_response` runs before any successful output checkpoint or settlement, for fresh and cached responses. It requires the exact role-specific response type, simulation flag, environment/task/principal/invocation digest and bounded consumption. Invocation digest binds the complete approved model/provider/price/role assignment and source/packet/limits; existing output schemas have no separate model field. Wrong assignment/configuration is rejected before execution. |
| B — untrusted deadline | Plan deadline 1100, clock 1200, caller deadline 2000: the port executed successfully because it checked only the invocation's deadline. | Shared `validate_invocation` checks exact plan task/environment/delegated identity/model, equal trusted deadline, plan call ceiling, provider configuration and request retry revision bound. New work checks the trusted clock before intent/reservation/provider execution. Task-wide reservation ceilings are shared with the Director. Cached legitimate output can reconcile/settle after expiry; missing output cannot trigger a new expired call. |
| C — incompatible reservations | Director-first replay added one settlement without another model call. Port-first continuation raised `ContractError: unknown reservation`. Both used shared output keys but different reservation IDs. | Both now call `execute_invocation`/`reconcile_execution` and use the Director's existing stable reservation convention. Existing store reservation/settlement idempotency is reused. Validated cached outputs settle only their existing reservation; no new reservation is created to legitimize an orphaned output. Director continuation preserves an already-authorized port reservation size within the plan ceiling instead of replacing it with its own estimate. |

Stable reservation convention remains `research-` plus SHA-256 of `task_id + ':' + packet_version + ':' + principal`, scoped by the existing authenticated environment database. Immutable invocation intent binds its complete digest; changed units/source/assignment/limits for that logical operation conflict before budget mutation. This preserves accepted Director state rather than rekeying it. A cancelled/settled reservation without a successful output fails closed and cannot initiate another model call.

The existing task journal lock serializes Director/port execution and reconciliation. The helper expects the caller to hold it; Director already does, and FakeExecutionPort now does for both calls and reconcile. SQLite continues to reserve/settle transactionally. Provider outputs and budget settlement remain separate durable steps: a crash between them resumes the exact output and settles once without executing the provider again.

## Rejection and deadline evidence

Rejected/malformed/late port responses create an immutable `RejectedExecution` record under `output:rejected:<digest>` in the same environment/task journal, with the authenticated actor and invocation digest. This is distinct from the successful `output:<version>:<principal>` checkpoint and cannot be loaded as a successful draft/verdict. Failure notes are bounded generic text, not raw provider/source payloads. Existing budget-reservation audit evidence remains; no settlement, refund, approval or successful output is invented. Reservations remain held for explicit reconciliation.

Unauthorized invocation metadata fails before provider execution and budget changes. Legitimate output replay after deadline validates the original plan/intent/response and performs only idempotent settlement. The Director retains accepted behavior for a valid response that returns late: known synthetic consumption is accounted, while subsequent deadline checks prevent packet/verification completion; the port retains its stricter late-output rejection. No new call is allowed after the trusted deadline in either path.

## Added regression coverage

The 22 new tests cover:

- Wrong invocation digest, researcher/verifier principal, task, environment, response type and malformed response; no successful checkpoint/settlement, durable rejection evidence and no verifier approval.
- Wrong model assignment before reservation, forged longer deadline (1100 vs 2000 at time 1200), expired plan with missing output, committed replay after expiry, call/retry revision limits and task cost ceiling.
- Director-first and port-first continuation with one reservation/settlement; port-first uses two reserved units while the Director's normal source estimate is one, proving the established invocation is preserved.
- Concurrent Director/port calls, conflicting invocation replay and conflicting reservation size with no budget overwrite.
- Interruption after output checkpoint but before settlement, concurrent recovery after expiry, and fresh-process Director continuation from a port checkpoint with a provider stub that forbids another call.
- All four environments and all 12 unequal pairs deny cross-environment execution/reconciliation.

The original 283 tests remain unchanged, including provisioning, forged registrations, large SQLite rollback journals, packet/version history, source extraction, independent assessment, validity conflicts, fake Memory/HQ/export/Sync and cached notification recovery.

## Actual validation and reviewer diagnostics

| Command / check | Actual result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v` | **305 passed**, 0 failures, 0 errors, **64.166 seconds**, exit 0 on the final code. An earlier full run also passed 305 in 40.785 seconds before the final continuation-size refinement. |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_execution_corrections.py' -v` | **22 passed**, 0 failures, 0 errors, **0.954 seconds**, exit 0 on the final code. |
| Independent temporary-fixture reviewer reproductions via `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python3 -` | Wrong digest: ContractError, successful output remains None. Extended deadline: ContractError before call. Director-first: **0 additional settlements** and no provider call. Port-first: successful Director continuation, **1 total settlement**, no repeated provider call. |
| In-memory source compilation | **43 Python files** compiled without bytecode writes. |
| Standard-library package metadata check | pyproject.toml parses; existing package layout includes execution.py; dependencies remain empty; no install/build/download. |
| Frozen release integrity | Archive SHA-256 unchanged: `99d4384e1d00592ce193bbcf91678dda62ffe6509a49b3c107e57cb17225ead8`. Inventory/archive files untouched; only research/workflow.py among the 77 original working-tree payload paths differs under this correction authorization. |

Fresh-process recovery test exited 0 and reused the original budget state. Existing hot-journal diagnostics ran for all four environments: child exit 29, original `SQLITE_READONLY_ROLLBACK` reproduced, supported recovery succeeded with committed revisions/verdicts/retry state preserved. Forged receipt diagnostic exited 30 and rejected fabricated registration without modifying the database/hot journal. Original validity diagnostics remained fixed.

All synthetic data and writes were confined to temporary test directories. Tests prohibit sockets; subprocess recovery uses a trusted test snapshot and also prohibits sockets after imports. No secrets or production records were accessed.

## Remaining limits and unresolved production interfaces

These changes authenticate nothing outside the existing offline bootstrap. Production host identities, protected registration authority, real acquisition provenance, approved provider/model and price manifests, actual execution/usage/attestation lookup, independent factual verification, Memory-owned promotion/currentness/full retrieval and Photon authoritative delivery remain blocked as documented in Phase 7C/7D.

No old `integration-<invocation digest>` reservation is silently migrated, deleted or refunded. If manually retained pre-correction harness state has that incompatible accounting convention, reconciliation fails closed rather than creating a second canonical charge; operator-reviewed repair is required. Accepted Director `research-...` identities remain compatible. The frozen Phase 7A artifact has not been repackaged or deployed.

An interrupted synthetic call before successful output publication may still need deterministic fixture replay; this is not a real-provider exactly-once guarantee. Real ambiguous usage requires authoritative provider reconciliation and retained reservations. Genuine-shaped JSON, a synthetic APPROVED result or a locally marked model assignment still cannot authorize production research or Memory promotion.

Stop after this correction and validation for owner review; no live integration is enabled.
