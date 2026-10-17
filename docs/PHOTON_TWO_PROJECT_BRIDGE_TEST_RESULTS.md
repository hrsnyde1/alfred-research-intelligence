# Corrected Photon two-project bridge test results

2026-10-16. **PASS for Mac-local compatibility corrections: 41 staged tests and 347 Research regression tests.** No live connection or Linux change. Corrected patch requires a fresh Linux validation; the prior 23-test Linux PASS applies only to the archived pre-correction revision.

## Exact commands and actual results

```sh
node --test --test-concurrency=1 staging/photon-two-project-v1/tests/*.test.mjs
python3 -B -m unittest discover -s staging/photon-two-project-v1/tests -p 'test_*.py' -v
PYTHONPATH=src:tests python3 -B -m unittest discover -s tests -v
node --check staging/photon-two-project-v1/modified/plugins/platforms/photon/sidecar/index.mjs
node --check staging/photon-two-project-v1/modified/plugins/platforms/photon/sidecar/research-worker.mjs
```

| Suite/check | Actual result | Runtime / exit |
|---|---|---|
| Full relevant staged Node tests | 30 passed; 0 failed/skipped | 381.252 ms; 0 |
| Full relevant staged Python tests | 11 passed; 0 failed/skipped | 0.085 s; 0 |
| Full existing Research suite | 347 passed; 0 failed | 41.167 s; 0 |
| Node syntax checks/Python AST parsing | PASS | 0 |
| Updated patch applied to isolated baseline copy | PASS; all nine result digests match | 0 |

Node v24.21.0/Python 3.14.3 on Mac. Source/tests/log inventory and complete logs are in artifacts/audits/photon-compatibility-corrections-20261016/. Tests use only synthetic credential strings, injected fake transports, temporary ledger files and disposable worker threads. No SDK factory is invoked against Photon. The worker-protocol test substitutes a fake SDK in a test-only copy of the exact worker source; it proves no real spectrum-ts import remains before execution. No production code has a test/fake bypass flag.

Original 23 checks remain: 11 Research module tests, two copied installed-SDK selector/package checks and ten guard/Personal compatibility tests. Added 18 tests: 17 Node correction tests and one Python host-token boundary test. All 305 original Research tests plus prior 27 intake and 15 project-contract tests continue passing. Existing Research source/tests were not edited.

## Targeted reproductions

1. Existing Development body `{spaceId,text,format}` through the archived HTTP handler reproduces the prior status400. Identical body and original synthetic legacy credential through the corrected exact HTTP handler returns Personal status200; no Development source/body change.
2. Archived awaited Research initialization prevents its following Personal-ready marker until fake auth resolves. Corrected index starts Research only in the already-listening callback. A stalled disposable worker is terminated after a bounded simulated deadline while Personal sends continue. An actual test worker is terminated and threadId becomes -1, rather than leaving a late connection behind.

## Exact Node test names

- original Development request reproduces and succeeds unchanged through Personal
- explicit Personal and authorized Research select independent connections concurrently
- legacy authority cannot elevate itself using a Research project field
- Research authority has no Personal default and no Personal send permission
- unknown or invalid credentials cannot use either project; no token fallback
- copied caller objects and colliding caller tokens cannot gain Research authority
- disabled Research performs no configuration/factory work; original Personal startup retained
- authentication stall cannot delay Personal readiness and is terminated without retries
- authentication failure never terminates or changes healthy Personal connection
- missing Research credentials or caller authority fails closed without affecting Personal
- Research send timeout rejects its pending state without Personal retry leakage
- shutdown and late ready events cannot revive Research; restart is a new independent lifecycle
- Research internal retries have a hard session lifetime and no automatic reconnect
- real disposable worker stall is terminated; no SDK/credentials are imported
- production worker protocol with substituted fake SDK keeps concurrent traffic separate
- cancelling Research delivery retains healthy Personal consumer and removes only its waiter
- original awaited startup blocker reproduces before correction and releases only after auth
- disabled mode never initializes or subscribes Research
- missing credentials and reused Personal credentials deny enabled Research
- inbound project and message namespaces are independent of Personal originals
- wrong line sender or space cannot enter shared consumer
- explicit project and exact scope required for send
- cache restore pins dedicated line and duplicate logical send is accepted once
- same ACK for separate inbound operations does not collapse
- ambiguous external outcome never resends
- restart with protected durable ledger preserves project send separation
- unsupported Research media/actions deny without Personal fallback
- separate app receives only explicit Research project credentials
- copied installed SDK packages are consistently 12.7.0
- installed client selector selects exact line and rejects another project line

## Python regression additions and evidence

All ten original test_guard.Tests methods remain. New test_research_http_uses_separate_host_credential_and_missing_never_falls_back extracts the actual staged _sidecar_call and proves only the separately configured Research header is sent; missing or Personal-equal token fails before any HTTP call. The original function-equivalence and HTTP payload tests continue to prove Personal behavior.

Private capability tests reject copied caller descriptors, incorrect/unknown tokens, Personal credential elevation, Research-to-Personal default and a present invalid Research token even with a valid legacy token. Concurrent fake HTTP sends use distinct connection collectors. Lifecycle tests cover disabled/missing config, auth stall/failure, request timeout, no automatic retry, hard session lease, shutdown/late-ready/restart and actual worker termination. Parent-delivery cancellation retains the healthy Personal consumer and removes only the Research waiter.

No test failures remained in final runs. One new test fixture's temporary ledger was moved to the OS temp directory before final validation so a later read-only source mount remains compatible. Baseline source was unchanged and the pre-correction source fixture is hash-frozen under tests/fixtures/ for before/after reproduction.

## Limits

Shared legacy credential maps to a trusted caller class, not independently identifiable Development versus Hermes processes. Worker threads protect lifecycle/global state but not secrets against arbitrary code in the same OS process. Host event-loop scheduling is not a hard real-time guarantee. Actual SDK authentication, SDK internal retry behavior, full Hermes plugin loading and new worker behavior under Linux resource/timeout isolation remain untested. No live caller secret or endpoint was used. New Linux validation must include worker-thread cleanup and state permissions; the old Linux transcript is not sufficient.
