# Latest Root Inventory

- generated_by: aide-lite
- source_commit: 6f2698c6e109a3b35d20402bb9871c1e4a674688
- source_mode: repo_intelligence_index_plus_tracked_delta
- file_count: 16297
- root_count: 20
- no_apply: true
- file_moves: false
- file_deletes: false
- reference_rewrites: false
- provider_or_model_calls: none
- network_calls: none
- next_phase: Q41 Existing Tool Absorption v0

## Root Status Counts

- canonical: 1
- mixed: 5
- review_required: 14

## Root Risk Counts

- high: 19
- low: 1

## Roots

- `.aide`: files=540 status=mixed risk=high
- `.aide.local.example`: files=5 status=review_required risk=high
- `.github`: files=1 status=review_required risk=high
- `contracts`: files=320 status=review_required risk=high
- `control`: files=6949 status=mixed risk=high
- `crates`: files=12 status=review_required risk=high
- `data`: files=5 status=review_required risk=high
- `deploy`: files=2 status=review_required risk=high
- `docs`: files=1343 status=canonical risk=low
- `evals`: files=43 status=review_required risk=high
- `examples`: files=4537 status=review_required risk=high
- `external`: files=5 status=review_required risk=high
- `native`: files=91 status=mixed risk=high
- `repo-root`: files=8 status=review_required risk=high
- `runtime`: files=674 status=mixed risk=high
- `scripts`: files=676 status=review_required risk=high
- `site`: files=69 status=review_required risk=high
- `snapshots`: files=14 status=review_required risk=high
- `surfaces`: files=121 status=mixed risk=high
- `tests`: files=882 status=review_required risk=high

## Warnings

- unknown_or_unknown-owner_root_candidates: .aide, .aide.local.example, .github, contracts, control, crates, data, deploy, docs, evals, examples, external
- mixed_root_candidates: .aide, control, native, runtime, surfaces
- high_risk_root_candidates: .aide, .aide.local.example, .github, contracts, control, crates, data, deploy, evals, examples, external, native
