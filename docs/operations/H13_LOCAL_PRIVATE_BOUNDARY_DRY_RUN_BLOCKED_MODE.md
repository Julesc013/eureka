# H13 Local Private Boundary Dry Run Blocked Mode

Blocked mode is the default. If committed approval is absent or a forbidden operation is requested, the CLI emits a blocked result with candidates and previews only. No source, account, URL, filesystem, CAS, pack, evidence, or index operation occurs.

## Validation

Run `python scripts/validate_h13_local_private_boundary_dry_run.py` and the H13 boundary dry-run script checks. Outputs remain candidates/previews only and prepare H13-BUNDLE-04 review integration.
