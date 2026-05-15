# Validation

LOCAL-13 validation results:

- `git diff --check`: pass.
- JSON parsing for LOCAL-13 policies, inventories, and report: pass.
- `python scripts/eureka_clean_machine_bootstrap.py --repo . --json`: pass with warnings when ignored local instance state is present and skipped.
- `python scripts/eureka_clean_machine_smoke.py --repo . --instance ./eureka-instance --json`: pass.
- `python scripts/eureka_clean_machine_report.py ...`: pass with warnings because actual second-machine proof was not performed.
- `python scripts/validate_clean_machine_bootstrap.py`: pass with warnings for existing leakage.
- Focused LOCAL-13 tests: pass.
- `python scripts/check_architecture_boundaries.py`: pass.
- `python scripts/check_generated_artifact_cleanliness.py --check --json`: fails before commit because the LOCAL-13 audit pack is untracked; this is expected to pass after commit.
- LOCAL validators: current LOCAL-13 validator passes with warnings; older LOCAL validators that assert previous queue pointers fail after the queue advances to LOCAL-14.
- Runtime leakage checks: fail on the pre-existing leakage baseline; LOCAL-13 did not increase leakage.
- Full discovery: fail_other after historical discovery-lane output and runtime leakage findings.

No deployment, production readiness, or public launch readiness is claimed.
