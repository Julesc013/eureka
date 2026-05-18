# IA Source Cache Write Runbook

IA-03 writes Internet Archive metadata source-cache records only. It does not
write evidence, review queues, candidate indexes, reviewed indexes, or the
master index.

## Dry Run

```powershell
python scripts/eureka_ia_source_cache_write.py --instance ..\instances\default --operator-token local-dev-token --from-fixtures --dry-run --json
```

Dry-run validates inputs and builds would-write records without mutating the
operator instance.

## Temp Apply Proof

Use a temporary explicit instance:

```powershell
$Temp = Join-Path $env:TEMP "eureka-ia03-proof"
python scripts/eureka_init_instance.py --instance $Temp --json
python scripts/eureka_set_operator_token.py --instance $Temp --token local-dev-token --json
python scripts/eureka_ia_source_cache_write.py --instance $Temp --operator-token local-dev-token --from-fixtures --from-live-preview control/inventory/ia_02_tls_continue_normalized_preview.json --apply --json
```

Apply mode requires `--apply`, `--instance`, and a valid operator token.

## Boundaries

Source-cache records are source observations, not truth. IA-03 keeps raw live
responses, evidence writes, index mutation, downloads, uploads, extraction,
model/provider calls, deployment, and public/production readiness claims
forbidden.

IA-04 is the first task that may define evidence-ledger integration.
