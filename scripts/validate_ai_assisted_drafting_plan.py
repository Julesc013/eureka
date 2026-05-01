from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.engine.ai.typed_output_validator import (  # noqa: E402
    load_json,
    validate_typed_ai_output_file,
)


SCHEMA_VERSION = "ai_assisted_drafting_plan_validation.v0"
VALIDATOR_ID = "ai_assisted_drafting_plan_validator_v0"

POLICY_PATH = REPO_ROOT / "control" / "inventory" / "ai_providers" / "ai_assisted_drafting_policy.json"
EXAMPLE_ROOT = REPO_ROOT / "examples" / "ai_assisted_drafting" / "minimal_drafting_flow_v0"
PROVIDER_PATH = REPO_ROOT / "examples" / "ai_providers" / "disabled_stub_provider_v0" / "AI_PROVIDER.json"
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "ai-assisted-evidence-drafting-plan-v0"

ARCH_DOC = REPO_ROOT / "docs" / "architecture" / "AI_ASSISTED_EVIDENCE_DRAFTING.md"
REF_DOC = REPO_ROOT / "docs" / "reference" / "AI_ASSISTED_DRAFTING_CONTRACT.md"
AI_PROVIDER_DOC = REPO_ROOT / "docs" / "reference" / "AI_PROVIDER_CONTRACT.md"
TYPED_OUTPUT_DOC = REPO_ROOT / "docs" / "reference" / "TYPED_AI_OUTPUT_CONTRACT.md"
AI_BOUNDARY_DOC = REPO_ROOT / "docs" / "architecture" / "AI_ASSISTANCE_BOUNDARY.md"
AI_OUTPUT_OPS_DOC = REPO_ROOT / "docs" / "operations" / "AI_OUTPUT_VALIDATION.md"
EVIDENCE_DOC = REPO_ROOT / "docs" / "reference" / "EVIDENCE_PACK_CONTRACT.md"
CONTRIBUTION_DOC = REPO_ROOT / "docs" / "reference" / "CONTRIBUTION_PACK_CONTRACT.md"
MASTER_INDEX_DOC = REPO_ROOT / "docs" / "reference" / "MASTER_INDEX_REVIEW_QUEUE_CONTRACT.md"

EXAMPLE_FILES = {
    "flow": "DRAFTING_FLOW.json",
    "input_context": "INPUT_CONTEXT.example.json",
    "typed_output": "TYPED_AI_OUTPUT.example.json",
    "evidence_candidate": "EVIDENCE_CANDIDATE.example.json",
    "contribution_candidate": "CONTRIBUTION_CANDIDATE.example.json",
    "readme": "README.md",
    "checksums": "CHECKSUMS.SHA256",
}
REQUIRED_POLICY_FIELDS = {
    "schema_version",
    "policy_id",
    "status",
    "drafting_runtime_implemented",
    "model_calls_implemented",
    "default_enabled",
    "remote_providers_enabled_by_default",
    "private_data_allowed_by_default",
    "telemetry_enabled_by_default",
    "allowed_drafting_tasks",
    "forbidden_drafting_tasks",
    "allowed_input_contexts",
    "restricted_input_contexts",
    "forbidden_input_contexts",
    "output_validation_required",
    "required_review",
    "evidence_acceptance_automatic",
    "contribution_acceptance_automatic",
    "master_index_acceptance_automatic",
    "public_search_mutation_allowed",
    "local_index_mutation_allowed",
    "privacy_policy",
    "rights_policy",
    "risk_policy",
    "relation_to_pack_contracts",
    "relation_to_review_queue",
    "created_by_slice",
    "notes",
}
REQUIRED_ALLOWED_TASKS = {
    "draft_alias_candidate",
    "draft_metadata_claim_candidate",
    "draft_compatibility_claim_candidate",
    "draft_review_description_claim_candidate",
    "draft_member_path_claim_candidate",
    "draft_source_match_candidate",
    "draft_identity_match_candidate_for_review",
    "draft_explanation_text",
    "draft_absence_explanation",
    "draft_contribution_item_candidate",
    "draft_evidence_pack_record_candidate",
}
REQUIRED_FORBIDDEN_TASKS = {
    "decide_canonical_truth",
    "decide_rights_clearance",
    "decide_malware_safety",
    "decide_source_trust",
    "auto_merge_identity",
    "auto_accept_master_index",
    "auto_mutate_public_search",
    "auto_mutate_local_index",
    "fetch_arbitrary_url",
    "scrape_web",
    "process_private_data_remotely_by_default",
    "extract_credentials",
    "execute_installer",
    "download_artifact",
}
REQUIRED_AUDIT_FILES = {
    "README.md",
    "PLAN_SUMMARY.md",
    "INPUT_CONTEXT_POLICY.md",
    "OUTPUT_MAPPING_POLICY.md",
    "PRIVACY_AND_PROVIDER_POLICY.md",
    "REVIEW_AND_ACCEPTANCE_POLICY.md",
    "EXAMPLE_FLOW_REVIEW.md",
    "RUNTIME_BOUNDARIES.md",
    "RISKS_AND_LIMITATIONS.md",
    "NEXT_STEPS.md",
    "ai_assisted_evidence_drafting_plan_report.json",
}
FALSE_POLICY_FIELDS = {
    "drafting_runtime_implemented",
    "model_calls_implemented",
    "default_enabled",
    "remote_providers_enabled_by_default",
    "private_data_allowed_by_default",
    "telemetry_enabled_by_default",
    "evidence_acceptance_automatic",
    "contribution_acceptance_automatic",
    "master_index_acceptance_automatic",
    "public_search_mutation_allowed",
    "local_index_mutation_allowed",
}
FLOW_FALSE_FIELDS = {
    "drafting_runtime_implemented",
    "model_call_performed",
    "provider_runtime_loaded",
    "private_data_processed",
    "telemetry_performed",
    "evidence_acceptance_performed",
    "contribution_acceptance_performed",
    "public_search_mutated",
    "local_index_mutated",
    "runtime_state_mutated",
    "master_index_mutated",
}
SECRET_VALUE_RE = re.compile(r"(sk-[A-Za-z0-9_-]{8,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)", re.IGNORECASE)
PRIVATE_PATH_RE = re.compile(
    r"([A-Za-z]:[\\/](Users|Documents and Settings|Projects)[\\/]|"
    r"\\\\[^\\/\s]+[\\/][^\\/\s]+[\\/]|"
    r"/(Users|home|var/folders|private/tmp|tmp)/)",
    re.IGNORECASE,
)
POSITIVE_AUTHORITY_PATTERNS = (
    "rights clearance approved",
    "rights clearance complete",
    "rights cleared",
    "malware safety approved",
    "malware safety guaranteed",
    "canonical truth established",
    "accepted as canonical truth",
    "master index accepted",
    "public search updated",
    "local index updated",
    "automatic acceptance approved",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate AI-Assisted Evidence Drafting Plan v0 without model calls.")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_plan()
    stream = stdout or sys.stdout
    if args.json:
        stream.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        stream.write(_format_plain(report))
    return 0 if report["ok"] else 1


def validate_plan() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    policy = _load_mapping(POLICY_PATH, errors)
    example_payloads = _load_example_payloads(errors)
    checksum_status = _validate_checksums(errors)
    typed_output_status = _validate_typed_output(errors)

    if policy:
        _validate_policy(policy, errors)
    if example_payloads:
        _validate_example_flow(example_payloads, errors)
    _validate_docs(errors)
    audit_status = _validate_audit_pack(errors)

    return {
        "schema_version": SCHEMA_VERSION,
        "validator_id": VALIDATOR_ID,
        "ok": not errors,
        "status": "valid" if not errors else "invalid",
        "policy_path": _rel(POLICY_PATH),
        "example_root": _rel(EXAMPLE_ROOT),
        "audit_root": _rel(AUDIT_ROOT),
        "checked_example_files": sorted(EXAMPLE_FILES.values()),
        "checksum_status": checksum_status,
        "typed_output_status": typed_output_status,
        "audit_status": audit_status,
        "errors": errors,
        "warnings": warnings,
        "model_calls_performed": False,
        "network_performed": False,
        "mutation_performed": False,
        "drafting_runtime_implemented": False,
        "provider_runtime_loaded": False,
        "evidence_acceptance_performed": False,
        "contribution_acceptance_performed": False,
        "public_search_mutated": False,
        "local_index_mutated": False,
        "master_index_mutation_performed": False,
    }


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    missing = sorted(REQUIRED_POLICY_FIELDS - set(policy))
    if missing:
        errors.append(f"{_rel(POLICY_PATH)}: missing required fields: {', '.join(missing)}.")
    if policy.get("schema_version") != "ai_assisted_drafting_policy.v0":
        errors.append(f"{_rel(POLICY_PATH)}: schema_version must be ai_assisted_drafting_policy.v0.")
    if policy.get("status") != "planning_only":
        errors.append(f"{_rel(POLICY_PATH)}: status must be planning_only.")
    for field in sorted(FALSE_POLICY_FIELDS):
        if policy.get(field) is not False:
            errors.append(f"{_rel(POLICY_PATH)}: {field} must be false.")
    for field in ("output_validation_required", "required_review"):
        if policy.get(field) is not True:
            errors.append(f"{_rel(POLICY_PATH)}: {field} must be true.")

    allowed = set(_as_str_list(policy.get("allowed_drafting_tasks")))
    forbidden = set(_as_str_list(policy.get("forbidden_drafting_tasks")))
    missing_allowed = sorted(REQUIRED_ALLOWED_TASKS - allowed)
    missing_forbidden = sorted(REQUIRED_FORBIDDEN_TASKS - forbidden)
    if missing_allowed:
        errors.append(f"{_rel(POLICY_PATH)}: missing allowed drafting tasks: {', '.join(missing_allowed)}.")
    if missing_forbidden:
        errors.append(f"{_rel(POLICY_PATH)}: missing forbidden drafting tasks: {', '.join(missing_forbidden)}.")

    privacy = policy.get("privacy_policy")
    if isinstance(privacy, Mapping):
        if privacy.get("remote_private_processing_default") is not False:
            errors.append(f"{_rel(POLICY_PATH)}: remote private processing must be disabled by default.")
        if privacy.get("credential_values_must_never_be_sent_or_logged") is not True:
            errors.append(f"{_rel(POLICY_PATH)}: credential values must never be sent or logged.")
    else:
        errors.append(f"{_rel(POLICY_PATH)}: privacy_policy must be an object.")

    rights = policy.get("rights_policy")
    if not isinstance(rights, Mapping) or rights.get("rights_clearance_authority") is not False:
        errors.append(f"{_rel(POLICY_PATH)}: rights clearance authority must be false.")
    risk = policy.get("risk_policy")
    if not isinstance(risk, Mapping) or risk.get("malware_safety_authority") is not False:
        errors.append(f"{_rel(POLICY_PATH)}: malware safety authority must be false.")


def _validate_example_flow(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    flow = payloads["flow"]
    if flow.get("status") != "synthetic_example":
        errors.append("DRAFTING_FLOW.json: status must be synthetic_example.")
    for field in sorted(FLOW_FALSE_FIELDS):
        if flow.get(field) is not False:
            errors.append(f"DRAFTING_FLOW.json: {field} must be false.")
    if flow.get("required_review") is not True or flow.get("candidate_only") is not True:
        errors.append("DRAFTING_FLOW.json: required_review and candidate_only must be true.")

    input_context = payloads["input_context"]
    if input_context.get("privacy_classification") != "public_safe":
        errors.append("INPUT_CONTEXT.example.json: example context must be public_safe.")
    for field in ("contains_private_paths", "contains_credentials", "contains_long_copyrighted_text", "contains_executable_payload"):
        if input_context.get(field) is not False:
            errors.append(f"INPUT_CONTEXT.example.json: {field} must be false.")
    if input_context.get("remote_provider_default_allowed") is not False:
        errors.append("INPUT_CONTEXT.example.json: remote provider default must be false.")

    typed_output = payloads["typed_output"]
    if typed_output.get("required_review") is not True:
        errors.append("TYPED_AI_OUTPUT.example.json: required_review must be true.")
    if typed_output.get("status") != "candidate":
        errors.append("TYPED_AI_OUTPUT.example.json: status must be candidate.")
    created_by = typed_output.get("created_by_provider")
    if not isinstance(created_by, Mapping) or created_by.get("runtime_call_performed") is not False:
        errors.append("TYPED_AI_OUTPUT.example.json: runtime_call_performed must be false.")

    _validate_candidate(payloads["evidence_candidate"], "EVIDENCE_CANDIDATE.example.json", "accepted_as_evidence", errors)
    _validate_candidate(payloads["contribution_candidate"], "CONTRIBUTION_CANDIDATE.example.json", "accepted_as_contribution", errors)

    for label, payload in payloads.items():
        text = json.dumps(payload, sort_keys=True)
        _scan_text_for_private_or_secret(text, f"{label} example", errors)
        lowered = text.lower()
        for phrase in POSITIVE_AUTHORITY_PATTERNS:
            if phrase in lowered:
                errors.append(f"{label} example: positive authority claim is not allowed: {phrase}.")


def _validate_candidate(payload: Mapping[str, Any], label: str, accepted_field: str, errors: list[str]) -> None:
    if payload.get("required_review") is not True:
        errors.append(f"{label}: required_review must be true.")
    if payload.get("candidate_only") is not True:
        errors.append(f"{label}: candidate_only must be true.")
    if payload.get(accepted_field) is not False:
        errors.append(f"{label}: {accepted_field} must be false.")
    if payload.get("automatic_acceptance") is not False:
        errors.append(f"{label}: automatic_acceptance must be false.")
    if payload.get("review_status") != "review_required":
        errors.append(f"{label}: review_status must be review_required.")
    if payload.get("privacy_classification") not in {"public_safe", "local_private", "review_required"}:
        errors.append(f"{label}: privacy_classification is unsupported.")


def _validate_typed_output(errors: list[str]) -> str:
    output_path = EXAMPLE_ROOT / EXAMPLE_FILES["typed_output"]
    if not output_path.exists():
        errors.append(f"{_rel(output_path)}: typed AI output example is missing.")
        return "unavailable"
    provider_manifest = None
    try:
        provider_manifest = load_json(PROVIDER_PATH)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{_rel(PROVIDER_PATH)}: provider manifest could not be loaded: {exc}.")
    result = validate_typed_ai_output_file(output_path, provider_manifest=provider_manifest)
    if not result.get("ok"):
        for error in result.get("errors", []):
            errors.append(f"{_rel(output_path)}: {error}")
        return "failed"
    return "passed"


def _validate_docs(errors: list[str]) -> None:
    docs = [ARCH_DOC, REF_DOC, AI_PROVIDER_DOC, TYPED_OUTPUT_DOC, AI_BOUNDARY_DOC, AI_OUTPUT_OPS_DOC, EVIDENCE_DOC, CONTRIBUTION_DOC, MASTER_INDEX_DOC]
    required_phrases = {
        "ai-assisted evidence drafting": [ARCH_DOC, REF_DOC],
        "no model calls": [ARCH_DOC, REF_DOC],
        "not truth": [ARCH_DOC, REF_DOC, AI_BOUNDARY_DOC],
        "required review": [ARCH_DOC, REF_DOC],
        "typed output validation": [ARCH_DOC, REF_DOC, TYPED_OUTPUT_DOC, AI_OUTPUT_OPS_DOC],
        "evidence candidates": [ARCH_DOC, REF_DOC, EVIDENCE_DOC],
        "contribution candidates": [ARCH_DOC, REF_DOC, CONTRIBUTION_DOC],
        "master index": [ARCH_DOC, REF_DOC, MASTER_INDEX_DOC],
        "no runtime": [ARCH_DOC, REF_DOC],
    }
    for path in docs:
        if not path.exists():
            errors.append(f"{_rel(path)}: required documentation is missing.")
    for phrase, paths in required_phrases.items():
        for path in paths:
            if path.exists() and phrase not in _compact(path.read_text(encoding="utf-8")):
                errors.append(f"{_rel(path)}: missing required phrase: {phrase}.")


def _validate_audit_pack(errors: list[str]) -> str:
    if not AUDIT_ROOT.exists():
        errors.append(f"{_rel(AUDIT_ROOT)}: audit pack is missing.")
        return "unavailable"
    present = {path.name for path in AUDIT_ROOT.iterdir()}
    missing = sorted(REQUIRED_AUDIT_FILES - present)
    if missing:
        errors.append(f"{_rel(AUDIT_ROOT)}: missing audit files: {', '.join(missing)}.")
        return "failed"
    report_path = AUDIT_ROOT / "ai_assisted_evidence_drafting_plan_report.json"
    report = _load_mapping(report_path, errors)
    if not report:
        return "failed"
    if report.get("status") != "planning_only":
        errors.append(f"{_rel(report_path)}: status must be planning_only.")
    for field in ("drafting_runtime_implemented", "model_calls_implemented", "api_keys_added", "telemetry_added", "public_search_mutated", "local_index_mutated", "master_index_mutated"):
        if report.get(field) is not False:
            errors.append(f"{_rel(report_path)}: {field} must be false.")
    if report.get("outputs_remain_candidates") is not True:
        errors.append(f"{_rel(report_path)}: outputs_remain_candidates must be true.")
    return "passed"


def _load_example_payloads(errors: list[str]) -> dict[str, Mapping[str, Any]]:
    payloads: dict[str, Mapping[str, Any]] = {}
    if not EXAMPLE_ROOT.exists():
        errors.append(f"{_rel(EXAMPLE_ROOT)}: example drafting flow root is missing.")
        return payloads
    for key, filename in EXAMPLE_FILES.items():
        if key in {"readme", "checksums"}:
            continue
        path = EXAMPLE_ROOT / filename
        payload = _load_mapping(path, errors)
        if payload:
            payloads[key] = payload
    required = {"flow", "input_context", "typed_output", "evidence_candidate", "contribution_candidate"}
    missing = sorted(required - set(payloads))
    if missing:
        errors.append(f"{_rel(EXAMPLE_ROOT)}: missing example payloads: {', '.join(missing)}.")
    return payloads


def _validate_checksums(errors: list[str]) -> str:
    checksums_path = EXAMPLE_ROOT / EXAMPLE_FILES["checksums"]
    if not checksums_path.exists():
        errors.append(f"{_rel(checksums_path)}: checksum file is missing.")
        return "unavailable"
    expected: dict[str, str] = {}
    for line in checksums_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 2:
            errors.append(f"{_rel(checksums_path)}: malformed checksum line: {line}.")
            continue
        expected[parts[1]] = parts[0].lower()
    for filename in sorted(value for key, value in EXAMPLE_FILES.items() if key != "checksums"):
        path = EXAMPLE_ROOT / filename
        if not path.exists():
            errors.append(f"{_rel(path)}: checksum-covered file is missing.")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected.get(filename) != digest:
            errors.append(f"{_rel(path)}: checksum mismatch.")
    return "passed" if not any("checksum" in error.lower() for error in errors) else "failed"


def _load_mapping(path: Path, errors: list[str]) -> Mapping[str, Any] | None:
    if not path.exists():
        errors.append(f"{_rel(path)}: file is missing.")
        return None
    try:
        payload = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{_rel(path)}: could not parse JSON: {exc}.")
        return None
    if not isinstance(payload, Mapping):
        errors.append(f"{_rel(path)}: expected a JSON object.")
        return None
    return payload


def _scan_text_for_private_or_secret(text: str, label: str, errors: list[str]) -> None:
    if SECRET_VALUE_RE.search(text):
        errors.append(f"{label}: secret-like value is not allowed.")
    if PRIVATE_PATH_RE.search(text):
        errors.append(f"{label}: private absolute path is not allowed.")


def _as_str_list(value: Any) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _compact(text: str) -> str:
    return " ".join(text.lower().split())


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except (OSError, ValueError):
        return str(path)


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "AI-Assisted Evidence Drafting Plan validation",
        f"status: {report['status']}",
        f"policy_path: {report['policy_path']}",
        f"example_root: {report['example_root']}",
        f"checksum_status: {report['checksum_status']}",
        f"typed_output_status: {report['typed_output_status']}",
        f"audit_status: {report['audit_status']}",
        f"model_calls_performed: {report['model_calls_performed']}",
        f"network_performed: {report['network_performed']}",
        f"mutation_performed: {report['mutation_performed']}",
        f"drafting_runtime_implemented: {report['drafting_runtime_implemented']}",
        f"public_search_mutated: {report['public_search_mutated']}",
        f"local_index_mutated: {report['local_index_mutated']}",
        f"master_index_mutation_performed: {report['master_index_mutation_performed']}",
    ]
    if report["errors"]:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
