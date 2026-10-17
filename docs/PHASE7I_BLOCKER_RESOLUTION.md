# Phase 7I staging blocker resolution

Mac-only documentary investigation, 2026-10-16. No Linux access/writes, transfer, installs, production access or test execution. This document refines the earlier readiness plan; it does not authorize staging.

## Blocker status

| Blocker | Resolution | Remaining gate |
| --- | --- | --- |
| Node/PDF availability | Neither required for 23 extension cases; existing optional tests explicitly skip | Accept reduced integration coverage or separately approve runtime discovery/provisioning |
| Public-key fixture | Exact scoped synthetic fixture contract specified below | Review/authorize test-only harness; not implemented/executed here |
| Three missing Phase 7H reports | Reconstructed from source/manifest/recorded outputs, with unknowns marked | Owner review; historical reports now available, not invented execution evidence |
| OS sandbox | Required checks and safer mount/output plan specified in checklist | Working bwrap unverified; AppArmor restriction may block; stop rather than weaken host policy |

**Ready for separate authorization of a gated preflight and reduced-coverage test plan, not unconditional execution or full compatibility acceptance.** No Node/PDF installation is necessary for extension-only validation. Successful sandbox preflight and fixture-harness review remain mandatory before full copied-suite execution.

## Exact dependency coverage

All names below are existing methods; source paths are under baseline/tests (unchanged in work).

| Dependency | Optional test | Evidence |
| --- | --- | --- |
| Node | test_obsidian_candidate.CandidateTests.test_actual_node_journal_and_python_bridge_confirm_three_version_sequence | test_obsidian_candidate.py:1813–1816 |
| Node | test_obsidian_candidate.CandidateTests.test_actual_node_signed_hq_edit_reaches_confirmed_memory_outcome | :2105–2108 |
| Node | test_obsidian_disposable_delivery.DisposableDeliveryTests.test_actual_node_receipt_signatures_cross_python_inbox_boundary | test_obsidian_disposable_delivery.py:199–202 |
| Node | test_obsidian_disposable_delivery.DisposableDeliveryTests.test_exact_node_sender_frame_crosses_forced_relay_and_hmac_boundary | :305–308 |
| PyMuPDF | test_obsidian_candidate.CandidateTests.test_pdf_reference_when_reviewed_parser_available | test_obsidian_candidate.py:1133–1137 imports pymupdf, then skips on ImportError |

Mandatory for the planned Research extension check: all 23 new methods must actually execute and pass, plus existing nonoptional compatibility tests under equal baseline/work conditions. No extension test imports Node or PyMuPDF. Four Node tests and one PDF test are optional for reduced-coverage staging, mandatory to claim their specific device/PDF integrations validated. Two Node cases were among the original 17 failures: skipping them cannot count as fixing them.

Important correction to prior readiness evidence: Linux inspection checked `find_spec('fitz')`, not the test's actual `pymupdf` import. A missing fitz spec alone is not conclusive proof pymupdf is absent. Future sandbox preflight must check pymupdf directly. No installation or new Linux inspection performed here. Pytest is unused.

## Exact synthetic public-key contract

Failure: DisposableDeliveryTests.test_initialization_rejects_existing_keys_and_authorized_file, subcase `.ssh/authorized_keys`, test lines 159–173. It expects ValueError for existing bytes `synthetic-existing-unchanged`, retaining those bytes; it substitutes state/account/skeleton but not the installed public-key source. Source disposable_delivery.py:142–158 reads AUTHORIZED_PUBLIC, requires regular non-symlink root:root 0644 <=1024-byte one-line ssh-ed25519 public material, then constructs `restrict,command="<RECEIVE_KEY_COMMAND>" <type> <base64>\n`. initialize at :190 compares expected bytes via _verified_file before creating inbox.aes. Missing file raises FileNotFoundError instead of expected ValueError.

Smallest harness: generate a fresh Ed25519 key with installed cryptography entirely in test memory; serialize its PUBLIC component as OpenSSH plus newline. Build the expected forced-command line from that type/base64 and existing RECEIVE_KEY_COMMAND. Scope `patch.object(disposable, '_authorized_line', return_value=expected)` ONLY around this one test invocation, identically for both copies, following neighboring test at :181. Do not patch initialize, _verified_file, HMAC/receipt verification, ownership tests or denial assertions. Discard ephemeral private material immediately; never serialize or transfer it. No real key, production file or /opt read needed. Malformed existing authorized_keys still fails exact size/digest comparison and no inbox is created. This injects an independently controlled fixture/trust anchor, not an approval or signature bypass.

This adjusted case does not test _authorized_line's own root-owner loader. If loader coverage is required, separately approve an ephemeral root-mapped USER namespace with a generated synthetic public file and patch only AUTHORIZED_PUBLIC; check all owner/mode/symlink/format denial branches without sudo/host ownership changes. It is not required merely to resolve this test dependency. Do not use a fake host fstat result to pretend ownership checks were tested.

## Minimal source-only transfer inventory

Concrete static import closure for test_research fixture helper and staging extension; not all Research application modules or all Research tests. Preserve repo-relative layout so embedded parent paths remain valid. Baseline manifest supplies 34 files in each copy, plus two added work files, runner, baseline manifest, fixture helper and needed Research modules. CHANGES.patch, prior reports/results and logs are not needed to execute tests and stay on Mac. A reviewed future fixture harness/preflight script is additional and must receive its own hash before transfer. No scripts are created by this documentation task.

Inventory below is exact for CURRENT existing files; review and regenerate if bytes change. Baseline's 34 hashes also match original manifest. These hashes are transfer integrity, not production authorization. Static closure should be proven in sandbox before acceptance; any missing import fails closed rather than loading installed production code.

| Relative path | SHA-256 |
| --- | --- |
| `artifacts/staging/phase7h-memory/BASELINE_MANIFEST.json` | `13c01987ac459d9aa95ef266cc39884a909f88e93bc1dbc4fa5ed6fa03e7b700` |
| `artifacts/staging/phase7h-memory/baseline/deploy/focused-v1/obsidian_export.py` | `ba42372ba7221a1273f14e07a10688694997abb468ab18ed92e601d2aef11d54` |
| `artifacts/staging/phase7h-memory/baseline/deploy/obsidian-editor/disposable-test/inspect-delivery-state.py` | `f12e46da999151ccd6598d3d5a93171697b88c33e3aef60a5db1bb95d4318597` |
| `artifacts/staging/phase7h-memory/baseline/device/alfred-memory-editor/core.js` | `887635ef18b5b4f2f50efd4019b233bc4748f7b2c26389776472c0d06cf52fc6` |
| `artifacts/staging/phase7h-memory/baseline/device/alfred-memory-editor/device.js` | `a7aa4ef8f31296c93445285d527a5faa816f04124e4413710990ebbacba69ec9` |
| `artifacts/staging/phase7h-memory/baseline/device/alfred-memory-editor/test/hq-integration-driver.js` | `04dd42011a324967af4511853530e77780624afdb5c79d1b3c9fb132bfd679df` |
| `artifacts/staging/phase7h-memory/baseline/focused_v1/__init__.py` | `a45b4b3c132df7e1d8c830087185e752fc3dcd8f26b9d4a56e6626fe2dc3f8cb` |
| `artifacts/staging/phase7h-memory/baseline/focused_v1/server.py` | `2042c95d517601da03654b942b04bf96ed69bedf5afa0351ef64463542eba5ea` |
| `artifacts/staging/phase7h-memory/baseline/focused_v1/store.py` | `5ca002bd93e486875191292c21ba782fb2df5eb3fa4d525654e80ad29069cf8c` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/__init__.py` | `ad5ff6eece3dceb083367cd470edd09eda66d1bb5fcd134905df9ed0a6a06e8f` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/alfred_editor_v1.py` | `abd5f415cc075193ff65885c200d58d22a8af66d227a6ced7331e71403c9e8ff` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/bridge.py` | `775448b247c3a8813cbd3f94a2b1e17fe211c9fca1a72033b165ee7e0226a818` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/capture_routes.py` | `394418ff4ba612bddc7d20a2d07dce0cdfba0bf55664425c8a0f103141fa9db1` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/context.py` | `1d7faf8d4330e18d4a0c02f26ce536534f7d597becadf95b541bfb5c858cd7e8` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/context_service.py` | `86884fa67b808ea954d769c07f78a150ad1dd51290dd9f117667470aaccdd981` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/cycle.py` | `db66c01071c152513e63358355b83c795dd0c16f0ae3ab2bb941b168512e2ba8` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/disposable_delivery.py` | `79e4fd9718c9647e52933cb241e52955adb3b8059d1039ed4907d16cf7605115` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/disposable_forced.py` | `51c0446f383f908453b135a9d2dc3e11b15db44c3babdb0467bc45f46ea9a3f2` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/editor_origin.py` | `b24ad623668846195dfd533e3fad89090e4f935305f2365a00baaa836d97079a` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/editor_transport.py` | `8c7406b5db9e2d9e1b97280a48b24b81d59219db404b7038acb1feed8d59b14d` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/hq_sync_once.py` | `0724ed765fc43e67d4435b7eb12ac2225181c728557c933196e54bdbcdacdfc5` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/ingress.py` | `1c89ad12ee9392fb7ee215a772846af641b2258725c6c66e78f6737fc26ac7d9` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/notifications.py` | `52b7b374da786315a3d2b0f7ffbe8d1b5051a5ca8f86d6766d2a05397b0de153` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/outcome_gate.py` | `9ebc79cb0eb4e93e35b17e9b54a30de100b0abd6d724dacfbb794a8ecab2de8f` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/recovery.py` | `66cb0baa8ed5a6a750e6cb151767a36932c094c88940a08c710c7288013aaabb` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/references.py` | `3a138940515de1e8c7bed4f2958ddc22d243d32a31d340f6f476cd2823f090d5` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/routing.py` | `328afa38ae7897fef333d30b16f56a172e9429aa292e5b82ab5b29c57b183570` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/scaffold.py` | `0dce2be530e784154079a70d37657cea33f75ef2cf3a08084722dc5ee0195eac` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/scoped_ports.py` | `c8110549122df6c300bd0514dfd07c4ac326edceef8d5a2276840a5f544de000` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/service_api.py` | `f7fdcd5b01bf12b13415b8f4bbd7edbb7629ae0856b7267bca743b6773282cc5` |
| `artifacts/staging/phase7h-memory/baseline/obsidian_candidate/snapshot.py` | `d27b3b5dc2b67476da421ca10128651352ca0ed4c584cde40204ac6e5be47b43` |
| `artifacts/staging/phase7h-memory/baseline/scripts/count_only_v1_ownership.py` | `b4953049ee6c6d21e13dcee11c657cbb4edb5d16cfc56180a3ec02bb0f4b3129` |
| `artifacts/staging/phase7h-memory/baseline/tests/test_focused_v1_obsidian_export.py` | `8e7cc28875fc714a517ec13755af2a1e7e42b8cabefac37a075b253626d481b1` |
| `artifacts/staging/phase7h-memory/baseline/tests/test_obsidian_candidate.py` | `746f42e2c4f094374b04ded1677ccd95cbb5cbcd03d8bfe432c7c4c511596cef` |
| `artifacts/staging/phase7h-memory/baseline/tests/test_obsidian_disposable_delivery.py` | `14ba0777502fd895aefc66648987f7c2ac8d9ee26d9e9a9442d4da439ad78167` |
| `artifacts/staging/phase7h-memory/run_tests.py` | `e2b06dece0f86b528d47fcd41be115236df4e6157125a69e713a378b951454b2` |
| `artifacts/staging/phase7h-memory/work/deploy/focused-v1/obsidian_export.py` | `ba42372ba7221a1273f14e07a10688694997abb468ab18ed92e601d2aef11d54` |
| `artifacts/staging/phase7h-memory/work/deploy/obsidian-editor/disposable-test/inspect-delivery-state.py` | `f12e46da999151ccd6598d3d5a93171697b88c33e3aef60a5db1bb95d4318597` |
| `artifacts/staging/phase7h-memory/work/device/alfred-memory-editor/core.js` | `887635ef18b5b4f2f50efd4019b233bc4748f7b2c26389776472c0d06cf52fc6` |
| `artifacts/staging/phase7h-memory/work/device/alfred-memory-editor/device.js` | `a7aa4ef8f31296c93445285d527a5faa816f04124e4413710990ebbacba69ec9` |
| `artifacts/staging/phase7h-memory/work/device/alfred-memory-editor/test/hq-integration-driver.js` | `04dd42011a324967af4511853530e77780624afdb5c79d1b3c9fb132bfd679df` |
| `artifacts/staging/phase7h-memory/work/focused_v1/__init__.py` | `a45b4b3c132df7e1d8c830087185e752fc3dcd8f26b9d4a56e6626fe2dc3f8cb` |
| `artifacts/staging/phase7h-memory/work/focused_v1/research_stage.py` | `15e24eb7aa3f84f8796d12dd9d4684d2748943cfda58dc3fa8827428b12dcd3a` |
| `artifacts/staging/phase7h-memory/work/focused_v1/server.py` | `2042c95d517601da03654b942b04bf96ed69bedf5afa0351ef64463542eba5ea` |
| `artifacts/staging/phase7h-memory/work/focused_v1/store.py` | `0d84c9c12c0715f14be7729a5007073ebc99f55fa7820e6bed81a55834d969c1` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/__init__.py` | `ad5ff6eece3dceb083367cd470edd09eda66d1bb5fcd134905df9ed0a6a06e8f` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/alfred_editor_v1.py` | `abd5f415cc075193ff65885c200d58d22a8af66d227a6ced7331e71403c9e8ff` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/bridge.py` | `775448b247c3a8813cbd3f94a2b1e17fe211c9fca1a72033b165ee7e0226a818` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/capture_routes.py` | `394418ff4ba612bddc7d20a2d07dce0cdfba0bf55664425c8a0f103141fa9db1` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/context.py` | `1d7faf8d4330e18d4a0c02f26ce536534f7d597becadf95b541bfb5c858cd7e8` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/context_service.py` | `86884fa67b808ea954d769c07f78a150ad1dd51290dd9f117667470aaccdd981` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/cycle.py` | `db66c01071c152513e63358355b83c795dd0c16f0ae3ab2bb941b168512e2ba8` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/disposable_delivery.py` | `79e4fd9718c9647e52933cb241e52955adb3b8059d1039ed4907d16cf7605115` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/disposable_forced.py` | `51c0446f383f908453b135a9d2dc3e11b15db44c3babdb0467bc45f46ea9a3f2` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/editor_origin.py` | `b24ad623668846195dfd533e3fad89090e4f935305f2365a00baaa836d97079a` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/editor_transport.py` | `8c7406b5db9e2d9e1b97280a48b24b81d59219db404b7038acb1feed8d59b14d` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/hq_sync_once.py` | `0724ed765fc43e67d4435b7eb12ac2225181c728557c933196e54bdbcdacdfc5` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/ingress.py` | `1c89ad12ee9392fb7ee215a772846af641b2258725c6c66e78f6737fc26ac7d9` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/notifications.py` | `52b7b374da786315a3d2b0f7ffbe8d1b5051a5ca8f86d6766d2a05397b0de153` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/outcome_gate.py` | `9ebc79cb0eb4e93e35b17e9b54a30de100b0abd6d724dacfbb794a8ecab2de8f` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/recovery.py` | `66cb0baa8ed5a6a750e6cb151767a36932c094c88940a08c710c7288013aaabb` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/references.py` | `3a138940515de1e8c7bed4f2958ddc22d243d32a31d340f6f476cd2823f090d5` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/routing.py` | `328afa38ae7897fef333d30b16f56a172e9429aa292e5b82ab5b29c57b183570` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/scaffold.py` | `0dce2be530e784154079a70d37657cea33f75ef2cf3a08084722dc5ee0195eac` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/scoped_ports.py` | `c8110549122df6c300bd0514dfd07c4ac326edceef8d5a2276840a5f544de000` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/service_api.py` | `f7fdcd5b01bf12b13415b8f4bbd7edbb7629ae0856b7267bca743b6773282cc5` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/snapshot.py` | `d27b3b5dc2b67476da421ca10128651352ca0ed4c584cde40204ac6e5be47b43` |
| `artifacts/staging/phase7h-memory/work/scripts/count_only_v1_ownership.py` | `b4953049ee6c6d21e13dcee11c657cbb4edb5d16cfc56180a3ec02bb0f4b3129` |
| `artifacts/staging/phase7h-memory/work/tests/test_focused_v1_obsidian_export.py` | `8e7cc28875fc714a517ec13755af2a1e7e42b8cabefac37a075b253626d481b1` |
| `artifacts/staging/phase7h-memory/work/tests/test_obsidian_candidate.py` | `746f42e2c4f094374b04ded1677ccd95cbb5cbcd03d8bfe432c7c4c511596cef` |
| `artifacts/staging/phase7h-memory/work/tests/test_obsidian_disposable_delivery.py` | `14ba0777502fd895aefc66648987f7c2ac8d9ee26d9e9a9442d4da439ad78167` |
| `artifacts/staging/phase7h-memory/work/tests/test_research_memory_stage.py` | `53e1f0b095443401ec79daa8a0a7c534a48c47b649972395123af1d457e6cd1e` |
| `src/alfred_research/__init__.py` | `2a60c397556e8490825530a85704189794e117e282102b60c9ff5edb8f2e72fc` |
| `src/alfred_research/budgets.py` | `1ee260b88aff86f5c3adbaf6a70ee0966e8269632904f43d7b6721e3e01c8dc2` |
| `src/alfred_research/contracts.py` | `af82cd018c2784c8c0d37bbab6d20eddf00626846c724d3462046ba0fe383e58` |
| `src/alfred_research/persistence.py` | `29e154287fc4d84bcdbc2dc46bc9e73334ab91711566b570cb354dad55e6e65a` |
| `src/alfred_research/registration.py` | `7d69330d4ac9f96eb873121c4be510258edefb1042a5473300c371c455cf2217` |
| `src/alfred_research/research/__init__.py` | `e1026ca5d72fa1f526f91cd95c08e65f6de2150602d2080fe6906e5eaf19cfe3` |
| `src/alfred_research/research/contracts.py` | `fbee7a024940c7c8468a46bcefc9da5aac17afce5798c93814f1cbe544581c61` |
| `src/alfred_research/research/execution.py` | `57eceb97c5e02155bf0f619ea8199631ca0eec5aa68b6f63a3d01614196dbfc0` |
| `src/alfred_research/research/journal.py` | `3429382ab1f0d1481f134e4edbc77d03e7b69c33e7a48165558e19334aafe901` |
| `src/alfred_research/research/provider.py` | `732166250bcdc8e75c08d8c6f4f501c9dac1850270c9b19e443fd3718a9ba5dd` |
| `src/alfred_research/research/workflow.py` | `211a93c1539531bc8c86db0e82035ba839c27db7727723dbfb1fa05e53d9c5c5` |
| `src/alfred_research/sources/__init__.py` | `99428e6b8f94a5aa6ca188cd4e958bf12a084cf32bd8385ab3a8cd9a5dcc5d1b` |
| `src/alfred_research/sources/adapters.py` | `158298b805597afe3cce6ba514b9ae3f8db91330eab6cd92dfe74b1614bc548a` |
| `src/alfred_research/sources/contracts.py` | `927edf3ecb58863bc058eadec00c5aa719d3020432cb666c9cdf4b20d4e17efd` |
| `src/alfred_research/sources/policy.py` | `b414a3a25cbcbf0cf69ec7c54d449bd2128ebf9a6b8b56c733fa785919e2513f` |
| `src/alfred_research/sources/processor.py` | `19032ed0485f2fea21d7a5ac43b8b5d5fc270c45999ab28fe8365ec052703b5a` |
| `src/alfred_research/state.py` | `6bfffa7887617ea8b8a0d2c8fd2fa10584550bfb6f89a3cb107b1da82ab43da7` |
| `src/alfred_research/tenancy.py` | `2cefc72a8f86d8035e4c351963ad3398f14b04be04ab2f9e247c033088adf4f1` |
| `src/alfred_research/verification.py` | `093d6e6249ee6eec2d2595d5e703282155ccaa6c2daf3535e2382c1796f6841b` |
| `tests/test_research.py` | `0607876fab47cab4df1dd5b1d2dbe6e52ddd3bbcc0a6cfc8c96c57a6ca294435` |

Existing-file inventory: **92 files**, including **19 Research package modules**. No recursive directory copy is authorized. Exclude .git, caches, .env/configuration, databases/journals, previous output logs, private data and credentials.
