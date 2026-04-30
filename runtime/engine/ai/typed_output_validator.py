from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence


MAX_GENERATED_TEXT_CHARS = 2000

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
ALLOWED_OUTPUT_STATUSES = {
    "suggestion",
    "candidate",
    "rejected",
    "superseded",
    "accepted_for_review",
}
ALLOWED_PRIVACY_CLASSES = {
    "public_safe",
    "local_private",
    "review_required",
    "restricted",
    "unknown",
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
REQUIRED_TASK_REQUEST_FIELDS = {
    "schema_version",
    "task_id",
    "task_type",
    "input_refs",
    "input_policy",
    "privacy_classification",
    "allowed_provider_types",
    "required_output_type",
    "user_or_operator_approval_required",
    "notes",
}
REQUIRED_PROVIDER_FIELDS = {
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
REQUIRED_PROHIBITED_USES = {
    "canonical_truth",
    "rights_clearance",
    "malware_safety",
    "automatic_acceptance",
}
FORBIDDEN_AUTHORITY_VALUES = {
    "canonical_truth_decision",
    "source_trust_final_decision",
    "rights_clearance_decision",
    "malware_safety_decision",
    "automatic_identity_merge",
    "automatic_master_index_acceptance",
}
FORBIDDEN_AUTHORITY_KEYS = {
    "accepted_public",
    "automatic_acceptance",
    "automatic_acceptance_allowed",
    "automatic_identity_merge",
    "canonical_truth",
    "canonical_truth_allowed",
    "malware_safety",
    "malware_safety_allowed",
    "rights_clearance",
    "rights_clearance_allowed",
    "source_trust_final_decision",
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
FORBIDDEN_AUTHORITY_TEXT_PATTERNS = (
    re.compile(r"\bgrants?\s+rights\s+clearance\b", re.IGNORECASE),
    re.compile(r"\brights\s+clearance\s+(is\s+)?(approved|granted|complete|cleared)\b", re.IGNORECASE),
    re.compile(r"\bmalware\s+safety\s+(is\s+)?(approved|guaranteed|cleared|safe)\b", re.IGNORECASE),
    re.compile(r"\bcanonical\s+truth\s+(is\s+)?(selected|decided|proven)\b", re.IGNORECASE),
    re.compile(r"\bautomatic\s+acceptance\s+(is\s+)?(approved|granted|allowed)\b", re.IGNORECASE),
)


def load_json(path: str | Path) -> Any:
    target = Path(path)
    return json.loads(target.read_text(encoding="utf-8"))


def validate_provider_manifest(manifest: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_PROVIDER_FIELDS - set(manifest))
    if missing:
        errors.append(f"missing required provider manifest fields: {', '.join(missing)}.")
    if manifest.get("schema_version") != "ai_provider_manifest.v0":
        errors.append("schema_version must be ai_provider_manifest.v0.")
    if manifest.get("provider_type") not in ALLOWED_PROVIDER_TYPES:
        errors.append("provider_type is unsupported.")
    if manifest.get("status") not in ALLOWED_PROVIDER_STATUSES:
        errors.append("status is unsupported.")
    if manifest.get("default_enabled") is not False:
        errors.append("default_enabled must be false.")
    if manifest.get("local_filesystem_required") is not False:
        errors.append("local_filesystem_required must be false for v0 validation examples.")

    supported_tasks = _as_list(manifest.get("supported_tasks"))
    allowed_outputs = _as_list(manifest.get("allowed_output_types"))
    forbidden_outputs = set(_as_list(manifest.get("forbidden_output_types")))
    if set(supported_tasks) - ALLOWED_TASK_TYPES:
        errors.append("supported_tasks contains unsupported task types.")
    if set(allowed_outputs) - ALLOWED_OUTPUT_TYPES:
        errors.append("allowed_output_types contains unsupported output types.")
    if not FORBIDDEN_AUTHORITY_VALUES <= forbidden_outputs:
        errors.append("forbidden_output_types must include truth, trust, rights, malware, identity-merge, and auto-acceptance prohibitions.")

    credential_policy = _as_mapping(manifest.get("credential_policy"))
    privacy_policy = _as_mapping(manifest.get("privacy_policy"))
    logging_policy = _as_mapping(manifest.get("logging_policy"))
    input_policy = _as_mapping(manifest.get("input_data_policy"))
    output_policy = _as_mapping(manifest.get("output_policy"))
    cache_policy = _as_mapping(manifest.get("cache_policy"))
    review_policy = _as_mapping(manifest.get("human_review_policy"))
    evidence_policy = _as_mapping(manifest.get("evidence_linking_policy"))

    _require_false(credential_policy, "credentials_in_manifest_allowed", errors)
    _require_false(credential_policy, "storage_implemented", errors)
    _require_false(privacy_policy, "private_data_allowed_by_default", errors)
    _require_false(privacy_policy, "remote_private_data_transfer_allowed", errors)
    _require_false(privacy_policy, "local_paths_allowed_by_default", errors)
    _require_false(logging_policy, "prompt_logging_enabled_by_default", errors)
    _require_false(logging_policy, "output_logging_enabled_by_default", errors)
    _require_false(logging_policy, "telemetry_enabled_by_default", errors)
    _require_false(logging_policy, "external_log_upload_enabled", errors)
    _require_false(input_policy, "private_inputs_allowed_by_default", errors)
    _require_false(input_policy, "local_source_access_granted", errors)
    _require_false(input_policy, "live_source_access_granted", errors)
    _require_false(input_policy, "silent_private_data_processing_allowed", errors)
    _require_true(output_policy, "outputs_are_suggestions_only", errors)
    _require_true(output_policy, "required_review", errors)
    _require_false(output_policy, "canonical_truth_allowed", errors)
    _require_false(output_policy, "rights_clearance_allowed", errors)
    _require_false(output_policy, "malware_safety_allowed", errors)
    _require_false(output_policy, "automatic_acceptance_allowed", errors)
    _require_false(cache_policy, "cache_enabled_by_default", errors)
    _require_false(cache_policy, "private_cache_allowed_by_default", errors)
    _require_false(cache_policy, "cache_runtime_implemented", errors)
    _require_true(review_policy, "review_required_for_all_outputs", errors)
    _require_true(review_policy, "master_index_acceptance_requires_review_queue", errors)
    _require_true(evidence_policy, "unsupported_claims_require_review", errors)

    if manifest.get("provider_type") == "remote_api":
        if manifest.get("network_required") is not True:
            errors.append("remote_api providers must declare network_required true.")
        if manifest.get("credential_required") is not True:
            errors.append("remote_api providers must declare credential_required true.")
        _require_true(credential_policy, "explicit_operator_approval_required", errors)

    errors.extend(_scan_payload_for_secrets(manifest))
    return errors


def validate_ai_task_request(request: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TASK_REQUEST_FIELDS - set(request))
    if missing:
        errors.append(f"missing required AI task request fields: {', '.join(missing)}.")
    if request.get("schema_version") != "ai_task_request.v0":
        errors.append("schema_version must be ai_task_request.v0.")
    if request.get("task_type") not in ALLOWED_TASK_TYPES:
        errors.append("task_type is unsupported.")
    if request.get("required_output_type") not in ALLOWED_OUTPUT_TYPES:
        errors.append("required_output_type is unsupported.")
    if request.get("privacy_classification") not in ALLOWED_PRIVACY_CLASSES:
        errors.append("privacy_classification is unsupported.")
    if request.get("user_or_operator_approval_required") is not True:
        errors.append("user_or_operator_approval_required must be true.")
    if not isinstance(request.get("input_refs"), list):
        errors.append("input_refs must be an array.")
    allowed_provider_types = request.get("allowed_provider_types")
    if not isinstance(allowed_provider_types, list):
        errors.append("allowed_provider_types must be an array.")
    elif set(allowed_provider_types) - ALLOWED_PROVIDER_TYPES:
        errors.append("allowed_provider_types contains unsupported provider types.")

    input_policy = _as_mapping(request.get("input_policy"))
    _require_true(input_policy, "private_data_requires_explicit_approval", errors)
    _require_false(input_policy, "local_paths_allowed", errors)
    _require_false(input_policy, "remote_transfer_allowed", errors)
    _require_false(input_policy, "live_fetch_allowed", errors)
    errors.extend(_scan_payload_for_secrets(request))
    return errors


def validate_typed_ai_output(
    output: Mapping[str, Any],
    provider_manifest: Mapping[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TYPED_OUTPUT_FIELDS - set(output))
    if missing:
        errors.append(f"missing required typed AI output fields: {', '.join(missing)}.")
    if output.get("schema_version") != "typed_ai_output.v0":
        errors.append("schema_version must be typed_ai_output.v0.")
    if not output.get("output_id"):
        errors.append("output_id is required.")

    task_type = output.get("task_type")
    output_type = output.get("output_type")
    status = output.get("status")
    if task_type not in ALLOWED_TASK_TYPES:
        errors.append("task_type is unsupported.")
    if task_type in FORBIDDEN_TASK_TYPES:
        errors.append("task_type is a forbidden authority or unsafe task.")
    if output_type not in ALLOWED_OUTPUT_TYPES:
        errors.append("output_type is unsupported.")
    if output_type in FORBIDDEN_AUTHORITY_VALUES:
        errors.append("output_type is a forbidden authority output.")
    if status not in ALLOWED_OUTPUT_STATUSES:
        errors.append("status is unsupported.")
    if status == "accepted_public":
        errors.append("status must not claim accepted_public.")
    if output.get("required_review") is not True:
        errors.append("required_review must be true.")

    prohibited_uses = output.get("prohibited_uses")
    if not isinstance(prohibited_uses, list):
        errors.append("prohibited_uses must be an array.")
        prohibited_set: set[str] = set()
    else:
        prohibited_set = {str(value) for value in prohibited_uses}
    if not REQUIRED_PROHIBITED_USES <= prohibited_set:
        errors.append("prohibited_uses must include canonical_truth, rights_clearance, malware_safety, and automatic_acceptance.")

    limitations = output.get("limitations")
    if not isinstance(limitations, list) or not limitations:
        errors.append("limitations must be a non-empty array.")
    elif not all(isinstance(item, str) and item.strip() for item in limitations):
        errors.append("limitations entries must be non-empty strings.")

    for field in ("source_refs", "evidence_refs"):
        if field in output and not isinstance(output[field], list):
            errors.append(f"{field} must be an array when present.")

    generated_text = output.get("generated_text")
    if generated_text is not None:
        if not isinstance(generated_text, str):
            errors.append("generated_text must be a string when present.")
        elif len(generated_text) > MAX_GENERATED_TEXT_CHARS:
            errors.append(f"generated_text must be {MAX_GENERATED_TEXT_CHARS} characters or fewer.")

    provider_ref = _as_mapping(output.get("provider_ref"))
    created_by = _as_mapping(output.get("created_by_provider"))
    if created_by.get("runtime_call_performed") is not False:
        errors.append("created_by_provider.runtime_call_performed must be false.")
    if provider_ref.get("provider_id") != created_by.get("provider_id"):
        errors.append("created_by_provider.provider_id must match provider_ref.provider_id.")
    if provider_ref.get("provider_version") != created_by.get("provider_version"):
        errors.append("created_by_provider.provider_version must match provider_ref.provider_version.")

    claims = output.get("structured_claims", [])
    if claims is not None and not isinstance(claims, list):
        errors.append("structured_claims must be an array when present.")
    elif isinstance(claims, list):
        for index, claim in enumerate(claims):
            errors.extend(_validate_structured_claim(claim, index))

    if provider_manifest:
        errors.extend(_validate_provider_manifest_alignment(output, provider_manifest))

    privacy_classification = output.get("privacy_classification", "public_safe")
    if privacy_classification not in ALLOWED_PRIVACY_CLASSES and privacy_classification != "local_private_safe":
        errors.append("privacy_classification is unsupported when present.")
    private_path_errors = _scan_payload_for_private_paths(output)
    if private_path_errors:
        if privacy_classification != "local_private" or status in {"suggestion", "candidate", "accepted_for_review"}:
            errors.extend(private_path_errors)

    errors.extend(_scan_payload_for_secrets(output))
    errors.extend(_scan_for_authority_claims(output))
    return errors


def validate_typed_ai_output_file(
    path: str | Path,
    provider_manifest: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    target = Path(path)
    errors: list[str] = []
    output: Any = None
    try:
        output = load_json(target)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"could not parse typed AI output file: {exc}.")
    if isinstance(output, Mapping):
        errors.extend(validate_typed_ai_output(output, provider_manifest=provider_manifest))
    elif output is not None:
        errors.append("typed AI output file must contain a JSON object.")
    return {
        "path": str(target),
        "ok": not errors,
        "output_id": output.get("output_id") if isinstance(output, Mapping) else None,
        "task_type": output.get("task_type") if isinstance(output, Mapping) else None,
        "output_type": output.get("output_type") if isinstance(output, Mapping) else None,
        "errors": errors,
    }


def validate_ai_output_bundle(root: str | Path) -> dict[str, Any]:
    bundle_root = Path(root)
    errors: list[str] = []
    checked_outputs: list[dict[str, Any]] = []
    checked_providers: list[dict[str, Any]] = []
    provider_manifest: Mapping[str, Any] | None = None

    provider_path = bundle_root / "AI_PROVIDER.json"
    if provider_path.exists():
        try:
            loaded_provider = load_json(provider_path)
            if isinstance(loaded_provider, Mapping):
                provider_manifest = loaded_provider
                provider_errors = validate_provider_manifest(loaded_provider)
                checked_providers.append(
                    {
                        "path": str(provider_path),
                        "provider_id": loaded_provider.get("provider_id"),
                        "ok": not provider_errors,
                        "errors": provider_errors,
                    }
                )
                errors.extend(f"{provider_path}: {error}" for error in provider_errors)
            else:
                errors.append(f"{provider_path}: AI_PROVIDER.json must contain a JSON object.")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{provider_path}: could not parse provider manifest: {exc}.")
    else:
        errors.append(f"{provider_path}: AI provider manifest is missing for output bundle validation.")

    examples_dir = bundle_root / "examples"
    if not examples_dir.exists() or not examples_dir.is_dir():
        errors.append(f"{examples_dir}: examples directory is missing.")
    else:
        for path in sorted(examples_dir.glob("*.json")):
            result = validate_typed_ai_output_file(path, provider_manifest=provider_manifest)
            checked_outputs.append(result)
            errors.extend(f"{path}: {error}" for error in result["errors"])
        if not checked_outputs:
            errors.append(f"{examples_dir}: no typed AI output JSON examples found.")

    return {
        "schema_version": "typed_ai_output_bundle_validation.v0",
        "ok": not errors,
        "bundle_root": str(bundle_root),
        "checked_providers": checked_providers,
        "checked_outputs": checked_outputs,
        "passed": sum(1 for item in checked_outputs if item["ok"]),
        "failed": sum(1 for item in checked_outputs if not item["ok"]),
        "errors": errors,
        "model_calls_performed": False,
        "network_performed": False,
        "mutation_performed": False,
        "import_performed": False,
    }


def collect_validation_errors(
    payload: Mapping[str, Any],
    *,
    provider_manifest: Mapping[str, Any] | None = None,
    payload_kind: str = "typed_ai_output",
) -> list[str]:
    if payload_kind == "provider_manifest":
        return validate_provider_manifest(payload)
    if payload_kind == "ai_task_request":
        return validate_ai_task_request(payload)
    if payload_kind == "typed_ai_output":
        return validate_typed_ai_output(payload, provider_manifest=provider_manifest)
    return [f"unsupported payload_kind: {payload_kind}."]


def _validate_provider_manifest_alignment(
    output: Mapping[str, Any],
    provider_manifest: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    provider_errors = validate_provider_manifest(provider_manifest)
    errors.extend(f"provider manifest: {error}" for error in provider_errors)
    provider_ref = _as_mapping(output.get("provider_ref"))
    created_by = _as_mapping(output.get("created_by_provider"))
    provider_id = provider_manifest.get("provider_id")
    provider_version = provider_manifest.get("provider_version")
    provider_type = provider_manifest.get("provider_type")
    if provider_ref.get("provider_id") != provider_id:
        errors.append("provider_ref.provider_id must match provider manifest.")
    if provider_ref.get("provider_version") != provider_version:
        errors.append("provider_ref.provider_version must match provider manifest.")
    if provider_ref.get("provider_type") != provider_type:
        errors.append("provider_ref.provider_type must match provider manifest.")
    if created_by.get("provider_id") != provider_id:
        errors.append("created_by_provider.provider_id must match provider manifest.")
    if created_by.get("provider_version") != provider_version:
        errors.append("created_by_provider.provider_version must match provider manifest.")
    if output.get("task_type") not in set(_as_list(provider_manifest.get("supported_tasks"))):
        errors.append("task_type is not listed in provider supported_tasks.")
    if output.get("output_type") not in set(_as_list(provider_manifest.get("allowed_output_types"))):
        errors.append("output_type is not listed in provider allowed_output_types.")
    if provider_manifest.get("default_enabled") is not False:
        errors.append("provider default_enabled must be false.")
    if provider_type == "remote_api":
        privacy = output.get("privacy_classification")
        remote_private_allowed = _as_mapping(provider_manifest.get("privacy_policy")).get("remote_private_data_transfer_allowed")
        if privacy in {"local_private", "local_private_safe"} and remote_private_allowed is not True:
            errors.append("remote provider output cannot be marked local_private_safe/local_private without explicit remote private-data policy.")
    return errors


def _validate_structured_claim(claim: Any, index: int) -> list[str]:
    errors: list[str] = []
    if not isinstance(claim, Mapping):
        return [f"structured_claims[{index}] must be a JSON object."]
    claim_type = claim.get("claim_type")
    if claim_type not in ALLOWED_OUTPUT_TYPES:
        errors.append(f"structured_claims[{index}].claim_type must be a candidate output/claim type.")
    if claim_type in FORBIDDEN_AUTHORITY_VALUES:
        errors.append(f"structured_claims[{index}].claim_type is a forbidden authority type.")
    if claim.get("review_required") is not True:
        errors.append(f"structured_claims[{index}].review_required must be true.")
    if "evidence_refs" in claim and not isinstance(claim["evidence_refs"], list):
        errors.append(f"structured_claims[{index}].evidence_refs must be an array when present.")
    if "limitations" in claim:
        limitations = claim["limitations"]
        if not isinstance(limitations, list) or not all(isinstance(value, str) and value.strip() for value in limitations):
            errors.append(f"structured_claims[{index}].limitations must be non-empty strings when present.")
    return errors


def _scan_payload_for_secrets(payload: Any) -> list[str]:
    errors: list[str] = []
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            key_text = str(key).lower()
            if key_text in SECRET_KEYS and value not in (False, None, "", [], {}):
                errors.append(f"prohibited secret-like field has a value: {key}.")
            errors.extend(_scan_payload_for_secrets(value))
    elif isinstance(payload, list):
        for value in payload:
            errors.extend(_scan_payload_for_secrets(value))
    elif isinstance(payload, str):
        for pattern in SECRET_VALUE_PATTERNS:
            if pattern.search(payload):
                errors.append("prohibited API key or secret-like value found.")
                break
    return errors


def _scan_payload_for_private_paths(payload: Any) -> list[str]:
    text = json.dumps(payload, sort_keys=True) if not isinstance(payload, str) else payload
    for pattern in PRIVATE_PATH_PATTERNS:
        if pattern.search(text):
            return ["private or absolute local path found."]
    return []


def _scan_for_authority_claims(output: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, value in output.items():
        key_text = str(key).lower()
        if key_text in FORBIDDEN_AUTHORITY_KEYS and value is True:
            errors.append(f"forbidden authority flag must not be true: {key}.")

    generated_text = output.get("generated_text")
    if isinstance(generated_text, str):
        for pattern in FORBIDDEN_AUTHORITY_TEXT_PATTERNS:
            if pattern.search(generated_text):
                errors.append("generated_text appears to claim forbidden truth, rights, malware, or automatic-acceptance authority.")
                break

    for index, claim in enumerate(output.get("structured_claims", []) or []):
        if not isinstance(claim, Mapping):
            continue
        claim_type = str(claim.get("claim_type", ""))
        if claim_type in FORBIDDEN_AUTHORITY_VALUES:
            errors.append(f"structured_claims[{index}].claim_type is a forbidden authority type.")
        claim_value = claim.get("claim_value")
        if isinstance(claim_value, Mapping):
            for key, value in claim_value.items():
                if str(key).lower() in FORBIDDEN_AUTHORITY_KEYS and value is True:
                    errors.append(f"structured_claims[{index}].claim_value contains forbidden authority flag: {key}.")
        claim_text = json.dumps(claim_value, sort_keys=True) if claim_value is not None else ""
        for pattern in FORBIDDEN_AUTHORITY_TEXT_PATTERNS:
            if pattern.search(claim_text):
                errors.append(f"structured_claims[{index}].claim_value appears to claim forbidden authority.")
                break
    return errors


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> Sequence[Any]:
    return value if isinstance(value, list) else []


def _require_true(payload: Mapping[str, Any], field: str, errors: list[str]) -> None:
    if payload.get(field) is not True:
        errors.append(f"{field} must be true.")


def _require_false(payload: Mapping[str, Any], field: str, errors: list[str]) -> None:
    if payload.get(field) is not False:
        errors.append(f"{field} must be false.")
