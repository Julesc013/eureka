# IA Candidate Index Runbook

IA-05 writes provisional Internet Archive metadata candidate-index records only.
Candidate records are search/discovery candidates for future review; they are
not accepted truth, not reviewed records, and not master-index records.

## Dry Run

The default mode is dry-run. It validates evidence inputs and builds would-write
candidate records without mutating an instance:

```powershell
python scripts/eureka_ia_candidate_index_write.py --instance ..\instances\default --operator-token local-dev-token --from-evidence-ledger --dry-run --json
```

The command may fall back to deterministic IA-04 evidence candidates when no
explicit evidence ledger is present, which keeps the lane useful for local
verification without touching the operator instance.

## Temp Apply Proof

Use a temporary instance for apply proof:

```powershell
python scripts/eureka_init_instance.py --instance <temp-instance> --json
python scripts/eureka_validate_instance.py --instance <temp-instance> --json
python scripts/eureka_set_operator_token.py --instance <temp-instance> --token local-dev-token --json
python scripts/eureka_ia_source_cache_write.py --instance <temp-instance> --operator-token local-dev-token --from-fixtures --from-live-preview control/inventory/ia_02_tls_continue_normalized_preview.json --apply --json
python scripts/eureka_ia_evidence_ledger_write.py --instance <temp-instance> --operator-token local-dev-token --from-source-cache --apply --json
python scripts/eureka_ia_candidate_index_write.py --instance <temp-instance> --operator-token local-dev-token --from-evidence-ledger --apply --json
```

Do not use `..\instances\default` for apply proof unless an operator explicitly
asks for that local instance to be mutated.

## Boundaries

IA-05 keeps these false:

- `accepted_truth`
- `reviewed_record_created`
- `reviewed_index_mutation_performed`
- `master_index_mutation_performed`
- `raw_response_committed`
- `download_performed`
- `upload_performed`
- `extraction_executed`
- `model_provider_used`

IA-05 may write provisional candidate records to an explicit temporary instance.
It must not create reviewed records or mutate reviewed/master indexes.

## Validation

```powershell
python scripts/validate_ia_candidate_index_integration.py
python -m unittest tests.runtime.test_ia_candidate_index_integration
python -m unittest tests.runtime.test_ia_candidate_records
python -m unittest tests.runtime.test_ia_candidate_boundaries
python -m unittest tests.operations.test_ia_candidate_index_scripts
```

## IA-06 Handoff

IA-06 may add a review/promotion dry-run. IA-05 does not promote candidates and
does not claim production or public-launch readiness.
