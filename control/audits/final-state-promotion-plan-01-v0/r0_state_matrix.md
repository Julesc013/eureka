# R0 State Matrix

|capability_id|status|implemented|tested|evidence_path|validator|
|---|---|---|---|---|---|
|source_observation|pass|True|True|control/inventory/source_observation_seam_inventory.json|python scripts/validate_source_observation_seam.py|
|source_cache|pass|True|True|control/inventory/source_cache_store_inventory.json|python scripts/validate_source_cache_store.py|
|evidence_ledger|pass|True|True|control/inventory/evidence_ledger_store_inventory.json|python scripts/validate_evidence_ledger_store.py|
|review_queue|pass|True|True|control/inventory/review_queue_store_inventory.json|python scripts/validate_review_queue_store.py|
|public_index|pass|True|True|control/inventory/public_index_store_inventory.json|python scripts/validate_reviewed_public_index.py|
|one_source_live_test|pass|True|True|control/inventory/one_source_live_test_result.json|python scripts/validate_one_source_live_test.py|
|contract_taxonomy_cleanup|partial|True|True|control/inventory/r0_contract_taxonomy_remediation_result.json|python scripts/validate_contract_taxonomy_remediation.py|
|generated_artifact_drift_remediation|pass_with_warnings|True|True|control/inventory/r0_generated_artifact_remediation_result.json|python scripts/validate_generated_artifact_drift.py|
|legacy_runtime_leakage_remediation|pass_with_warnings|True|True|control/inventory/legacy_runtime_leakage_remediation_result.json|python scripts/validate_legacy_runtime_leakage_remediation.py|
|r0_closeout|pass_with_warnings|True|True|control/inventory/r0_final_closeout_result.json||
|r0_promotion_to_main|pass_with_warnings|True|True|control/inventory/dev_to_main_r0_merge_result.json||
