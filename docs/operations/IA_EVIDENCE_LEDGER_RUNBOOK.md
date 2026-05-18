# IA Evidence Ledger Runbook

IA-04 converts Internet Archive metadata source-cache records into local
evidence-ledger candidate records. The candidates are review inputs only.

## Scope

Allowed inputs:

- IA-01 fixture-derived source-cache records
- IA-02 redacted live-preview source-cache records
- deterministic test fixtures

Forbidden inputs:

- raw live response bodies
- downloaded IA files
- item file contents
- model/provider output
- extracted archive members
- arbitrary URLs

## Dry Run

```powershell
python scripts/eureka_ia_evidence_ledger_write.py --instance ..\instances\default --operator-token local-dev-token --from-source-cache --dry-run --json
```

Dry-run builds would-write evidence candidates and does not mutate the
operator instance.

## Temp Apply Proof

Use a temporary explicit instance:

```powershell
$Instance = Join-Path $env:TEMP "eureka-ia04-instance"
python scripts/eureka_init_instance.py --instance $Instance --json
python scripts/eureka_validate_instance.py --instance $Instance --json
python scripts/eureka_set_operator_token.py --instance $Instance --token local-dev-token --json
python scripts/eureka_ia_source_cache_write.py --instance $Instance --operator-token local-dev-token --from-fixtures --from-live-preview control/inventory/ia_02_tls_continue_normalized_preview.json --apply --json
python scripts/eureka_ia_evidence_ledger_write.py --instance $Instance --operator-token local-dev-token --from-source-cache --apply --json
```

Apply requires `--apply`, an explicit `--instance`, and a configured operator
token. IA-04 proof uses a temporary instance, not `..\instances\default`.

## Boundaries

Evidence candidates:

- require review
- are not accepted truth
- do not mutate candidate, reviewed, or master indexes
- do not commit raw IA responses
- do not download, upload, extract, execute, deploy, or call model providers

IA-05 is the next gate for candidate index integration. IA-04 does not start
that work.
