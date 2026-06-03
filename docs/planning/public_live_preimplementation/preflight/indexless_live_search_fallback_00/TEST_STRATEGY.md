# Test Strategy

Run focused tests only. Full unittest discovery remains out of scope for normal
AI sessions.

| Test | Likely test file | Fixture needed | Behavior under test | Expected assertion | Blocking status |
| --- | --- | --- | --- | --- | --- |
| Local reviewed/result path unchanged | `runtime/engine/resolution_runs/tests/test_service.py` | existing demo catalog | deterministic search with results | run has existing `result_summary`, no fallback lane/source call | blocking |
| Index/local unavailable creates fallback candidate or need | new or same file | fake search service with no results; fake fallback provider | local miss triggers fallback eligibility | run contains candidate or need state, not verified | blocking |
| Local insufficient creates fallback candidate or need | new engine run test | fake weak/insufficient local response if supported | insufficient threshold | fallback activates only by policy | nonblocking unless implemented |
| Fallback disabled returns degraded state | `runtime/engine/resolution_runs/tests/test_service.py` | fallback policy disabled | no source call | `policy_blocked`, `unavailable`, or `need` notice; provider not called | blocking |
| Source disabled returns degraded state | same | source allowlist excludes provider | source family gate | provider not called, source disabled notice | blocking |
| Source timeout returns degraded state | same plus provider fake | fake timeout/exception | failure handling | run completed/failed honestly with unavailable/unknown state, no truth | blocking |
| Budget exceeded returns degraded state | same plus provider fake | fake budget cap | budget enforcement | no excess calls, budget notice | blocking |
| Candidate is not verified | same plus public projection test | fake candidate | truth boundary | `accepted_truth=false`, `review_required=true`, no `verified` status | blocking |
| Fallback does not write reviewed truth | same plus mocks | fake stores or assert untouched | review/index boundary | no reviewed/public/master index mutation | blocking |
| Public route does not expose operator-only actions | `runtime/gateway/tests/test_public_search_api.py` or new public run projection test | fallback candidate envelope | action policy | promote/reject/rebuild_index absent/blocked; review_candidate not allowed | blocking |
| Public UI does not directly call sources | public API or surface test | fake provider counting calls | routing boundary | public route uses run/projection or provider count remains zero in surface | blocking |
| Run events/logging emitted if event model supports it | engine run test | event-enabled run config | observability | notices/events include local miss, policy, fallback outcome | nonblocking if notices used first |

## Validation Lanes

Recommended focused commands for implementation:

```text
py -3 -m unittest runtime.engine.resolution_runs.tests.test_service
py -3 -m unittest runtime.gateway.tests.test_public_search_api
py -3 -m unittest tests.runtime.test_archive_org_public_metadata_candidates
py -3 -m unittest tests.runtime.test_source_action_policy
```

Use `scripts/eureka_test_select.py --changed --failed-first --json` if the
repo selector indicates a narrower lane after code changes.
