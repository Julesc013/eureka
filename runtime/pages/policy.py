"""Policy checks for the P103 local page dry-run runtime."""

from __future__ import annotations

from pathlib import Path
import re
import tempfile
from typing import Any, Iterable, Mapping, Sequence

from runtime.pages.errors import PagePolicyError


REPO_ROOT = Path(__file__).resolve().parents[2]
OBJECT_PAGE_EXAMPLES_ROOT = REPO_ROOT / "examples" / "object_pages"
SOURCE_PAGE_EXAMPLES_ROOT = REPO_ROOT / "examples" / "source_pages"
COMPARISON_PAGE_EXAMPLES_ROOT = REPO_ROOT / "examples" / "comparison_pages"
PAGE_DRY_RUN_EXAMPLES_ROOT = REPO_ROOT / "examples" / "page_runtime_dry_run"
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "object-source-comparison-page-local-dry-run-runtime-v0"

APPROVED_EXAMPLE_ROOTS = (
    OBJECT_PAGE_EXAMPLES_ROOT,
    SOURCE_PAGE_EXAMPLES_ROOT,
    COMPARISON_PAGE_EXAMPLES_ROOT,
    PAGE_DRY_RUN_EXAMPLES_ROOT,
)

PAGE_KINDS = {"object_page", "source_page", "comparison_page", "unknown"}
PAGE_STATUSES = {
    "synthetic_example",
    "public_safe_example",
    "fixture_backed",
    "candidate",
    "review_required",
    "conflicted",
    "placeholder",
    "future",
    "unknown",
}
LANES = {"official", "preservation", "community", "candidate", "absence", "conflicted", "demo", "unknown"}
PRIVACY_STATUSES = {"public_safe", "redacted", "local_private", "rejected_sensitive", "unknown"}
PUBLIC_SAFETY_STATUSES = {"public_safe", "review_required", "rejected", "unknown"}
ACTION_STATUSES = {
    "inspect_only",
    "compare_only",
    "cite_only",
    "risky_actions_disabled",
    "unsafe_action_claim_detected",
    "unknown",
}
CONFLICT_GAP_STATUSES = {
    "no_known_conflict_or_gap",
    "conflict_present",
    "gap_present",
    "conflict_and_gap_present",
    "unknown",
}

FORBIDDEN_CLI_FIELDS = {
    "--url",
    "--live-source",
    "--source-url",
    "--connector",
    "--source-cache-path",
    "--evidence-ledger-path",
    "--candidate-path",
    "--store-root",
    "--index-path",
    "--database",
    "--serve",
    "--route",
    "--hosted",
    "--write-public",
    "--mutate",
    "--publish",
    "--promote",
    "--download",
    "--install",
    "--execute",
}

FORBIDDEN_RECORD_KEYS = {
    "url",
    "source_url",
    "live_source",
    "connector_param",
    "source_cache_path",
    "evidence_ledger_path",
    "candidate_path",
    "promotion_path",
    "store_root",
    "index_path",
    "database",
    "local_path",
    "filesystem_root",
    "page_path",
    "object_page_path",
    "source_page_path",
    "comparison_page_path",
}

RAW_PAYLOAD_KEYS = {
    "raw_payload",
    "payload_dump",
    "binary_payload",
    "base64_payload",
    "raw_content",
    "file_bytes",
    "executable_payload",
    "raw_private_query",
}
SECRET_KEY_PARTS = ("api_key", "auth_token", "password", "secret", "credential", "token")
RISKY_ACTION_WORDS = {
    "download",
    "install",
    "execute",
    "upload",
    "mirror",
    "arbitrary_url_fetch",
    "package_manager",
    "emulator",
    "vm",
}
SAFE_ACTION_WORDS = {
    "inspect",
    "inspect_metadata",
    "inspect_source_metadata",
    "view_metadata",
    "view_sources",
    "view_evidence",
    "view_related_results",
    "view_source_limitations",
    "compare",
    "cite",
    "cite_source_page",
}

URL_PATTERN = re.compile(r"\b(?:https?|ftp)://|(?<![A-Za-z])(?:file|data|javascript):", re.IGNORECASE)
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

HARD_TRUE_FIELDS = {"local_dry_run"}
HARD_FALSE_FIELDS = {
    "hosted_runtime_enabled",
    "public_routes_added",
    "api_routes_added",
    "public_search_runtime_mutated",
    "public_search_response_changed",
    "live_source_called",
    "external_calls_performed",
    "connector_runtime_executed",
    "source_cache_read",
    "source_cache_mutated",
    "evidence_ledger_read",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "candidate_promotion_performed",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "telemetry_exported",
    "credentials_used",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "execution_enabled",
}
HARD_BOOLEANS: dict[str, bool] = {"local_dry_run": True, **{key: False for key in sorted(HARD_FALSE_FIELDS)}}

MUTATION_SUMMARY = {
    "public_search_runtime_mutated": False,
    "source_cache_read": False,
    "source_cache_mutated": False,
    "evidence_ledger_read": False,
    "evidence_ledger_mutated": False,
    "candidate_index_mutated": False,
    "candidate_promotion_performed": False,
    "public_index_mutated": False,
    "local_index_mutated": False,
    "master_index_mutated": False,
}

RECORD_FALSE_FIELDS = HARD_FALSE_FIELDS | {
    "hosted_deployment_performed",
    "public_search_order_changed",
    "runtime_object_page_implemented",
    "runtime_source_page_implemented",
    "runtime_comparison_page_implemented",
    "persistent_object_page_store_implemented",
    "persistent_source_page_store_implemented",
    "persistent_comparison_page_store_implemented",
    "object_page_generated_from_live_source",
    "source_page_generated_from_live_source",
    "comparison_page_generated_from_live_source",
    "source_sync_worker_executed",
    "downloads_enabled",
    "uploads_enabled",
    "installs_enabled",
    "execution_enabled",
    "arbitrary_url_fetch_enabled",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "source_trust_claimed",
    "comparison_winner_claimed",
}


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


def detect_forbidden_cli_args(argv: Sequence[str]) -> list[str]:
    return sorted({item.split("=", 1)[0] for item in argv if item.split("=", 1)[0] in FORBIDDEN_CLI_FIELDS})


def assert_no_forbidden_cli_args(argv: Sequence[str]) -> None:
    forbidden = detect_forbidden_cli_args(argv)
    if forbidden:
        raise PagePolicyError(f"forbidden page dry-run argument(s): {', '.join(forbidden)}")


def ensure_approved_input_root(path: Path, *, allow_temp: bool = False) -> Path:
    resolved = path.resolve()
    if any(is_relative_to(resolved, root) for root in APPROVED_EXAMPLE_ROOTS):
        return resolved
    if allow_temp and is_relative_to(resolved, Path(tempfile.gettempdir())):
        return resolved
    raise PagePolicyError(f"input root is not approved for page dry-run: {path}")


def ensure_approved_output_path(path: Path) -> Path:
    resolved = path.resolve()
    if is_relative_to(resolved, AUDIT_ROOT) or is_relative_to(resolved, Path(tempfile.gettempdir())):
        return resolved
    raise PagePolicyError(f"output path is not approved for page dry-run reports/previews: {path}")


def default_example_roots() -> tuple[Path, ...]:
    return tuple(root for root in APPROVED_EXAMPLE_ROOTS if root.exists())


def normalize_page_kind(record: Mapping[str, Any]) -> str:
    for key in ("page_kind", "object_page_kind", "source_page_kind", "comparison_page_kind"):
        value = record.get(key)
        if isinstance(value, str) and value in PAGE_KINDS:
            return value
    if "object_identity" in record:
        return "object_page"
    if "source_identity" in record:
        return "source_page"
    if "comparison_identity" in record or "subjects" in record:
        return "comparison_page"
    return "unknown"


def normalize_status(value: Any) -> str:
    if isinstance(value, str):
        lowered = value.casefold()
        if value in PAGE_STATUSES:
            return value
        if "public_safe" in lowered:
            return "public_safe_example"
        if "fixture" in lowered:
            return "fixture_backed"
        if "synthetic" in lowered:
            return "synthetic_example"
        if "candidate" in lowered:
            return "candidate"
        if "conflict" in lowered:
            return "conflicted"
        if "placeholder" in lowered:
            return "placeholder"
        if "future" in lowered:
            return "future"
        if "review" in lowered or "approval" in lowered:
            return "review_required"
    return "unknown"


def normalize_lane(value: Any) -> str:
    if isinstance(value, str):
        lowered = value.casefold()
        if value in LANES:
            return value
        if lowered in {"fixture", "synthetic", "example", "demo"}:
            return "demo"
        if "official" in lowered:
            return "official"
        if "preservation" in lowered:
            return "preservation"
        if "community" in lowered:
            return "community"
        if "candidate" in lowered:
            return "candidate"
        if "absence" in lowered:
            return "absence"
        if "conflict" in lowered:
            return "conflicted"
    return "unknown"


def normalize_privacy(value: Any) -> str:
    if isinstance(value, str):
        lowered = value.casefold()
        if value in PRIVACY_STATUSES:
            return value
        if "public_safe" in lowered or "public metadata" in lowered:
            return "public_safe"
        if "redact" in lowered:
            return "redacted"
        if "private" in lowered:
            return "local_private"
        if "sensitive" in lowered:
            return "rejected_sensitive"
    return "unknown"


def normalize_public_safety(value: Any) -> str:
    if isinstance(value, str) and value in PUBLIC_SAFETY_STATUSES:
        return value
    if isinstance(value, str) and "public_safe" in value.casefold():
        return "public_safe"
    if value is True:
        return "public_safe"
    if value is False:
        return "review_required"
    return "unknown"


def normalize_action_status(value: Any) -> str:
    if isinstance(value, str) and value in ACTION_STATUSES:
        return value
    if isinstance(value, str):
        lowered = value.casefold()
        if "inspect" in lowered:
            return "inspect_only"
        if "compare" in lowered:
            return "compare_only"
        if "cite" in lowered:
            return "cite_only"
        if "disabled" in lowered:
            return "risky_actions_disabled"
    return "unknown"


def scan_page_policy(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, value in iter_items(record):
        key_lower = key.casefold()
        if key_lower in FORBIDDEN_RECORD_KEYS:
            errors.append(f"forbidden field present: {key}")
        if key_lower in RAW_PAYLOAD_KEYS:
            errors.append(f"raw payload field present: {key}")
        if _secret_like_key_value(key_lower, value):
            errors.append(f"secret-like field present: {key}")
        if key_lower in RECORD_FALSE_FIELDS and value is not False:
            errors.append(f"{key} must be false")
        if key_lower in {"allowed_actions", "allowed_capabilities", "enabled_actions"}:
            errors.extend(_scan_allowed_actions(value, key))
        if _risky_enabled_field(key_lower, value):
            errors.append(f"unsafe action claim detected: {key} enabled")
    for value in iter_strings(record):
        if URL_PATTERN.search(value):
            errors.append("URL-like value is not allowed in dry-run page records")
        for label, pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(value):
                errors.append(f"private or unsafe path detected: {label}")
        for label, pattern in SENSITIVE_PATTERNS:
            if pattern.search(value):
                errors.append(f"sensitive value detected: {label}")
    return sorted(set(errors))


def assert_hard_booleans(report: Mapping[str, Any]) -> list[str]:
    hard = report.get("hard_booleans", {})
    if not isinstance(hard, Mapping):
        return ["hard_booleans must be an object"]
    errors: list[str] = []
    for key in HARD_TRUE_FIELDS:
        if hard.get(key) is not True:
            errors.append(f"hard_booleans.{key} must be true")
    for key in HARD_FALSE_FIELDS:
        if hard.get(key) is not False:
            errors.append(f"hard_booleans.{key} must be false")
    return errors


def _secret_like_key_value(key_lower: str, value: Any) -> bool:
    if not any(part in key_lower for part in SECRET_KEY_PARTS):
        return False
    if value in (False, None):
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True


def _risky_enabled_field(key_lower: str, value: Any) -> bool:
    if value is not True:
        return False
    return any(word in key_lower for word in RISKY_ACTION_WORDS)


def _scan_allowed_actions(value: Any, key: str) -> list[str]:
    errors: list[str] = []
    for action in iter_strings(value):
        normalized = action.casefold().replace("-", "_").replace(" ", "_")
        if any(word in normalized for word in RISKY_ACTION_WORDS):
            errors.append(f"unsafe action listed in {key}: {action}")
    return errors
