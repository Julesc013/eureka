"""Policy checks for the P104 local pack import dry-run runtime."""

from __future__ import annotations

from pathlib import Path
import re
import tempfile
from typing import Any, Iterable, Mapping, Sequence

from runtime.packs.errors import PackImportPolicyError


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PACKS_ROOT = REPO_ROOT / "examples" / "source_packs"
EVIDENCE_PACKS_ROOT = REPO_ROOT / "examples" / "evidence_packs"
INDEX_PACKS_ROOT = REPO_ROOT / "examples" / "index_packs"
CONTRIBUTION_PACKS_ROOT = REPO_ROOT / "examples" / "contribution_packs"
PACKS_ROOT = REPO_ROOT / "examples" / "packs"
PACK_IMPORT_DRY_RUN_ROOT = REPO_ROOT / "examples" / "pack_import_dry_run"
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "pack-import-local-dry-run-runtime-v0"

APPROVED_EXAMPLE_ROOTS = (
    SOURCE_PACKS_ROOT,
    EVIDENCE_PACKS_ROOT,
    INDEX_PACKS_ROOT,
    CONTRIBUTION_PACKS_ROOT,
    PACKS_ROOT,
    PACK_IMPORT_DRY_RUN_ROOT,
)

PACK_KINDS = {"source_pack", "evidence_pack", "index_pack", "contribution_pack", "pack_set", "unknown"}
VALIDATION_STATUSES = {"valid", "invalid", "validator_missing", "validator_not_run", "warning", "unknown"}
PRIVACY_STATUSES = {"public_safe", "redacted", "local_private", "rejected_sensitive", "unknown"}
PUBLIC_SAFETY_STATUSES = {"public_safe", "review_required", "rejected", "unknown"}
RISK_STATUSES = {
    "metadata_only",
    "executable_reference",
    "private_data_risk",
    "credential_risk",
    "URL_fetch_risk",
    "mutation_risk",
    "unknown",
}
MUTATION_IMPACTS = {
    "none_dry_run_only",
    "source_cache_candidate_effect",
    "evidence_ledger_candidate_effect",
    "candidate_index_candidate_effect",
    "public_index_candidate_effect",
    "master_index_candidate_effect",
    "blocked_mutation_claim",
    "unknown",
}
PROMOTION_READINESS = {"not_ready", "review_required", "candidate_ready_future", "blocked", "unknown"}

MUTATION_IMPACT_ALIASES = {
    "source_inventory_candidate_effect": "source_cache_candidate_effect",
    "source_pack_candidate_effect": "source_cache_candidate_effect",
    "evidence_pack_candidate_effect": "evidence_ledger_candidate_effect",
    "index_pack_candidate_effect": "public_index_candidate_effect",
    "contribution_review_candidate_effect": "candidate_index_candidate_effect",
}

FORBIDDEN_CLI_FIELDS = {
    "--url",
    "--fetch-url",
    "--live-source",
    "--source-url",
    "--connector",
    "--source-cache-path",
    "--evidence-ledger-path",
    "--candidate-path",
    "--quarantine-path",
    "--staging-path",
    "--store-root",
    "--index-path",
    "--database",
    "--serve",
    "--upload",
    "--admin",
    "--write-authoritative",
    "--mutate",
    "--publish",
    "--promote",
    "--execute",
    "--run-scripts",
    "--follow-urls",
}

FORBIDDEN_RECORD_KEYS = {
    "url",
    "fetch_url",
    "source_url",
    "live_source",
    "connector",
    "connector_param",
    "source_cache_path",
    "evidence_ledger_path",
    "candidate_path",
    "quarantine_path",
    "staging_path",
    "store_root",
    "index_path",
    "database",
    "local_path",
    "filesystem_root",
    "pack_path",
    "import_path",
}
EXECUTION_CLAIM_KEYS = {
    "execute",
    "execution_enabled",
    "pack_content_executed",
    "run_scripts",
    "scripts_enabled",
    "installer_payload_enabled",
    "allows_executables",
    "package_manager_enabled",
    "emulator_enabled",
    "vm_enabled",
}
MUTATION_CLAIM_KEYS = {
    "authoritative_pack_import_runtime_implemented",
    "import_performed",
    "write_authoritative",
    "mutate",
    "source_cache_mutated",
    "evidence_ledger_mutated",
    "candidate_index_mutated",
    "public_index_mutated",
    "local_index_mutated",
    "master_index_mutated",
    "promotion_decision_created",
    "accepted_record_created",
    "public_contribution_intake_enabled",
    "upload_endpoint_enabled",
    "admin_endpoint_enabled",
}
SECRET_KEY_PARTS = ("api_key", "auth_token", "password", "secret", "credential", "private_key")

URL_PATTERN = re.compile(r"\b(?:https?|ftp)://|(?<![A-Za-z])(?:file|data|javascript):", re.IGNORECASE)
PRIVATE_PATH_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("windows_absolute_path", re.compile(r"\b[A-Za-z]:[\\/]", re.IGNORECASE)),
    ("posix_private_path", re.compile(r"(?<![A-Za-z0-9_])/(?:home|users|tmp|var|private|root)/", re.IGNORECASE)),
    ("path_traversal", re.compile(r"(^|[\\/])\.\.([\\/]|$)")),
)
SENSITIVE_VALUE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("secret_assignment", re.compile(r"\b(?:api[_-]?key|auth[_-]?token|password|secret|credential)\s*[:=]", re.IGNORECASE)),
    ("placeholder_secret_value", re.compile(r"\bsecret-value\b", re.IGNORECASE)),
    ("ip_address", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")),
    ("account_identifier", re.compile(r"\b(?:account[_ -]?id|user[_ -]?id|session[_ -]?id)\s*[:=]", re.IGNORECASE)),
    ("email_address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
)

HARD_TRUE_FIELDS = {"local_dry_run"}
HARD_FALSE_FIELDS = {
    "admin_endpoint_enabled",
    "accepted_record_created",
    "authoritative_pack_import_runtime_implemented",
    "candidate_index_mutated",
    "credentials_used",
    "downloads_enabled",
    "evidence_ledger_mutated",
    "execution_enabled",
    "external_calls_performed",
    "hosted_runtime_enabled",
    "installs_enabled",
    "live_source_called",
    "local_index_mutated",
    "master_index_mutated",
    "pack_content_executed",
    "pack_urls_followed",
    "promotion_decision_created",
    "promotion_runtime_enabled",
    "public_contribution_intake_enabled",
    "public_index_mutated",
    "quarantine_store_written",
    "real_pack_staging_performed",
    "source_cache_mutated",
    "staging_store_written",
    "telemetry_exported",
    "upload_endpoint_enabled",
}
HARD_BOOLEANS: dict[str, bool] = {"local_dry_run": True, **{key: False for key in sorted(HARD_FALSE_FIELDS)}}

MUTATION_SUMMARY = {
    "authoritative_pack_import_runtime_implemented": False,
    "real_pack_staging_performed": False,
    "quarantine_store_written": False,
    "staging_store_written": False,
    "promotion_decision_created": False,
    "accepted_record_created": False,
    "source_cache_mutated": False,
    "evidence_ledger_mutated": False,
    "candidate_index_mutated": False,
    "public_index_mutated": False,
    "local_index_mutated": False,
    "master_index_mutated": False,
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
        raise PackImportPolicyError(f"forbidden dry-run arguments rejected: {', '.join(forbidden)}")


def default_example_roots() -> tuple[Path, ...]:
    return tuple(root for root in APPROVED_EXAMPLE_ROOTS if root.exists())


def ensure_approved_input_root(path: Path, *, allow_temp: bool = False) -> Path:
    resolved = path.resolve()
    if allow_temp and is_relative_to(resolved, Path(tempfile.gettempdir())):
        return resolved
    if not any(is_relative_to(resolved, root) for root in APPROVED_EXAMPLE_ROOTS if root.exists()):
        raise PackImportPolicyError(f"input root is not under an approved repo example root: {path}")
    if any(pattern.search(str(resolved)) for _, pattern in PRIVATE_PATH_PATTERNS):
        if not is_relative_to(resolved, REPO_ROOT):
            raise PackImportPolicyError("input root uses a private or traversal path")
    return resolved


def ensure_approved_output_path(path: Path) -> Path:
    resolved = path.resolve()
    if is_relative_to(resolved, AUDIT_ROOT) or is_relative_to(resolved, Path(tempfile.gettempdir())):
        return resolved
    raise PackImportPolicyError(
        "output path must be under control/audits/pack-import-local-dry-run-runtime-v0 or a temp directory"
    )


def normalize_enum(value: Any, allowed: set[str], aliases: Mapping[str, str] | None = None) -> str:
    if isinstance(value, bool):
        return "public_safe" if value and "public_safe" in allowed else "unknown"
    if not isinstance(value, str):
        return "unknown"
    normalized = value.strip().casefold().replace("-", "_").replace(" ", "_")
    if aliases and normalized in aliases:
        normalized = aliases[normalized]
    return normalized if normalized in allowed else "unknown"


def normalize_pack_kind(record: Mapping[str, Any], *, filename: str | None = None) -> str:
    explicit = normalize_enum(record.get("pack_kind") or record.get("pack_type"), PACK_KINDS)
    if explicit != "unknown":
        return explicit
    schema = str(record.get("schema_version", "")).casefold()
    if schema.startswith("source_pack."):
        return "source_pack"
    if schema.startswith("evidence_pack."):
        return "evidence_pack"
    if schema.startswith("index_pack."):
        return "index_pack"
    if schema.startswith("contribution_pack."):
        return "contribution_pack"
    if "pack_set" in schema:
        return "pack_set"
    names = {
        "SOURCE_PACK.json": "source_pack",
        "EVIDENCE_PACK.json": "evidence_pack",
        "INDEX_PACK.json": "index_pack",
        "CONTRIBUTION_PACK.json": "contribution_pack",
    }
    return names.get(filename or "", "unknown")


def scan_pack_policy(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, value in iter_items(record):
        normalized_key = key.strip().casefold().replace("-", "_")
        if normalized_key in FORBIDDEN_RECORD_KEYS and _truthy(value):
            errors.append(f"forbidden path/live/source field detected: {key}")
        if normalized_key in EXECUTION_CLAIM_KEYS and _truthy(value):
            errors.append(f"executable or script claim detected: {key}")
        if normalized_key in MUTATION_CLAIM_KEYS and _truthy(value):
            errors.append(f"mutation/promotion/import claim detected: {key}")
        if any(part in normalized_key for part in SECRET_KEY_PARTS) and _truthy(value):
            errors.append(f"secret-like field detected: {key}")
    for text in iter_strings(record):
        for label, pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(text):
                errors.append(f"private path detected: {label}")
        if URL_PATTERN.search(text):
            errors.append("URL reference detected; dry-run will not follow URLs")
        for label, pattern in SENSITIVE_VALUE_PATTERNS:
            if pattern.search(text):
                errors.append(f"sensitive value detected: {label}")
    return sorted(set(errors))


def _truthy(value: Any) -> bool:
    if value is False or value is None:
        return False
    if isinstance(value, str):
        return value.strip().casefold() not in {"", "false", "no", "none", "not_applicable", "disabled"}
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return bool(value)
