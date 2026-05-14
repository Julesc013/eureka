# Validation

- `git diff --check`: PASS.
- `python -m json.tool` for HUNT policies, inventories, and report: PASS.
- `python scripts/validate_search_hunt_track.py --json`: PASS_WITH_WARNINGS; carries final baseline warning disposition forward.
- `python -m unittest tests.operations.test_search_hunt_track`: PASS.
- `python scripts/check_architecture_boundaries.py`: PASS.
- `python -m unittest discover -s tests -t .`: PASS, 4330 tests.
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS.
- `py -3 .aide/scripts/aide_lite.py test`: PASS.
- `py -3 .aide/scripts/aide_lite.py selftest`: PASS.
- `py -3 .aide/scripts/aide_lite.py verify`: WARN, diff-scope/context metadata only while HUNT-00 files are uncommitted.
- `py -3 .aide/scripts/aide_lite.py review-pack`: PASS_WITH_WARNINGS.
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: expected pre-commit FAIL because this audit pack is new generated output; rerun after commit is required.
