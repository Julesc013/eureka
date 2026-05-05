"""Policy checks for the P98 local source cache dry-run runtime."""

from __future__ import annotations

from pathlib import Path
import re
import tempfile
from typing import Any, Iterable, Mapping, Sequence

from runtime.source_cache.errors import SourceCachePolicyError


REPO_ROOT = Path(__file__).resolve().parents[2]
DRY_RUN_EXAMPLES_ROOT = REPO_ROOT / "examples" / "source_cache" / "dry_run"
SOURCE_CACHE_EXAMPLES_ROOT = REPO_ROOT / "examples" / "source_cache"
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "source-cache-local-dry-run-runtime-v0"

SOURCE_FAMILIES = {
    "internet_archive",
    "wayback_cdx_memento",
    "github_releases",
    "pypi",
    "npm",
    "software_heritage",
    "local_fixture",
    "unknown",
}
LEGACY_SOURCE_FAMILY_ALIASES = {
    "wayback": "wayback_cdx_memento",
    "recorded_fixture": "local_fixture",
}
RECORD_KINDS = {
    "metadata_summary",
    "availability_summary",
    "capture_metadata_summary",
    "release_metadata_summary",
    "package_metadata_summary",
    "software_identity_summary",
    "unknown",
}
LEGACY_RECORD_KIND_ALIASES = {
    "source_metadata": "metadata_summary",
    "source_availability": "availability_summary",
    "wayback_capture_metadata": "capture_metadata_summary",
    "release_metadata": "release_metadata_summary",
    "package_metadata": "package_metadata_summary",
    "source_identifier_metadata": "software_identity_summary",
    "recorded_fixture_metadata": "metadata_summary",
    "fixture_metadata": "metadata_summary",
}
PRIVACY_STATUSES = {"public_safe", "redacted", "local_private", "rejected_sensitive", "unknown"}
PRIVACY_ALIASES = {
    "public_safe_example": "public_safe",
    "public_safe_metadata": "public_safe",
}
PUBLIC_SAFETY_STATUSES = {"public_safe", "review_required", "rejected", "unknown"}
EVIDENCE_READINESS = {
    "evidence_candidate_ready",
    "evidence_review_required",
    "insufficient",
    "not_applicable",
    "unknown",
}
POLICY_STATUSES = {
    "approved_example",
    "approval_required",
    "operator_required",
    "blocked_by_policy",
    "unknown",
}

FORBIDDEN_CLI_FIELDS = {
    "--url",
    "--live-source",
    "--source-url",
    "--connector",
    "--store-root",
    "--index-path",
    "--database",
    "--write-authoritative",
    "--mutate",
    "--publish",
    "--promote",
}

FORBIDDEN_RECORD_KEYS = {
    "url",
    "source_url",
    "live_source",
    "connector",
    "store_root",
    "index_path",
    "database",
    "source_cache_path",
    "evidence_ledger_path",
    "candidate_path",
    "promotion_path",
    "local_path",
    "filesystem_root",
    "api_key",
    "auth_token",
    "password",
    "secret",
}

HARD_TRUE_FIELDS = {"local_dry_run"}
HARD_FALSE_FIELDS = {
    "live_source_called",
    "external_calls_performed",
    "connector_runtime_executed",
    "source_sync_worker_executed",
    "authoritative_source_cache_written",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "public_search_runtime_mutated",
    "telemetry_exported",
    "credentials_used",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
}
HARD_BOOLEANS: dict[str, bool] = {"local_dry_run": True, **{key: False for key in sorted(HARD_FALSE_FIELDS)}}

MUTATION_SUMMARY = {
    "authoritative_source_cache_written": False,
    "source_cache_mutated": False,
    "evidence_ledger_mutated": False,
    "candidate_index_mutated": False,
    "public_index_mutated": False,
    "local_index_mutated": False,
    "master_index_mutated": False,
    "public_search_runtime_mutated": False,
}

URL_PATTERN = re.compile(r"\b(?:https?|ftp)://", re.IGNORECASE)
PRIVATE_PATH_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("windows_absolute_path", re.compile(r"\b[A-Za-z]:[\\/]", re.IGNORECASE)),
    ("posix_private_path", re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE)),
    ("path_traversal", re.compile(r"(^|[\\/])\.\.([\\/]|$)")),
)
SENSITIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("api_key_marker", re.compile(r"\b(?:api[_-]?key|auth[_-]?token|private[_-]?key)\b", re.IGNORECASE)),
    ("secret_marker", re.compile(r"\b(?:password|secret|credential)\s*[:=]", re.IGNORECASE)),
    ("ip_address", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")),
    ("account_identifier", re.compile(r"\b(?:account[_ -]?id|user[_ -]?id|session[_ -]?id)\s*[:=]", re.IGNORECASE)),
    ("email_address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
)


def repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(resolved)


def is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for nested in value.values():
            yield from iter_strings(nested)
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        for nested in value:
            yield from iter_strings(nested)


def iter_keys(value: Any) -> Iterable[str]:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            yield str(key)
            yield from iter_keys(nested)
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        for nested in value:
            yield from iter_keys(nested)


def detect_forbidden_cli_args(argv: Sequence[str]) -> list[str]:
    return sorted({item.split("=", 1)[0] for item in argv if item.split("=", 1)[0] in FORBIDDEN_CLI_FIELDS})


def assert_no_forbidden_cli_args(argv: Sequence[str]) -> None:
    forbidden = detect_forbidden_cli_args(argv)
    if forbidden:
        raise SourceCachePolicyError(f"forbidden dry-run argument(s): {', '.join(forbidden)}")


def ensure_approved_input_root(path: Path, *, allow_temp: bool = False) -> Path:
    resolved = path.resolve()
    if is_relative_to(resolved, SOURCE_CACHE_EXAMPLES_ROOT):
        return resolved
    if allow_temp and is_relative_to(resolved, Path(tempfile.gettempdir())):
        return resolved
    raise SourceCachePolicyError(f"input root is not approved for source-cache dry-run: {path}")


def ensure_approved_output_path(path: Path) -> Path:
    resolved = path.resolve()
    if is_relative_to(resolved, AUDIT_ROOT) or is_relative_to(resolved, Path(tempfile.gettempdir())):
        return resolved
    raise SourceCachePolicyError(f"output path is not approved for source-cache dry-run reports: {path}")


def scan_candidate_policy(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in iter_keys(record):
        if key in FORBIDDEN_RECORD_KEYS:
            errors.append(f"forbidden field present: {key}")
    for value in iter_strings(record):
        if URL_PATTERN.search(value):
            errors.append("URL-like value is not allowed in dry-run source-cache candidates")
        for label, pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(value):
                errors.append(f"private or unsafe path detected: {label}")
        for label, pattern in SENSITIVE_PATTERNS:
            if pattern.search(value):
                errors.append(f"sensitive value detected: {label}")
    return sorted(set(errors))


def normalize_enum(value: Any, allowed: set[str], aliases: Mapping[str, str] | None = None) -> str:
    if isinstance(value, str):
        normalized = aliases.get(value, value) if aliases else value
        if normalized in allowed:
            return normalized
    return "unknown"


def assert_mutation_disabled(report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    hard = report.get("hard_booleans", {})
    if not isinstance(hard, Mapping):
        return ["hard_booleans must be an object"]
    for key in HARD_TRUE_FIELDS:
        if hard.get(key) is not True:
            errors.append(f"hard_booleans.{key} must be true")
    for key in HARD_FALSE_FIELDS:
        if hard.get(key) is not False:
            errors.append(f"hard_booleans.{key} must be false")
    return errors
