# IA Review Promotion Dry-Run

IA-06 writes Internet Archive metadata candidates into a local review queue and
builds promotion previews only.

## Scope

Allowed inputs:

- IA fixture candidate-index records
- IA live-preview candidate-index records
- deterministic test candidates

Allowed mutations:

- review queue items in an explicit temporary or local instance
- review decisions in an explicit temporary or local instance

Forbidden mutations:

- reviewed index
- master index
- public index
- accepted truth
- raw IA response bodies
- downloads, uploads, extraction, provider calls, or deployment

## Review Queue

Dry-run is the default:

```powershell
python scripts/eureka_ia_review_queue.py --instance ..\instances\default --from-candidate-index --decision approve_for_reviewed_index_dry_run --dry-run --json
```

Apply requires a temp or explicit local instance plus an operator token:

```powershell
python scripts/eureka_ia_review_queue.py --instance <temp-instance> --operator-token local-dev-token --from-candidate-index --decision approve_for_reviewed_index_dry_run --apply --json
```

Use temporary instances for proof. Do not use `..\instances\default` for apply
unless an operator explicitly asks for that instance to be mutated.

## Promotion Dry-Run

Promotion creates reviewed-record previews only:

```powershell
python scripts/eureka_ia_promotion_dry_run.py --from-review-decisions --from-review-report <review-report.json> --json
```

`approve_for_reviewed_index_dry_run` may create a preview. All other decisions
remain queue classifications and do not create previews.

## Validation

```powershell
python scripts/validate_ia_review_promotion_dry_run.py
python -m unittest tests.runtime.test_ia_review_queue_integration
python -m unittest tests.runtime.test_ia_review_decisions
python -m unittest tests.runtime.test_ia_promotion_dry_run
python -m unittest tests.runtime.test_ia_promotion_boundaries
python -m unittest tests.operations.test_ia_review_promotion_scripts
```

IA-07 is the next gate for reviewed local index rebuild work. IA-06 does not
start that work.

