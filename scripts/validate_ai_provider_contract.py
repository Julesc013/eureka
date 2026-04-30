from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = REPO_ROOT / "contracts" / "ai"
INVENTORY_DIR = REPO_ROOT / "control" / "inventory" / "ai_providers"
DEFAULT_PROVIDER_ROOT = REPO_ROOT / "examples" / "ai_providers" / "disabled_stub_provider_v0"

REQUIRED_SCHEMA_FILES = {
    "ai_provider_manifest.v0.json",
    "typed_ai_output.v0.json",
    "ai_task_request.v0.json",
}
REQUIRED_PROVIDER_FILES = {
    "AI_PROVIDER.json",
    "README.md",
    "PRIVACY_AND_SAFETY.md",
    "CHECKSUMS.SHA256",
}
REQUIRED_MANIFEST_FIELDS = {
    "schema_version",
    "provider_id",
    "provider_version",
    "provider_label",
    "provider_type",
    "status",
    "default_enabled",
    "network_required",
    "local_filesystem_required",
    "credential_required",
    "credential_policy",
    "privacy_policy",
    "logging_policy",
    "supported_tasks",
    "allowed_output_types",
    "forbidden_output_types",
    "input_data_policy",
    "output_policy",
    "cache_policy",
    "invalidation_policy",
    "evidence_linking_policy",
    "human_review_policy",
    "safety_boundaries",
    "notes",
}
REQUIRED_TYPED_OUTPUT_FIELDS = {
    "schema_version",
    "output_id",
    "provider_ref",
    "task_type",
    "output_type",
    "status",
    "limitations",
    "required_review",
    "prohibited_uses",
    "created_by_provider",
    "notes",
}
ALLOWED_PROVIDER_TYPES = {
    "local_model",
    "local_server",
    "remote_api",
    "browser_model",
    "native_model",
    "development_tool",
    "disabled_stub",
}
ALLOWED_PROVIDER_STATUSES = {
    "draft",
    "local_private",
    "disabled_by_default",
    "review_required",
    "allowed_for_local_testing",
    "rejected",
    "superseded",
}
ALLOWED_TASK_TYPES = {
    "query_interpretation_suggestion",
    "alias_suggestion",
    "metadata_extraction_suggestion",
    "compatibility_claim_candidate",
    "review_description_claim_extraction",
    "member_path_candidate_extraction",
    "source_matching_suggestion",
    "duplicate_identity_candidate",
    "explanation_draft",
    "OCR_cleanup_suggestion",
    "absence_explanation_draft",
    "contribution_pack_draft_assist",
}
FORBIDDEN_TASK_TYPES = {
    "canonical_truth_decision",
    "source_trust_final_decision",
    "rights_clearance_decision",
    "malware_safety_decision",
    "automatic_identity_merge",
    "automatic_master_index_acceptance",
    "silent_private_data_processing",
    "unbounded_web_browsing",
    "arbitrary_url_fetch",
    "credential_extraction",
    "installer_execution",
    "download_execution",
    "telemetry_collection",
}
ALLOWED_OUTPUT_TYPES = {
    "interpreted_query_candidate",
    "alias_candidate",
    "metadata_claim_candidate",
    "compatibility_claim_candidate",
    "review_claim_candidate",
    "member_path_candidate",
    "source_match_candidate",
    "identity_match_candidate",
    "explanation_draft",
    "ocr_cleanup_candidate",
    "absence_explanation_draft",
    "contribution_draft_candidate",
}
REQUIRED_PROHIBITED_USES = {
    "canonical_truth",
    "rights_clearance",
    "malware_safety",
    "automatic_acceptance",
}
SECRET_KEYS = {
    "api_key",
    "apikey",
    "auth_token",
    "authorization",
    "bearer",
    "client_secret",
    "credential",
    "credentials",
    "password",
    "private_key",
    "secret",
    "session",
    "token",
}
SECRET_VALUE_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"api[_-]?key\s*[:=]\s*[A-Za-z0-9_-]{8,}", re.IGNORECASE),
    re.compile(r"secret\s*[:=]\s*[A-Za-z0-9_-]{8,}", re.IGNORECASE),
)
PRIVATE_PATH_PATTERNS = (
    re.compile(r"\b[A-Za-z]:[\\/][^\s\"']+"),
    re.compile(r"(^|[\s\"'])(/Users|/home|/tmp|/var|/etc)/[^\s\"']+"),
    re.compile(r"\\\\[^\\\s]+\\[^\\\s]+"),
)
FORBIDDEN_EXTENSIONS = {
    ".app",
    ".bat",
    ".cmd",
    ".deb",
    ".dmg",
    ".dll",
    ".exe",
    ".iso",
    ".msi",
    ".pkg",
    ".ps1",
    ".rpm",
    ".sh",
}
FORBIDDEN_RUNTIME_PATHS = (
    REPO_ROOT / "runtime" / "engine" / "ai",
    REPO_ROOT / "runtime" / "engine" / "ai_providers",
    REPO_ROOT / "runtime" / "gateway" / "ai",
    REPO_ROOT / "runtime" / "gateway" / "ai_providers",
    REPO_ROOT / "surfaces" / "web" / "ai",
    REPO_ROOT / "surfaces" / "native" / "ai",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate AI Provider Contract v0 and disabled example provider.")
    parser.add_argument("--provider-root", default=str(DEFAULT_PROVIDER_ROOT), help="AI provider example directory.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--strict", action="store_true", help="Require checksum coverage for every provider file.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_ai_provider_contract(Path(args.provider_root), strict=args.strict)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_ai_provider_contract(provider_root: Path, *, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    root = provider_root if provider_root.is_absolute() else REPO_ROOT / provider_root
    root = root.resolve()

    schemas = _validate_schemas(errors)
    policy = _validate_inventory(errors)
    manifest, typed_outputs = _validate_provider_root(root, strict=strict, errors=errors, warnings=warnings)
    _validate_runtime_absence(errors)

    provider_id = manifest.get("provider_id") if isinstance(manifest, Mapping) else None
    return {
        "schema_version": "ai_provider_contract_validation.v0",
        "validator_id": "ai_provider_contract_validator_v0",
        "status": "invalid" if errors else "valid",
        "ok": not errors,
        "strict": strict,
        "provider_root": _rel(root),
        "provider_id": provider_id,
        "schema_count": len(schemas),
        "typed_output_count": len(typed_outputs),
        "policy_id": policy.get("policy_id") if isinstance(policy, Mapping) else None,
        "default_enabled": manifest.get("default_enabled") if isinstance(manifest, Mapping) else None,
        "runtime_implemented": False,
        "model_calls_performed": False,
        "network_performed": False,
        "api_keys_present": False,
        "telemetry_enabled": False,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_schemas(errors: list[str]) -> list[dict[str, Any]]:
    schemas: list[dict[str, Any]] = []
    if not CONTRACT_DIR.exists():
        errors.append(f"{_rel(CONTRACT_DIR)}: AI contract directory is missing.")
        return schemas
    for name in sorted(REQUIRED_SCHEMA_FILES):
        path = CONTRACT_DIR / name
        payload = _load_json(path, errors)
        if isinstance(payload, dict):
            schemas.append(payload)
            if payload.get("x-runtime_implemented") is not False:
                errors.append(f"{_rel(path)}: x-runtime_implemented must be false.")
    provider_schema = CONTRACT_DIR / "ai_provider_manifest.v0.json"
    output_schema = CONTRACT_DIR / "typed_ai_output.v0.json"
    request_schema = CONTRACT_DIR / "ai_task_request.v0.json"
    _expect_schema_defs(provider_schema, "allowed_task_type", ALLOWED_TASK_TYPES, errors)
    _expect_schema_defs(provider_schema, "forbidden_task_or_output", FORBIDDEN_TASK_TYPES, errors)
    _expect_schema_defs(provider_schema, "allowed_output_type", ALLOWED_OUTPUT_TYPES, errors)
    for path in (output_schema, request_schema):
        if path.exists():
            text = path.read_text(encoding="utf-8")
            if "model calls" not in text and "model call" not in text:
                errors.append(f"{_rel(path)}: must state that model calls are not implemented.")
    return schemas


def _validate_inventory(errors: list[str]) -> dict[str, Any]:
    policy = _load_json(INVENTORY_DIR / "ai_provider_policy.json", errors)
    examples = _load_json(INVENTORY_DIR / "example_ai_providers.json", errors)
    if not isinstance(policy, dict):
        return {}
    if policy.get("status") != "contract_only":
        errors.append("control/inventory/ai_providers/ai_provider_policy.json: status must be contract_only.")
    for field in (
        "no_runtime_implemented",
        "no_model_calls_implemented",
        "remote_providers_disabled_by_default",
        "local_providers_disabled_by_default",
        "private_data_disabled_by_default",
        "telemetry_disabled_by_default",
        "required_review",
        "no_truth_authority",
        "no_rights_clearance",
        "no_malware_safety",
        "no_auto_acceptance",
    ):
        if policy.get(field) is not True:
            errors.append(f"control/inventory/ai_providers/ai_provider_policy.json: {field} must be true.")
    if policy.get("default_enabled") is not False:
        errors.append("control/inventory/ai_providers/ai_provider_policy.json: default_enabled must be false.")
    if set(policy.get("allowed_task_types", [])) != ALLOWED_TASK_TYPES:
        errors.append("control/inventory/ai_providers/ai_provider_policy.json: allowed_task_types must match v0 set.")
    if set(policy.get("forbidden_task_types", [])) != FORBIDDEN_TASK_TYPES:
        errors.append("control/inventory/ai_providers/ai_provider_policy.json: forbidden_task_types must match v0 set.")
    _scan_payload_for_secrets(policy, "control/inventory/ai_providers/ai_provider_policy.json", errors)
    if isinstance(examples, dict):
        providers = examples.get("providers")
        if not isinstance(providers, list) or not providers:
            errors.append("control/inventory/ai_providers/example_ai_providers.json: providers must be a non-empty list.")
        else:
            for index, provider in enumerate(providers):
                if not isinstance(provider, Mapping):
                    errors.append(f"control/inventory/ai_providers/example_ai_providers.json: providers[{index}] must be an object.")
                    continue
                _validate_inventory_provider(provider, index, errors)
    return policy


def _validate_inventory_provider(provider: Mapping[str, Any], index: int, errors: list[str]) -> None:
    prefix = f"control/inventory/ai_providers/example_ai_providers.json: providers[{index}]"
    provider_type = provider.get("provider_type")
    if provider_type not in ALLOWED_PROVIDER_TYPES:
        errors.append(f"{prefix}.provider_type is unsupported.")
    if provider.get("default_enabled") is not False:
        errors.append(f"{prefix}.default_enabled must be false.")
    if provider.get("runtime_implemented") is not False:
        errors.append(f"{prefix}.runtime_implemented must be false.")
    if provider_type == "remote_api":
        if provider.get("network_required") is not True:
            errors.append(f"{prefix}: remote_api must declare network_required true.")
        if provider.get("credential_required") is not True:
            errors.append(f"{prefix}: remote_api must declare credential_required true.")
        if provider.get("explicit_operator_approval_required") is not True:
            errors.append(f"{prefix}: remote_api must require explicit operator approval.")
    _scan_payload_for_secrets(provider, prefix, errors)


def _validate_provider_root(
    root: Path,
    *,
    strict: bool,
    errors: list[str],
    warnings: list[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest: dict[str, Any] = {}
    typed_outputs: list[dict[str, Any]] = []
    if not root.exists() or not root.is_dir():
        errors.append(f"{_rel(root)}: provider root is missing or is not a directory.")
        return manifest, typed_outputs
    for rel_path in sorted(REQUIRED_PROVIDER_FILES):
        if not (root / rel_path).is_file():
            errors.append(f"{_rel(root / rel_path)}: required provider file is missing.")
    _scan_tree_for_forbidden_files(root, errors)
    _scan_tree_text(root, errors)
    _validate_checksums(root, strict=strict, errors=errors)

    loaded_manifest = _load_json(root / "AI_PROVIDER.json", errors)
    if isinstance(loaded_manifest, dict):
        manifest = loaded_manifest
        _validate_manifest(manifest, _rel(root / "AI_PROVIDER.json"), errors)
    examples_dir = root / "examples"
    if not examples_dir.exists():
        errors.append(f"{_rel(examples_dir)}: typed output examples directory is missing.")
    else:
        for path in sorted(examples_dir.glob("*.json")):
            payload = _load_json(path, errors)
            if isinstance(payload, dict):
                typed_outputs.append(payload)
                _validate_typed_output(payload, _rel(path), manifest, errors)
        if not typed_outputs:
            errors.append(f"{_rel(examples_dir)}: at least one typed output example is required.")
    if manifest.get("provider_id") == "example.disabled_stub_provider_v0" and len(typed_outputs) < 2:
        warnings.append("Disabled stub example should keep at least two typed output examples.")
    return manifest, typed_outputs


def _validate_manifest(manifest: Mapping[str, Any], label: str, errors: list[str]) -> None:
    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    if missing:
        errors.append(f"{label}: missing required manifest fields: {', '.join(missing)}.")
    if manifest.get("schema_version") != "ai_provider_manifest.v0":
        errors.append(f"{label}: schema_version must be ai_provider_manifest.v0.")
    if manifest.get("provider_type") not in ALLOWED_PROVIDER_TYPES:
        errors.append(f"{label}: provider_type is unsupported.")
    if manifest.get("status") not in ALLOWED_PROVIDER_STATUSES:
        errors.append(f"{label}: status is unsupported.")
    if manifest.get("default_enabled") is not False:
        errors.append(f"{label}: default_enabled must be false.")
    if manifest.get("local_filesystem_required") is not False:
        errors.append(f"{label}: local_filesystem_required must be false in v0 examples.")
    if set(manifest.get("supported_tasks", [])) - ALLOWED_TASK_TYPES:
        errors.append(f"{label}: supported_tasks contains unsupported task types.")
    if set(manifest.get("allowed_output_types", [])) - ALLOWED_OUTPUT_TYPES:
        errors.append(f"{label}: allowed_output_types contains unsupported output types.")
    if not REQUIRED_FORBIDDEN_TASK_NAMES_PRESENT(manifest):
        errors.append(f"{label}: forbidden_output_types must include truth, rights, malware, auto-acceptance, private-data, web, credential, execution, and telemetry prohibitions.")
    credential_policy = _as_mapping(manifest.get("credential_policy"))
    privacy_policy = _as_mapping(manifest.get("privacy_policy"))
    logging_policy = _as_mapping(manifest.get("logging_policy"))
    output_policy = _as_mapping(manifest.get("output_policy"))
    input_policy = _as_mapping(manifest.get("input_data_policy"))
    cache_policy = _as_mapping(manifest.get("cache_policy"))
    evidence_policy = _as_mapping(manifest.get("evidence_linking_policy"))
    review_policy = _as_mapping(manifest.get("human_review_policy"))
    _require_false(credential_policy, "credentials_in_manifest_allowed", label, errors)
    _require_false(credential_policy, "storage_implemented", label, errors)
    _require_false(privacy_policy, "private_data_allowed_by_default", label, errors)
    _require_false(privacy_policy, "remote_private_data_transfer_allowed", label, errors)
    _require_false(privacy_policy, "local_paths_allowed_by_default", label, errors)
    _require_false(logging_policy, "prompt_logging_enabled_by_default", label, errors)
    _require_false(logging_policy, "output_logging_enabled_by_default", label, errors)
    _require_false(logging_policy, "telemetry_enabled_by_default", label, errors)
    _require_false(logging_policy, "external_log_upload_enabled", label, errors)
    _require_false(input_policy, "private_inputs_allowed_by_default", label, errors)
    _require_false(input_policy, "local_source_access_granted", label, errors)
    _require_false(input_policy, "live_source_access_granted", label, errors)
    _require_false(input_policy, "silent_private_data_processing_allowed", label, errors)
    _require_true(output_policy, "outputs_are_suggestions_only", label, errors)
    _require_true(output_policy, "required_review", label, errors)
    _require_false(output_policy, "canonical_truth_allowed", label, errors)
    _require_false(output_policy, "rights_clearance_allowed", label, errors)
    _require_false(output_policy, "malware_safety_allowed", label, errors)
    _require_false(output_policy, "automatic_acceptance_allowed", label, errors)
    _require_false(cache_policy, "cache_enabled_by_default", label, errors)
    _require_false(cache_policy, "private_cache_allowed_by_default", label, errors)
    _require_false(cache_policy, "cache_runtime_implemented", label, errors)
    _require_true(evidence_policy, "unsupported_claims_require_review", label, errors)
    _require_true(review_policy, "review_required_for_all_outputs", label, errors)
    _require_true(review_policy, "master_index_acceptance_requires_review_queue", label, errors)
    if manifest.get("provider_type") == "remote_api":
        if manifest.get("network_required") is not True:
            errors.append(f"{label}: remote_api providers must declare network_required true.")
        if manifest.get("credential_required") is not True:
            errors.append(f"{label}: remote_api providers must declare credential_required true.")
        _require_true(credential_policy, "explicit_operator_approval_required", label, errors)
    _scan_payload_for_secrets(manifest, label, errors)


def REQUIRED_FORBIDDEN_TASK_NAMES_PRESENT(manifest: Mapping[str, Any]) -> bool:
    values = set(manifest.get("forbidden_output_types", []))
    required = {
        "canonical_truth_decision",
        "rights_clearance_decision",
        "malware_safety_decision",
        "automatic_master_index_acceptance",
        "silent_private_data_processing",
        "unbounded_web_browsing",
        "arbitrary_url_fetch",
        "credential_extraction",
        "installer_execution",
        "download_execution",
        "telemetry_collection",
    }
    return required <= values


def _validate_typed_output(
    payload: Mapping[str, Any],
    label: str,
    manifest: Mapping[str, Any],
    errors: list[str],
) -> None:
    missing = sorted(REQUIRED_TYPED_OUTPUT_FIELDS - set(payload))
    if missing:
        errors.append(f"{label}: missing required typed output fields: {', '.join(missing)}.")
    if payload.get("schema_version") != "typed_ai_output.v0":
        errors.append(f"{label}: schema_version must be typed_ai_output.v0.")
    if payload.get("task_type") not in ALLOWED_TASK_TYPES:
        errors.append(f"{label}: unsupported task_type.")
    if payload.get("output_type") not in ALLOWED_OUTPUT_TYPES:
        errors.append(f"{label}: unsupported output_type.")
    if payload.get("required_review") is not True:
        errors.append(f"{label}: required_review must be true.")
    prohibited_uses = set(payload.get("prohibited_uses", []))
    if not REQUIRED_PROHIBITED_USES <= prohibited_uses:
        errors.append(f"{label}: prohibited_uses must include canonical_truth, rights_clearance, malware_safety, and automatic_acceptance.")
    created_by = _as_mapping(payload.get("created_by_provider"))
    _require_false(created_by, "runtime_call_performed", label, errors)
    provider_ref = _as_mapping(payload.get("provider_ref"))
    if manifest:
        if provider_ref.get("provider_id") != manifest.get("provider_id"):
            errors.append(f"{label}: provider_ref.provider_id must match AI_PROVIDER.json.")
        if provider_ref.get("provider_version") != manifest.get("provider_version"):
            errors.append(f"{label}: provider_ref.provider_version must match AI_PROVIDER.json.")
        if payload.get("task_type") not in set(manifest.get("supported_tasks", [])):
            errors.append(f"{label}: task_type is not listed in provider supported_tasks.")
        if payload.get("output_type") not in set(manifest.get("allowed_output_types", [])):
            errors.append(f"{label}: output_type is not listed in provider allowed_output_types.")
    for index, claim in enumerate(payload.get("structured_claims", [])):
        if isinstance(claim, Mapping) and claim.get("review_required") is not True:
            errors.append(f"{label}: structured_claims[{index}].review_required must be true.")
    _scan_payload_for_secrets(payload, label, errors)
    _scan_text_for_private_paths(json.dumps(payload, sort_keys=True), label, errors)


def _validate_checksums(root: Path, *, strict: bool, errors: list[str]) -> None:
    checksum_path = root / "CHECKSUMS.SHA256"
    if not checksum_path.exists():
        errors.append(f"{_rel(checksum_path)}: missing checksum file.")
        return
    entries: dict[str, str] = {}
    for line_number, line in enumerate(checksum_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            errors.append(f"{_rel(checksum_path)}:{line_number}: invalid checksum line.")
            continue
        digest, rel_path = parts[0], parts[1].strip()
        entries[rel_path] = digest
    for rel_path, expected in entries.items():
        target = root / rel_path
        if not target.is_file():
            errors.append(f"{_rel(checksum_path)}: checksummed file missing: {rel_path}.")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"{_rel(target)}: checksum mismatch.")
    required = {
        "AI_PROVIDER.json",
        "README.md",
        "PRIVACY_AND_SAFETY.md",
    }
    required.update(str(path.relative_to(root)).replace("\\", "/") for path in (root / "examples").glob("*.json"))
    missing = sorted(required - set(entries))
    if missing:
        errors.append(f"{_rel(checksum_path)}: missing checksum entries: {', '.join(missing)}.")
    if strict:
        files = {
            str(path.relative_to(root)).replace("\\", "/")
            for path in root.rglob("*")
            if path.is_file() and path.name != "CHECKSUMS.SHA256"
        }
        extra_missing = sorted(files - set(entries))
        if extra_missing:
            errors.append(f"{_rel(checksum_path)}: strict mode missing checksum entries: {', '.join(extra_missing)}.")


def _scan_tree_for_forbidden_files(root: Path, errors: list[str]) -> None:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in FORBIDDEN_EXTENSIONS:
            errors.append(f"{_rel(path)}: forbidden executable or script payload extension for AI provider v0.")


def _scan_tree_text(root: Path, errors: list[str]) -> None:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{_rel(path)}: binary or non-UTF-8 payload is not allowed in AI provider examples.")
            continue
        _scan_text_for_secrets(text, _rel(path), errors)
        _scan_text_for_private_paths(text, _rel(path), errors)
        if "http://" in text or "https://" in text:
            errors.append(f"{_rel(path)}: example provider files must not include live URLs.")


def _validate_runtime_absence(errors: list[str]) -> None:
    for path in FORBIDDEN_RUNTIME_PATHS:
        if path.exists():
            errors.append(f"{_rel(path)}: AI provider runtime path exists; P41 is contract-only.")


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.exists():
        errors.append(f"{_rel(path)}: missing JSON file.")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
        return None


def _expect_schema_defs(schema_path: Path, def_name: str, expected: set[str], errors: list[str]) -> None:
    payload = _load_json(schema_path, errors)
    if not isinstance(payload, Mapping):
        return
    defs = payload.get("$defs")
    if not isinstance(defs, Mapping):
        errors.append(f"{_rel(schema_path)}: missing $defs.")
        return
    entry = defs.get(def_name)
    if not isinstance(entry, Mapping) or not isinstance(entry.get("enum"), list):
        errors.append(f"{_rel(schema_path)}: $defs.{def_name}.enum is missing.")
        return
    if set(entry["enum"]) != expected:
        errors.append(f"{_rel(schema_path)}: $defs.{def_name}.enum does not match v0 policy.")


def _scan_payload_for_secrets(payload: Any, label: str, errors: list[str]) -> None:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            key_text = str(key).lower()
            if key_text in SECRET_KEYS and value not in (False, None, "", [], {}):
                errors.append(f"{label}: prohibited secret-like field has a value: {key}.")
            _scan_payload_for_secrets(value, label, errors)
    elif isinstance(payload, list):
        for value in payload:
            _scan_payload_for_secrets(value, label, errors)
    elif isinstance(payload, str):
        _scan_text_for_secrets(payload, label, errors)


def _scan_text_for_secrets(text: str, label: str, errors: list[str]) -> None:
    for pattern in SECRET_VALUE_PATTERNS:
        if pattern.search(text):
            errors.append(f"{label}: prohibited API key or secret-like value found.")


def _scan_text_for_private_paths(text: str, label: str, errors: list[str]) -> None:
    for pattern in PRIVATE_PATH_PATTERNS:
        if pattern.search(text):
            errors.append(f"{label}: private or absolute local path found.")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _require_true(payload: Mapping[str, Any], field: str, label: str, errors: list[str]) -> None:
    if payload.get(field) is not True:
        errors.append(f"{label}: {field} must be true.")


def _require_false(payload: Mapping[str, Any], field: str, label: str, errors: list[str]) -> None:
    if payload.get(field) is not False:
        errors.append(f"{label}: {field} must be false.")


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "AI Provider Contract validation",
        f"status: {report['status']}",
        f"provider_root: {report['provider_root']}",
        f"provider_id: {report.get('provider_id')}",
        f"typed_outputs: {report['typed_output_count']}",
        f"runtime_implemented: {report['runtime_implemented']}",
        f"model_calls_performed: {report['model_calls_performed']}",
        f"network_performed: {report['network_performed']}",
    ]
    if report["errors"]:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.append("")
        lines.append("Warnings")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
