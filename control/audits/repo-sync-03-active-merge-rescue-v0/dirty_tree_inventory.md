# Dirty Tree Inventory

- Branch before rescue: `main`
- Safety branch: `sync/preserve-dirty-work-20260509`
- Local HEAD before rescue: `2f63e190964d19bd7f7d6c9130e716ecbd61b6ac`
- Origin main observed: `f83b005dcd68bc9710bccefe8d788b64c5fce461`
- Merge head before rescue: `6c852097ec812ddd2c8584dbff5b847bdebd94c5`
- Preservation commit: `03355592851ae643c33ec8d29ff3ca5b6b61b984`

## Counts Before Preservation

- Staged paths: `317`
- Unstaged paths: `3`
- Untracked paths: `0`
- Unmerged entries: `0`

## Classification

- `aide_context_or_eval`: `.aide/context/*`, `.aide/evals/runs/*`
- `obs_side_lane`: OBS audit packs, observation inventories, observation examples,
  observation scripts, and observation tests
- `track_b_source_cache`: source cache runtime, policies, docs, examples, tests
- `track_b_evidence_ledger`: evidence ledger runtime, policies, docs, examples, tests
- `b23_or_later`: Track B integration audit and pack/export/promotion/review spine work
- `runtime_or_tests`: `runtime/local/foundry/`, `scripts/`, and `tests/`
- `docs_or_ops`: `docs/reference/`, `docs/architecture/`, and `docs/operations/`

## Risk Flags

No obvious risky path names were detected. No `.aide.local`, `.local/eureka`,
`.cache/eureka`, secret, credential, token, raw prompt, private key, downloaded
binary, or local cache path was present in the dirty path list.
