# H13 Local Private Boundary Dry Run

H13 local/private boundary dry-runs are controlled policy rehearsals. They evaluate committed request envelopes and fixture-equivalent metadata only. They do not access local/private/restricted sources, fetch URLs, use accounts, import CAS blobs, export/import packs, write source cache or evidence, mutate indexes, publish data, or accept truth.

## Validation

Run `python scripts/validate_h13_local_private_boundary_dry_run.py` and the H13 boundary dry-run script checks. Outputs remain candidates/previews only and prepare H13-BUNDLE-04 review integration.
