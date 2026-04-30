from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
CARD_SCHEMA = REPO_ROOT / "contracts" / "api" / "search_result_card.v0.json"
RESPONSE_SCHEMA = REPO_ROOT / "contracts" / "api" / "search_response.v0.json"
EXAMPLES_DIR = REPO_ROOT / "contracts" / "api" / "examples"
PACK_DIR = REPO_ROOT / "control" / "audits" / "public-search-result-card-contract-v0"
REPORT_PATH = PACK_DIR / "public_search_result_card_contract_report.json"
REFERENCE_DOC = REPO_ROOT / "docs" / "reference" / "PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md"

REQUIRED_PACK_FILES = {
    "README.md",
    "RESULT_CARD_FIELD_MATRIX.md",
    "STABILITY_DECISIONS.md",
    "CLIENT_RENDERING_GUIDANCE.md",
    "ACTION_AND_RISK_GUIDANCE.md",
    "EXAMPLES.md",
    "public_search_result_card_contract_report.json",
}
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "contract_id",
    "stability",
    "result_id",
    "title",
    "record_kind",
    "result_lane",
    "user_cost",
    "source",
    "identity",
    "evidence",
    "compatibility",
    "actions",
    "rights",
    "risk",
    "warnings",
    "limitations",
    "gaps",
}
REQUIRED_LANES = {
    "best_direct_answer",
    "installable_or_usable_now",
    "inside_bundles",
    "official",
    "preservation",
    "community",
    "documentation",
    "mentions_or_traces",
    "absence_or_next_steps",
    "still_searching",
    "other",
}
REQUIRED_SOURCE_CHECKED_AS = {
    "local_index",
    "recorded_fixture",
    "static_summary",
    "future_live_probe",
    "not_checked",
}
REQUIRED_IDENTITY_STATUSES = {
    "exact",
    "candidate",
    "ambiguous",
    "unresolved",
    "synthetic_member",
    "article_segment",
    "unknown",
}
REQUIRED_COMPATIBILITY_STATUSES = {
    "supported",
    "unsupported",
    "unknown",
    "partial",
    "candidate",
    "not_applicable",
}
REQUIRED_ACTION_STATUSES = {"allowed", "blocked", "future_gated", "unavailable"}
READ_ONLY_ACTIONS = {
    "inspect",
    "preview",
    "read",
    "cite",
    "export_manifest",
    "view_provenance",
    "compare",
    "view_source",
    "view_absence_report",
}
UNSAFE_ACTIONS = {
    "download",
    "download_member",
    "mirror",
    "install_handoff",
    "package_manager_handoff",
    "emulator_handoff",
    "vm_handoff",
    "execute",
    "restore_apply",
    "uninstall",
    "rollback",
    "upload",
    "submit_private_source",
}
REQUIRED_BLOCKED_EXAMPLES = {"download", "install_handoff", "execute", "upload"}
REQUIRED_RIGHTS_STATUSES = {
    "unknown",
    "public_metadata_only",
    "source_terms_apply",
    "restricted",
    "review_required",
    "not_applicable",
}
REQUIRED_RISK_VALUES = {
    "none",
    "metadata_only",
    "executable_unknown",
    "executable_present",
    "not_applicable",
}
REQUIRED_SCAN_STATUSES = {"not_scanned", "unavailable", "future", "not_applicable"}
REQUIRED_STABILITY_CATEGORIES = {
    "stable_draft",
    "experimental",
    "volatile",
    "internal",
    "future",
}
FORBIDDEN_PUBLIC_PROPERTY_KEYS = {
    "private_local_path",
    "raw_source_payload",
    "source_credentials",
    "download_url",
    "install_url",
    "execute_url",
    "malware_safe",
    "rights_cleared",
}
REQUIRED_DOC_PHRASES = (
    "contract-only",
    "Local Public Search Runtime v0",
    "local/prototype result",
    "Hosted public exposure still waits",
    "does not enable downloads",
    "installers",
    "execution",
    "uploads",
    "not a production ranking guarantee",
    "must not claim malware safety",
    "must not claim rights clearance",
    "Public Search Safety / Abuse Guard v0",
)
PROHIBITED_POSITIVE_CLAIMS = (
    "public search is live",
    "/api/v1/search is live",
    "result cards are emitted by a live hosted backend",
    "production ranking guarantee",
    "production api stability is guaranteed",
    "malware safe",
    "rights cleared",
    "downloads are enabled",
    "installers are enabled",
    "execution is enabled",
    "uploads are enabled",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Public Search Result Card Contract v0 without network access."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_public_search_result_card_contract()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_public_search_result_card_contract() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    card_schema = _load_json(CARD_SCHEMA, errors)
    response_schema = _load_json(RESPONSE_SCHEMA, errors)
    report = _load_json(REPORT_PATH, errors)
    examples = _load_examples(errors)

    _validate_schema(card_schema, errors)
    _validate_response_alignment(response_schema, errors)
    _validate_pack(report, errors)
    _validate_examples(examples, errors)
    _validate_docs(errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "public_search_result_card_contract_validator_v0",
        "contract_id": "public_search_result_card_contract_v0",
        "schema": _rel(CARD_SCHEMA),
        "response_schema": _rel(RESPONSE_SCHEMA),
        "audit_pack": _rel(PACK_DIR),
        "examples": sorted(_rel(path) for path in examples),
        "required_lanes": sorted(REQUIRED_LANES),
        "unsafe_actions": sorted(UNSAFE_ACTIONS),
        "field_stability_categories": sorted(REQUIRED_STABILITY_CATEGORIES),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_schema(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("contracts/api/search_result_card.v0.json: must be a JSON object.")
        return
    expected_scalars = {
        "x-contract_id": "eureka_public_search_result_card_v0",
        "x-created_by_slice": "public_search_result_card_contract_v0",
        "x-status": "contract_only",
    }
    for key, expected in expected_scalars.items():
        if payload.get(key) != expected:
            errors.append(f"search_result_card.v0.json: {key} must be {expected!r}.")
    required = set(_string_list(payload.get("required")))
    missing_required = sorted(REQUIRED_TOP_LEVEL_FIELDS - required)
    if missing_required:
        errors.append(f"search_result_card.v0.json: missing required fields {missing_required}.")
    properties = _mapping(payload.get("properties"))
    _require_property_keys("search_result_card.v0.json", properties, REQUIRED_TOP_LEVEL_FIELDS, errors)

    lane_enum = set(_string_list(_mapping(properties.get("result_lane")).get("enum")))
    if not REQUIRED_LANES.issubset(lane_enum):
        errors.append(
            "search_result_card.v0.json: result_lane enum missing "
            f"{sorted(REQUIRED_LANES - lane_enum)}."
        )

    defs = _mapping(payload.get("$defs"))
    _validate_user_cost(_mapping(defs.get("user_cost")), errors)
    _validate_source(_mapping(defs.get("source")), errors)
    _validate_identity(_mapping(defs.get("identity")), errors)
    _validate_evidence(_mapping(defs.get("evidence")), errors)
    _validate_compatibility(_mapping(defs.get("compatibility")), errors)
    _validate_actions(_mapping(defs.get("action_entry")), payload, errors)
    _validate_rights(_mapping(defs.get("rights")), errors)
    _validate_risk(_mapping(defs.get("risk")), errors)
    _validate_stability(_mapping(defs.get("stability")), errors)

    public_property_keys = _collect_property_keys(payload)
    forbidden_as_public = sorted(FORBIDDEN_PUBLIC_PROPERTY_KEYS & public_property_keys)
    if forbidden_as_public:
        errors.append(
            "search_result_card.v0.json: forbidden public property keys present "
            f"{forbidden_as_public}."
        )
    forbidden_list = set(_string_list(payload.get("x-forbidden_fields")))
    missing_forbidden = sorted(FORBIDDEN_PUBLIC_PROPERTY_KEYS - forbidden_list)
    if missing_forbidden:
        errors.append(
            "search_result_card.v0.json: x-forbidden_fields missing "
            f"{missing_forbidden}."
        )


def _validate_user_cost(payload: Mapping[str, Any], errors: list[str]) -> None:
    properties = _mapping(payload.get("properties"))
    score = _mapping(properties.get("score"))
    if score.get("minimum") != 0 or score.get("maximum") != 9:
        errors.append("search_result_card.v0.json: user_cost.score must be bounded 0..9.")
    labels = set(_string_list(_mapping(properties.get("label")).get("enum")))
    for label in ("very_low", "low", "medium", "high", "unknown"):
        if label not in labels:
            errors.append(f"search_result_card.v0.json: user_cost.label missing {label}.")
    required = set(_string_list(payload.get("required")))
    for field in ("score", "label", "reasons", "explanation"):
        if field not in required:
            errors.append(f"search_result_card.v0.json: user_cost missing required {field}.")


def _validate_source(payload: Mapping[str, Any], errors: list[str]) -> None:
    properties = _mapping(payload.get("properties"))
    checked_as = set(_string_list(_mapping(properties.get("checked_as")).get("enum")))
    if not REQUIRED_SOURCE_CHECKED_AS.issubset(checked_as):
        errors.append(
            "search_result_card.v0.json: source.checked_as missing "
            f"{sorted(REQUIRED_SOURCE_CHECKED_AS - checked_as)}."
        )
    required = set(_string_list(payload.get("required")))
    for field in ("source_id", "source_family", "source_status", "coverage_depth", "checked_as", "limitations"):
        if field not in required:
            errors.append(f"search_result_card.v0.json: source missing required {field}.")


def _validate_identity(payload: Mapping[str, Any], errors: list[str]) -> None:
    properties = _mapping(payload.get("properties"))
    statuses = set(_string_list(_mapping(properties.get("identity_status")).get("enum")))
    if not REQUIRED_IDENTITY_STATUSES.issubset(statuses):
        errors.append(
            "search_result_card.v0.json: identity_status missing "
            f"{sorted(REQUIRED_IDENTITY_STATUSES - statuses)}."
        )
    for field in (
        "public_target_ref",
        "resolved_resource_id",
        "object_id",
        "release_or_state_id",
        "representation_id",
        "member_target_ref",
        "native_source_id",
    ):
        if field not in properties:
            errors.append(f"search_result_card.v0.json: identity missing {field}.")


def _validate_evidence(payload: Mapping[str, Any], errors: list[str]) -> None:
    required = set(_string_list(payload.get("required")))
    for field in ("evidence_count", "summaries", "provenance_notes", "missing_evidence"):
        if field not in required:
            errors.append(f"search_result_card.v0.json: evidence missing required {field}.")
    summary = _mapping(_mapping(_mapping(payload.get("properties")).get("summaries")).get("items"))
    if summary.get("$ref") == "#/$defs/evidence_summary":
        schema = _load_json(CARD_SCHEMA, errors)
        summary = _mapping(_mapping(_mapping(schema).get("$defs")).get("evidence_summary"))
    summary_props = _mapping(summary.get("properties"))
    for field in ("evidence_id", "evidence_kind", "source_id", "locator", "snippet", "confidence"):
        if field not in summary_props:
            errors.append(f"search_result_card.v0.json: evidence summary missing {field}.")


def _validate_compatibility(payload: Mapping[str, Any], errors: list[str]) -> None:
    properties = _mapping(payload.get("properties"))
    statuses = set(_string_list(_mapping(properties.get("status")).get("enum")))
    if not REQUIRED_COMPATIBILITY_STATUSES.issubset(statuses):
        errors.append(
            "search_result_card.v0.json: compatibility.status missing "
            f"{sorted(REQUIRED_COMPATIBILITY_STATUSES - statuses)}."
        )
    for field in ("target_platforms", "architecture", "evidence_summaries", "confidence", "caveats", "unknowns"):
        if field not in properties:
            errors.append(f"search_result_card.v0.json: compatibility missing {field}.")


def _validate_actions(action_entry: Mapping[str, Any], schema: Mapping[str, Any], errors: list[str]) -> None:
    properties = _mapping(action_entry.get("properties"))
    statuses = set(_string_list(_mapping(properties.get("status")).get("enum")))
    if not REQUIRED_ACTION_STATUSES.issubset(statuses):
        errors.append(
            "search_result_card.v0.json: action status enum missing "
            f"{sorted(REQUIRED_ACTION_STATUSES - statuses)}."
        )
    action_ids = set(_string_list(_mapping(properties.get("action_id")).get("enum")))
    missing_read = sorted(READ_ONLY_ACTIONS - action_ids)
    missing_unsafe = sorted(UNSAFE_ACTIONS - action_ids)
    if missing_read:
        errors.append(f"search_result_card.v0.json: action_id enum missing allowed actions {missing_read}.")
    if missing_unsafe:
        errors.append(f"search_result_card.v0.json: action_id enum missing unsafe actions {missing_unsafe}.")
    if set(_string_list(schema.get("x-default_allowed_actions"))) != READ_ONLY_ACTIONS:
        errors.append("search_result_card.v0.json: x-default_allowed_actions must list read-only actions.")
    blocked_or_future = set(_string_list(schema.get("x-blocked_or_future_gated_actions")))
    if not UNSAFE_ACTIONS.issubset(blocked_or_future):
        errors.append(
            "search_result_card.v0.json: x-blocked_or_future_gated_actions missing "
            f"{sorted(UNSAFE_ACTIONS - blocked_or_future)}."
        )


def _validate_rights(payload: Mapping[str, Any], errors: list[str]) -> None:
    properties = _mapping(payload.get("properties"))
    statuses = set(_string_list(_mapping(properties.get("rights_status")).get("enum")))
    if not REQUIRED_RIGHTS_STATUSES.issubset(statuses):
        errors.append(
            "search_result_card.v0.json: rights_status missing "
            f"{sorted(REQUIRED_RIGHTS_STATUSES - statuses)}."
        )
    distribution = set(_mapping(properties.get("distribution_allowed")).get("enum", []))
    if not {True, False, "unknown"}.issubset(distribution):
        errors.append("search_result_card.v0.json: distribution_allowed must allow true, false, and unknown.")


def _validate_risk(payload: Mapping[str, Any], errors: list[str]) -> None:
    properties = _mapping(payload.get("properties"))
    risk_values = set(_string_list(_mapping(properties.get("executable_risk")).get("enum")))
    if not REQUIRED_RISK_VALUES.issubset(risk_values):
        errors.append(
            "search_result_card.v0.json: executable_risk missing "
            f"{sorted(REQUIRED_RISK_VALUES - risk_values)}."
        )
    scans = set(_string_list(_mapping(properties.get("malware_scan_status")).get("enum")))
    if not REQUIRED_SCAN_STATUSES.issubset(scans):
        errors.append(
            "search_result_card.v0.json: malware_scan_status missing "
            f"{sorted(REQUIRED_SCAN_STATUSES - scans)}."
        )


def _validate_stability(payload: Mapping[str, Any], errors: list[str]) -> None:
    required = set(_string_list(payload.get("required")))
    if required != REQUIRED_STABILITY_CATEGORIES:
        errors.append("search_result_card.v0.json: stability block must require all stability categories.")
    properties = _mapping(payload.get("properties"))
    for category in REQUIRED_STABILITY_CATEGORIES:
        if category not in properties:
            errors.append(f"search_result_card.v0.json: stability missing {category}.")


def _validate_response_alignment(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("contracts/api/search_response.v0.json: must be a JSON object.")
        return
    if payload.get("x-result_card_schema") != "contracts/api/search_result_card.v0.json":
        errors.append("search_response.v0.json: x-result_card_schema must point to the result-card schema.")
    if payload.get("x-results_are_public_search_result_cards") is not True:
        errors.append("search_response.v0.json: must mark results as public search result cards.")
    result = _mapping(_mapping(payload.get("$defs")).get("result"))
    props = _mapping(result.get("properties"))
    for field in (
        "source",
        "identity",
        "rights",
        "risk",
        "warnings",
        "gaps",
        "member",
        "representation",
        "parent_lineage",
    ):
        if field not in props:
            errors.append(f"search_response.v0.json: result properties missing result-card field {field}.")
    prohibited = set(_string_list(payload.get("x-prohibited_result_fields")))
    for field in ("download_url", "install_url", "private_local_path", "raw_source_payload"):
        if field not in prohibited:
            errors.append(f"search_response.v0.json: x-prohibited_result_fields missing {field}.")


def _validate_pack(report: Any, errors: list[str]) -> None:
    if not PACK_DIR.is_dir():
        errors.append("public search result-card audit pack is missing.")
        return
    present = {path.name for path in PACK_DIR.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_PACK_FILES - present)
    if missing:
        errors.append(f"public search result-card audit pack missing files {missing}.")
    if not isinstance(report, Mapping):
        errors.append("public_search_result_card_contract_report.json: must be a JSON object.")
        return
    expected = {
        "report_id": "public_search_result_card_contract_v0",
        "created_by_slice": "public_search_result_card_contract_v0",
        "status": "implemented_contract_only",
        "schema": "contracts/api/search_result_card.v0.json",
        "response_schema": "contracts/api/search_response.v0.json",
        "documentation": "docs/reference/PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md",
        "next_recommended_milestone": "Public Search Safety / Abuse Guard v0",
    }
    for key, expected_value in expected.items():
        if report.get(key) != expected_value:
            errors.append(f"public_search_result_card_contract_report.json: {key} must be {expected_value!r}.")
    report_lanes = set(_string_list(report.get("required_result_lanes")))
    if not REQUIRED_LANES.issubset(report_lanes):
        errors.append("public_search_result_card_contract_report.json: required_result_lanes is incomplete.")
    categories = set(_string_list(report.get("field_stability_categories")))
    if categories != REQUIRED_STABILITY_CATEGORIES:
        errors.append("public_search_result_card_contract_report.json: field stability categories are incomplete.")

    matrix_text = (PACK_DIR / "RESULT_CARD_FIELD_MATRIX.md").read_text(encoding="utf-8")
    for phrase in ("stable_draft", "experimental", "volatile", "internal", "future"):
        if phrase not in matrix_text:
            errors.append(f"RESULT_CARD_FIELD_MATRIX.md: missing stability phrase {phrase}.")


def _validate_examples(examples: Mapping[Path, Any], errors: list[str]) -> None:
    if len(examples) < 5:
        errors.append("contracts/api/examples: expected at least five result-card examples.")
    seen_unsafe_blocked_or_future: set[str] = set()
    for path, payload in examples.items():
        if not isinstance(payload, Mapping):
            errors.append(f"{_rel(path)}: example must be a JSON object.")
            continue
        if payload.get("contract_id") != "eureka_public_search_result_card_v0":
            errors.append(f"{_rel(path)}: contract_id is unexpected.")
        missing = sorted(REQUIRED_TOP_LEVEL_FIELDS - set(payload))
        if missing:
            errors.append(f"{_rel(path)}: missing required fields {missing}.")
        if payload.get("result_lane") not in REQUIRED_LANES:
            errors.append(f"{_rel(path)}: result_lane is not recognized.")

        actions = _mapping(payload.get("actions"))
        allowed = _action_ids(actions.get("allowed"))
        blocked = _action_ids(actions.get("blocked"))
        future = _action_ids(actions.get("future_gated"))
        unsafe_allowed = sorted(UNSAFE_ACTIONS & allowed)
        if unsafe_allowed:
            errors.append(f"{_rel(path)}: unsafe actions are allowed {unsafe_allowed}.")
        seen_unsafe_blocked_or_future.update((blocked | future) & UNSAFE_ACTIONS)

        rights = _mapping(payload.get("rights"))
        if rights.get("rights_status") in {"cleared", "licensed"}:
            errors.append(f"{_rel(path)}: rights block must not claim clearance.")
        risk = _mapping(payload.get("risk"))
        if risk.get("malware_scan_status") in {"clean", "passed", "safe"}:
            errors.append(f"{_rel(path)}: risk block must not claim malware safety.")
    missing_demonstrated = sorted(REQUIRED_BLOCKED_EXAMPLES - seen_unsafe_blocked_or_future)
    if missing_demonstrated:
        errors.append(
            "contracts/api/examples: examples must demonstrate blocked/future unsafe actions "
            f"{missing_demonstrated}."
        )


def _validate_docs(errors: list[str]) -> None:
    if not REFERENCE_DOC.is_file():
        errors.append("docs/reference/PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md: missing.")
        return
    text = REFERENCE_DOC.read_text(encoding="utf-8")
    folded = text.casefold()
    for phrase in REQUIRED_DOC_PHRASES:
        if phrase.casefold() not in folded:
            errors.append(f"PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md: missing phrase {phrase!r}.")
    for claim in PROHIBITED_POSITIVE_CLAIMS:
        allowed_negations = {
            f"not a {claim}",
            f"does not {claim}",
            f"does not claim {claim}",
            f"must not claim {claim}",
            f"does not claim {claim}ty",
            f"must not claim {claim}ty",
        }
        if claim in folded and not any(negation in folded for negation in allowed_negations):
            errors.append(f"PUBLIC_SEARCH_RESULT_CARD_CONTRACT.md: contains prohibited claim {claim!r}.")


def _load_examples(errors: list[str]) -> dict[Path, Any]:
    examples: dict[Path, Any] = {}
    if not EXAMPLES_DIR.is_dir():
        errors.append("contracts/api/examples: examples directory is missing.")
        return examples
    for path in sorted(EXAMPLES_DIR.glob("search_result_card_*.v0.json")):
        examples[path] = _load_json(path, errors)
    return examples


def _load_json(path: Path, errors: list[str]) -> Any:
    if not path.is_file():
        errors.append(f"{_rel(path)}: missing.")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON at line {exc.lineno}: {exc.msg}.")
        return None


def _collect_property_keys(payload: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(payload, Mapping):
        properties = payload.get("properties")
        if isinstance(properties, Mapping):
            keys.update(str(key) for key in properties)
            for value in properties.values():
                keys.update(_collect_property_keys(value))
        for key in ("$defs", "items", "anyOf", "oneOf", "allOf"):
            value = payload.get(key)
            if isinstance(value, Mapping):
                keys.update(_collect_property_keys(value))
            elif isinstance(value, list):
                for item in value:
                    keys.update(_collect_property_keys(item))
    return keys


def _require_property_keys(
    label: str, payload: Mapping[str, Any], required: set[str], errors: list[str]
) -> None:
    missing = sorted(required - set(payload))
    if missing:
        errors.append(f"{label}: properties missing {missing}.")


def _action_ids(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    ids: set[str] = set()
    for item in value:
        if isinstance(item, Mapping) and isinstance(item.get("action_id"), str):
            ids.add(item["action_id"])
    return ids


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    return [item for item in value] if isinstance(value, list) and all(isinstance(item, str) for item in value) else []


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"status: {report['status']}",
        f"contract_id: {report['contract_id']}",
        f"schema: {report['schema']}",
        f"response_schema: {report['response_schema']}",
        f"audit_pack: {report['audit_pack']}",
        f"examples: {len(report['examples'])}",
    ]
    if report["errors"]:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
