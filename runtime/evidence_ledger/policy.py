"""Policy checks for the P99 local evidence-ledger dry-run runtime."""

from __future__ import annotations

from pathlib import Path
import re
import tempfile
from typing import Any, Iterable, Mapping, Sequence

from runtime.evidence_ledger.errors import EvidenceLedgerPolicyError


REPO_ROOT = Path(__file__).resolve().parents[2]
DRY_RUN_EXAMPLES_ROOT = REPO_ROOT / "examples" / "evidence_ledger" / "dry_run"
EVIDENCE_LEDGER_EXAMPLES_ROOT = REPO_ROOT / "examples" / "evidence_ledger"
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "evidence-ledger-local-dry-run-runtime-v0"

EVIDENCE_KINDS = {
    "source_metadata_observation",
    "availability_observation",
    "capture_presence_observation",
    "capture_absence_observation",
    "release_metadata_observation",
    "package_metadata_observation",
    "software_identity_observation",
    "compatibility_observation",
    "file_listing_observation",
    "scoped_absence_observation",
    "conflict_observation",
    "unknown",
}
LEGACY_EVIDENCE_KIND_ALIASES = {
    "absence_observation": "scoped_absence_observation",
    "member_listing_observation": "file_listing_observation",
    "fixture_observation": "source_metadata_observation",
}
CLAIM_KINDS = {
    "metadata_claim",
    "availability_claim",
    "identity_claim",
    "version_claim",
    "compatibility_claim",
    "source_presence_claim",
    "scoped_absence_claim",
    "conflict_claim",
    "unknown",
}
LEGACY_CLAIM_KIND_ALIASES = {
    "describes": "metadata_claim",
    "has_version": "version_claim",
    "supports_platform": "compatibility_claim",
    "does_not_support_platform": "compatibility_claim",
    "compatibility_claim": "compatibility_claim",
    "contains_member": "metadata_claim",
    "has_checksum": "metadata_claim",
    "source_available": "source_presence_claim",
    "source_unavailable": "scoped_absence_claim",
    "source_matches_query": "source_presence_claim",
    "scoped_absence": "scoped_absence_claim",
    "release_metadata": "version_claim",
    "package_metadata": "metadata_claim",
}
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
PROVENANCE_STATUSES = {
    "synthetic_example",
    "fixture_backed",
    "recorded_fixture_backed",
    "source_cache_candidate",
    "source_cache_future",
    "manual_observation_future",
    "unknown",
}
LEGACY_PROVENANCE_ALIASES = {
    "fixture_example": "fixture_backed",
    "recorded_fixture": "recorded_fixture_backed",
    "source_cache_record": "source_cache_future",
    "manual_observation": "manual_observation_future",
}
REVIEW_STATUSES = {
    "structurally_valid",
    "review_required",
    "policy_review_required",
    "conflict_review_required",
    "rejected",
    "unknown",
}
LEGACY_REVIEW_STATUS_ALIASES = {
    "unreviewed": "review_required",
    "evidence_required": "review_required",
    "human_review_required": "review_required",
    "rights_review_required": "policy_review_required",
    "risk_review_required": "policy_review_required",
    "rejected_future": "rejected",
}
PRIVACY_STATUSES = {"public_safe", "redacted", "local_private", "rejected_sensitive", "unknown"}
PRIVACY_ALIASES = {
    "public_safe_example": "public_safe",
    "public_safe_metadata": "public_safe",
}
PUBLIC_SAFETY_STATUSES = {"public_safe", "review_required", "rejected", "unknown"}
RIGHTS_RISK_STATUSES = {
    "metadata_only",
    "source_terms_apply",
    "review_required",
    "executable_reference",
    "malware_review_required",
    "restricted",
    "unknown",
}
PROMOTION_READINESS = {
    "not_ready",
    "review_required",
    "candidate_ready_future",
    "rejected",
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
    "--accept-truth",
    "--accept-evidence",
}

FORBIDDEN_RECORD_KEYS = {
    "url",
    "source_url",
    "live_source",
    "connector",
    "store_root",
    "index_path",
    "database",
    "evidence_ledger_path",
    "source_cache_path",
    "source_sync_path",
    "candidate_path",
    "promotion_path",
    "local_path",
    "filesystem_root",
    "api_key",
    "auth_token",
    "password",
    "secret",
}
TRUTH_ACCEPTANCE_KEYS = {
    "accepted_as_truth",
    "claim_accepted_as_truth",
    "truth_accepted",
    "accepted_evidence_now",
}
PROMOTION_KEYS = {
    "promotion_decision",
    "promotion_decision_created",
    "candidate_promotion_performed",
    "promoted",
    "accepted_record_created",
}

HARD_TRUE_FIELDS = {"local_dry_run"}
HARD_FALSE_FIELDS = {
    "live_source_called",
    "external_calls_performed",
    "connector_runtime_executed",
    "source_sync_worker_executed",
    "authoritative_evidence_ledger_written",
    "evidence_ledger_mutated",
    "source_cache_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "public_search_runtime_mutated",
    "claim_accepted_as_truth",
    "promotion_decision_created",
    "telemetry_exported",
    "credentials_used",
    "downloads_enabled",
    "installs_enabled",
    "execution_enabled",
}
HARD_BOOLEANS: dict[str, bool] = {"local_dry_run": True, **{key: False for key in sorted(HARD_FALSE_FIELDS)}}

MUTATION_SUMMARY = {
    "authoritative_evidence_ledger_written": False,
    "evidence_ledger_mutated": False,
    "source_cache_mutated": False,
    "candidate_index_mutated": False,
    "public_index_mutated": False,
    "local_index_mutated": False,
    "master_index_mutated": False,
    "public_search_runtime_mutated": False,
    "claim_accepted_as_truth": False,
    "promotion_decision_created": False,
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


def iter_items(value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            yield str(key), nested
            yield from iter_items(nested)
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        for nested in value:
            yield from iter_items(nested)


def iter_keys(value: Any) -> Iterable[str]:
    for key, _ in iter_items(value):
        yield key


def detect_forbidden_cli_args(argv: Sequence[str]) -> list[str]:
    return sorted({item.split("=", 1)[0] for item in argv if item.split("=", 1)[0] in FORBIDDEN_CLI_FIELDS})


def assert_no_forbidden_cli_args(argv: Sequence[str]) -> None:
    forbidden = detect_forbidden_cli_args(argv)
    if forbidden:
        raise EvidenceLedgerPolicyError(f"forbidden dry-run argument(s): {', '.join(forbidden)}")


def ensure_approved_input_root(path: Path, *, allow_temp: bool = False) -> Path:
    resolved = path.resolve()
    if is_relative_to(resolved, EVIDENCE_LEDGER_EXAMPLES_ROOT):
        return resolved
    if allow_temp and is_relative_to(resolved, Path(tempfile.gettempdir())):
        return resolved
    raise EvidenceLedgerPolicyError(f"input root is not approved for evidence-ledger dry-run: {path}")


def ensure_approved_output_path(path: Path) -> Path:
    resolved = path.resolve()
    if is_relative_to(resolved, AUDIT_ROOT) or is_relative_to(resolved, Path(tempfile.gettempdir())):
        return resolved
    raise EvidenceLedgerPolicyError(f"output path is not approved for evidence-ledger dry-run reports: {path}")


def scan_candidate_policy(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, value in iter_items(record):
        if key in FORBIDDEN_RECORD_KEYS:
            errors.append(f"forbidden field present: {key}")
        if key in TRUTH_ACCEPTANCE_KEYS and value is not False:
            errors.append(f"truth acceptance field must be false: {key}")
        if key in PROMOTION_KEYS and value not in (False, None, "", [], {}):
            errors.append(f"promotion decision field must be absent or false: {key}")
        if key in {"status", "review_status", "claim_status"} and isinstance(value, str) and "promoted" in value:
            errors.append(f"promotion status is not allowed in dry-run evidence candidates: {key}")
    for value in iter_strings(record):
        if URL_PATTERN.search(value):
            errors.append("URL-like value is not allowed in dry-run evidence-ledger candidates")
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
