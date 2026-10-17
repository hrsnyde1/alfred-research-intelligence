# Research iMessage identity support

2026-10-16. **D — Not established; additional provider information required. Activation BLOCKED.** Multiple dedicated lines are supported by the installed SDK architecture, but a second Apple Account, its messaging host, current project entitlement and authoritative destination/sending binding are not established. Multiple conversations do not establish multiple accounts. A is not supported by the evidence; B is conditional on provider confirmation; C cannot yet be determined.

## Inspection and evidence

Read the Personal intake implementation/approvals, Phase 7C adapter specification, prior route contract/change/acceptance documents, current intake source and test definitions, and installed Photon/Spectrum source definitions. Prior route audit found no Phase 7F findings. No tests, SDK initialization, inbound subscriptions or provider/account APIs were executed.

Fresh SSH used `ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81`. Only source/package/type files and `systemctl show` fields Id, ActiveState, SubState, User, Group, WorkingDirectory and CanReload were read. Local sandbox initially denied SSH; approved read-only retry succeeded. Remote rg was unavailable; grep/sed read source instead. No package installation occurred.

Installed source root: `/home/alfred/.hermes/hermes-agent/`. Sidecar package is 0.4.0, pins spectrum-ts 12.7.0. SHA-256:

| File relative to root | Digest |
|---|---|
| plugins/platforms/photon/sidecar/index.mjs | ef019d1d50e4ca680aede49276181f8eff8d396d9b7c22a73bb5da2b2d7bb8e4 |
| plugins/platforms/photon/adapter.py | 841ed6cb6e2d392fcec33f8983dd34fffe677c6a8d40e442bc449e66beeb16e5 |
| plugins/platforms/photon/sidecar/package.json | 46d0f09d403e8d67261e23d5114dda13654179234ff748959923b8806c186cca |
| plugins/platforms/photon/sidecar/node_modules/@spectrum-ts/imessage/dist/index.js | 9faf0be1530dde1e2f80b580d12377a1fa6b0995c3595794648237a2c8f241ee |
| plugins/platforms/photon/sidecar/node_modules/@spectrum-ts/imessage/dist/index.d.ts | 06b9442709fa2832f3e1abb985291d87787dcf2c406b372cba1c59c75929f26d |

Prior full Hermes source evidence and metadata remain in `artifacts/audits/personal-research-route-20261016/`; bridge digests were freshly reconfirmed. Hermes routing/hook observations below refer to that captured installed source, not a fresh digest of every Hermes module or proof of loaded process code.

## Architecture and capability decision

| Question | Evidence and finding |
|---|---|
| Which host owns the Apple sign-in? | Linux runs a Spectrum client bridge using project authentication and remote iMessage provider; not the local Messages database provider. Actual upstream Mac/device, operator and signed-in account are **unknown**. No Apple login metadata was accessed. |
| Multiple identities? | Provider types index.d.ts:189–193,553–581 allow RemoteClient[] and clients entries with address/token/phone. index.js:2502–2518 merges streams by line key; cloud code reconciles dedicated instances. This establishes multiple client lines, not independent Apple Account support or current entitlement. |
| Second Apple Account or receiving number on existing connection? | Not established. Provider shared-token mode index.js:250–255 explicitly documents no recipient on inbound and no from on send. Dedicated lines select clients by phone. Active shared/dedicated mode and line count were not queried. |
| Authoritative destination? | Dedicated stream supplies its configured line label to conversion, not necessarily the actual Apple receiving alias. space.phone can be that label or `shared`; it must not be treated as authoritative Apple recipient without provider attestation. No independent recipient/account/connection identity survives bridge normalization. |
| Outbound choice? | SDK send selects clientForPhone(client,space.phone), index.js:2972. Shared mode uses one shared client. Bridge POST /send accepts spaceId/text/format, not explicit authorized line/account. Rehydration space.get lacks params.phone, which SDK requires with multiple clients; space.create without phone can select a random dedicated line. |
| Simultaneous Personal/Research without another service? | SDK stream aggregation makes this structurally plausible for dedicated lines. Current bridge cache keyed only by spaceId and missing explicit line selection prevent a safe claim. Account/device prerequisites and entitlement remain unresolved. No second service is justified yet. |

Official primary [Spectrum repository](https://github.com/photon-hq/spectrum-ts) describes hosted iMessage and separate local-provider options. Its current README is contextual evidence, not proof of installed-version entitlements or this project's actual host/account. The package homepage fetch failed; no provider capability answer is inferred from it.

Fresh service metadata: alfred-hermes.service active/running as alfredmsg, cwd /var/lib/alfredmsg/hermes; alfred-photon.service active/running as alfredphoton, cwd the sidecar directory. Both CanReload=no. Prior audit could not read the active Hermes service home (0700); readable credential-bearing alternative config was deliberately not opened. Thus effective Personal account/profile/route binding remains unverified. No personal addresses, Apple IDs, tokens, message content/history, databases or vaults were read or reproduced.

## Exact next owner action

Ask the Photon project owner/provider and messaging-device owner for a **nonsecret, redacted capability/binding manifest**, without creating or signing into anything: active shared/dedicated mode; authorized line count and second-line entitlement; whether independent Apple Accounts are supported per project/connection; actual messaging host/device custody; account/device/number prerequisites; stable connection/instance IDs; authoritative inbound local-destination fields and alias semantics; outbound account selection/receipt behavior; restart and line-removal semantics. Supply opaque labels in these reports; keep actual address mapping under owner control. Do not supply tokens, account credentials, histories or raw environment/config dumps.

If dedicated independent lines and explicit binding are proven, review the small existing bridge/Hermes extension described in the route document (conditional B). If the provider requires another host/account connection, return a separate C proposal for approval. Neither outcome authorizes identity registration or activation.
