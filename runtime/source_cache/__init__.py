"""Local dry-run source cache helpers.

P98 implements a bounded local dry-run only. It does not call live sources,
execute connectors, or write authoritative source-cache state.
"""

from runtime.source_cache.dry_run import (
    classify_candidate,
    discover_candidates,
    load_candidate,
    run_source_cache_dry_run,
    validate_candidate_shape,
)
from runtime.source_cache.models import (
    SourceCacheCandidateSummary,
    SourceCacheDryRunError,
    SourceCacheDryRunReport,
)
from runtime.source_cache.records import (
    SourceCacheEntry,
    SourceCacheRead,
    SourceCacheStatus,
    SourceCacheSummary,
    SourceCacheWrite,
)
from runtime.source_cache.store import SourceCacheStore, build_cache_entry

__all__ = [
    "SourceCacheCandidateSummary",
    "SourceCacheDryRunError",
    "SourceCacheDryRunReport",
    "SourceCacheEntry",
    "SourceCacheRead",
    "SourceCacheStatus",
    "SourceCacheStore",
    "SourceCacheSummary",
    "SourceCacheWrite",
    "build_cache_entry",
    "classify_candidate",
    "discover_candidates",
    "load_candidate",
    "run_source_cache_dry_run",
    "validate_candidate_shape",
]
