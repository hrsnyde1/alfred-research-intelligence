# Phase 7T — complete compared-file diff and compatibility report

2026-10-16. **Installed tested-baseline comparison PASS: 34/34 paths match; no mismatch.** Minimal overlay: one modified original plus two added files. Candidate bytes are identical to Phase 7S inputs. No Linux source writes or new tests.

## Comparison authority and scope

Installed current target: `/opt/alfred-obsidian-v1/releases/4d5ba29bd3027e74c808a8feaf1b5dadfded22f0`; source at its `source/` child. Test baseline authority: `artifacts/staging/phase7h-memory/BASELINE_MANIFEST.json`, SHA-256 `13c01987ac459d9aa95ef266cc39884a909f88e93bc1dbc4fa5ed6fa03e7b700`. All 34 listed byte counts/hashes match both untouched local baseline and current installed source; final reinspection matches initial inspection. Linux staged payload/checksum also matches tested pins.

This is the complete file-by-file comparison for the **34-path tested snapshot and two candidate additions**, not an invented complete snapshot of every installed file. Other installed source consumers are left untouched and need review before installation. Both added paths were explicitly checked absent in installed source. No unrecorded installed file is overwritten by the planned overlay. Candidate includes no removed files.

## File-by-file hashes

Paths below are relative to the copied Memory source root. UNCHANGED means original baseline, installed allowlisted source and candidate-inherited bytes match; these files are not redundantly packaged. ADDED means absent in tested/installed baseline and supplied in candidate. The test addition is validation-only.

| Path | Status | Baseline / installed SHA-256 | Candidate SHA-256 |
| --- | --- | --- | --- |
| `deploy/focused-v1/obsidian_export.py` | UNCHANGED | `ba42372ba7221a1273f14e07a10688694997abb468ab18ed92e601d2aef11d54` | `ba42372ba7221a1273f14e07a10688694997abb468ab18ed92e601d2aef11d54` |
| `deploy/obsidian-editor/disposable-test/inspect-delivery-state.py` | UNCHANGED | `f12e46da999151ccd6598d3d5a93171697b88c33e3aef60a5db1bb95d4318597` | `f12e46da999151ccd6598d3d5a93171697b88c33e3aef60a5db1bb95d4318597` |
| `device/alfred-memory-editor/core.js` | UNCHANGED | `887635ef18b5b4f2f50efd4019b233bc4748f7b2c26389776472c0d06cf52fc6` | `887635ef18b5b4f2f50efd4019b233bc4748f7b2c26389776472c0d06cf52fc6` |
| `device/alfred-memory-editor/device.js` | UNCHANGED | `a7aa4ef8f31296c93445285d527a5faa816f04124e4413710990ebbacba69ec9` | `a7aa4ef8f31296c93445285d527a5faa816f04124e4413710990ebbacba69ec9` |
| `device/alfred-memory-editor/test/hq-integration-driver.js` | UNCHANGED | `04dd42011a324967af4511853530e77780624afdb5c79d1b3c9fb132bfd679df` | `04dd42011a324967af4511853530e77780624afdb5c79d1b3c9fb132bfd679df` |
| `focused_v1/__init__.py` | UNCHANGED | `a45b4b3c132df7e1d8c830087185e752fc3dcd8f26b9d4a56e6626fe2dc3f8cb` | `a45b4b3c132df7e1d8c830087185e752fc3dcd8f26b9d4a56e6626fe2dc3f8cb` |
| `focused_v1/research_stage.py` | ADDED | Absent | `15e24eb7aa3f84f8796d12dd9d4684d2748943cfda58dc3fa8827428b12dcd3a` |
| `focused_v1/server.py` | UNCHANGED | `2042c95d517601da03654b942b04bf96ed69bedf5afa0351ef64463542eba5ea` | `2042c95d517601da03654b942b04bf96ed69bedf5afa0351ef64463542eba5ea` |
| `focused_v1/store.py` | MODIFIED | `5ca002bd93e486875191292c21ba782fb2df5eb3fa4d525654e80ad29069cf8c` | `0d84c9c12c0715f14be7729a5007073ebc99f55fa7820e6bed81a55834d969c1` |
| `obsidian_candidate/__init__.py` | UNCHANGED | `ad5ff6eece3dceb083367cd470edd09eda66d1bb5fcd134905df9ed0a6a06e8f` | `ad5ff6eece3dceb083367cd470edd09eda66d1bb5fcd134905df9ed0a6a06e8f` |
| `obsidian_candidate/alfred_editor_v1.py` | UNCHANGED | `abd5f415cc075193ff65885c200d58d22a8af66d227a6ced7331e71403c9e8ff` | `abd5f415cc075193ff65885c200d58d22a8af66d227a6ced7331e71403c9e8ff` |
| `obsidian_candidate/bridge.py` | UNCHANGED | `775448b247c3a8813cbd3f94a2b1e17fe211c9fca1a72033b165ee7e0226a818` | `775448b247c3a8813cbd3f94a2b1e17fe211c9fca1a72033b165ee7e0226a818` |
| `obsidian_candidate/capture_routes.py` | UNCHANGED | `394418ff4ba612bddc7d20a2d07dce0cdfba0bf55664425c8a0f103141fa9db1` | `394418ff4ba612bddc7d20a2d07dce0cdfba0bf55664425c8a0f103141fa9db1` |
| `obsidian_candidate/context.py` | UNCHANGED | `1d7faf8d4330e18d4a0c02f26ce536534f7d597becadf95b541bfb5c858cd7e8` | `1d7faf8d4330e18d4a0c02f26ce536534f7d597becadf95b541bfb5c858cd7e8` |
| `obsidian_candidate/context_service.py` | UNCHANGED | `86884fa67b808ea954d769c07f78a150ad1dd51290dd9f117667470aaccdd981` | `86884fa67b808ea954d769c07f78a150ad1dd51290dd9f117667470aaccdd981` |
| `obsidian_candidate/cycle.py` | UNCHANGED | `db66c01071c152513e63358355b83c795dd0c16f0ae3ab2bb941b168512e2ba8` | `db66c01071c152513e63358355b83c795dd0c16f0ae3ab2bb941b168512e2ba8` |
| `obsidian_candidate/disposable_delivery.py` | UNCHANGED | `79e4fd9718c9647e52933cb241e52955adb3b8059d1039ed4907d16cf7605115` | `79e4fd9718c9647e52933cb241e52955adb3b8059d1039ed4907d16cf7605115` |
| `obsidian_candidate/disposable_forced.py` | UNCHANGED | `51c0446f383f908453b135a9d2dc3e11b15db44c3babdb0467bc45f46ea9a3f2` | `51c0446f383f908453b135a9d2dc3e11b15db44c3babdb0467bc45f46ea9a3f2` |
| `obsidian_candidate/editor_origin.py` | UNCHANGED | `b24ad623668846195dfd533e3fad89090e4f935305f2365a00baaa836d97079a` | `b24ad623668846195dfd533e3fad89090e4f935305f2365a00baaa836d97079a` |
| `obsidian_candidate/editor_transport.py` | UNCHANGED | `8c7406b5db9e2d9e1b97280a48b24b81d59219db404b7038acb1feed8d59b14d` | `8c7406b5db9e2d9e1b97280a48b24b81d59219db404b7038acb1feed8d59b14d` |
| `obsidian_candidate/hq_sync_once.py` | UNCHANGED | `0724ed765fc43e67d4435b7eb12ac2225181c728557c933196e54bdbcdacdfc5` | `0724ed765fc43e67d4435b7eb12ac2225181c728557c933196e54bdbcdacdfc5` |
| `obsidian_candidate/ingress.py` | UNCHANGED | `1c89ad12ee9392fb7ee215a772846af641b2258725c6c66e78f6737fc26ac7d9` | `1c89ad12ee9392fb7ee215a772846af641b2258725c6c66e78f6737fc26ac7d9` |
| `obsidian_candidate/notifications.py` | UNCHANGED | `52b7b374da786315a3d2b0f7ffbe8d1b5051a5ca8f86d6766d2a05397b0de153` | `52b7b374da786315a3d2b0f7ffbe8d1b5051a5ca8f86d6766d2a05397b0de153` |
| `obsidian_candidate/outcome_gate.py` | UNCHANGED | `9ebc79cb0eb4e93e35b17e9b54a30de100b0abd6d724dacfbb794a8ecab2de8f` | `9ebc79cb0eb4e93e35b17e9b54a30de100b0abd6d724dacfbb794a8ecab2de8f` |
| `obsidian_candidate/recovery.py` | UNCHANGED | `66cb0baa8ed5a6a750e6cb151767a36932c094c88940a08c710c7288013aaabb` | `66cb0baa8ed5a6a750e6cb151767a36932c094c88940a08c710c7288013aaabb` |
| `obsidian_candidate/references.py` | UNCHANGED | `3a138940515de1e8c7bed4f2958ddc22d243d32a31d340f6f476cd2823f090d5` | `3a138940515de1e8c7bed4f2958ddc22d243d32a31d340f6f476cd2823f090d5` |
| `obsidian_candidate/routing.py` | UNCHANGED | `328afa38ae7897fef333d30b16f56a172e9429aa292e5b82ab5b29c57b183570` | `328afa38ae7897fef333d30b16f56a172e9429aa292e5b82ab5b29c57b183570` |
| `obsidian_candidate/scaffold.py` | UNCHANGED | `0dce2be530e784154079a70d37657cea33f75ef2cf3a08084722dc5ee0195eac` | `0dce2be530e784154079a70d37657cea33f75ef2cf3a08084722dc5ee0195eac` |
| `obsidian_candidate/scoped_ports.py` | UNCHANGED | `c8110549122df6c300bd0514dfd07c4ac326edceef8d5a2276840a5f544de000` | `c8110549122df6c300bd0514dfd07c4ac326edceef8d5a2276840a5f544de000` |
| `obsidian_candidate/service_api.py` | UNCHANGED | `f7fdcd5b01bf12b13415b8f4bbd7edbb7629ae0856b7267bca743b6773282cc5` | `f7fdcd5b01bf12b13415b8f4bbd7edbb7629ae0856b7267bca743b6773282cc5` |
| `obsidian_candidate/snapshot.py` | UNCHANGED | `d27b3b5dc2b67476da421ca10128651352ca0ed4c584cde40204ac6e5be47b43` | `d27b3b5dc2b67476da421ca10128651352ca0ed4c584cde40204ac6e5be47b43` |
| `scripts/count_only_v1_ownership.py` | UNCHANGED | `b4953049ee6c6d21e13dcee11c657cbb4edb5d16cfc56180a3ec02bb0f4b3129` | `b4953049ee6c6d21e13dcee11c657cbb4edb5d16cfc56180a3ec02bb0f4b3129` |
| `tests/test_focused_v1_obsidian_export.py` | UNCHANGED | `8e7cc28875fc714a517ec13755af2a1e7e42b8cabefac37a075b253626d481b1` | `8e7cc28875fc714a517ec13755af2a1e7e42b8cabefac37a075b253626d481b1` |
| `tests/test_obsidian_candidate.py` | UNCHANGED | `746f42e2c4f094374b04ded1677ccd95cbb5cbcd03d8bfe432c7c4c511596cef` | `746f42e2c4f094374b04ded1677ccd95cbb5cbcd03d8bfe432c7c4c511596cef` |
| `tests/test_obsidian_disposable_delivery.py` | UNCHANGED | `14ba0777502fd895aefc66648987f7c2ac8d9ee26d9e9a9442d4da439ad78167` | `14ba0777502fd895aefc66648987f7c2ac8d9ee26d9e9a9442d4da439ad78167` |
| `tests/test_research_memory_stage.py` | ADDED | Absent | `53e1f0b095443401ec79daa8a0a7c534a48c47b649972395123af1d457e6cd1e` |

Counts: **33 unchanged, 1 modified, 2 added, 0 removed**. Full unabridged changed-file patch: [FULL_DIFF.patch](../artifacts/releases/alfred-memory-research-extension-0.1.0-rc1-phase7t-linux-20261016/contents/FULL_DIFF.patch), SHA-256 `8add6781899c220bb4489636599db2401ffbe8263ed30bdf813f9cab5df50e1f`. Added files appear as complete `/dev/null` additions; no implementation/test lines are omitted in the patch.

## Existing API compatibility

Only `MemoryStore.create` duplicate lookup/response changes: select stored review_state and return it instead of literal approved. Id/saved/duplicate keys, provenance actor/task/content comparison, authorization, insert behavior and stored review state are preserved. No row is reviewed/promoted by this response fix. An approved original with pending replacement still reports the original stored state; this is not approval of the edit. Existing branch kind handling is unchanged and remains a separately owned policy question.

`focused_v1/server.py` and `obsidian_candidate/service_api.py` are byte-identical to installed baseline. `/v1/memory` actions capture/create/update/delete/search/forget/review/pending_reviews, 131072-byte request bound and errors are unchanged. `/v1/obsidian-memory` and bridge fixed-actor behavior are untouched. No Research action or route is registered. Existing source consumers outside the 34-path snapshot have not had behavioral regression coverage; truthful duplicate reply values can affect clients and require component-owner review.

No Obsidian code, export mapping, Sync worker, view file or vault format is changed. Research records are stored separately in staging tables, never auto-approved generic memories or a default legacy export projection. This is source-level preservation plus the selected test scope, not a full Obsidian behavioral acceptance result.

## Additive Python API / contract inventory

All APIs below are **staging/test-only**, not enabled wire contracts:

| Type / operation | Implemented boundary |
| --- | --- |
| Candidate (`memory_research_candidate.staging.v1`) | Immutable typed packet, full source, decision/review, contributor set, category/topics/audiences/policy/acquisition refs and validity; exact packet/source/review/claim-evidence bindings and <=131072 canonical bytes |
| Attestation (`memory_research_attestation.test.v1`) | Candidate digest, verifier, issuer-local attestation ID, issue/expiry and SIMULATED marking; validated against injected in-memory authority, not a production signature issuer |
| Actor / TestAuthority | Explicit issued object identities/grants, company/role/classification/audience constraints, contributor binding and fixed verifier assignment; constructors deny normal production/default use |
| submit | Candidate validation, validity/attestation/current grant checks, distinct acceptance receipt and candidate state |
| commit / simulate_promotion | Separate CAS transitions and durable operation receipts; COMMITTED is not readable promoted knowledge; simulate_promotion remains NON_PRODUCTION |
| retrieve / reconcile / history | Full scoped candidate+citation retrieval; historical receipt replay labeled; current eligibility recomputed; historical access separate from fresh trust |
| revise / flag_conflict / expire / dispute / supersede / revoke | Immutable revision/CAS or current-state invalidation; stale/conflicting payload replay rejected; no silent old promotion reuse |
| promote / dispatch_research | Always Denied; no genuine production promotion path |
| delete / request_export | Always Unavailable pending Memory-owner retention/export policy |

Receipt schema `memory_research_receipt.staging.v1` carries schema/marking/issuer, receipt/operation IDs/type, caller/company, record/version/sequence, candidate and packet/version/source digests, decision/attestation refs, policy/classification/request digest, observed time, state and simulated outcome. It is not a signed production receipt contract or durable real verifier trust source. Current clocks/validity are injected integer policy, not an approved production UTC/time encoding.

## Database/schema inventory and migration requirements

Existing MemoryStore source still expects **PRAGMA user_version=3**. No base-schema alteration or data migration is needed for the duplicate-response correction. Live database schema/version was **not read** and must be supplied/approved independently before installation.

Only explicit test-only ResearchStage initialization adds:

```sql
CREATE TABLE research_stage_meta(version INTEGER NOT NULL);
INSERT INTO research_stage_meta VALUES(1);
CREATE TABLE research_stage_heads(env TEXT,id TEXT,revision INTEGER,state TEXT,sequence INTEGER,
 PRIMARY KEY(env,id));
CREATE TABLE research_stage_versions(env TEXT,id TEXT,revision INTEGER,digest TEXT,body TEXT,attestation TEXT,
 PRIMARY KEY(env,id,revision));
CREATE TABLE research_stage_ops(env TEXT,operation_id TEXT,payload_digest TEXT,receipt TEXT,
 PRIMARY KEY(env,operation_id));
```

`research_stage_meta` version 1 is separate from base user_version=3. If absent without initialize=True, construction fails; unsupported meta version fails. No migration utility is bundled and no startup migration has been enabled. This prototype DDL/meta check is not production migration validation: owner must define full schema/constraints/indexes/version policy, transaction/failure recovery, compatibility of old readers, backup/restore and rollback on real format examples using synthetic databases first. Do not run test initialize=True on production or reset an incompatible database.

Production approval must address full structured evidence/receipt retention, deletion/hold/suppression/tombstones, currentness and revocation ordering, immutable history limits and restore behavior. Existing production delete ledger must remain authoritative; prototype Research deletion/export intentionally fails closed. Source user_version staying 3 does not itself prove a downgrade/old-reader is safe once production projections exist.

## Authentication / permissions / production disable

Existing legacy authentication and token/assignment policy are unchanged. Prototype authority is injected/in-memory, independent of candidate data, and knows only synthetic actor grants. There is no authenticated Research HTTP port, persistent production attestation trust, issuer rotation/revocation integration, credential provisioning or real company mapping. Hashes/candidate APPROVED text/client booleans do not create factual trust.

Before production: establish host-issued tenant/principal/task/purpose mapping; explicit write, independent verifier, Memory-owned promoter and specialist read grants; exact provider/model/execution/issuer policy; trusted current attestation/receipt validation and revocation epochs. Director/lead/support/submitter may not self-verify or receive default promotion authority. A client role string, category, generic Alfred/bridge bearer or TestAuthority flag cannot confer real promotion permissions. Test admin/promoter permissions affect simulated states only.

Current production status is **disabled**: constructor guards, unconditional promote/dispatch denial, no route mount, no legacy projection, deletion/export unavailable. There is no second Memory service or new daemon. Existing /v1 behavior remains operational because no candidate code was installed here.

## Regression and rollback considerations

Phase 7S validates seven selected test-only methods plus paired duplicate response comparison. Sixteen extension methods, concurrency/restart/rotation, inherited Linux atomic/peer failures and broad legacy/Obsidian/device/export cases remain unexecuted. Historical Mac copied-suite failures must not be counted fixed. Existing outside-snapshot clients/backup/ops/Hermes modules also require owner regression review. No tests rerun in Phase 7T.

For a later approved dormant source-only release, rollback would restore the exact compatible prior source release under the Memory owner's process; no migration is implied and the old duplicate reply defect would return. No hot in-place overwrite or automatic service restart is authorized. If later schema/data or promotion/projection changes occur, source rollback alone is insufficient: disable new ingress/promotion grants, preserve operation receipts and current revocation/deletion state, reconcile ambiguous operations, and restore only a proven compatible snapshot. Never drop tables, downgrade user_version, restore stale trust/deletion generations or rewind published Obsidian state as an ad hoc rollback.

## Exact read-only comparison commands

Initial and final source checks, both SSH/Python exit 0, empty stderr:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' < /tmp/phase7t_inspect.py > /tmp/phase7t_inspect.out 2> /tmp/phase7t_inspect.err
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' < /tmp/phase7t_inspect.py > /tmp/phase7t_final_inspect.out 2> /tmp/phase7t_final_inspect.err
```

The initial sandbox-denied transport exited 255 before remote execution, then the approved retry completed. The stdlib inspection hashes only the 34 allowlisted installed source paths and 17 staging files, reads current symlink target, checksum manifest and immediate source filenames, and requests only ActiveState/SubState for alfred-memory-v1.service. No config, environment, logs, DB, vault or credential read. Script SHA-256: `ce930bfd92084456fabeaec588f4cb7983581529a31cc85252204d60ce7a5238`.

Added-path absence check, SSH exit 0:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 "python3 -I -S -B -c 'import pathlib,json,os; b=pathlib.Path("/opt/alfred-obsidian-v1/current/source").resolve(); print(json.dumps({p:os.path.lexists(b/p) for p in ("focused_v1/research_stage.py","tests/test_research_memory_stage.py")}))'"
```

Both paths reported false. Additional installed immediate filenames outside the tested snapshot were: focused_v1 backup.py, hermes_plugin, history.py, ops.py, requirements.txt, stage.py; obsidian_candidate hermes_composite.py, hermes_plugin, requirements-offline.txt. Those contents were not read or packaged. No full installed-source manifest is claimed.

## Complete changed-file unified diff

The following is the entire source/test diff used in the package, including both additions. Unchanged originals are fully accounted for in the hash table above.

```diff
--- /dev/null
+++ candidate/focused_v1/research_stage.py
@@ -0,0 +1,373 @@
+"""Memory-owned, explicitly test-only Research extension. NOT a live API.
+
+Uses the copied MemoryStore's SQLite transaction boundary, never generic
+auto-approved memories or vault projections. Production schema, attestation
+issuer and grants remain unresolved: production entrypoints always deny.
+"""
+from contextlib import contextmanager
+from dataclasses import dataclass
+import json
+from threading import RLock
+from typing import ClassVar
+from uuid import uuid4
+
+from alfred_research.contracts import (Contract, ResearchPacket, VerificationDecision,
+    ENVIRONMENTS, canonical, hash_content, integer, require, digest)
+from alfred_research.sources import SourceResult
+from alfred_research.research.contracts import VerificationReview
+from focused_v1.store import Denied, Unavailable
+
+MARKING = 'SIMULATED / NON_PRODUCTION'
+
+
+@dataclass(frozen=True, kw_only=True)
+class Candidate(Contract):
+    schema: ClassVar[str] = 'memory_research_candidate.staging.v1'
+    environment: str
+    packet: ResearchPacket
+    source: SourceResult
+    decision: VerificationDecision
+    review: VerificationReview
+    contributors: tuple[str, ...]
+    category: str
+    topics: tuple[str, ...]
+    audiences: tuple[str, ...]
+    policy_ref: str
+    acquisition_ref: str
+    valid_from: int
+    valid_until: int
+    marking: str = MARKING
+
+    def validate(self):
+        require(self.marking == MARKING, 'production candidate unsupported')
+        require(self.packet.environment == self.source.environment == self.decision.environment == self.environment,
+                'candidate scope mismatch')
+        require(self.packet.source == self.source.submitted and self.source.revision == (self.packet.source.revision,),
+                'source revision mismatch')
+        require(self.decision.packet_digest == self.packet.digest, 'packet decision mismatch')
+        require(self.review.environment==self.environment and self.review.task_id==self.packet.task_id and
+                self.review.packet_version==self.packet.packet_version and self.review.packet_digest==self.packet.digest and
+                self.review.source_digest==self.source.digest and self.review.verifier==self.decision.verifier and
+                self.review.verdict==self.decision.verdict and
+                {a.claim_id for a in self.review.assessments}=={c.claim_id for c in self.packet.claims},
+                'complete exact per-claim review required')
+        if self.decision.verdict=='APPROVED':
+            require(all(a.verdict=='APPROVED' for a in self.review.assessments),'unsupported material claim')
+        require(self.packet.researcher in self.contributors and self.decision.verifier not in self.contributors,
+                'independent verification required')
+        require(len(set(self.contributors)) == len(self.contributors) and 0 < len(self.contributors) <= 8,
+                'bounded contributors required')
+        require(0 < len(self.audiences) <= 11 and len(set(self.audiences)) == len(self.audiences) and len(self.topics) <= 16,
+                'bounded specialist metadata required')
+        integer(self.valid_from);integer(self.valid_until,1)
+        require(self.valid_until > self.valid_from, 'invalid validity')
+        evidence={e.evidence_id:e for e in self.source.evidence}
+        require(all(e.evidence_id in evidence and e.content_digest == hash_content(evidence[e.evidence_id]) and
+                    e.location == evidence[e.evidence_id].location for e in self.packet.evidence),
+                'packet evidence does not match full source evidence')
+        require(len(canonical(self)) <= 131072, 'candidate exceeds existing request ceiling')
+
+
+@dataclass(frozen=True, kw_only=True)
+class Attestation(Contract):
+    schema: ClassVar[str] = 'memory_research_attestation.test.v1'
+    environment: str
+    attestation_id: str
+    candidate_digest: str
+    verifier: str
+    issued_at: int
+    expires_at: int
+    marking: str = MARKING
+
+    def validate(self):
+        require(self.marking == MARKING, 'no genuine attestation issuer configured')
+        digest(self.candidate_digest)
+        integer(self.issued_at);integer(self.expires_at,1)
+        require(self.expires_at>self.issued_at,'invalid attestation lifetime')
+
+
+@dataclass(frozen=True)
+class Actor:
+    principal: str
+    environment: str
+    role: str
+
+
+class TestAuthority:
+    """Injected independently of candidates/DB; no production or automatic grants."""
+    __test__ = False
+    def __init__(self, grants, *, test_only=False, production=False):
+        if test_only is not True or production is not False:raise Denied('production authority disabled')
+        self.lock=RLock();self.grants=dict(grants);self.issued={};self.attestations={};self.contributors={}
+        for principal,grant in self.grants.items():
+            require(grant['environment'] in ENVIRONMENTS and grant['role'] in
+                    ('admin','writer','verifier','promoter','reader'),'unknown test grant')
+
+    def actor(self, principal):
+        with self.lock:
+            g=self.grants.get(principal)
+            if not g:raise Denied('unknown test principal')
+            a=Actor(principal,g['environment'],g['role']);self.issued[id(a)]=a;return a
+
+    def authorize(self, actor, env, roles, candidate=None):
+        g=self.grants.get(getattr(actor,'principal',None))
+        if (self.issued.get(id(actor)) is not actor or not g or actor.environment!=env or
+            g['environment']!=env or actor.role!=g['role'] or actor.role not in roles):raise Denied('scope/grant denied')
+        if candidate is not None:
+            if candidate.packet.classification not in g.get('classifications',()):raise Denied('classification denied')
+            if actor.role=='reader' and not set(g.get('audiences',())) & set(candidate.audiences):raise Denied('specialist denied')
+        return g
+
+    def bind_contributors(self, actor, task_id, contributors):
+        with self.lock:
+            self.authorize(actor,actor.environment,('admin',))
+            key=(actor.environment,task_id)
+            if key in self.contributors and self.contributors[key]!=tuple(contributors):raise Denied('delegation conflict')
+            self.contributors[key]=tuple(contributors)
+
+    def issue(self, actor, candidate, now, expires_at):
+        with self.lock:
+            grant=self.authorize(actor,candidate.environment,('verifier',),candidate)
+            if (candidate.contributors!=self.contributors.get((candidate.environment,candidate.packet.task_id)) or
+                actor.principal!=candidate.decision.verifier or candidate.decision.verdict!='APPROVED' or
+                (candidate.decision.verifier_provider,candidate.decision.verifier_model)!=grant.get('assignment')):
+                raise Denied('independent approved verifier assignment/delegation required')
+            a=Attestation(environment=candidate.environment,attestation_id=str(uuid4()),candidate_digest=hash_content(candidate),
+                verifier=actor.principal,issued_at=now,expires_at=expires_at)
+            self.attestations[a.attestation_id]=a;return a
+
+    def validate(self, attestation, candidate, now):
+        if (self.attestations.get(attestation.attestation_id)!=attestation or
+            attestation.environment!=candidate.environment or attestation.candidate_digest!=hash_content(candidate) or
+            attestation.verifier!=candidate.decision.verifier or not attestation.issued_at<=now<attestation.expires_at or
+            candidate.decision.verdict!='APPROVED' or
+            self.contributors.get((candidate.environment,candidate.packet.task_id))!=candidate.contributors):
+            raise Denied('missing/edited/stale test attestation')
+        grant=self.grants.get(attestation.verifier)
+        if (not grant or grant['role']!='verifier' or grant['environment']!=candidate.environment or
+            grant.get('assignment')!=(candidate.decision.verifier_provider,candidate.decision.verifier_model)):
+            raise Denied('verifier grant revoked/changed')
+        if candidate.source.outcome!='SUPPORTED_FETCHED' or not candidate.source.evidence:
+            raise Denied('incomplete source cannot simulate promotion')
+
+
+class ResearchStage:
+    """Additive staging-only tables in existing Memory persistence; no HTTP route.
+
+    initialize=True is explicit synthetic schema setup, never a production
+    migration. Core user_version=3 is preserved. Actual trust/purge/export
+    policies are unconfigured and fail closed.
+    """
+    def __init__(self, memory, authority, admin, *, clock, test_only=False, production=False,
+                 initialize=False, hook=None):
+        if test_only is not True or production is not False:raise Denied('production Research Memory disabled')
+        if type(authority) is not TestAuthority:raise Denied('only explicit test authority configured')
+        authority.authorize(admin,admin.environment,('admin',))
+        self.memory,self.authority,self.clock=memory,authority,clock
+        self.hook=hook or (lambda _:None)
+        with authority.lock,memory._db() as db:
+            exists=db.execute("SELECT 1 FROM sqlite_master WHERE name='research_stage_meta'").fetchone()
+            if not exists:
+                if not initialize:raise Unavailable('staging Research schema not provisioned')
+                db.executescript('''
+CREATE TABLE research_stage_meta(version INTEGER NOT NULL);
+INSERT INTO research_stage_meta VALUES(1);
+CREATE TABLE research_stage_heads(env TEXT,id TEXT,revision INTEGER,state TEXT,sequence INTEGER,
+ PRIMARY KEY(env,id));
+CREATE TABLE research_stage_versions(env TEXT,id TEXT,revision INTEGER,digest TEXT,body TEXT,attestation TEXT,
+ PRIMARY KEY(env,id,revision));
+CREATE TABLE research_stage_ops(env TEXT,operation_id TEXT,payload_digest TEXT,receipt TEXT,
+ PRIMARY KEY(env,operation_id));
+''')
+            if [r[0] for r in db.execute('SELECT version FROM research_stage_meta')]!=[1]:
+                raise Unavailable('unsupported staging Research schema')
+
+    @contextmanager
+    def _tx(self,actor,env,roles):
+        with self.authority.lock:
+            self.authority.authorize(actor,env,roles)
+            with self.memory._db() as db:
+                db.execute('BEGIN IMMEDIATE');yield db
+
+    def _load(self,db,env,record_id,revision=None):
+        digest(record_id)
+        head=db.execute('SELECT * FROM research_stage_heads WHERE env=? AND id=?',(env,record_id)).fetchone()
+        if not head:raise Denied('record unavailable')
+        row=db.execute('SELECT * FROM research_stage_versions WHERE env=? AND id=? AND revision=?',
+                       (env,record_id,head['revision'] if revision is None else revision)).fetchone()
+        if not row:raise Denied('revision unavailable')
+        return head,Candidate.from_json(row['body']),Attestation.from_json(row['attestation'])
+
+    def _replay(self,db,actor,op,payload):
+        require(type(op) is str and 0<len(op)<=128,'bounded operation ID required')
+        digest=hash_content((actor.principal,payload))
+        row=db.execute('SELECT * FROM research_stage_ops WHERE env=? AND operation_id=?',(actor.environment,op)).fetchone()
+        if row:
+            if row['payload_digest']!=digest:raise Denied('conflicting operation replay')
+            return json.loads(row['receipt'])
+
+    def _receipt(self,db,actor,op,payload,kind,record_id,revision,sequence,state,candidate):
+        row=db.execute('SELECT attestation FROM research_stage_versions WHERE env=? AND id=? AND revision=?',
+                       (actor.environment,record_id,revision)).fetchone()
+        receipt={'schema':'memory_research_receipt.staging.v1','marking':MARKING,'issuer':'test-memory-owned',
+            'receipt_id':str(uuid4()),'operation_id':op,'operation':kind,'environment':actor.environment,
+            'actor':actor.principal,'record_id':record_id,'record_version':revision,'sequence':sequence,
+            'candidate_digest':hash_content(candidate),'packet_digest':candidate.packet.digest,
+            'packet_version':candidate.packet.packet_version,'decision_id':candidate.decision.decision_id,
+            'attestation_id':json.loads(row[0])['attestation_id'],'source_digest':candidate.source.digest,
+            'policy_ref':candidate.policy_ref,'classification':candidate.packet.classification,
+            'request_digest':hash_content((actor.principal,payload)),
+            'observed_at':self.clock(),'state':state,'outcome':'SIMULATED_SUCCESS'}
+        db.execute('INSERT INTO research_stage_ops VALUES(?,?,?,?)',
+                   (actor.environment,op,hash_content((actor.principal,payload)),json.dumps(receipt,sort_keys=True)))
+        return receipt
+
+    def submit(self,actor,op,candidate,attestation):
+        with self._tx(actor,candidate.environment,('writer','admin')) as db:
+            self.authority.authorize(actor,candidate.environment,('writer','admin'),candidate)
+            require(candidate.valid_from<=self.clock()<candidate.valid_until,'candidate expired/not yet valid')
+            self.authority.validate(attestation,candidate,self.clock())
+            payload=('submit',candidate.payload(),attestation.payload())
+            prior=self._replay(db,actor,op,payload)
+            if prior:return prior
+            identity=candidate.payload();identity.pop('valid_from');identity.pop('valid_until')
+            record_id=hash_content((candidate.environment,identity))
+            head=db.execute('SELECT * FROM research_stage_heads WHERE env=? AND id=?',(candidate.environment,record_id)).fetchone()
+            if head:
+                h,c,a=self._load(db,candidate.environment,record_id)
+                require((c.valid_from,c.valid_until)==(candidate.valid_from,candidate.valid_until),'VALIDITY_CONFLICT')
+                require(c==candidate and a==attestation,'duplicate candidate conflict')
+                revision,sequence=h['revision'],h['sequence']
+            else:
+                revision,sequence=1,1
+                db.execute('INSERT INTO research_stage_heads VALUES(?,?,?,?,?)',(candidate.environment,record_id,1,'CANDIDATE',1))
+                db.execute('INSERT INTO research_stage_versions VALUES(?,?,?,?,?,?)',
+                    (candidate.environment,record_id,1,hash_content(candidate),canonical(candidate).decode(),canonical(attestation).decode()))
+            receipt=self._receipt(db,actor,op,payload,'submit',record_id,revision,sequence,'CANDIDATE',candidate)
+        self.hook('submit:committed');return receipt
+
+    def promote(self,*args,**kwargs):
+        raise Denied('production promotion/attestation authority is unconfigured; synthetic verdicts forbidden')
+
+    def _change(self,actor,op,record_id,expected,kind,state):
+        integer(expected,1)
+        with self._tx(actor,actor.environment,('admin','promoter') if kind!='commit' else ('writer','admin')) as db:
+            h,c,a=self._load(db,actor.environment,record_id)
+            self.authority.authorize(actor,actor.environment,('admin','promoter','writer'),c)
+            payload=(kind,record_id,expected)
+            prior=self._replay(db,actor,op,payload)
+            if prior:return prior
+            require(h['sequence']==expected,'state version conflict')
+            if kind in ('commit','simulate_promote'):
+                require(c.valid_from<=self.clock()<c.valid_until,'record expired')
+                self.authority.validate(a,c,self.clock())
+                require(h['state']==('CANDIDATE' if kind=='commit' else 'COMMITTED'),'invalid lifecycle prerequisite')
+            else:require(h['state'] not in ('REVOKED','SUPERSEDED'),'terminal state cannot be restored')
+            seq=h['sequence']+1
+            db.execute('UPDATE research_stage_heads SET state=?,sequence=? WHERE env=? AND id=?',
+                       (state,seq,actor.environment,record_id))
+            receipt=self._receipt(db,actor,op,payload,kind,record_id,h['revision'],seq,state,c)
+        self.hook(kind+':committed');return receipt
+
+    def commit(self,actor,op,record_id,expected):return self._change(actor,op,record_id,expected,'commit','COMMITTED')
+    def simulate_promotion(self,actor,op,record_id,expected):
+        return self._change(actor,op,record_id,expected,'simulate_promote','PROMOTED_SIMULATED')
+    def revoke(self,actor,op,record_id,expected):return self._change(actor,op,record_id,expected,'revoke','REVOKED')
+    def dispute(self,actor,op,record_id,expected):return self._change(actor,op,record_id,expected,'dispute','DISPUTED')
+    def expire(self,actor,op,record_id,expected):return self._change(actor,op,record_id,expected,'expire','EXPIRED')
+    def supersede(self,actor,op,record_id,expected):return self._change(actor,op,record_id,expected,'supersede','SUPERSEDED')
+
+    def flag_conflict(self,actor,op,left,right,expected_left,expected_right):
+        integer(expected_left,1);integer(expected_right,1)
+        with self._tx(actor,actor.environment,('admin',)) as db:
+            require(left!=right,'distinct findings required')
+            lh,lc,la=self._load(db,actor.environment,left);rh,rc,ra=self._load(db,actor.environment,right)
+            self.authority.authorize(actor,actor.environment,('admin',),lc)
+            self.authority.authorize(actor,actor.environment,('admin',),rc)
+            payload=('conflict',left,right,expected_left,expected_right)
+            prior=self._replay(db,actor,op,payload)
+            if prior:return prior
+            require(lh['sequence']==expected_left and rh['sequence']==expected_right,'stale conflict targets')
+            require(lh['state'] not in ('REVOKED','SUPERSEDED') and rh['state'] not in ('REVOKED','SUPERSEDED'),
+                    'conflict cannot restore terminal findings')
+            for record_id,head in ((left,lh),(right,rh)):
+                db.execute("UPDATE research_stage_heads SET state='DISPUTED',sequence=? WHERE env=? AND id=?",
+                           (head['sequence']+1,actor.environment,record_id))
+            receipt=self._receipt(db,actor,op,payload,'conflict',left,lh['revision'],lh['sequence']+1,'DISPUTED',lc)
+            receipt['related_record_id']=right
+            db.execute('UPDATE research_stage_ops SET receipt=? WHERE env=? AND operation_id=?',
+                       (json.dumps(receipt,sort_keys=True),actor.environment,op))
+            return receipt
+
+    def retrieve(self,actor,op,record_id):
+        with self._tx(actor,actor.environment,('reader','admin')) as db:
+            h,c,a=self._load(db,actor.environment,record_id)
+            self.authority.authorize(actor,actor.environment,('reader','admin'),c)
+            require(h['state']=='PROMOTED_SIMULATED' and c.valid_from<=self.clock()<c.valid_until,
+                    'not current simulated knowledge')
+            self.authority.validate(a,c,self.clock())
+            payload=('retrieve',record_id,h['revision'],h['sequence'])
+            prior=self._replay(db,actor,op,payload)
+            receipt=prior or self._receipt(db,actor,op,payload,'retrieve',record_id,h['revision'],h['sequence'],
+                                          'RETRIEVED_SIMULATED',c)
+            return {'candidate':c.payload(),'receipt':receipt,'historical_receipt_replay':prior is not None}
+
+    def reconcile(self,actor,op):
+        require(type(op) is str and 0<len(op)<=128,'bounded operation ID required')
+        with self._tx(actor,actor.environment,('admin','writer','promoter','reader')) as db:
+            row=db.execute('SELECT receipt FROM research_stage_ops WHERE env=? AND operation_id=?',
+                           (actor.environment,op)).fetchone()
+            if not row:raise Unavailable('operation outcome unknown; do not invent success')
+            receipt=json.loads(row['receipt'])
+            h,c,a=self._load(db,actor.environment,receipt['record_id'],receipt['record_version'])
+            self.authority.authorize(actor,actor.environment,('admin','writer','promoter','reader'),c)
+            if receipt['actor']!=actor.principal and actor.role!='admin':raise Denied('operation scope denied')
+            eligible=(h['revision']==receipt['record_version'] and
+                      receipt['candidate_digest']==hash_content(c) and h['state']=='PROMOTED_SIMULATED' and
+                      c.valid_from<=self.clock()<c.valid_until)
+            try:self.authority.validate(a,c,self.clock())
+            except Denied:eligible=False
+            return {'receipt':receipt,'current_state':h['state'],'historical':True,'currently_eligible':eligible}
+
+    def revise(self,actor,op,record_id,expected,candidate,attestation):
+        integer(expected,1)
+        with self._tx(actor,candidate.environment,('admin',)) as db:
+            h,old,a=self._load(db,actor.environment,record_id)
+            self.authority.authorize(actor,actor.environment,('admin',),candidate)
+            self.authority.authorize(actor,actor.environment,('admin',),old)
+            self.authority.validate(attestation,candidate,self.clock())
+            require(candidate.valid_from<=self.clock()<candidate.valid_until,'revision expired')
+            payload=('revise',record_id,expected,candidate.payload(),attestation.payload())
+            prior=self._replay(db,actor,op,payload)
+            if prior:return prior
+            require(h['sequence']==expected and h['state'] not in ('REVOKED','SUPERSEDED'), 'stale/terminal revision')
+            require(candidate.packet.task_id==old.packet.task_id and
+                    candidate.packet.packet_version>=old.packet.packet_version,'revision task/version mismatch')
+            if candidate.packet.digest!=old.packet.digest:
+                require(candidate.packet.packet_version>old.packet.packet_version,'changed packet needs new version')
+            version,sequence=h['revision']+1,h['sequence']+1
+            db.execute('INSERT INTO research_stage_versions VALUES(?,?,?,?,?,?)',(actor.environment,record_id,version,
+                hash_content(candidate),canonical(candidate).decode(),canonical(attestation).decode()))
+            db.execute('UPDATE research_stage_heads SET revision=?,state=?,sequence=? WHERE env=? AND id=?',
+                       (version,'COMMITTED',sequence,actor.environment,record_id))
+            return self._receipt(db,actor,op,payload,'revise',record_id,version,sequence,'COMMITTED',candidate)
+
+    def history(self,actor,record_id):
+        with self._tx(actor,actor.environment,('admin',)) as db:
+            h,c,a=self._load(db,actor.environment,record_id)
+            self.authority.authorize(actor,actor.environment,('admin',),c)
+            records=tuple(Candidate.from_json(r[0]) for r in db.execute(
+                'SELECT body FROM research_stage_versions WHERE env=? AND id=? ORDER BY revision',
+                (actor.environment,record_id)))
+            for record in records:self.authority.authorize(actor,actor.environment,('admin',),record)
+            return tuple(record.payload() for record in records)
+
+    def delete(self,*args,**kwargs):
+        raise Unavailable('Research retention/legal-hold/deletion-ledger mapping requires owner approval')
+    def request_export(self,*args,**kwargs):
+        raise Unavailable('Research export/Sync mapping is unconfigured; existing pipeline unchanged')
+
+
+def dispatch_research(*args,**kwargs):
+    """Never mounted by existing /v1/memory or /v1/obsidian-memory handlers."""
+    raise Denied('production Research action contract and authentication are unapproved')
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
--- /dev/null
+++ candidate/tests/test_research_memory_stage.py
@@ -0,0 +1,274 @@
+"""Synthetic Memory-owned extension tests; no production services or vaults."""
+from pathlib import Path
+import sys
+ROOT=Path(__file__).resolve().parents[5]
+sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'tests'))
+import test_research as research
+from alfred_research.contracts import ENVIRONMENTS,hash_content,ContractError
+from focused_v1.store import MemoryStore,Denied,Unavailable
+from focused_v1.server import dispatch
+from focused_v1.research_stage import Candidate,TestAuthority,Actor,ResearchStage,dispatch_research,MARKING
+from obsidian_candidate.service_api import VersionedMemoryStore,dispatch as bridge_dispatch
+from dataclasses import replace
+from concurrent.futures import ThreadPoolExecutor
+from unittest.mock import patch
+import secrets,tempfile,unittest,json
+import subprocess,os
+
+
+class MemoryResearchStageTests(unittest.TestCase):
+    def setUp(self):
+        self.r=research.ResearchTests();self.r.setUp();self.addCleanup(self.r.doCleanups)
+        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
+        self.memory=VersionedMemoryStore(Path(self.temp.name)/'memory.sqlite3',deletion_key=secrets.token_bytes(32),initialize=True)
+        self.owner_token=secrets.token_urlsafe(32);self.agent_token=secrets.token_urlsafe(32)
+        self.memory.provision('owner','alfred',self.owner_token);self.memory.provision('agent','agent',self.agent_token)
+        self.memory.assign(self.owner_token,'agent','test-task')
+        self.now=1000;grants={}
+        for env in ENVIRONMENTS:
+            for role in ('admin','writer','promoter','reader'):
+                grants[env+'-'+role]={'environment':env,'role':role,'classifications':('internal',),
+                    'audiences':('frontend',)}
+            grants[env+'-verifier']={'environment':env,'role':'verifier','classifications':('internal',),
+                'assignment':('synthetic','synthetic-verifier')}
+        self.authority=TestAuthority(grants,test_only=True)
+        self.actors={key:self.authority.actor(key) for key in grants}
+        self.stage=ResearchStage(self.memory,self.authority,self.actor(),clock=lambda:self.now,test_only=True,initialize=True)
+
+    def actor(self,env='personal',role='admin'):return self.actors[env+'-'+role]
+
+    def candidate(self,env='personal',key='one',text='React UI evidence with citations'):
+        task,source=self.r.task(env,kind='github',objective='Inspect repository',text=text,request_id=key)
+        d,v=self.r.runtime();_,plan,packet=self.r.start(task,source,director=d)
+        review=self.r.review(v,packet)
+        decision=self.r.store.verification_history(self.r.ctx(env),task.task_id)[0]
+        contributors=(plan.director.principal,plan.lead.principal)
+        c=Candidate(environment=env,packet=packet,source=source,decision=decision,review=review,contributors=contributors,
+            category='Development/Frontend',topics=('UI',),audiences=('frontend',),policy_ref='synthetic-policy',
+            acquisition_ref='fixture-acquisition-only',valid_from=900,valid_until=2000)
+        self.authority.bind_contributors(self.actor(env),task.task_id,contributors)
+        attestation=self.authority.issue(self.actor(env,'verifier'),c,1000,2000)
+        return c,attestation
+
+    def promoted(self,env='personal',key='one'):
+        c,a=self.candidate(env,key);s=self.stage.submit(self.actor(env,'writer'),key+'-submit',c,a)
+        committed=self.stage.commit(self.actor(env,'writer'),key+'-commit',s['record_id'],s['sequence'])
+        promoted=self.stage.simulate_promotion(self.actor(env,'promoter'),key+'-promote',s['record_id'],committed['sequence'])
+        return c,a,s,committed,promoted
+
+    def test_duplicate_create_actual_pending_rejected_approved(self):
+        first=self.memory.create(self.agent_token,task_id='test-task',kind='preference',content='Synthetic preference',source_message_id='message')
+        for state in ('pending','rejected','approved'):
+            with self.memory._db() as db:
+                db.execute('UPDATE memories SET review_state=? WHERE id=?',(state,first['id']))
+                before=[tuple(r) for r in db.execute('SELECT * FROM memories')]
+            result=self.memory.create(self.agent_token,task_id='test-task',kind='preference',content='Synthetic preference',source_message_id='message')
+            self.assertEqual(result['review_state'],state);self.assertTrue(result['duplicate'])
+            with self.memory._db() as db:self.assertEqual([tuple(r) for r in db.execute('SELECT * FROM memories')],before)
+
+    def test_duplicate_create_preserves_pending_edit_and_authorization(self):
+        first=self.memory.create(self.owner_token,task_id='test-task',kind='preference',content='Original preference',source_message_id='message')
+        with self.memory._db() as db:db.execute("UPDATE memories SET principal='agent' WHERE id=?",(first['id'],))
+        self.memory.update(self.agent_token,task_id='test-task',memory_id=first['id'],expected_version=1,content='Pending replacement')
+        result=self.memory.create(self.agent_token,task_id='test-task',kind='preference',content='Original preference',source_message_id='message')
+        self.assertEqual(result['review_state'],'approved')
+        with self.memory._db() as db:self.assertEqual(db.execute('SELECT pending_content FROM memories').fetchone()[0],'Pending replacement')
+        with self.assertRaises(Denied):self.memory.create(self.owner_token,task_id='test-task',kind='preference',content='Original preference',source_message_id='message')
+
+    def test_existing_routes_and_new_records_never_use_autoapproval(self):
+        c,a,s,commit,promote=self.promoted()
+        self.assertEqual(dispatch(self.memory,self.agent_token,{'action':'search','task_id':'test-task','query':'React'}),[])
+        self.assertIsNone(bridge_dispatch(self.memory,self.owner_token,{'action':'get_current','memory_id':s['record_id']}))
+        with self.assertRaises(ValueError):dispatch(self.memory,self.owner_token,{'action':'research_promote'})
+        with self.assertRaises(Denied):dispatch_research({'approved':True})
+        with self.assertRaises(Denied):self.stage.promote(self.actor('personal','promoter'),s['record_id'])
+
+    def test_production_default_missing_authority_and_synthetic_promotion_denied(self):
+        with self.assertRaises(Denied):TestAuthority({})
+        with self.assertRaises(Denied):ResearchStage(self.memory,self.authority,self.actor(),clock=lambda:1000)
+        with self.assertRaises(Denied):ResearchStage(self.memory,self.authority,self.actor(),clock=lambda:1000,test_only=True,production=True)
+        with self.assertRaises(Denied):self.stage.promote(None,approved=True)
+        c,a=self.candidate()
+        for verdict in ('REJECTED','NEEDS_MORE_RESEARCH'):
+            bad=replace(c,decision=replace(c.decision,verdict=verdict),review=replace(c.review,verdict=verdict))
+            with self.assertRaises(Denied):self.authority.issue(self.actor('personal','verifier'),bad,1000,2000)
+
+    def test_exact_packet_version_digest_source_and_selfverification(self):
+        c,a=self.candidate()
+        for bad in (lambda:replace(c,packet=replace(c.packet,packet_version=2)),
+                    lambda:replace(c,source=replace(c.source,revision=('b'*40,))),
+                    lambda:replace(c,decision=replace(c.decision,packet_digest='f'*64)),
+                    lambda:replace(c,contributors=c.contributors+(c.decision.verifier,))):
+            with self.assertRaises(ContractError):bad()
+        with self.assertRaises(Denied):self.stage.submit(self.actor('personal','writer'),'bad',replace(c,policy_ref='changed'),a)
+
+    def test_forged_edited_missing_revoked_attestation(self):
+        c,a=self.candidate()
+        with self.assertRaises(Denied):self.stage.submit(self.actor('personal','writer'),'bad',c,replace(a,attestation_id='forged'))
+        del self.authority.attestations[a.attestation_id]
+        with self.assertRaises(Denied):self.stage.submit(self.actor('personal','writer'),'missing',c,a)
+
+    def test_no_default_promoter_and_forged_context(self):
+        c,a=self.candidate();s=self.stage.submit(self.actor('personal','writer'),'submit',c,a)
+        commit=self.stage.commit(self.actor('personal','writer'),'commit',s['record_id'],1)
+        with self.assertRaises(Denied):self.stage.simulate_promotion(self.actor('personal','writer'),'forged',s['record_id'],2)
+        with self.assertRaises(Denied):self.stage.simulate_promotion(Actor('personal-promoter','personal','promoter'),'forged',s['record_id'],2)
+
+    def test_distinct_commit_promotion_and_full_fresh_retrieval(self):
+        c,a,s,commit,promote=self.promoted()
+        r=self.stage.retrieve(self.actor('personal','reader'),'read',s['record_id'])
+        self.assertEqual([x['operation'] for x in (s,commit,promote,r['receipt'])],['submit','commit','simulate_promote','retrieve'])
+        self.assertEqual(r['candidate'],c.payload());self.assertEqual(r['receipt']['attestation_id'],a.attestation_id)
+        self.assertTrue(all(x['marking']==MARKING for x in (s,commit,promote,r['receipt'])))
+        self.now=1001;r2=self.stage.retrieve(self.actor('personal','reader'),'read2',s['record_id'])
+        self.assertNotEqual(r2['receipt']['receipt_id'],r['receipt']['receipt_id'])
+        replay=self.stage.retrieve(self.actor('personal','reader'),'read',s['record_id'])
+        self.assertTrue(replay['historical_receipt_replay']);self.assertEqual(replay['receipt'],r['receipt'])
+
+    def test_commit_not_promotion_and_replay_idempotent(self):
+        c,a=self.candidate();s=self.stage.submit(self.actor('personal','writer'),'submit',c,a)
+        self.assertEqual(self.stage.submit(self.actor('personal','writer'),'submit',c,a),s)
+        with self.assertRaises(ContractError):self.stage.commit(self.actor('personal','writer'),'bool',s['record_id'],True)
+        commit=self.stage.commit(self.actor('personal','writer'),'commit',s['record_id'],1)
+        self.assertEqual(self.stage.commit(self.actor('personal','writer'),'commit',s['record_id'],1),commit)
+        with self.assertRaises(ContractError):self.stage.retrieve(self.actor('personal','reader'),'read',s['record_id'])
+        with self.assertRaises(Denied):self.stage.submit(self.actor('personal','writer'),'submit',replace(c,topics=('other',)),a)
+
+    def test_expiration_dispute_supersession_revocation_exclude_current(self):
+        for operation in ('expire','dispute','supersede','revoke'):
+            c,a,s,commit,p=self.promoted(key=operation)
+            getattr(self.stage,operation)(self.actor(),operation+'-invalidate',s['record_id'],p['sequence'])
+            with self.assertRaises(ContractError):self.stage.retrieve(self.actor('personal','reader'),operation+'-read',s['record_id'])
+            self.assertFalse(self.stage.reconcile(self.actor(),operation+'-promote')['currently_eligible'])
+        c,a,s,commit,p=self.promoted(key='clock');self.now=2000
+        with self.assertRaises(ContractError):self.stage.retrieve(self.actor('personal','reader'),'expired',s['record_id'])
+
+    def test_attestation_and_reader_revocation_take_effect_immediately(self):
+        c,a,s,commit,p=self.promoted()
+        del self.authority.attestations[a.attestation_id]
+        with self.assertRaises(Denied):self.stage.retrieve(self.actor('personal','reader'),'revoked',s['record_id'])
+        del self.authority.grants['personal-reader']
+        with self.assertRaises(Denied):self.stage.retrieve(self.actor('personal','reader'),'lost-grant',s['record_id'])
+
+    def test_validity_duplicate_conflict_and_authorized_immutable_revision(self):
+        c,a,s,commit,p=self.promoted()
+        changed=replace(c,valid_until=1001)
+        att=self.authority.issue(self.actor('personal','verifier'),changed,1000,2000)
+        with self.assertRaisesRegex(ContractError,'VALIDITY_CONFLICT'):self.stage.submit(self.actor('personal','writer'),'conflict',changed,att)
+        with self.assertRaises(ContractError):replace(c,valid_until=-1)
+        revised=self.stage.revise(self.actor(),'revision',s['record_id'],p['sequence'],changed,att)
+        history=self.stage.history(self.actor(),s['record_id'])
+        self.assertEqual(len(history),2);self.assertEqual(history[0],c.payload());self.assertEqual(history[1],changed.payload())
+        self.now=1002
+        with self.assertRaises(ContractError):self.stage.retrieve(self.actor('personal','reader'),'current',s['record_id'])
+
+    def test_concurrent_duplicate_and_stale_revisions(self):
+        c,a=self.candidate()
+        with ThreadPoolExecutor(max_workers=4) as pool:
+            results=list(pool.map(lambda _:self.stage.submit(self.actor('personal','writer'),'submit',c,a),range(4)))
+        self.assertEqual(len({r['receipt_id'] for r in results}),1)
+        s=results[0];self.stage.commit(self.actor('personal','writer'),'commit',s['record_id'],1)
+        changed=replace(c,valid_until=2100);att=self.authority.issue(self.actor('personal','verifier'),changed,1000,2000)
+        self.stage.revise(self.actor(),'revise',s['record_id'],2,changed,att)
+        with self.assertRaises(ContractError):self.stage.revise(self.actor(),'stale',s['record_id'],2,c,a)
+
+    def test_crash_after_commit_restart_reconciles_one_effect(self):
+        c,a=self.candidate();s=self.stage.submit(self.actor('personal','writer'),'submit',c,a)
+        def crash(stage):
+            if stage=='commit:committed':raise RuntimeError('interrupted after durable commit')
+        self.stage.hook=crash
+        with self.assertRaises(RuntimeError):self.stage.commit(self.actor('personal','writer'),'commit',s['record_id'],1)
+        recovered=ResearchStage(self.memory,self.authority,self.actor(),clock=lambda:1000,test_only=True)
+        historical=recovered.reconcile(self.actor(),'commit')['receipt']
+        self.assertEqual(recovered.commit(self.actor('personal','writer'),'commit',s['record_id'],1),historical)
+        with self.memory._db() as db:self.assertEqual(db.execute('SELECT count(*) FROM research_stage_ops WHERE operation_id=?',('commit',)).fetchone()[0],1)
+        with self.assertRaises(Unavailable):recovered.reconcile(self.actor(),'unknown')
+
+    def test_all_twelve_environment_pairs_deny_reads_writes_and_receipts(self):
+        for env in ENVIRONMENTS:
+            c,a,s,commit,p=self.promoted(env,key=env)
+            for other in ENVIRONMENTS:
+                if env==other:continue
+                with self.assertRaises(Denied):self.stage.submit(self.actor(other,'writer'),'cross',c,a)
+                with self.assertRaises(Denied):self.stage.retrieve(self.actor(other,'reader'),'cross',s['record_id'])
+                with self.assertRaises(Unavailable):self.stage.reconcile(self.actor(other),env+'-promote')
+                with self.assertRaises(Denied):self.stage.revoke(self.actor(other),'cross',s['record_id'],p['sequence'])
+
+    def test_oversize_full_evidence_no_truncation_and_missing_specialist_grant(self):
+        c,a=self.candidate(text='React UI '+'evidence '*250)
+        with self.assertRaises(ContractError):replace(c,topics=tuple('x'*16000 for _ in range(10)))
+        s=self.stage.submit(self.actor('personal','writer'),'submit',c,a);self.stage.commit(self.actor('personal','writer'),'commit',s['record_id'],1)
+        self.stage.simulate_promotion(self.actor('personal','promoter'),'promote',s['record_id'],2)
+        result=self.stage.retrieve(self.actor('personal','reader'),'read',s['record_id'])
+        self.assertGreater(len(result['candidate']['source']['evidence'][0]['text']),1536)
+        self.authority.grants['personal-reader']['audiences']=('backend',)
+        with self.assertRaises(Denied):self.stage.retrieve(self.actor('personal','reader'),'denied',s['record_id'])
+
+    def test_unapproved_deletion_and_export_fail_closed(self):
+        with self.assertRaises(Unavailable):self.stage.delete(self.actor(),'delete','anything')
+        with self.assertRaises(Unavailable):self.stage.request_export(self.actor(),'export','anything')
+
+    def test_conflicting_findings_both_flagged_without_a_winner(self):
+        c,a,left,lc,lp=self.promoted(key='left');c,a,right,rc,rp=self.promoted(key='right')
+        receipt=self.stage.flag_conflict(self.actor(),'conflict',left['record_id'],right['record_id'],lp['sequence'],rp['sequence'])
+        self.assertEqual(receipt['related_record_id'],right['record_id'])
+        for item in (left,right):
+            with self.assertRaises(ContractError):self.stage.retrieve(self.actor('personal','reader'),'read-'+item['record_id'],item['record_id'])
+        self.assertEqual(self.stage.flag_conflict(self.actor(),'conflict',left['record_id'],right['record_id'],lp['sequence'],rp['sequence']),receipt)
+
+    def test_incomplete_review_and_missing_trust_on_restart_denied(self):
+        c,a=self.candidate()
+        with self.assertRaises(ContractError):replace(c,review=replace(c.review,packet_digest='f'*64))
+        s=self.stage.submit(self.actor('personal','writer'),'submit',c,a)
+        self.stage.commit(self.actor('personal','writer'),'commit',s['record_id'],1)
+        self.stage.simulate_promotion(self.actor('personal','promoter'),'promote',s['record_id'],2)
+        new=TestAuthority(self.authority.grants,test_only=True)
+        restarted=ResearchStage(self.memory,new,new.actor('personal-admin'),clock=lambda:1000,test_only=True)
+        with self.assertRaises(Denied):restarted.retrieve(new.actor('personal-reader'),'read',s['record_id'])
+
+    def test_historical_promotion_cannot_authorize_new_revision(self):
+        c,a,s,commit,p=self.promoted()
+        changed=replace(c,valid_until=2100)
+        new=self.authority.issue(self.actor('personal','verifier'),changed,1000,2000)
+        revision=self.stage.revise(self.actor(),'revision',s['record_id'],p['sequence'],changed,new)
+        self.stage.simulate_promotion(self.actor('personal','promoter'),'new-promotion',s['record_id'],revision['sequence'])
+        old=self.stage.reconcile(self.actor(),'one-promote')
+        self.assertFalse(old['currently_eligible']);self.assertEqual(old['receipt'],p)
+
+    def test_changed_verifier_assignment_denies_promotion(self):
+        c,a=self.candidate();s=self.stage.submit(self.actor('personal','writer'),'submit',c,a)
+        self.stage.commit(self.actor('personal','writer'),'commit',s['record_id'],1)
+        self.authority.grants['personal-verifier']['assignment']=('synthetic','unapproved-model')
+        with self.assertRaises(Denied):self.stage.simulate_promotion(self.actor('personal','promoter'),'promote',s['record_id'],2)
+
+    def test_fresh_process_recovers_commit_without_new_effect(self):
+        c,a=self.candidate();s=self.stage.submit(self.actor('personal','writer'),'submit',c,a)
+        committed=self.stage.commit(self.actor('personal','writer'),'commit',s['record_id'],1)
+        code='''import json,sys,socket
+from focused_v1.store import MemoryStore
+from focused_v1.research_stage import TestAuthority,ResearchStage
+v=json.load(sys.stdin)
+socket.socket=lambda *a,**k: (_ for _ in ()).throw(AssertionError('network forbidden'))
+for grant in v['grants'].values():
+ if 'assignment' in grant:grant['assignment']=tuple(grant['assignment'])
+authority=TestAuthority(v['grants'],test_only=True)
+memory=MemoryStore(v['path'],deletion_key=bytes.fromhex(v['test_key']))
+stage=ResearchStage(memory,authority,authority.actor('personal-admin'),clock=lambda:1000,test_only=True)
+result=stage.commit(authority.actor('personal-writer'),'commit',v['record'],1)
+print(json.dumps(result))
+'''
+        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(Path(__file__).resolve().parents[1])+os.pathsep+str(ROOT/'src'))
+        result=subprocess.run([sys.executable,'-c',code],input=json.dumps({'grants':self.authority.grants,
+            'path':str(self.memory.path),'test_key':self.memory.key.hex(),'record':s['record_id']}),
+            text=True,capture_output=True,env=env,timeout=10)
+        self.assertEqual(result.returncode,0,result.stderr)
+        self.assertEqual(json.loads(result.stdout),committed)
+        with self.memory._db() as db:self.assertEqual(db.execute("SELECT count(*) FROM research_stage_ops WHERE operation_id='commit'").fetchone()[0],1)
+
+    def test_missing_schema_does_not_automatically_migrate(self):
+        other=MemoryStore(Path(self.temp.name)/'other'/'memory.sqlite3',deletion_key=secrets.token_bytes(32),initialize=True)
+        with self.assertRaises(Unavailable):ResearchStage(other,self.authority,self.actor(),clock=lambda:1000,test_only=True)
+        with other._db() as db:self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='research_stage_meta'").fetchone())
+
+
+if __name__=='__main__':unittest.main()
```
