# Return Contract

Expected compact return file:

```text
../eureka-evidence-runs/artifact_evidence_collection_00/artifact_evidence_collection_summary.json
```

Required top-level fields:

```text
schema_version
run_id
collected_at
collector
target_results
raw_artifacts_retained_outside_repo
downloads_performed
executables_fetched
install_or_execution_performed
rights_clearance_claimed
malware_safety_claimed
resume_recommended_task
```

Each `target_results` entry should include:

```text
target_id
status
source_refs
observed_fields
remaining_gaps
recommended_review_action
```

Allowed `status` values:

```text
evidence_collected
partially_collected
blocked
not_found
deferred
```

Resume task after a valid compact return:

```text
MANUAL-ARTIFACT-OBSERVATION-BATCH-03
```

## Additive Template Files

The following files clarify the return shape without changing the contract:

- `evidence_packet_template.json`
- `source_reference_template.json`
- `artifact_identity_evidence_checklist.md`
- `artifact_integrity_evidence_checklist.md`
- `acquisition_evidence_checklist.md`
- `prohibited_claims.md`
- `example_return_packet.json`

If a future collector has already started against the original contract, keep
this file stable and use the templates as optional field guidance.
