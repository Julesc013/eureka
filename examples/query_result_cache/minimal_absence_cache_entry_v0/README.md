# Minimal Absence Cache Entry v0

This synthetic example shows a scoped no-hit outcome for
`no-such-local-index-hit`. It is not a global absence claim and it does not
write a miss ledger, search need, probe, candidate index, local index, or
master index.

Validate it with:

```bash
python scripts/validate_search_result_cache_entry.py --entry-root examples/query_result_cache/minimal_absence_cache_entry_v0
```
