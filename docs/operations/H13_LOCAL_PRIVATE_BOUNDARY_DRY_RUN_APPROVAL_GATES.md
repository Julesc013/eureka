# H13 Local Private Boundary Dry Run Approval Gates

Approval requires an exact committed request key, boundary_dry_run_approved true, operation_scope boundary_dry_run_only, boundary_only operation class, all access/import/export/write/publication approvals false, allowlisted output paths, and a reviewed kill switch.

## Validation

Run `python scripts/validate_h13_local_private_boundary_dry_run.py` and the H13 boundary dry-run script checks. Outputs remain candidates/previews only and prepare H13-BUNDLE-04 review integration.
