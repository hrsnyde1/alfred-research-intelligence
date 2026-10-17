# Separate Photon project implementation

2026-10-16. **Mac-local synthetic implementation complete; Linux activation blocked.** Owner confirms separate Personal and Research projects, with Research dedicated number and credentials already provisioned. This supersedes the unresolved same-project question in earlier reports. No credential values were requested or inspected.

## Connection decision

Installed Spectrum 12.7.0 core `dist/index.js:4042` resolves credentials per Spectrum(options) call, loads its project config and allocates platformStates, message broadcasters and lifecycle state inside that call. Provider clients are initialized against that runtime; its WeakMap state is client-scoped. This supports independent app instances in one process at the source-design level. It does not prove live two-project behavior or complete process isolation: log level/telemetry and any environment-derived defaults are shared concerns requiring review. Explicit options and telemetry disabled or independently reviewed are required; never use ambient fallback to Personal credentials.

Existing sidecar has one app and global caches, so it does **not** support two independently bound projects unchanged. Proposed minimal live design is two app/connector objects within the existing Photon process, one consumer seam feeding the existing Hermes orchestrator. Keep the Personal app/credential mapping intact; add Research-scoped client/state. A separate Research-only connector process is a fallback if SDK lifecycle or shared globals cannot pass staging; it must subscribe only to Research, never Personal. No second Hermes or new service was created or required by this implementation.

Read all six requested input reports plus current intake and notification/reconciliation source. Fresh SSH used BatchMode=yes and StrictHostKeyChecking=yes with bounded connection options, reading SDK factory text and bridge digests only. Bridge SHA-256 remains ef019d1d50e4ca680aede49276181f8eff8d396d9b7c22a73bb5da2b2d7bb8e4; adapter remains 841ed6cb6e2d392fcec33f8983dd34fffe677c6a8d40e442bc449e66beeb16e5. No SDK app was initialized, no provider APIs/logs/messages/config secrets read and no Linux writes made.

## Exact local changes

Created `src/alfred_research/integration/photon_projects.py` and `tests/test_photon_projects.py`. Existing intake, notification, state and production integration source are unchanged.

- ProjectBinding fixes project, receiving line, conversation, explicit sender, intended profile, role and credential reference. Two project and credential references must be distinct. Missing references deny construction.
- Each exact FakeProjectConnection issues object-identity observations for its own binding. Copied/deserialized/forged events have no authority; foreign connection objects cannot adopt a configured project. This models a trusted host boundary, not real Spectrum authentication.
- ProjectAttachment passes Personal observations unchanged to the original callback. Research goes only to PersonalHermesIntake, under a scope-derived issuer bound to project/line/conversation. Personal Research remains the existing `personal` environment; message text cannot choose a company or project.
- Disabled or failed Research intake returns terminal UNAVAILABLE, with no Personal callback. The host must implement this terminal policy before all ordinary-agent/command/busy-session paths in production; the local class does not patch Hermes.
- Existing PendingSources, one pinned GitHub source, journal persistence, operation conflict checks and acceptance acknowledgment are reused. No Research task/source digest is fabricated, no acquisition or Memory call occurs.
- Research ACK reauthenticates the original connection/event and rechecks intake before send. It cannot accept an arbitrary From/project in payload or copied ACK. Fake transport reconciles durable accepted operations before effects; lookup exceptions propagate rather than trigger resend. Project-scoped namespaces prevent cache/retry collisions. Simulated acceptance is not delivery.

Credential references are synthetic opaque names; no resolver or secret storage exists. Fake connection and attachment both require test_only=True and reject production=True. Even genuine-looking IDs cannot enable production.

## Notification boundary

Existing workflow Notifications/FakePhotonPort require a materialized task and receipt-validated completion. Pending intake deliberately has no task, so its ACK cannot use that task-based FINAL path. This implementation reuses IntakeAcknowledgment and WorkflowJournal plus the existing reconcile-before-effect pattern for a synthetic acceptance ledger only. It does not replace the workflow notification engine or create a live retry loop. Future completion must enter existing receipt/currentness checks and carry the same protected project binding through the Hermes-owned delivery obligation. FINAL sending is not implemented here.

## Proposed production delta

1. Existing sidecar: separate Personal/Research Spectrum app objects with explicit protected credential bindings; independent client/cache/message/probe/lifecycle state; versioned authenticated project/line provenance; explicit dedicated-line selection for every Research action. Preserve Personal app and its line. Reject unexpected clients and missing/ambiguous binding. No new Personal subscription.
2. Existing Photon adapter: carry trusted connection/project/line through normalization and every outbound helper. Scope cache/session/event IDs by project+line+conversation; event ID adds dedupe scope. No source-body routing or credential selection.
3. Existing Hermes admission/routing: reserved Research connection cannot fall through on missing profile/handler/error. Cover command/busy/pending-reply lanes before existing hook. Preserve Personal route and callback. Persist identity on existing delivery obligations/recovery with reviewed versioning.
4. Protected configuration: add only Research credential references and owner-approved line/sender/conversation/profile policy, disabled by default. Actual effective configuration and installation diff need owner review; proposed keys are not claimed to exist today.

These are plans, not installed changes. Genuine host issuer, live intake registration/acquisition, provider reconciliation/delivery evidence and rollback-compatible state remain unresolved. See Linux activation gates.
