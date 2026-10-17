# Phase 7J Memory test harness review

2026-10-16. Mac-only static review of baseline/work test files, imported fixture helper, relevant callable code, saved runner, source diff, Phase 7I plans and reconstructed Phase 7H reports. No test execution. All 92 inventory hashes rechecked and match. Shared copies differ only in store.py duplicate response; new module/test are separately included. Original tests are unchanged. Static review establishes intended call paths, not an effective OS confinement boundary.

Paths below are relative to artifacts/staging/phase7h-memory; baseline line references also apply to unchanged work files.

## Findings and required controls

| Risk | Actual reviewed call path | Required treatment |
| --- | --- | --- |
| HTTP interaction | baseline/tests/test_obsidian_candidate.py:377–405,459–465,546–555 creates ThreadingHTTPServer at 127.0.0.1 port 0 and calls those fixture endpoints | Private network namespace; host loopback excluded. Local server fixtures are not live Memory API calls |
| Unix sockets | Same test file :950–966,2347–2366,2384–2406; disposable tests :458–476 use synthetic temporary socket paths | Private tmp/mount/net namespaces; authenticated peer checks unchanged; no production sockets mounted |
| Hardcoded production public-key dependency | disposable_delivery.py:39,142–158,190; test_obsidian_disposable_delivery.py:159–173 reads installed key unless fixture injected | Hide /opt; raw run may fail closed. One-case synthetic expected-line injection only for labeled adjusted run |
| Hardcoded runtime configuration | test_obsidian_candidate.py:2298–2338 includes /run/alfred-obsidian-editor-hq/ingress.sock and loopback:12345 in a temp JSON; load_alfred_editor uses injected self.port | Strings are validation input, not a live listener/client in that test. Keep host /run/network inaccessible against accidental fallback |
| Public system fixtures | disposable tests :111–136 read pinned /etc/skel | Allow only reviewed public skeleton files, read-only; no host /etc wholesale mount |
| Environment inheritance | run_tests.py copies os.environ; Node tests pass **os.environ; new test :260 copies environment to Python child | env -i before launcher; explicit safe PATH/HOME/TMPDIR/PYTHONPATH; no SSH_AUTH_SOCK, provider secrets, proxies, production configuration variables or inherited service FDs |
| External commands | candidate tests :1837,2130; disposable tests :220,344 run Node -e/driver, bounded 10-second calls; extension :261 runs sys.executable -c restart fixture | Child processes stay inside same OS sandbox. Node optional/skipped when absent. Python restart is mandatory synthetic coverage |
| SSH transport capability | candidate :2368–2383 uses injected runner recording SSH command; disposable :316–340 Node sender uses fake EventEmitter child | No actual SSH needed. Omit SSH credentials/network; do not rely on mocks alone for prevention |
| Sync executable capability | candidate :1984–2103 creates temp synthetic-ob shell text, passes injected bounded runner or mocks subprocess.run; hq_sync_once.py:42–70 can execute supplied binary | Existing cases use fakes, not real Obsidian. Do not expose real Sync binary/config. Private sandbox remains necessary for future call-path drift |
| Filesystem mutation | Existing three Memory test modules create TemporaryDirectory roots for SQLite, synthetic vaults, archives, token/key/config files; work extension setUp :20–24 does same | TMPDIR must be private tmpfs, no host temp sharing. All fixture writes bounded there |
| Non-temp writes | run_tests.py writes baseline/work-tests.txt, results.json, runtime-stderr.txt under staging parent | Only dedicated new result destinations writable; do not overwrite source/manifests/prior Mac evidence |
| Inert hostile text | test_focused_v1_obsidian_export.py includes $(touch /tmp/nope), script tags and synthetic password text as memory content | Data only; no shell evaluation. Do not mistake synthetic strings for real secrets |
| Import/config loading | Test modules load copied modules/helpers through relative paths/PYTHONPATH; new extension imports tests/test_research.py, which imports 19-module closure | Read-only transferred closure; clean Python startup, no user site/.pth/config fallback. Verify every Alfred module origin, including child process |

No demonstrated direct production write occurs in intended test paths. The installed public-key read is the concrete unisolated production dependency; raw host execution is prohibited. Source callable defaults have live capabilities (HTTP/SSH/Sync/config), so absence of intended test calls does not authorize unsandboxed execution.

## Fixture/signature review

The proposed Phase 7I one-method wrapper generates an ephemeral Ed25519 pair using cryptography, retains only generated OpenSSH public type/base64, builds a forced-command expected line, and patches _authorized_line only around test_initialization_rejects_existing_keys_and_authorized_file. It leaves original assertions, initialize, _verified_file, ownership checks and all HMAC/receipt signature verification intact. It does not execute RECEIVE_KEY_COMMAND; that is part of expected bytes. No private key serialization, real key access or permanent signing authority.

The existing neighboring test :175–182 supplies synthetic base64 expected bytes and a synthetic /opt command string; this is not a production key. Other tests generate secrets.token_bytes or synthetic tokens inside their temp roots. New restart case :244–267 passes synthetic temporary MemoryStore deletion key to its child and independently blocks child sockets. Neither should inherit real credentials. Generated private key deletion is not a claim of guaranteed cryptographic memory erasure.

Wrapper is suitable in principle for fixture-adjusted comparison, but it is documentation-only: no complete hashed executable harness exists or has run. Its in-memory insertion/import ordering must be verified; the child must add the selected copy's tests directory before importing test_obsidian_disposable_delivery, wrap exactly one method, preserve test count and record fixture mode. Do not patch the whole suite. Missing or multiple insertion anchors fail closed. Loader ownership/symlink checks are not covered by replacing _authorized_line and must not be claimed tested.

## Optional and mandatory coverage

Four Node tests and one pymupdf test explicitly skip if unavailable; do not install dependencies or count skips as passes. Two Node cases were original Mac failures, so skips leave those reproductions unresolved. All 23 extension tests must execute/pass; mandatory Linux rename/peer cases must execute. Matching pinned Ubuntu skeleton permits two additional original cases to run. Compare exact IDs and reasons, not only totals. Stored Mac outcomes remain 102/125 tests with identical 17 failures/3 errors/3 skips; no new outcome measured in Phase 7J.

## Assessment

Fixture design can preserve checks without real keys. Current runner is not a sandbox: its Python connect guard permits host loopback and arbitrary Unix paths, and does not constrain child Node calls. Earlier launcher templates lack demonstrated policy permission, synthetic account fixtures, finalized output confinement and aggregate resource limits. **Harness execution readiness is BLOCKED until the execution gate is satisfied.** No source/test modification was made during this review.
