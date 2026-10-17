# Research-only connector synthetic validation

2026-10-16. Mac-local synthetic PASS; live Linux connection/installation not executed.

| Command | Actual result |
|---|---|
| node --test staging/research-photon-connector-v1/connector.test.mjs |17passed,0failed/skip;198.786ms |
| node --check staging/research-photon-connector-v1/main.mjs | exit0 |
| node --test staging/photon-two-project-v1/tests/*.test.mjs |30passed,0failed/skip;275.366ms |
| python3 -m unittest discover -s tests -q |347passed,41.079s,exit0 |

New17 tests: disabled no credential/client access; independent explicit auth; missing credentials; wrong project credentials; missing binding; durable pending/replay; forged sender/line/space; conflicting replay; explicit Research send/dedupe; outbound payload conflict; restart dedupe; failure leaves unrelated Personal object unchanged; live intake seam refused; UNKNOWN no-resend; line-scoped event IDs; standalone disabled entrypoint without SDK; symlink credential rejection. Full names/output are test-results.txt. Test identities/secrets are fake; no actual SDK/provider client was initialized. Temp state only. Personal isolation tests model absent Personal references and independent fake object; production process independence is architectural, not a live failure-injection claim.

Python suite emitted existing unclosed SQLite ResourceWarnings; all347 tests passed including crash/recovery regressions. No production state or related source was modified. Existing bridge Python guard tests were not rerun in this task;30 Node and347 Research counts are reported separately, not mislabeled as a new41 Linux run.

All new source/test/config/artifact SHA256 digests: staging/research-photon-connector-v1/SHA256.json. research-project.mjs is an exact copy of the reviewed module, not a patch to active Personal source. Inventory includes two proposed service files, synthetic disabled policy, connector/CLI/tests and test output; real credentials/identities absent. No Linux test execution/deployment or live messaging occurred.

Limits: new service sandbox/UID/mount/dependency closure not yet verified on Linux; no actual provider auth, multi-host Apple behavior, receipt/delivery guarantees or current Research line metadata established. Hermes task attachment remains unavailable in production and explicitly fails closed. Next action is owner-authorized isolated Linux synthetic validation of this separate candidate, followed by separately reviewed Research-only installation/credential activation and one controlled messaging canary. Personal remains untouched.
