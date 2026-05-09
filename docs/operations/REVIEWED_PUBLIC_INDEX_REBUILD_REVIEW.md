# Reviewed Public Index Rebuild Review

B20 review is contract review, not publication review.

Before a future public-index rebuild runtime can exist, reviewers must confirm:

- candidate promotion dry-run records are reviewed and evidence-backed
- evidence summaries preserve source and provenance refs
- source policy, rights, risk, compatibility, and identity posture are explicit
- missing evidence blocks or defers readiness
- unresolved conflicts and duplicate uncertainty are preserved
- public search effects are previews only
- public-index and master-index mutation remain disabled until a later approved task

## Forbidden Current Outcomes

Current B20 artifacts cannot:

- mutate public-index or master-index files
- accept candidates or evidence
- create current public truth
- write `site/dist/` or `data/public_index/`
- claim rights clearance, malware safety, verified installability, exhaustive search, or production readiness
- enable hosted review, source access, source sync, downloads, uploads, accounts, telemetry, or provider calls

## Validation

Run:

```bash
git diff --check
python scripts/validate_reviewed_public_index_rebuild_contract.py
python -m unittest tests.contracts.test_reviewed_public_index_rebuild_contract
python scripts/check_architecture_boundaries.py
```
