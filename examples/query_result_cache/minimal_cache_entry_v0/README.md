# Minimal Search Result Cache Entry v0

This example is synthetic and public-safe. It shows how a future shared
query/result cache entry may summarize `windows 7 apps` results from the
controlled public index without retaining raw query text, storing user
identifiers, writing telemetry, mutating indexes, or treating the cache as
truth.

Validate it with:

```bash
python scripts/validate_search_result_cache_entry.py --entry-root examples/query_result_cache/minimal_cache_entry_v0
```
