# Separate-project Linux activation gates

2026-10-16. **BLOCKED — no Linux transfer, live connection or activation authorized.** The owner has confirmed separate provisioned projects; do not request or provision them again.

## Required protected references

| Logical reference (proposal, not installed key) | Required binding |
|---|---|
| PHOTON_PERSONAL_PROJECT_ID_REF | Existing Personal project identity; preserve current resolver/config |
| PHOTON_PERSONAL_PROJECT_SECRET_REF | Existing Personal secret reference; never reused for Research |
| PHOTON_RESEARCH_PROJECT_ID_REF | Separately provisioned Research project identity |
| PHOTON_RESEARCH_PROJECT_SECRET_REF | Research-only connection secret reference |
| PHOTON_RESEARCH_LINE_REF | Verified dedicated instance/line mapping in Research project |
| RESEARCH_HERMES_ROUTE_REF | Current issuer/grant, exact sender/conversation, target profile and policy revision |

Names above describe desired logical references, not actual environment variables or secret locations. Owner chooses the existing approved protected credential store and least-privilege resolver. Do not put values in source, fixtures, Memory, documentation, task logs or GitHub. Missing Research reference disables its connection; never substitute Personal credentials. Explicitly resolve both app configurations, disallow environment fallback and redact SDK error/telemetry output. One process can prevent accidental cross-use through capabilities but is not an OS security boundary against a compromised process; stronger separation needs separate owner review.

## Installation prerequisites

- Owner supplies nonsecret project/instance bindings, authorized sender and exact conversation/profile, active Personal route revision and effective config metadata. Provisioning is confirmed; live bindings are not independently inspected.
- Photon/Hermes owners review two-app lifecycle, shared SDK telemetry/log state and all explicit-line calls. Validate installed source/dependency digests before implementation. Existing SDK factory design supports separate instances but live coexistence remains untested.
- Implement and review the host changes listed in the implementation report. Existing hook alone fails open; Research reservation must precede every ordinary-agent path. No missing profile or disabled intake may delegate to Personal.
- Approve genuine host authentication and durable registration separately. Offline observed objects, synthetic credentials and production=True locks are not a live issuer. Acquisition, execution and Memory remain separately disabled/gated.
- Authorize bounded Linux synthetic staging tests first: lifecycle failures, cross-project caches/IDs, all outgoing action types, revocation, unknown outcomes and restoration. No live credentials needed for those tests.
- Review complete installation/rollback source/config manifests, state format compatibility, Personal behavior regression, credential-store permissions and service ordering. Restart/quiescence is not authorized; no exact deployment commands are safe until effective paths/config are reviewed.
- Separately approve live Research connection and one controlled message/ACK plus Personal control evidence. Prove actual destination/project, profile exclusion, correct Research From and unchanged Personal line; SDK acceptance is not delivery.

## Rollback invariants

Disable Research ingress/egress through a retained fail-closed guard; stop only its app/connector after reconciling in-flight/unknown sends under owner authorization. Preserve Personal connection/config and existing orchestrator. Never send unresolved Research obligations through Personal, remove its reservation before disabling ingress, or add a second Personal consumer. Retain pending/dedupe/completed delivery records; do not rewind Memory/Obsidian. Old code may resume only when Research stream is demonstrably detached and its durable obligations remain quarantined. No credential rotation, line deprovisioning or service restart is implied.

**Next owner approval:** review the synthetic implementation, then authorize a concrete host-extension staging task and protected reference configuration design. Production connection and controlled messaging require later explicit approval.
