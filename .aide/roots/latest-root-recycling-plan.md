# Root Recycling Plan

- plan_id: q40-root-recycling-no-apply-plan
- status: dry_run
- source_commit: 6f2698c6e109a3b35d20402bb9871c1e4a674688
- risk_class: high
- no_apply: true
- file_moves: false
- file_deletes: false
- reference_rewrites: false
- target_repo_mutation: false

## Recommended Sequence

- inventory
- classify
- plan
- review
- future_salvage_map
- future_move_map
- future_alias_plan
- future_apply
- future_validate
- future_retire_exception

## Root Plans

- `.aide`: risk=high status=mixed review_files=542
- `.aide.local.example`: risk=high status=review_required review_files=5
- `.github`: risk=high status=review_required review_files=1
- `contracts`: risk=high status=review_required review_files=320
- `control`: risk=high status=mixed review_files=6949
- `crates`: risk=high status=review_required review_files=12
- `data`: risk=high status=review_required review_files=5
- `deploy`: risk=high status=review_required review_files=2
- `docs`: risk=low status=canonical review_files=790
- `evals`: risk=high status=review_required review_files=43
- `examples`: risk=high status=review_required review_files=4537
- `external`: risk=high status=review_required review_files=5
- `native`: risk=high status=mixed review_files=91
- `repo-root`: risk=high status=review_required review_files=8
- `runtime`: risk=high status=mixed review_files=674
- `scripts`: risk=high status=review_required review_files=676
- `site`: risk=high status=review_required review_files=69
- `snapshots`: risk=high status=review_required review_files=14
- `surfaces`: risk=high status=mixed review_files=121
- `tests`: risk=high status=review_required review_files=882

## Blocked Reasons

- .aide: high
- .aide.local.example: high
- .github: high
- contracts: high
- control: high
- crates: high
- data: high
- deploy: high
- evals: high
- examples: high
- external: high
- native: high
- repo-root: high
- runtime: high
- scripts: high
- site: high
- snapshots: high
- surfaces: high
- tests: high

## Boundary

- Q40 plans only. It does not move roots, delete files, rewrite references, absorb tools, or apply maps.
