# Pack Discovery And Classification

Discovery is limited to known manifest filenames:

- `SOURCE_PACK.json`
- `EVIDENCE_PACK.json`
- `INDEX_PACK.json`
- `CONTRIBUTION_PACK.json`
- `PACK_IMPORT_DRY_RUN_INPUT.json`

Classification dimensions:

- `pack_kind`: source_pack, evidence_pack, index_pack, contribution_pack,
  pack_set, unknown
- `schema_version`: manifest schema or unknown
- `validation_status`: valid, invalid, validator_missing, validator_not_run,
  warning, unknown
- `privacy_status`: public_safe, redacted, local_private, rejected_sensitive,
  unknown
- `public_safety_status`: public_safe, review_required, rejected, unknown
- `risk_status`: metadata_only, executable_reference, private_data_risk,
  credential_risk, URL_fetch_risk, mutation_risk, unknown
- `mutation_impact`: none_dry_run_only, source_cache_candidate_effect,
  evidence_ledger_candidate_effect, candidate_index_candidate_effect,
  public_index_candidate_effect, master_index_candidate_effect,
  blocked_mutation_claim, unknown
- `promotion_readiness`: not_ready, review_required, candidate_ready_future,
  blocked, unknown

The source-pack example may describe a source-inventory candidate effect; the
runtime normalizes it to a source-cache candidate effect because no source
inventory or source-cache mutation exists in P104.
