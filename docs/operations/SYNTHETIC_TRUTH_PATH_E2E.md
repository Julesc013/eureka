# Synthetic Truth Path E2E Runbook

Run the complete local proof:

```powershell
python scripts/eureka_synthetic_truth_path.py run `
  --scenario minimal-success `
  --out .eureka/test/e2e-reference/synthetic-truth-path
```

Validate the scenario:

```powershell
python scripts/eureka_synthetic_truth_path.py validate `
  --scenario-dir .eureka/test/e2e-reference/synthetic-truth-path/minimal-success `
  --strict
```

Inspect status:

```powershell
python scripts/eureka_synthetic_truth_path.py status `
  --scenario-dir .eureka/test/e2e-reference/synthetic-truth-path/minimal-success `
  --json
```

Restore active synthetic projections to baseline:

```powershell
python scripts/eureka_synthetic_truth_path.py rollback `
  --scenario-dir .eureka/test/e2e-reference/synthetic-truth-path/minimal-success
```

Verify the test snapshot:

```powershell
python scripts/eureka_synthetic_truth_path.py verify-snapshot `
  --scenario-dir .eureka/test/e2e-reference/synthetic-truth-path/minimal-success
```

Generated state is local and ignored by git. It remains under `.eureka/test/e2e-reference/synthetic-truth-path/`.

Non-claims:

- no real IA candidate is reviewed or promoted
- no production reviewed record is created
- no public or master index is mutated
- no public snapshot is published
- no provider, network, download, or execution action occurs
- fixity verifies local bytes only; it does not prove authenticity, safety, rights, or compatibility

