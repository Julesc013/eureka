# Test Selection

Selector commands run:

- `python scripts/eureka_test_select.py --changed --failed-first --json --output control/audits/workbench-result-lanes-closeout-01-v0/generated/selected_tests.json`
- `python scripts/eureka_test_select.py --task WORKBENCH-RESULT-LANES-01 --changed --failed-first --json`
- `python scripts/eureka_test_select.py --promotion --json`

Outcome:

- Changed and failed-first selector mode passed.
- WORKBENCH-RESULT-LANES-01 selected result-lane runtime validators, tests, and smoke commands.
- Promotion selector mode ran and refused promotion because active failure-ledger blockers remain.
- Full discovery remained required for this closeout and was run once.
