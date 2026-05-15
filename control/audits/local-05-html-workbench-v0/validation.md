# Validation

Planned LOCAL-05 validation:

- JSON syntax checks for policies, inventories, and audit report
- `python scripts/validate_local_html_workbench.py`
- focused workbench tests
- LOCAL validators from LOCAL-01 through LOCAL-04
- cleanliness and architecture checks
- runtime leakage checks
- full unittest discovery when feasible

Observed LOCAL-05 command results:

- JSON syntax checks: pass
- `python scripts/validate_local_html_workbench.py`: pass with warnings
- focused workbench tests: pass
- LOCAL-03 and LOCAL-04 validators: pass with warnings
- LOCAL-00 through LOCAL-02 validators before commit: fail because LOCAL-05 product paths were still uncommitted
- architecture boundary check: pass
- runtime leakage checks: fail from pre-existing findings
- full unittest discovery: fail_other
