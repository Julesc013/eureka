"""Validate manual observation protocol files without performing observations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = "control/inventory/observations/manual_observation_policy.json"
TAXONOMY_PATH = "control/inventory/observations/manual_observation_failure_taxonomy.json"
AUDIT_REPORT_PATH = "control/audits/obs0-01-manual-observation-protocol-v0/obs0_01_report.json"
BATCH_PENDING_PATH = "evals/search_usefulness/external_baselines/batches/batch_0/observations/pending_batch_0_observations.json"
DOC_PATHS = (
    "docs/operations/MANUAL_OBSERVATION_PROTOCOL.md",
    "docs/operations/MANUAL_OBSERVATION_ANTI_FABRICATION_CHECKLIST.md",
    "docs/operations/MANUAL_OBSERVATION_FAILURE_TAXONOMY.md",
)
BATCH_DOC_PATHS = (
    "evals/search_usefulness/external_baselines/batches/batch_0/OBSERVATION_PROTOCOL.md",
    "evals/search_usefulness/external_baselines/batches/batch_0/ANTI_FABRICATION_CHECKLIST.md",
    "evals/search_usefulness/external_baselines/batches/batch_0/FAILURE_TAXONOMY.md",
)
VALID_EXAMPLE_PATHS = (
    "examples/manual_observations/valid_no_result_observation_v0.json",
    "examples/manual_observations/valid_observed_result_v0.json",
    "examples/manual_observations/valid_pending_slot_observation_v0.json",
)
INVALID_EXAMPLE_PATH = "examples/manual_observations/invalid_fabricated_observation_v0.json"

REQUIRED_FIELDS = {
    "anti_fabrication_attestation",
    "collection_method",
    "eureka_equivalent_evidence_status",
    "failure_classes",
    "observed_at",
    "observed_limitations",
    "observation_id",
    "observation_status",
    "observer_entered_system_name",
    "query_string",
    "result_rank_or_position",
    "snippet_or_short_public_safe_summary",
    "title",
    "url_or_stable_source_locator",
    "usefulness_note",
}
ANTI_FABRICATION_RULES = {
    "no_api_calls",
    "no_automated_scraping_or_browser_automation",
    "no_copying_from_memory",
    "no_eureka_better_worse_without_comparable_evidence",
    "no_expected_external_result_without_observation",
    "no_inferred_observation_timestamps",
    "no_invented_result_ranks",
    "no_invented_snippets",
    "no_invented_titles",
    "no_invented_urls",
    "no_model_generated_search_summaries_as_observations",
    "no_observed_without_manual_session",
    "no_system_marked_searched_unless_manually_searched",
}
FORBIDDEN_AUTOMATION = {
    "automated_external_search",
    "browser_automation",
    "crawling",
    "external_api_call",
    "live_probe_runtime",
    "model_or_provider_call",
    "scraping",
    "source_connector_runtime",
    "url_fetching_by_script",
}
FAILURE_CLASSES = {
    "ambiguous_need",
    "capability_gap",
    "compatibility_gap",
    "dead_link_or_unavailable",
    "external_baseline_unavailable",
    "extraction_gap",
    "identity_gap",
    "near_match_only",
    "noisy_result_list",
    "not_evaluable",
    "observation_incomplete",
    "query_interpretation_gap",
    "ranking_gap",
    "representation_gap",
    "rights_or_policy_block",
    "source_gap",
    "temporal_version_gap",
}
PRODUCT_BOUNDARY_FIELDS = {
    "automated_external_search",
    "called_external_apis",
    "changed_generated_site_artifacts",
    "changed_product_behavior",
    "changed_public_routes",
    "enabled_accounts",
    "enabled_downloads",
    "enabled_hosting",
    "enabled_live_probes",
    "enabled_source_connectors",
    "enabled_source_sync",
    "enabled_telemetry",
    "enabled_uploads",
    "fabricated_results",
    "marked_pending_as_observed",
    "mutated_master_index",
    "opened_browsers",
    "performed_observations",
    "scraped_external_systems",
}
EXAMPLE_BOUNDARY_FIELDS = {
    "automated_external_search",
    "called_external_apis",
    "fabricated_results",
    "marked_pending_as_observed",
    "opened_browsers",
    "performed_observations",
    "scraped_external_systems",
}
OBSERVED_STATUSES = {"observed"}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate manual observation protocol governance files.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_manual_observation_protocol(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_manual_observation_protocol(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    policy = _load_json(root / POLICY_PATH, errors)
    taxonomy = _load_json(root / TAXONOMY_PATH, errors)
    audit_report = _load_json(root / AUDIT_REPORT_PATH, errors)

    errors.extend(validate_required_docs(root, DOC_PATHS, "docs"))
    errors.extend(validate_required_docs(root, BATCH_DOC_PATHS, "batch docs"))
    errors.extend(validate_policy(policy, POLICY_PATH))
    taxonomy_errors, taxonomy_classes = validate_taxonomy(taxonomy, TAXONOMY_PATH)
    errors.extend(taxonomy_errors)

    for path in VALID_EXAMPLE_PATHS:
        example = _load_json(root / path, errors)
        errors.extend(validate_observation_example(example, path, taxonomy_classes=taxonomy_classes))

    invalid_example = _load_json(root / INVALID_EXAMPLE_PATH, errors)
    invalid_errors = validate_observation_example(
        invalid_example,
        INVALID_EXAMPLE_PATH,
        taxonomy_classes=taxonomy_classes,
    )
    if not invalid_errors:
        errors.append(f"{INVALID_EXAMPLE_PATH}: invalid fabricated example unexpectedly passed")
    elif not any("fabricat" in error.lower() or "manual_session_completed" in error for error in invalid_errors):
        errors.append(f"{INVALID_EXAMPLE_PATH}: invalid example failed for unexpected reasons {invalid_errors}")

    errors.extend(validate_pending_batch(root / BATCH_PENDING_PATH, root))
    errors.extend(validate_audit_report(audit_report, AUDIT_REPORT_PATH))

    return {
        "schema_version": "manual_observation_protocol_validation.v0",
        "status": "valid" if not errors else "invalid",
        "policy": POLICY_PATH,
        "taxonomy": TAXONOMY_PATH,
        "valid_examples": list(VALID_EXAMPLE_PATHS),
        "invalid_example": INVALID_EXAMPLE_PATH,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def validate_required_docs(repo_root: Path, paths: Sequence[str], label: str) -> list[str]:
    errors: list[str] = []
    required_phrases = (
        "manual",
        "no",
        "pending",
    )
    for path in paths:
        full_path = repo_root / path
        if not full_path.is_file():
            errors.append(f"{label}: missing {path}")
            continue
        text = full_path.read_text(encoding="utf-8").lower()
        for phrase in required_phrases:
            if phrase not in text:
                errors.append(f"{path}: missing phrase {phrase!r}")
    return errors


def validate_policy(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "manual_observation_policy.v0":
        errors.append(f"{source}: schema_version must be manual_observation_policy.v0")
    for field in sorted(REQUIRED_FIELDS):
        if field not in _string_items(data.get("required_fields")):
            errors.append(f"{source}: required_fields missing {field}")
    for rule in sorted(ANTI_FABRICATION_RULES):
        if rule not in _string_items(data.get("anti_fabrication_rules")):
            errors.append(f"{source}: anti_fabrication_rules missing {rule}")
    for item in sorted(FORBIDDEN_AUTOMATION):
        if item not in _string_items(data.get("forbidden_automation")):
            errors.append(f"{source}: forbidden_automation missing {item}")
    if data.get("failure_taxonomy_ref") != TAXONOMY_PATH:
        errors.append(f"{source}: failure_taxonomy_ref must be {TAXONOMY_PATH}")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), PRODUCT_BOUNDARY_FIELDS, source))
    return errors


def validate_taxonomy(payload: Any, source: str) -> tuple[list[str], set[str]]:
    data = _mapping(payload)
    errors: list[str] = []
    if data.get("schema_version") != "manual_observation_failure_taxonomy.v0":
        errors.append(f"{source}: schema_version must be manual_observation_failure_taxonomy.v0")
    classes = data.get("classes")
    if not isinstance(classes, Sequence) or isinstance(classes, (str, bytes)):
        return errors + [f"{source}: classes must be an array"], set()
    class_ids: set[str] = set()
    for index, item in enumerate(classes):
        item_data = _mapping(item)
        class_id = item_data.get("class_id")
        if not isinstance(class_id, str):
            errors.append(f"{source}: classes[{index}] missing class_id")
            continue
        if class_id in class_ids:
            errors.append(f"{source}: duplicate class_id {class_id}")
        class_ids.add(class_id)
        for field in ("label", "meaning", "when_to_use", "when_not_to_use", "example_note"):
            if not isinstance(item_data.get(field), str) or not item_data.get(field):
                errors.append(f"{source}: {class_id} missing {field}")
    for class_id in sorted(FAILURE_CLASSES):
        if class_id not in class_ids:
            errors.append(f"{source}: missing failure class {class_id}")
    return errors, class_ids


def validate_observation_example(payload: Any, source: str, *, taxonomy_classes: set[str]) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if not data:
        return [f"{source}: expected JSON object"]
    if data.get("schema_version") != "manual_observation_record.v0":
        errors.append(f"{source}: schema_version must be manual_observation_record.v0")
    status = data.get("observation_status")
    kind = data.get("observation_kind")
    if status not in {"observed", "pending_manual_observation"}:
        errors.append(f"{source}: unsupported observation_status {status!r}")
    if kind not in {"top_result", "no_result", "pending_slot"}:
        errors.append(f"{source}: unsupported observation_kind {kind!r}")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), EXAMPLE_BOUNDARY_FIELDS, source))
    for class_id in _string_items(data.get("failure_classes")):
        if class_id not in taxonomy_classes:
            errors.append(f"{source}: unknown failure class {class_id}")
    attestation = _mapping(data.get("anti_fabrication_attestation"))
    for rule in sorted(ANTI_FABRICATION_RULES):
        if rule not in attestation:
            errors.append(f"{source}: attestation missing {rule}")
        elif attestation[rule] is not True:
            errors.append(f"{source}: attestation.{rule} must be true")
    if status == "pending_manual_observation":
        if data.get("results") not in ([], None):
            errors.append(f"{source}: pending example must not contain results")
        if data.get("observed_at") is not None:
            errors.append(f"{source}: pending example observed_at must be null")
        return errors
    if status in OBSERVED_STATUSES:
        if attestation.get("manual_session_completed") is not True:
            errors.append(f"{source}: manual_session_completed must be true for observed record")
        for field in ("observed_at", "observer_entered_system_name", "query_string"):
            value = data.get(field)
            if not isinstance(value, str) or not value or _looks_placeholder_or_inferred(value):
                errors.append(f"{source}: observed record has invalid {field}")
        if data.get("collection_method") != "manual":
            errors.append(f"{source}: observed record collection_method must be manual")
        if kind == "top_result":
            results = data.get("results")
            if not isinstance(results, Sequence) or isinstance(results, (str, bytes)) or not results:
                errors.append(f"{source}: observed top_result requires non-empty results")
            else:
                for index, result in enumerate(results):
                    errors.extend(validate_result_record(result, f"{source}: results[{index}]", taxonomy_classes))
        if kind == "no_result":
            if data.get("results") != []:
                errors.append(f"{source}: no_result example must have empty results")
            summary = _mapping(data.get("no_result_summary"))
            for field in ("result_count_visible", "searched_scope", "summary", "limitations"):
                if field not in summary:
                    errors.append(f"{source}: no_result_summary missing {field}")
    return errors


def validate_result_record(payload: Any, source: str, taxonomy_classes: set[str]) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if not isinstance(data.get("rank"), int) or data.get("rank") < 1:
        errors.append(f"{source}: rank must be integer >= 1")
    for field in ("title", "url_or_stable_source_locator", "snippet_or_short_public_safe_summary", "usefulness_note"):
        value = data.get(field)
        if not isinstance(value, str) or not value or _looks_placeholder_or_inferred(value):
            errors.append(f"{source}: invalid {field}")
    snippet = data.get("snippet_or_short_public_safe_summary")
    if isinstance(snippet, str) and len(snippet.split()) > 60:
        errors.append(f"{source}: snippet_or_short_public_safe_summary must be short")
    if not _string_items(data.get("observed_limitations")):
        errors.append(f"{source}: observed_limitations must be non-empty")
    if not isinstance(data.get("eureka_equivalent_evidence_status"), str):
        errors.append(f"{source}: missing eureka_equivalent_evidence_status")
    for class_id in _string_items(data.get("failure_classes")):
        if class_id not in taxonomy_classes:
            errors.append(f"{source}: unknown failure class {class_id}")
    return errors


def validate_pending_batch(path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []
    payload = _load_json(path, errors)
    data = _mapping(payload)
    if data.get("observation_status") != "pending_manual_observation":
        errors.append(f"{_rel(path, repo_root)}: batch file must remain pending")
    records = data.get("observations")
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes)):
        return errors + [f"{_rel(path, repo_root)}: observations must be an array"]
    for index, record in enumerate(records):
        item = _mapping(record)
        prefix = f"{_rel(path, repo_root)}#{index}"
        if item.get("observation_status") != "pending_manual_observation":
            errors.append(f"{prefix}: pending slot was marked observed")
        if item.get("top_results") != []:
            errors.append(f"{prefix}: pending slot must not contain top_results")
        if item.get("observed_at") is not None:
            errors.append(f"{prefix}: pending slot observed_at must remain null")
    return errors


def validate_audit_report(payload: Any, source: str) -> list[str]:
    data = _mapping(payload)
    errors: list[str] = []
    if not data:
        return [f"{source}: expected JSON object"]
    if data.get("schema_version") != "obs0_01_report.v0":
        errors.append(f"{source}: schema_version must be obs0_01_report.v0")
    errors.extend(_boundary_false_errors(_mapping(data.get("product_boundary")), PRODUCT_BOUNDARY_FIELDS, source))
    return errors


def _boundary_false_errors(boundary: Mapping[str, Any], fields: set[str], source: str) -> list[str]:
    errors: list[str] = []
    for field in sorted(fields):
        if field not in boundary:
            errors.append(f"{source}: product_boundary missing {field}")
        elif boundary[field] is not False:
            errors.append(f"{source}: product_boundary.{field} must be false")
    return errors


def _looks_placeholder_or_inferred(value: str) -> bool:
    normalized = value.strip().casefold()
    return (
        not normalized
        or normalized.startswith("<")
        or "inferred" in normalized
        or "from memory" in normalized
        or "expected top result" in normalized
        or "model-generated" in normalized
    )


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{path.as_posix()}: missing JSON file")
    except json.JSONDecodeError as exc:
        errors.append(f"{path.as_posix()}: invalid JSON at line {exc.lineno}: {exc.msg}")
    return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str)]


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"validate_manual_observation_protocol: {report['status']}",
        f"schema_version: {report['schema_version']}",
        f"policy: {report['policy']}",
        f"taxonomy: {report['taxonomy']}",
    ]
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
