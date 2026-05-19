# Validation

Required validation lane:

- `git status --short`
- `git diff --check`
- `python scripts/validate_repo_structure_canon.py`
- `python -m unittest tests.operations.test_repo_structure_canon`
- `python -m unittest tests.scripts.test_validate_repo_structure_canon`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python .aide/scripts/aide_lite.py doctor`
- `python .aide/scripts/aide_lite.py validate`
- `python .aide/scripts/aide_lite.py test`
- `python .aide/scripts/aide_lite.py selftest`
- `python .aide/scripts/aide_lite.py verify`
- `python .aide/scripts/aide_lite.py review-pack`

The final task report must state the exact pass, warning, or blocked result for
each command that was run.

## Pre-Commit Results

| Command | Result |
| --- | --- |
| `git status --short` | PASS, showed only intended task changes. |
| `git diff --check` | PASS, with line-ending warnings on AIDE context files. |
| `python scripts/validate_repo_structure_canon.py` | PASS, with recorded `scripts/` transitional debt warning. |
| `python -m unittest tests.operations.test_repo_structure_canon` | PASS. |
| `python -m unittest tests.scripts.test_validate_repo_structure_canon` | PASS. |
| `python scripts/check_architecture_boundaries.py` | PASS, no architecture-boundary violations. |
| `python scripts/check_generated_artifact_cleanliness.py --check --json` | FAIL before commit because the new audit pack is uncommitted `control/audits` drift; rerun after commit is required. |
| `python .aide/scripts/aide_lite.py doctor` | PASS. |
| `python .aide/scripts/aide_lite.py validate` | PASS. |
| `python .aide/scripts/aide_lite.py test` | PASS. |
| `python .aide/scripts/aide_lite.py selftest` | PASS. |
| `python .aide/scripts/aide_lite.py verify` | PASS after the task packet allowed paths were updated for `REPO-LAYOUT-CANON-01`. |
| `python .aide/scripts/aide_lite.py review-pack` | PASS, generated a bounded review packet; generated packet was not retained as source evidence for this layout canon. |

Post-commit checks still required:

- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python .aide/scripts/aide_lite.py commit check --latest`
- `git status --short`
