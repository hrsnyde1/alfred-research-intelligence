# Corrected Photon production installation candidate

2026-10-16. **Two identified compatibility blockers corrected in isolated staging. Installation remains BLOCKED pending new Linux validation and owner approval.** No production source, service, credential or routing configuration changed.

The existing Development /send contract is now accepted unchanged only under its existing authenticated legacy Personal credential. No sixth Development source change or new Development grant is required. An explicit Research payload cannot elevate that caller; Research requires a separately configured caller authority. The prior proposal to edit /usr/local/lib/alfred-v1.1/trusted_intake.py is superseded and must not be installed.

Personal listener startup no longer awaits Research. Research SDK work runs in a disposable worker thread inside the existing Photon process, with bounded auth/request deadlines and session lease. No new Hermes/Photon service or Personal inbound subscriber is introduced.

## Exact source candidate

Patch staging/photon-two-project-v1/bridge.patch, SHA-256 be1b8c0b900210f691b67e2e77cebea954b17909a9295d5f4edcbcacb29d632e. Baseline remains the exact installed source captured previously. Updated SOURCE_INVENTORY.json and TEST_INVENTORY.json freeze this revision; patch applied cleanly to an isolated baseline copy. Paths below relative to /home/alfred/.hermes/hermes-agent/:

| File | Original SHA-256 | Corrected candidate SHA-256 |
|---|---|---|
| gateway/photon_research.py | ABSENT | 4aba0fdf6ed2b45ae5c401255e8d9d759e78e1bd2e4e38c7fbc4c63ccab5ee14 |
| gateway/run_inbound.py | 6a1a40708075e3550a824eae5519e98db97f52ea7995154e8c7e941de4e02144 | 89c3cf4daa0a04473d6302bf53f20b6d3839bd4960f0bc70674c27b9c429b018 |
| plugins/platforms/photon/adapter.py | 841ed6cb6e2d392fcec33f8983dd34fffe677c6a8d40e442bc449e66beeb16e5 | 540288fed36df43cb2e3049a1e46b94b1ddb0e94a4e8efad3f947e4f389e64c1 |
| plugins/platforms/photon/sidecar/caller-bindings.mjs | ABSENT | 1bafa6bb31376fcdf5cf237003555fc7ba7d289711bcc192335ed565232075bf |
| plugins/platforms/photon/sidecar/index.mjs | ef019d1d50e4ca680aede49276181f8eff8d396d9b7c22a73bb5da2b2d7bb8e4 | 2ac209c3864cf4165d55fbfff7ffa9e29d9a43b010d35937bc08ea51c73082ba |
| plugins/platforms/photon/sidecar/research-lifecycle.mjs | ABSENT | 6ae5e27a677cc6df9c2065e73ce727ccf11174c8a915d29134792fbe3df089dc |
| plugins/platforms/photon/sidecar/research-project.mjs | ABSENT | ea65df22546e19233bb79e976aaf366470fb3fb5d197c1c40c006a9aa9cb6e96 |
| plugins/platforms/photon/sidecar/research-worker.mjs | ABSENT | 98ac1071ae1c06d0cba0e31bde819cec5288fe16cb577479c9862a6c8bf501a7 |

send-format.mjs remains unchanged. Five new modules plus three modified files constitute the proposed eight-file production delta. No SDK, Node, Development source, database or vault change. Original tested candidate is archived in staging/photon-two-project-v1-before-corrections; previous Linux stage remains untouched. This task did not recheck Linux production; freshness must be reverified before later installation.

## Existing host and disabled installation boundary

Prior verified launch paths are Node /home/alfred/.hermes/tools/node-26.7.0-linux-x64/bin/node and sidecar index.mjs; Hermes uses /home/alfred/.hermes/hermes-agent/.hermes/bin/hermes. Existing services run as alfredphoton and alfredmsg, CanReload=no. Hermes Requires/After Photon; both Want/After Development intake. Installation of Node/Python source requires later coordinated runtime replacement, not a guessed hot reload. No such action occurred.

First installation must remain Research-disabled with no Research project/caller credentials attached, no active Research profile/hook and no Research worker. Preserve the Personal credential and Development's legacy token/body, routes and grants. Proposed disabled flags in Photon and Hermes launch config must be reviewed for precedence before start. The exact active configuration and full shared-consumer inventory remain owner sign-off requirements.

## New protected caller reference

Besides the separately provisioned Research project ID/secret, later enablement requires PHOTON_RESEARCH_SIDECAR_TOKEN, distinct from Personal's existing sidecar token, mapped to x-hermes-research-token only in the authenticated Research send lane. The bridge and authorized host intake sender need this reference; Development/Personal ordinary callers and company agents do not. Missing/equal token denies Research authority and prevents worker initialization. No actual token was read/created/populated. The expected environment/scoped-secret resolver mapping requires owner review; reference names are not credentials.

Worker receives only explicit Research configuration and an empty environment, not Personal/caller tokens. Worker SDK stdout/stderr are not forwarded. The Node process still holds both authorities; this is not an adversarial memory boundary. Project selection audit emits fixed host-role/project/action fields only. Existing token holders are trusted host callers; source text does not choose an authority.

## Evidence and remaining approvals

Corrected Mac validation: 30 Node + 11 Python staged tests PASS and all 347 Research regressions PASS, including both original blocker reproductions and the original 23 staged checks. The earlier Linux 23-test PASS is historical and cannot qualify the corrected worker architecture.

Before installation approval: authorize a new frozen Linux synthetic transfer/run; reverify production/SDK/runtime baseline; test worker creation/termination under unchanged Bubblewrap resource controls; approve protected caller binding and no-secret-to-company boundary; confirm all shared clients; approve effective disabled config, source ownership, quiescence, coordinated restart, health/Personal regression and rollback. Update installation manifest for all eight files; do not use the earlier five-file manifest or proposed Development edit.

Before live Research: approve genuine host issuer/registration and durable intake hook, served-profile/conversation/sender/line mappings, provider reconciliation and controlled messaging. Approve the default five-minute hard Research session lease or separately review a bounded renewal design; no automatic auth restart exists. No live availability guarantee follows from fake tests.

**Minimum next step:** owner-authorized Linux isolated validation of this corrected revision. Research remains disabled and no production install/connection is authorized.
