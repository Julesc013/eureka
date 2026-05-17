# Validation

Planned validation for this preflight:

- `git diff --check`
- `python -m json.tool control/inventory/instance_layout_preflight_diff_classification.json`
- `python -m json.tool control/inventory/instance_layout_preflight_result.json`
- `python -m json.tool control/audits/instance-layout-preflight-01-v0/instance_layout_preflight_report.json`
- `git status --short --branch`
- `python .aide/scripts/aide_lite.py commit check --latest`

Boundary checks:

- Runtime modified: false
- Scripts modified: false
- Tests modified: false
- Operator instance moved: false
- Operator instance deleted: false
- Source probes executed: false
- Extraction executed: false
- Model/provider calls used: false
- Deployment performed: false
