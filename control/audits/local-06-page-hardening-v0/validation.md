# Validation

Planned validation lane:

- `git status --short`
- `git diff --check`
- JSON syntax checks for LOCAL-06 policies, inventories, and report
- `python scripts/validate_local_workbench_page_hardening.py`
- `python scripts/validate_local_html_workbench.py`
- manual loopback smoke with ignored local instance
- focused workbench hardening tests
- LOCAL validators
- generated artifact, architecture, and leakage checks
- full unittest discovery if feasible

Final command results are recorded in the commit body and final task response.

Post-commit notes:

- Older LOCAL validators pass or warn only on the pre-existing leakage gate.
- Full unittest discovery ran on a clean tree and failed with pre-existing/non-LOCAL-06 issues: public search index checksum drift, IA readiness task-packet expectations, and the runtime leakage gate.
