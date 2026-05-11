# H13 Local Private Boundary Dry Run No Access Policy

H13-BUNDLE-03 forbids local filesystem access beyond explicit committed fixture/request files, private-source access, user URL fetches, authenticated account access, restricted-source access, scans, listings, network/API/model calls, and browser automation.

## Validation

Run `python scripts/validate_h13_local_private_boundary_dry_run.py` and the H13 boundary dry-run script checks. Outputs remain candidates/previews only and prepare H13-BUNDLE-04 review integration.
