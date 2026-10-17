# Photon protected Research credential bindings

2026-10-16. **Design only; no credentials created, populated, read or copied.** Research-disabled installation must attach no Research credentials. Current installation candidate is BLOCKED by the shared Development caller incompatibility; live connection has further gates.

## Minimum secret references

Retain Personal project's existing credential resolution and sidecar authentication unchanged. Research needs two separate protected references:

| Logical protected reference | Only permitted runtime mapping |
|---|---|
| research-spectrum-project-id | PHOTON_RESEARCH_PROJECT_ID in alfred-photon.service Node process |
| research-spectrum-project-secret | PHOTON_RESEARCH_PROJECT_SECRET in that same Node process |

Reference names are proposals, not existing credential IDs or allocated filesystem paths. Project ID is not normally a secret, but treating both connection inputs as protected avoids accidental exposure and mismatched projects. Values never belong in this repository, source fixtures, Research Memory, docs, GitHub, command arguments, task logs or chat. No actual value is present in this document.

Use the existing owner-approved systemd credential mechanism/launcher rather than another secret service. Two distinct service credential entries could be named research-spectrum-project-id and research-spectrum-project-secret; their owner-managed sources and exact LoadCredential/LoadCredentialEncrypted mapping require approval. They must not alias Personal entries. A systemd credential entry alone does not populate the environment expected by the staged Node module; a narrowly reviewed change to the existing launch wrapper is required. Never put secret values into Environment= lines or use systemctl show Environment, raw argv/environment dumps or shell xtrace to verify them.

The reviewed launcher must read only those exact entries when a separately approved Research enable condition is true, assign explicit Research variables, suppress tracing, and exec the same Node entrypoint. It must not resolve or attach them for disabled installation. Missing/empty/mismatched/invalid references leave Research unavailable and cannot select Personal credentials. A live authentication failure must not block Personal startup; current awaited initialization is not yet bounded and must be corrected/tested before enablement. No wrapper implementation or credential-store change was made in this task.

## Nonsecret policy references

These values are protected owner policy, not message-supplied routing parameters:

- PHOTON_RESEARCH_ENABLED: explicitly 0 for initial bridge installation; 1 requires later explicit owner activation approval.
- PHOTON_RESEARCH_CONNECTION_REF: immutable opaque reference attesting the separately provisioned project connection.
- PHOTON_RESEARCH_LINE / SPACE / SENDER / PROFILE: exact approved dedicated line, conversation, authenticated requester and served Research profile. Reports use opaque labels; real phone/account identifiers are not printed here.
- PHOTON_PERSONAL_LINE: verified existing stable Personal line, unchanged. Shared-mode compatibility must be resolved before enabling two-project operation.
- PHOTON_RESEARCH_STATE_DIR: separately approved service-owned ledger path, proposed /var/lib/alfredphoton/research-transport-v1; absent during disabled install unless separately approved. No directory created.

Hermes needs only enable and binding metadata consumed by its guard, not the Research project secret or ID credential values. Do not inherit Research secrets into alfred-hermes.service, company profiles, model/provider requests, plugins or child tool environments. Company agents must not execute as alfredphoton or receive its credential directory/environment. Enforce this with service-user/filesystem/process boundaries and owner-reviewed tool permissions; prompt instructions are not a boundary. Current services use distinct users alfredphoton and alfredmsg, but credential-store/access mappings remain unverified without owner sign-off.

Both Spectrum apps share the Photon process after later activation; this isolates accidental routing, not adversarial code running inside that process. Existing sidecar token holders can reach the shared API and are trusted host callers; project tags are not new credentials. A compromised Hermes/Development host caller is outside the demonstrated isolation guarantee. If stronger adversarial separation is required, return for an approved architecture review rather than claiming this patch supplies it.

## Disabled configuration proposal

Proposed owner-controlled drop-ins, not written here:

`/etc/systemd/system/alfred-photon.service.d/60-research-disabled.conf`

```ini
[Service]
Environment=PHOTON_RESEARCH_ENABLED=0
```

`/etc/systemd/system/alfred-hermes.service.d/60-research-disabled.conf`

```ini
[Service]
Environment=PHOTON_RESEARCH_ENABLED=0
```

No Research LoadCredential, project variables, active profile route or plugin registration is required for the disabled phase. Owner must review existing wrapper/environment precedence and confirm the effective final flag is 0 without dumping other environment values. If existing files with these names exist, stop rather than overwrite; review/backup only approved nonsecret changes. No actual active configuration was opened to infer absence or precedence.

Later activation must use a separately reviewed configuration revision; it must not accidentally retain a competing enable/disable assignment. Missing or invalid configuration and unknown connection/line must fail closed. Exact live binding values remain unallocated to this work despite owner-confirmed project provisioning.

## Required approvals

Photon credential owner approves distinct protected references/resolver and log redaction. Security approves service identities and exclusion from company agent tools. Personal owner approves unchanged connection/line and maintenance behavior. Research owner approves requester, exact scope and genuine issuer/registration. Hermes owner approves served profile, terminal intake handler and effective config. SDK logging, errors and telemetry must be reviewed for secret leakage before any live credential is resolved; setting telemetry=false alone does not prove complete log redaction.

No secret inspection is needed to review this design. Owner may provide a nonsecret binding manifest listing reference names, consuming service, allowed UID, status and approval revision only.
