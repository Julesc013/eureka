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

__all__ = [
    "SourceCacheCandidateSummary",
    "SourceCacheDryRunError",
    "SourceCacheDryRunReport",
    "classify_candidate",
    "discover_candidates",
    "load_candidate",
    "run_source_cache_dry_run",
    "validate_candidate_shape",
]
