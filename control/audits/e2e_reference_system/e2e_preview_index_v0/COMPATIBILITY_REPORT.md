# Compatibility Report

Existing local search index behavior remains available as `--index local`.

New behavior:

- `scripts/eureka_index.py preview-build`
- `scripts/eureka_index.py preview-validate`
- `scripts/eureka_index.py preview-stats`
- `scripts/eureka_index.py preview-search`
- `scripts/eureka_index.py preview-list-generations`
- `scripts/eureka_index.py preview-compare`
- `scripts/eureka_index.py preview-rollback`
- `scripts/eureka_search.py --index preview`

The existing local search response shape is extended with preview authority and
ranking fields but retains no-mutation and non-verified result flags.
