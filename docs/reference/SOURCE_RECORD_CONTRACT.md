# Source Record Contract

A source record describes a source. It is not a connector, accepted evidence,
public truth, or permission to access the source.

Required boundary fields stay false:

- `source_record_is_public_truth`
- `source_record_is_accepted_evidence`
- `source_record_grants_live_access`
- `source_record_can_mutate_public_index`
- `source_record_can_mutate_master_index`
- `source_record_can_claim_rights_clearance`
- `source_record_can_claim_malware_safety`
- `source_record_can_claim_verified_installability`

Source records may describe family, trust lane, access modes, supported
capabilities, index depth, and future connector-family refs. Descriptive
capabilities do not grant permission.
