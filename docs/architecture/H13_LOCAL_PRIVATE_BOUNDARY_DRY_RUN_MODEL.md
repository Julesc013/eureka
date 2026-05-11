# H13 Local Private Boundary Dry Run Model

The H13 boundary dry-run model wraps H13 fixture normalizers with fail-closed approval gates. Source-specific wrappers expose request building, policy evaluation, and fixture-equivalent normalization without source access. Missing approval produces blocked output.

## Validation

Run `python scripts/validate_h13_local_private_boundary_dry_run.py` and the H13 boundary dry-run script checks. Outputs remain candidates/previews only and prepare H13-BUNDLE-04 review integration.
