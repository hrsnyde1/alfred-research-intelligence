# Phase 7H Memory diff review — reconstructed

Reconstructed on 2026-10-16 from existing Mac artifacts; not a contemporaneous execution report. No tests rerun, Linux accessed, staging source/tests changed, or dependencies installed during reconstruction. Unknown details are explicitly marked.

Original store SHA-256: `5ca002bd93e486875191292c21ba782fb2df5eb3fa4d525654e80ad29069cf8c`. Full original path/hash list: BASELINE_MANIFEST.json. All 34 original hashes verified; only store.py differs between shared paths. Two new files; no original tests changed.

## Exact existing-source diff

```diff
--- baseline/focused_v1/store.py
+++ work/focused_v1/store.py
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

## Current changed-file and diff identities

- `work/focused_v1/store.py`: `0d84c9c12c0715f14be7729a5007073ebc99f55fa7820e6bed81a55834d969c1`
- `work/focused_v1/research_stage.py`: `15e24eb7aa3f84f8796d12dd9d4684d2748943cfda58dc3fa8827428b12dcd3a`
- `work/tests/test_research_memory_stage.py`: `53e1f0b095443401ec79daa8a0a7c534a48c47b649972395123af1d457e6cd1e`
- `CHANGES.patch`: `009659f231af341a170a3cf483bcd208df8537ffbc8e1b23af0070d4bf3a43ed`

Full source/test additions are recorded in `artifacts/staging/phase7h-memory/CHANGES.patch` and actual files. Stored-review-state correction changes only response truthfulness; it does not approve a pending/rejected record. New module is not imported by existing Memory HTTP routing. Test-only authority, explicit initialization and always-denied production promotion/dispatch preserve production-disabled boundary.

Compatibility risks: new module depends on Research package codecs; synthetic additive tables are not an approved production migration; in-memory authority is not a production credential store. Historical receipt/current-state semantics have offline tests, not live host acceptance. Retention/deletion and export integration remain blocked. The inherited compatibility failures are unchanged and do not provide full compatibility clearance.
