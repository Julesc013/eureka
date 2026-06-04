# Validation Report

Task ID: `REVIEWED-CORPUS-SEED-BATCH-01`.

Status: `PASS_WITH_WARNINGS`.

The warning is the expected corpus gate warning: public alpha remains blocked by
insufficient reviewed corpus breadth.

Expected focused tests:

```text
py -3 -m unittest tests.evals.test_reviewed_corpus_seed_batch_01 tests.evals.test_reviewed_corpus_public_alpha_gate tests.runtime.test_surface_reviewed_corpus_seed_projection
```

Result:

```text
Ran 18 tests
OK
```

Adjacent eval/surface lane:

```text
py -3 -m unittest tests.evals.test_reviewed_corpus_seed_batch_01 tests.evals.test_reviewed_corpus_public_alpha_gate tests.runtime.test_surface_reviewed_corpus_seed_projection tests.evals.test_human_review_batch tests.evals.test_human_review_corpus_gate tests.runtime.test_surface_human_review_projection tests.evals.test_manual_observation_batch tests.evals.test_manual_observation_review_backlog tests.runtime.test_surface_manual_observation_projection tests.evals.test_reviewed_seed_corpus tests.runtime.test_surface_seed_corpus_projection tests.evals.test_hard_query_eval tests.runtime.test_surface_hard_query_eval tests.runtime.test_surface_baseline_renderers
```

Result:

```text
Ran 86 tests
OK
```

Required validation:

```text
git diff --check
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
py -3 scripts/eureka_test_select.py --changed --failed-first --json
```

Results:

| Command | Result |
|---|---|
| `git diff --check` | PASS; LF-to-CRLF warning for refreshed `.aide/context/latest-task-packet.md` |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS |
| `py -3 scripts/eureka_test_select.py --changed --failed-first --json` | PASS; full discovery not required |
| `python scripts/check_architecture_boundaries.py` | PASS |
| `python scripts/check_generated_artifact_cleanliness.py --check --json` | PASS |
| `python scripts/validate_test_lane_policy.py` | PASS |
| `python -m unittest tests.operations.test_test_lane_policy tests.scripts.test_eureka_test_select tests.scripts.test_validate_test_lane_policy` | PASS; 6 tests |

Full unittest discovery was not run inside the AI session because the selector did not require it.

## Boundary Checks

Protected paths modified: none.

Queue state modified: none.

Runtime behavior changed: no.

Product runtime source calls added: no.

Downloads, file fetches, and Wayback replay added: no.

Reviewed/public/master index mutation added: no.

Reviewed seed records consolidated as eval fixtures: 2.
