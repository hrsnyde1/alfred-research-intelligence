# Protected Alfred HQ synchronization — Phase 5 simulation

This is a proposed logical contract with a test-only implementation. It does not configure an HQ vault, use a Memory endpoint, or create a shared production database.

## Partitions and identity

Company records retain their original `gabos`, `fintra` or `sc_products` environment, record ID, Research catalog version, packet/decision, classification, evidence and access requirements. The company-scoped test transcript is also its distinct logical HQ destination partition. A successful HQ_SYNCED receipt references the immutable company candidate; no record is flattened into Personal Alfred or another company. Personal records do not use this company-to-HQ port.

There is no implicit HQ eligibility. Same-company issued Director must explicitly call hq_allow for the exact current promoted record/digest. A new correction/version needs its own eligibility operation; private status is not an automatic copying entitlement. Owner retrieval additionally requires a TestMemoryAccess bootstrap grant with the exact independently issued Personal Alfred Director context, allowlisted company partitions and permitted classification. Source content, request metadata, company Directors and freshly constructed/reissued lookalike contexts do not receive owner grants.

Company-to-company sharing remains forbidden. A personal owner may retrieve permitted company knowledge through hq_retrieve only; generic company Memory reads still reject that personal context. No owner context is delegated to a company principal. Owner receipt actor is retained in the originating company's transcript for audit.

## Operations

1. hq_allow records explicit, digest-bound company eligibility for current promoted data.
2. hq_sync checks current source identity, Research currentness, fake promotion, eligibility and company scope under the environment locks. Eligible success records HQ_SYNCED. Ineligible, expired, superseded, deleted, revoked or disputed data produces HQ_TOMBSTONE, explicitly indicating no current HQ copy. Successful tombstone application is not successful knowledge synchronization.
3. hq_retrieve requires independently authorized owner partition/classification access, a latest successful HQ_SYNCED receipt, explicit eligibility, current fake PROMOTED state and a fresh authoritative Research currentness check. It returns a separate RETRIEVABLE receipt plus the unchanged candidate with citations. Receipt replay cannot serve as fresh retrieval.

PARTIAL/FAILED sync fixtures are durable receipts and never establish HQ_SYNCED. A later failed sync prevents current HQ retrieval until a new successful sync; fail-closed availability is intentional. Ambiguous response after an immutable sync event raises DeliveryAmbiguous; the same operation ID reconciles the original historical result, not a fresh statement of current state.

## Evolution and retraction

Research correction/supersession immediately invalidates old current retrieval, including HQ retrieval, even before a subsequent explicit hq_sync writes its tombstone. An approved replacement goes through candidate/commit/promotion independently, preserves the Research relationship, and requires its own eligibility and synchronization. The supersede port checks the promoted replacement and the explicit Research relationship before marking the old fake record SUPERSEDED.

Deletion, revocation and expiry change fake lifecycle state through expected-sequence updates; HQ retrieval immediately denies the old record. A subsequent hq_sync durably records HQ_TOMBSTONE. Conflicts/expiration in Research also block fresh HQ reads immediately. No background synchronizer is introduced: propagation is exercised by explicit on-demand operations. Historical synthetic fixtures remain for audit; no live secure-erasure claim is made.

Revocation and synchronization share the same company lock. If synchronization precedes revocation, fresh retrieval still observes revoked state and fails; if revocation precedes sync, sync writes a tombstone. No stale synchronization can restore current access. Replays cannot overwrite state or give a historical success receipt fresh validity.

## Linux questions

Memory must own actual partition identifiers/credentials, eligibility policy, owner capability issuance and revocation, classification/purpose enforcement, receipt/transport authentication, source-master semantics, correction/delete propagation acknowledgements, backup/restore anti-rollback and unavailable-HQ behavior. Offline issued contexts and grants are synthetic bootstrap capabilities, not a production identity provider. Real end-to-end acceptance remains unverified.
