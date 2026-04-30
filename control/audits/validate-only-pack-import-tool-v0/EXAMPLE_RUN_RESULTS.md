# Example Run Results

Current known example validation:

- source pack: passed
- evidence pack: passed
- index pack: passed
- contribution pack: passed
- master-index review queue: passed

Command:

```bash
python scripts/validate_only_pack_import.py --all-examples --json
```

Observed report status:

- `report_status`: `validate_only_passed`
- `validation_summary.total`: 5
- `validation_summary.passed`: 5
- all hard mutation-safety fields: false

Typed AI output examples can also be included with `--include-ai-outputs`; they
are reported as an `ai_output_bundle` and remain review-required suggestions.
No model calls are made.
