# Phase 7U — Minimal change inventory

2026-10-16. Static inventory; no source/package changes or installation. See [release decision](PHASE7U_MEMORY_RELEASE_DECISION.md) for acceptance and rollback gates.

## Minimal runtime release

Exactly one changed runtime file: `focused_v1/store.py`. Two line substitutions, zero added runtime files, zero deleted files. No Research source, test fixture, grant, route, schema, migration or dependency change belongs in this release.

| Identity | Bytes | SHA-256 |
|---|---:|---|
| Untouched tested baseline store.py | 29402 | `5ca002bd93e486875191292c21ba782fb2df5eb3fa4d525654e80ad29069cf8c` |
| Corrected store.py / 7T source member | 29426 | `0d84c9c12c0715f14be7729a5007073ebc99f55fa7820e6bed81a55834d969c1` |

Local inputs are `artifacts/staging/phase7h-memory/{baseline,work}/focused_v1/store.py`; the candidate member is `contents/source/focused_v1/store.py`. Intended installed logical path is `source/focused_v1/store.py` within an owner-approved existing Memory release. No new destination or installation command is approved here.

```diff
--- baseline/focused_v1/store.py
+++ candidate/focused_v1/store.py
@@ -273,13 +273,13 @@
             raise Denied("Source memory was deleted")
         with self._db() as db:
             if source_message_id is not None:
-                prior = db.execute("SELECT id,principal,task_id,content FROM memories WHERE source_message_id=?",
+                prior = db.execute("SELECT id,principal,task_id,content,review_state FROM memories WHERE source_message_id=?",
                                    (source_message_id,)).fetchone()
                 if prior:
                     if prior["principal"] != actor["id"] or prior["task_id"] != task_id or \
                             prior["content"] != content:
                         raise Denied("Conflicting memory provenance")
-                    return {"id":prior["id"],"review_state":"approved","saved":True,"duplicate":True}
+                    return {"id":prior["id"],"review_state":prior["review_state"],"saved":True,"duplicate":True}
             db.execute("""INSERT INTO memories(id,principal,task_id,kind,content,source_message_id,
               created_at,updated_at,review_state,historical) VALUES(?,?,?,?,?,?,?,?,?,?)""",
               (identifier,actor["id"],task_id,kind,content,source_message_id,stamp,stamp,state,int(historical)))
```

The SELECT only reads existing review state; return uses that exact value. Existing authorization/provenance checks and response shape remain. No database migration or data rewrite is required. This diff is the complete narrow source correction.

## File-by-file source disposition

This table covers the 36 paths in the 7T full comparison: 33 unchanged, one modified, two added, zero removed. Hash is candidate/work identity; unchanged entries equal the recorded baseline. It does not cover every installed file. Unchanged files are retained from the existing compatible release, not new overlay payload. Historical test files remain tests rather than runtime installation files.

| Relative path | Decision | Candidate SHA-256 |
|---|---|---|
| `deploy/focused-v1/obsidian_export.py` | Unchanged baseline; no release change | `ba42372ba7221a1273f14e07a10688694997abb468ab18ed92e601d2aef11d54` |
| `deploy/obsidian-editor/disposable-test/inspect-delivery-state.py` | Unchanged baseline; no release change | `f12e46da999151ccd6598d3d5a93171697b88c33e3aef60a5db1bb95d4318597` |
| `device/alfred-memory-editor/core.js` | Unchanged baseline; no release change | `887635ef18b5b4f2f50efd4019b233bc4748f7b2c26389776472c0d06cf52fc6` |
| `device/alfred-memory-editor/device.js` | Unchanged baseline; no release change | `a7aa4ef8f31296c93445285d527a5faa816f04124e4413710990ebbacba69ec9` |
| `device/alfred-memory-editor/test/hq-integration-driver.js` | Unchanged baseline; no release change | `04dd42011a324967af4511853530e77780624afdb5c79d1b3c9fb132bfd679df` |
| `focused_v1/__init__.py` | Unchanged baseline; no release change | `a45b4b3c132df7e1d8c830087185e752fc3dcd8f26b9d4a56e6626fe2dc3f8cb` |
| `focused_v1/research_stage.py` | Research extension; synthetic-only, production BLOCKED | `15e24eb7aa3f84f8796d12dd9d4684d2748943cfda58dc3fa8827428b12dcd3a` |
| `focused_v1/server.py` | Unchanged baseline; no release change | `2042c95d517601da03654b942b04bf96ed69bedf5afa0351ef64463542eba5ea` |
| `focused_v1/store.py` | Narrow bug fix; only changed runtime payload | `0d84c9c12c0715f14be7729a5007073ebc99f55fa7820e6bed81a55834d969c1` |
| `obsidian_candidate/__init__.py` | Unchanged baseline; no release change | `ad5ff6eece3dceb083367cd470edd09eda66d1bb5fcd134905df9ed0a6a06e8f` |
| `obsidian_candidate/alfred_editor_v1.py` | Unchanged baseline; no release change | `abd5f415cc075193ff65885c200d58d22a8af66d227a6ced7331e71403c9e8ff` |
| `obsidian_candidate/bridge.py` | Unchanged baseline; no release change | `775448b247c3a8813cbd3f94a2b1e17fe211c9fca1a72033b165ee7e0226a818` |
| `obsidian_candidate/capture_routes.py` | Unchanged baseline; no release change | `394418ff4ba612bddc7d20a2d07dce0cdfba0bf55664425c8a0f103141fa9db1` |
| `obsidian_candidate/context.py` | Unchanged baseline; no release change | `1d7faf8d4330e18d4a0c02f26ce536534f7d597becadf95b541bfb5c858cd7e8` |
| `obsidian_candidate/context_service.py` | Unchanged baseline; no release change | `86884fa67b808ea954d769c07f78a150ad1dd51290dd9f117667470aaccdd981` |
| `obsidian_candidate/cycle.py` | Unchanged baseline; no release change | `db66c01071c152513e63358355b83c795dd0c16f0ae3ab2bb941b168512e2ba8` |
| `obsidian_candidate/disposable_delivery.py` | Unchanged baseline; no release change | `79e4fd9718c9647e52933cb241e52955adb3b8059d1039ed4907d16cf7605115` |
| `obsidian_candidate/disposable_forced.py` | Unchanged baseline; no release change | `51c0446f383f908453b135a9d2dc3e11b15db44c3babdb0467bc45f46ea9a3f2` |
| `obsidian_candidate/editor_origin.py` | Unchanged baseline; no release change | `b24ad623668846195dfd533e3fad89090e4f935305f2365a00baaa836d97079a` |
| `obsidian_candidate/editor_transport.py` | Unchanged baseline; no release change | `8c7406b5db9e2d9e1b97280a48b24b81d59219db404b7038acb1feed8d59b14d` |
| `obsidian_candidate/hq_sync_once.py` | Unchanged baseline; no release change | `0724ed765fc43e67d4435b7eb12ac2225181c728557c933196e54bdbcdacdfc5` |
| `obsidian_candidate/ingress.py` | Unchanged baseline; no release change | `1c89ad12ee9392fb7ee215a772846af641b2258725c6c66e78f6737fc26ac7d9` |
| `obsidian_candidate/notifications.py` | Unchanged baseline; no release change | `52b7b374da786315a3d2b0f7ffbe8d1b5051a5ca8f86d6766d2a05397b0de153` |
| `obsidian_candidate/outcome_gate.py` | Unchanged baseline; no release change | `9ebc79cb0eb4e93e35b17e9b54a30de100b0abd6d724dacfbb794a8ecab2de8f` |
| `obsidian_candidate/recovery.py` | Unchanged baseline; no release change | `66cb0baa8ed5a6a750e6cb151767a36932c094c88940a08c710c7288013aaabb` |
| `obsidian_candidate/references.py` | Unchanged baseline; no release change | `3a138940515de1e8c7bed4f2958ddc22d243d32a31d340f6f476cd2823f090d5` |
| `obsidian_candidate/routing.py` | Unchanged baseline; no release change | `328afa38ae7897fef333d30b16f56a172e9429aa292e5b82ab5b29c57b183570` |
| `obsidian_candidate/scaffold.py` | Unchanged baseline; no release change | `0dce2be530e784154079a70d37657cea33f75ef2cf3a08084722dc5ee0195eac` |
| `obsidian_candidate/scoped_ports.py` | Unchanged baseline; no release change | `c8110549122df6c300bd0514dfd07c4ac326edceef8d5a2276840a5f544de000` |
| `obsidian_candidate/service_api.py` | Unchanged baseline; no release change | `f7fdcd5b01bf12b13415b8f4bbd7edbb7629ae0856b7267bca743b6773282cc5` |
| `obsidian_candidate/snapshot.py` | Unchanged baseline; no release change | `d27b3b5dc2b67476da421ca10128651352ca0ed4c584cde40204ac6e5be47b43` |
| `scripts/count_only_v1_ownership.py` | Unchanged baseline; no release change | `b4953049ee6c6d21e13dcee11c657cbb4edb5d16cfc56180a3ec02bb0f4b3129` |
| `tests/test_focused_v1_obsidian_export.py` | Unchanged baseline; no release change | `8e7cc28875fc714a517ec13755af2a1e7e42b8cabefac37a075b253626d481b1` |
| `tests/test_obsidian_candidate.py` | Unchanged baseline; no release change | `746f42e2c4f094374b04ded1677ccd95cbb5cbcd03d8bfe432c7c4c511596cef` |
| `tests/test_obsidian_disposable_delivery.py` | Unchanged baseline; no release change | `14ba0777502fd895aefc66648987f7c2ac8d9ee26d9e9a9442d4da439ad78167` |
| `tests/test_research_memory_stage.py` | Test-only; exclude from runtime payload | `53e1f0b095443401ec79daa8a0a7c534a48c47b649972395123af1d457e6cd1e` |

## Existing mixed candidate package

Mac-local archive: `artifacts/releases/alfred-memory-research-extension-0.1.0-rc1-phase7t-linux-20261016/alfred-memory-research-extension-0.1.0-rc1-phase7t-linux-20261016.tar.gz`.

SHA-256: `77c8fa1487ccc4d42919ef38a334da4e98d5a29e5798bcb69429660bfd8eca00` (recomputed in Phase 7U). This is the mixed 7T review archive, not a separately packaged narrow fix. Do not install it wholesale. No new archive was created or transferred.

All ten regular candidate members are classified below. Metadata is review evidence, not runtime code or authorization. FULL_DIFF includes both tracks and is not the narrow patch above.

| Candidate member | Disposition | SHA-256 |
|---|---|---|
| `BASELINE_MANIFEST.json` | Review evidence; no runtime installation | `13c01987ac459d9aa95ef266cc39884a909f88e93bc1dbc4fa5ed6fa03e7b700` |
| `FULL_DIFF.patch` | Review evidence; no runtime installation | `8add6781899c220bb4489636599db2401ffbe8263ed30bdf813f9cab5df50e1f` |
| `README.md` | Review evidence; no runtime installation | `eb53835240a91d9340650f38279ec342c31723990d00bd94be56fcb733752f5b` |
| `RESEARCH_DEPENDENCIES.json` | Review evidence; no runtime installation | `2b0909fc50bc7ef1d3407746a057d93286dba8436f7139aed215672a3beaa4f5` |
| `TEST_EVIDENCE.json` | Review evidence; no runtime installation | `e5a09f9cbd138f86bb389bf645ff6ac7a402aad16cbe41bc39d36ab33bc58ba6` |
| `source/focused_v1/research_stage.py` | Research extension; synthetic-only, exclude from narrow release | `15e24eb7aa3f84f8796d12dd9d4684d2748943cfda58dc3fa8827428b12dcd3a` |
| `source/focused_v1/store.py` | Only narrow runtime change | `0d84c9c12c0715f14be7729a5007073ebc99f55fa7820e6bed81a55834d969c1` |
| `tests/test_research_memory_stage.py` | Test-only, exclude from runtime release | `53e1f0b095443401ec79daa8a0a7c534a48c47b649972395123af1d457e6cd1e` |
| `CANDIDATE_MANIFEST.json` | Integrity metadata; no runtime installation | `2e01004743beef79fefc874780d5679024f4cf0ec91a7988932c82339eb599b9` |
| `FILES.sha256` | Integrity metadata; no runtime installation | `c3948fe0d55785de7be6b498a8476c74c3b76256beacc97fbb863d2087b0ceed` |

The candidate manifest's eight listed payload/evidence files were size/hash checked locally; corrected store bytes match the work copy exactly. FILES.sha256 and manifest identities are recorded above. These checks do not replace an installation-time source/manifest verification or the prior archive integrity report.

## Research-only boundaries and excluded requirements

`research_stage.py` contains TestAuthority, synthetic candidate/attestation/receipt handling, explicit staging schema setup, commit/simulated-promotion/retrieval and validity controls. It remains production-disabled; real promote/dispatch deny, delete/export unavailable. Its added four staging tables and codec dependency closure are excluded from the one-file release. Tests, public-key fixtures, synthetic grants and operation state must never become production credentials, authorities or company data.

The untouched baseline includes existing server and Obsidian integration sources. The narrow correction does not change them, authentication configuration or permissions. Owner acceptance must still assess clients interpreting review_state. A current installed baseline recheck is mandatory: historical store hash above must match before use, and any drift stops installation pending review. No current Linux check was performed here.

**Disposition:** narrow fix ready for owner installation review; production Research extension blocked. Separate immutable narrow packaging and approved installation/acceptance/rollback actions remain outstanding. This phase created only the two requested Markdown reports.
