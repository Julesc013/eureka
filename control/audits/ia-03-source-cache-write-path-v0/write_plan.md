# Write Plan

Inputs:

- IA-01 fixture replay normalized records
- IA-02 TLS continuation redacted normalized live-preview records

Validation uses:

```powershell
python scripts/eureka_ia_source_cache_write.py --instance <temp-instance> --operator-token local-dev-token --from-fixtures --dry-run --json
python scripts/eureka_ia_source_cache_write.py --instance <temp-instance> --operator-token local-dev-token --from-fixtures --from-live-preview control/inventory/ia_02_tls_continue_normalized_preview.json --apply --json
```

The apply proof uses a temporary explicit instance only.
