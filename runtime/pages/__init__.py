"""Local dry-run page rendering runtime for approved examples only."""

from runtime.pages.dry_run import (
    classify_page,
    discover_pages,
    load_page,
    run_page_dry_run,
    validate_page_shape,
)

__all__ = [
    "classify_page",
    "discover_pages",
    "load_page",
    "run_page_dry_run",
    "validate_page_shape",
]
