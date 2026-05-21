# Workbench Result Lanes Runbook

Use the deterministic CLI for a local, read-only projection check:

```bash
python scripts/eureka_workbench_result_lanes.py --query sampleproject --projection operator_workbench --from-play-demo --from-ia-examples --json
python scripts/eureka_workbench_result_lanes.py --query sampleproject --projection public_web --from-play-demo --from-ia-examples --json
python scripts/eureka_workbench_result_lanes.py --query sampleproject --projection native_desktop_read_only --from-play-demo --from-ia-examples --json
```

The CLI reads deterministic fixture-shaped records only. It does not mutate an instance, run source probes, call live IA, write source cache or evidence records, create candidates, rebuild indexes, extract files, call models, deploy, download, or upload.

Validate with:

```bash
python scripts/validate_workbench_result_lanes.py
python -m unittest tests.runtime.test_workbench_result_lanes tests.runtime.test_workbench_lane_view_models tests.runtime.test_workbench_lane_boundaries
```
