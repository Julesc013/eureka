# Local Evidence Ledger Runtime Model

The Track B evidence ledger runtime is a local-foundry helper. It accepts explicit fixture or repo-local inputs, normalizes them into evidence candidate records, validates provenance/conflict/truth/product boundaries, and can build a snapshot for audit evidence.

## Record Model

An evidence ledger record contains:

- claim identity: `evidence_record_id`, `evidence_record_status`, `evidence_record_type`, `claim_type`
- source context: `source_id`, `source_label`, `source_locator`
- claim content: `claim_summary`, optional `claim_value_optional`, `claim_subject`, `observation_summary`
- provenance: `provenance_summary`, `lineage_refs`, related candidate/source-cache/search-need/workunit/pack refs
- governance: confidence, conflict summary, review gates, privacy posture, rights/risk posture, truth boundary, and product boundary

Snapshots aggregate records by status, type, claim type, and source. They also preserve conflict counts and make automatic merge/resolution false.

## Claim Handling

Claims are reviewable candidates. Metadata, identity, compatibility, checksum, filename/member, source locator, pack, contribution, conflict, review status, and provenance records can be summarized. None are promoted into accepted evidence or public truth.

Conflicting records must preserve conflict details and require review. The runtime does not merge or resolve them.

## Append Intent

The model is append-intent in shape, but no persistent append storage is implemented. Scripts can write explicit audit reports only when an output path is provided and allowed by policy.
