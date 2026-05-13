# Validation

Validation commands are recorded in the final task report. The LOCAL-07 validator,
focused tests, local validators, cleanliness checks, and architecture/leakage checks
were run where feasible.

Key results:

- LOCAL-07 validator: pass_with_warnings
- focused WorkUnit queue tests: pass
- local workbench/http/runtime validators: pass_with_warnings
- legacy LOCAL-01/02/track validators: fail on older task-packet expectations and
  dirty-tree checks
- architecture boundaries: pass
- runtime leakage gate: fail with 1030 pre-existing new unallowlisted production
  findings before and after LOCAL-07
- full unittest discovery: fail_other
