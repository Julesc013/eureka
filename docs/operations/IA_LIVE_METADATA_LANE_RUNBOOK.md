# IA Live Metadata Lane Runbook

Use the CLI for local verification:

```text
python scripts/eureka_ia_live_metadata_lane.py --query sampleproject --projection operator_workbench --dry-run --json
python scripts/eureka_ia_live_metadata_lane.py --query sampleproject --projection operator_workbench --mock-live --json
python scripts/eureka_ia_live_metadata_lane.py --query sampleproject --projection public_web --mock-live --json
```

Expected posture:

- Dry-run emits a lane and events without network access.
- Mock-live uses deterministic fixture transport and emits provisional
  candidates.
- Public and native projections return blocked command responses.
- Boundary reports keep all write, download, extraction, model, deployment, and
  launch flags false.

Optional real live smoke is intentionally not part of default validation. Only
run it when an operator explicitly supplies `--allow-live`, a token, and bounded
limits. Do not commit raw responses.
