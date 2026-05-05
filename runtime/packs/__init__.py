"""Local dry-run pack import runtime package.

P104 exposes only local dry-run loading, classification, validator reference,
and report generation helpers for approved repo examples. It does not import,
stage, quarantine, execute, upload, promote, fetch URLs, or mutate source,
evidence, candidate, public, local, or master indexes.
"""

from runtime.packs.dry_run import run_pack_import_dry_run

__all__ = ["run_pack_import_dry_run"]
