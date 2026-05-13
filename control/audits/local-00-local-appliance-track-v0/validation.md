# Validation

Validation is performed by `scripts/validate_local_appliance_track.py` and `tests/operations/test_local_appliance_track.py`.

LOCAL-00 leaves product/runtime paths untouched and keeps LAN, deployment, production readiness, and public launch readiness disabled.

Results recorded during LOCAL-00:

- `python scripts/validate_local_appliance_track.py`: pass.
- `python -m unittest tests.operations.test_local_appliance_track`: pass, 13 tests.
- `python scripts/check_architecture_boundaries.py`: pass.
- `git diff --check`: pass.
- `python -m unittest discover -s tests -t .`: fail from the existing runtime leakage gate; 4065 tests ran, with runtime leakage reporting 1030 new unallowlisted production-path findings.
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: expected to pass after commit because the new LOCAL-00 audit pack is intentional generated audit evidence.
