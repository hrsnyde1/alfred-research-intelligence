# Separate Photon project synthetic test results

2026-10-16. Mac-local validation only. No live SDK connection, real credentials/messages, Linux tests or service changes.

## Commands and evidence

```sh
PYTHONPATH=src:tests python3 -B -m unittest discover -s tests -p 'test_photon_projects.py' -v
PYTHONPATH=src:tests python3 -B -m unittest discover -s tests -v
```

Focused final result: **15 passed, 0 failed**, exit 0, unittest runtime 0.212 seconds. First full regression: **346 passed, 0 failed**, exit 0, 41.653 seconds (14 new tests plus 332 existing). Final full regression on the completed source: **347 passed, 0 failed**, exit 0, 42.907 seconds (305 original + 27 prior intake + 15 new tests). Logs are under artifacts/audits/separate-photon-project-20261016/.

Initial focused validation caught a missing environment field required by WorkflowJournal. Added explicit personal environment validation to the synthetic send record, then all focused tests passed. Added a pre-dispatch rejection for Personal connections at the Research ACK entry point, and an additional independent-ledger regression. No existing Research source was modified.

## Exact new tests

All under test_photon_projects.ProjectTests:

- test_research_and_personal_preserve_independent_routing
- test_missing_project_binding_rejected
- test_forged_project_sender_and_copied_observation_rejected
- test_wrong_line_or_conversation_denied
- test_event_ids_and_cache_issuance_do_not_cross_projects
- test_cross_project_send_and_reconcile_denied_both_directions
- test_independent_send_ledgers_same_operation_and_event_ids
- test_shared_credential_reference_or_project_denied
- test_disabled_research_does_not_fall_back
- test_unavailable_intake_never_calls_personal
- test_replay_restart_and_post_accept_crash_do_not_duplicate
- test_changed_payload_same_event_conflicts_without_second_send
- test_unknown_reconcile_outcome_never_resends
- test_default_and_production_bootstrap_denied
- test_foreign_connection_capability_cannot_adopt_project

Temporary registered synthetic Research stores/journals come from the existing foundation harness. Fake observations and credential references are test-only; no credential values are used. Crash testing here is a controlled exception after durable fake acceptance followed by connector/intake reconstruction; this is not an OS-level connector crash test. Existing intake regression includes real child-process crash recovery separately.

## Evidence limits

Tests prove the local offline capability model, project-scoped identities, terminal Research failure, replay/conflict behavior and fake reconcile-before-effect. Personal routing is an injected original callback, not a live Hermes instance. Fake transport authoritative absence/idempotency is not a Photon service guarantee. No claim is made about live token isolation, Apple From identity, provider delivery lookup, SDK two-project lifecycle or installed Hermes hook enforcement. Exact fake-type and production locks remain enabled.

Existing workflow notification contracts and final/currentness checks were preserved and exercised by regression. This module handles pending acceptance only; it cannot send a FINAL or turn a source URL into an acquired packet. All 305 original Research tests remain covered by full discovery, alongside the 27 prior intake tests.
