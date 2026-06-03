# Validation Matrix

## Planning Package Checks

| Check | Status |
| --- | --- |
| Required files created | planned in `build_reports/VALIDATION_REPORT.md` |
| Runtime behavior added | must remain no |
| Protected paths modified | must remain no, except AIDE context refreshed by pack |
| Archive claim promoted | must remain no |
| Public scope explicit | yes |
| Non-goals explicit | yes |
| Queue DAG present | yes |
| Task handoffs present | yes |

## Future Implementation Checks

| Area | Required validation |
| --- | --- |
| semantic contracts | existing TSIS validators and focused contract tests |
| resolver run mode | `test_resolution_run_kernel` plus fallback path tests |
| source observation | source observation policy and validation tests |
| review gate | review queue, review batch, promotion preview tests |
| public projection | public search/API read-only and route safety tests |
| renderer parity | representation and semantic renderer parity validators |
| operations | public alpha hosting/readiness/rollback validators |

Full unittest discovery remains external/CI by repo policy.

