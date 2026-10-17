# Photon account capability decision

2026-10-16. **D — Still unverified.** Provider-level dedicated multi-line operation is documented and implemented, but the existing project's mode, entitlement, Apple identity binding and messaging-host capabilities remain unknown. No evidence supports A for the existing host. B is a plausible conditional path for a separate managed number, not a confirmed path for an independently owned Apple Account. C requires provider/device evidence; another host is neither proven necessary nor ruled out.

## Scope and inspection

Read all four preceding identity documents. Fresh read-only SSH used:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 '<read-only command>'
```

Commands read installed SDK JavaScript/type declarations, computed source SHA-256 and requested only `systemctl show alfred-photon.service -p ActiveState -p User -p WorkingDirectory -p EnvironmentFiles`. Service is active as alfredphoton in the established sidecar directory; EnvironmentFiles returned no entries. This does not establish absence of inline environment, wrapper configuration or cloud-managed settings. No environment values or credential-bearing configuration were read. Initial sandbox SSH denial was followed by the approved read-only retry.

SDK source root is `/home/alfred/.hermes/hermes-agent/plugins/platforms/photon/sidecar/`. Current digests match the previous review:

| File | SHA-256 |
|---|---|
| index.mjs | ef019d1d50e4ca680aede49276181f8eff8d396d9b7c22a73bb5da2b2d7bb8e4 |
| node_modules/@spectrum-ts/imessage/dist/index.js | 9faf0be1530dde1e2f80b580d12377a1fa6b0995c3595794648237a2c8f241ee |

Installed spectrum-ts is 12.7.0 per previous package inspection. Source files were read as text, never imported. Hashes establish on-disk continuity, not the running process's loaded code. No provider authentication/token issuance, account API, message subscription, log/history read, test, configuration write or restart occurred. Personal addresses, Apple IDs and tokens are absent from this report.

## What installed code establishes

Sidecar index.mjs:344–350 uses one Spectrum app, project authentication and `imessage.config()` without explicit clients. This selects automatic cloud client discovery; it does **not** statically select shared or dedicated mode.

Provider index.js:434 onward calls `cloud.issueImessageTokens(projectId, projectSecret)` and branches on returned `tokenData.type`. Dedicated mode builds client entries from instance/token/number mappings; shared mode builds a single sentinel-labeled client. Reading or requesting this response would involve credentials and was excluded. The active mode cannot be deduced from service name, number of conversations, empty clients config or a successful message.

Provider index.d.ts:553–565 accepts optional `clients`, either one entry or an array; each entry has address, token and phone fields. This is a remote-client configuration schema, not an Apple Account registration or sign-in API. No values were inspected. index.js:2502–2518 aggregates dedicated line streams; internal instance keys distinguish entries, including cases where phone labels repeat.

Dedicated conversion receives the stream's configured phone label. The normalized bridge retains space.phone, messageId, space.id and sender.id, but no separate actual Apple-recipient/account or instance ID. Thus the prior statement that recipient metadata is absent needs precision: **a dedicated routing-line label is present; a verified actual Apple destination/account assertion is not established**. Shared mode's sentinel cannot identify an actual receiving number. Transport authentication and configured client provenance must be preserved before treating any line label as trusted.

SDK sending resolves `clientForPhone(client, space.phone)`; explicit space parameters select a dedicated line. Existing bridge POST /send has no identity selector, caches by spaceId alone and rehydrates via space.get without phone; bare-target creation omits phone. These paths need the previously proposed reviewed binding extension before a second line is exposed. No generic SDK type proves safe operation of the unchanged bridge with two accounts.

## Additional authoritative provider documentation

Reviewed official public documentation on 2026-10-16; it is current documentation, not a version-pinned or project-specific entitlement statement.

[Cloud provider configuration](https://photon.codes/docs/spectrum-ts/providers/imessage) states that automatic discovery includes project-owned lines and that explicit clients restrict subscriptions. Local macOS Messages access uses a separate provider, unlike this installation.

[Connection and routing](https://photon.codes/docs/spectrum-ts/providers/imessage/connection-and-routing) documents shared-pool and dedicated allocation. Dedicated multi-line operation uses phone parameters; space.phone indicates the routing number. With a second dedicated line, space.get requires phone and unpinned space.create chooses randomly. Shared-pool routing ignores the phone parameter. Line changes reach the app through credential renewal.

These establish managed-line routing support, not independent Apple Account sign-in, ownership of a particular device, actual alias-level destination attestation, or this project's plan. Do not provision a line while the existing bridge is unprepared: automatic discovery can expose it to the running app.

## Capability-by-capability decision

| Required capability | Installed SDK source | Active nonsecret configuration | Provider documentation / device action | Finding |
|---|---|---|---|---|
| 1. Existing deployment shared or dedicated | Cloud response selects mode dynamically; both branches exist | Active bridge metadata and source verified; no mode-only manifest available | Project owner must supply mode and line count without tokens | **Unknown** |
| 2. Dedicated line binds separate Apple identity | Remote instance/phone mapping exists; no Apple sign-in/account binding API established | No binding manifest | Managed dedicated numbers documented; independent Apple Account and aliases need provider confirmation | **Unknown for Option A** |
| 3. Connected host supports two signed-in identities simultaneously | Remote transport reveals no host account/session topology | Actual upstream host not identified | Provider/device administrator must attest account/session/host isolation | **Unknown**; two lines do not imply two sign-ins on one host |
| 4. Authenticated receiving identity/line per inbound event | Dedicated stream label is carried as space.phone; instance key not emitted by bridge; shared sentinel ambiguous | No active mode or attested label-to-identity mapping | Provider must confirm immutable connection binding, destination and alias semantics | **Conditional line provenance; actual receiving Apple identity unverified** |
| 5. Explicit outbound Research identity | Dedicated SDK selects client from space.phone; bridge lacks protected explicit selection | No approved Research binding | Per-phone dedicated routing documented; Apple From identity and receipts need confirmation | **SDK line selection confirmed; current bridge/Apple identity guarantee unverified** |
| 6. Additional line without new Photon service | One app aggregates multiple client streams | Existing service verified, entitlement unknown | One-app project discovery documented | **Provider architecture supports it; deployment readiness not established** |
| 7. Another messaging host required | Instance endpoints exist but physical host/session mapping is opaque | No host manifest | Provider/device administrator must answer | **Unknown** |
| 8. Unavailable settings | Schema does not reveal account custody or project allocation | Plan, mode, line inventory, host and account bindings unavailable | Owner-controlled provider/device metadata required | **Not resolvable by installed source alone** |

## Exact remaining nonsecret questions

Photon project owner/provider should answer with opaque labels and approval references, not account identifiers or secrets:

1. Which provider platform/API generation and plan does this active project use? Is its current mode shared or dedicated, and how many active dedicated instances/lines exist? Provide timestamped mode/count metadata only.
2. Can this project add a stable Research-only dedicated line independently of Personal, and does that represent a provider-managed number, an alias of the same Apple Account, or a separate Apple Account? Can an owner-controlled separate Apple Account be connected at all?
3. Can the existing SDK connection subscribe to both identities without a separate project, connection or Photon deployment? State entitlement and isolation constraints for SDK 12.7.0; distinguish cloud instance from physical host.
4. Which immutable instance/connection and authenticated destination fields identify each incoming event? Does space.phone attest the actual receiving number or merely the selected stream? How are email aliases, groups, repeated line labels, reconnects and shared mode handled? Can a stable instance reference be exposed without credentials?
5. Does selecting a dedicated client guarantee the approved Research From identity for every send/reply? Is there a receipt binding sender identity, connection and event? What happens if the line is removed, reassigned or unavailable—can the provider fall back to another identity?
6. Are line provisioning/auto-scale changes automatically exposed to this running project? Can Research remain unregistered or isolated until bridge routing is reviewed, while Personal stays unchanged? Provide renewal/revocation behavior without changing settings.

Messaging-device administrator/provider should answer:

7. Who operates the actual Apple messaging host, and is there one or more host/session per dedicated instance? Supply opaque custody/host references only.
8. Can the existing host maintain the required two independent messaging identities concurrently without signing out or disrupting Personal? Identify supported session/account arrangement; do not infer this from multiple receiving aliases.
9. If not, is another managed instance, OS user session, device or physical host required? Who supplies the Apple Account, trusted device/number, sign-in and recovery prerequisites? What provider-supported configuration would preserve Personal throughout? No sign-in or registration is requested now.

A safe response is a redacted owner-produced manifest containing mode, counts, capability revision, opaque host/connection/identity bindings and explicit yes/no answers with documentation references. Do not provide raw SDK authentication responses, config/environment dumps, tokens, phone numbers, Apple IDs or message histories. No provider contact was made on the owner's behalf.

## Release decision and next action

**D remains the evidence-supported decision.** A separate stable managed number may eventually fit B with the reviewed existing bridge/Hermes extension; an independently signed-in Apple Account could require C. Neither can be chosen from source or general documentation alone. The existing fail-closed route and activation gates remain applicable; no second consumer/service or Research profile is authorized.

**Next owner action:** have the Photon project owner and messaging-device administrator return the nine nonsecret answers above. Reassess A/B/C against that manifest, then separately approve any adapter staging or identity provisioning. Keep the Research identity uncreated and Personal service unchanged until closure.
