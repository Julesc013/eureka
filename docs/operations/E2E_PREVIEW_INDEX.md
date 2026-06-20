# E2E Preview Index Operations

Build from available local generated material:

```powershell
python scripts/eureka_index.py preview-build `
  --runs-root .eureka/e2e-reference/runs `
  --candidate-delta .eureka/source-wave/ia-metadata/candidate-index/latest/candidate_index_delta_manifest.json `
  --evidence-delta .eureka/source-wave/ia-metadata/evidence-ledger/latest/evidence_summary_delta_manifest.json `
  --source-observation-delta .eureka/source-wave/ia-metadata/source-observation-cache/latest/source_observation_delta_manifest.json `
  --out .eureka/e2e-reference/preview-index `
  --json
```

Validate:

```powershell
python scripts/eureka_index.py preview-validate `
  --index .eureka/e2e-reference/preview-index/current.json `
  --strict `
  --json
```

Search directly:

```powershell
python scripts/eureka_index.py preview-search `
  --index .eureka/e2e-reference/preview-index/current.json `
  --query "old blue FTP client for XP" `
  --json
```

Search through the existing local search surface:

```powershell
python scripts/eureka_search.py "old blue FTP client for XP" `
  --index preview `
  --index-path .eureka/e2e-reference/preview-index/current.json `
  --metadata-fallback none `
  --format json
```

Generation management:

```powershell
python scripts/eureka_index.py preview-list-generations --json
python scripts/eureka_index.py preview-compare --left <generation-a> --right <generation-b> --json
python scripts/eureka_index.py preview-rollback --to <generation-id> --json
```

Safety invariants:

- no provider/network calls;
- no downloads or file payload fetches;
- no reviewed-record creation;
- no reviewed/master mutation;
- no public-index mutation;
- no snapshot publication;
- no public exposure;
- no license change.
