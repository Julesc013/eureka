# Smoke Result

```json
{
  "artifact_verified_claim_created": false,
  "commands": [
    "python scripts/eureka_local_apply_preview_validate.py --from-live-metadata-review-examples --json",
    "python scripts/eureka_local_apply_live_metadata_previews.py --from-live-metadata-review-examples --use-temp-instance --json",
    "python scripts/eureka_local_apply_live_metadata_report.py --from-examples --json"
  ],
  "committed_instance_state": false,
  "deployment_performed": false,
  "download_performed": false,
  "extraction_executed": false,
  "malware_clean_claim_created": false,
  "master_index_mutated": false,
  "model_provider_used": false,
  "new_live_source_calls_performed": false,
  "operator_instance_mutated": false,
  "production_readiness_claimed": false,
  "public_index_mutated": false,
  "public_launch_readiness_claimed": false,
  "public_live_source_fanout_enabled": false,
  "public_mutation_enabled": false,
  "raw_live_response_committed": false,
  "reviewed_index_mutated": false,
  "reviewed_metadata_records_created": 1,
  "reviewed_source_leads_created": 2,
  "rights_clearance_claim_created": false,
  "schema_version": "local_apply_live_metadata_smoke_result.v0",
  "status": "pass",
  "task": "LOCAL-APPLY-LIVE-METADATA-PREVIEWS-00",
  "temp_instance_apply_passed": true,
  "verified_download_claim_created": false
}
```
