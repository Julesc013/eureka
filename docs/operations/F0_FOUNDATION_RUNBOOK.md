# F0 Foundation Runbook

Use this runbook for the fixture-only and manifest-only F0 foundation.

Smoke commands:

```bash
python scripts/eureka_f0_fixture_builder.py --check --json
python scripts/eureka_f0_manifest.py --fixture-manifest examples/f0/f0_fixture_manifest.json --json
python scripts/eureka_f0_workunit_seed.py --from-manifest examples/f0/safe_zip_expected_manifest.json --dry-run --json
python scripts/eureka_f0_smoke.py --fixture-manifest examples/f0/f0_fixture_manifest.json --projection operator_workbench --json
```

Boundary posture:

- no downloads
- no filesystem extraction
- no execution
- no arbitrary operator file reads
- no evidence writes
- no reviewed records
- no index mutation

F0 output is not truth. Treat every manifest and WorkUnit seed as review-gated candidate information. If a task requires live fetches, arbitrary local extraction, installer execution, model calls, or public fanout, stop and create a future policy task.
