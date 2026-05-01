#!/usr/bin/env python3
"""Validate the Post-P49 Platform Audit v0 pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = ROOT / "control" / "audits" / "post-p49-platform-audit-v0"
REPORT_PATH = AUDIT_ROOT / "post_p49_platform_audit_report.json"

CLASSIFICATIONS = {
    "implemented_runtime",
    "implemented_local_prototype",
    "implemented_static_artifact",
    "contract_only",
    "planning_only",
    "fixture_only",
    "manual_pending",
    "approval_gated",
    "operator_gated",
    "deferred",
    "blocked",
}

REQUIRED_FILES = [
    "README.md",
    "EXECUTIVE_SUMMARY.md",
    "MILESTONE_STATUS.md",
    "REPOSITORY_SHAPE_STATUS.md",
    "STATIC_PUBLICATION_STATUS.md",
    "PUBLIC_SEARCH_STATUS.md",
    "SEARCH_USEFULNESS_STATUS.md",
    "SOURCE_COVERAGE_STATUS.md",
    "EXTERNAL_BASELINE_STATUS.md",
    "PACK_AND_HIVE_MIND_STATUS.md",
    "PACK_IMPORT_AND_STAGING_STATUS.md",
    "AI_ASSISTANCE_STATUS.md",
    "QUERY_INTELLIGENCE_GAP_STATUS.md",
    "LIVE_BACKEND_AND_HOSTING_STATUS.md",
    "LIVE_PROBE_AND_CONNECTOR_STATUS.md",
    "NATIVE_RELAY_SNAPSHOT_STATUS.md",
    "RUST_STATUS.md",
    "SECURITY_PRIVACY_RIGHTS_OPS_STATUS.md",
    "LANGUAGE_AND_RUNTIME_STRATEGY.md",
    "COMMAND_RESULTS.md",
    "RISK_REGISTER.md",
    "BLOCKERS.md",
    "HUMAN_OPERATED_WORK.md",
    "APPROVAL_GATED_WORK.md",
    "OPERATOR_GATED_WORK.md",
    "DO_NOT_DO_NEXT.md",
    "NEXT_20_MILESTONES.md",
    "post_p49_platform_audit_report.json",
]

REQUIRED_TOP_LEVEL_KEYS = [
    "audit_id",
    "created_by_slice",
    "repo_head",
    "origin_main_head",
    "branch",
    "worktree_status",
    "audit_scope",
    "command_results",
    "milestone_status",
    "subsystem_status",
    "current_counts",
    "search_usefulness_summary",
    "archive_eval_summary",
    "external_baseline_summary",
    "github_pages_status",
    "public_search_status",
    "pack_validation_status",
    "staging_status",
    "ai_status",
    "query_intelligence_gap_status",
    "security_privacy_rights_ops_status",
    "language_runtime_strategy",
    "known_blockers",
    "human_operated_work",
    "approval_gated_work",
    "operator_gated_work",
    "deferred_work",
    "do_not_do_next",
    "next_20_milestones",
    "recommended_next_branch",
    "notes",
]

REQUIRED_SUBSYSTEMS = [
    "repository_shape",
    "static_site",
    "github_pages",
    "generated_public_data",
    "lite_text_files",
    "static_resolver_demos",
    "public_search_contracts",
    "public_search_local_runtime",
    "public_search_static_handoff",
    "public_search_rehearsal",
    "hosted_public_search",
    "archive_resolution_evals",
    "search_usefulness_audit",
    "source_expansion_v2",
    "search_usefulness_delta_v2",
    "external_baselines",
    "manual_observation_batch_0",
    "source_registry",
    "fixture_sources",
    "recorded_sources",
    "live_connectors",
    "source_cache_evidence_ledger",
    "source_pack_contract",
    "evidence_pack_contract",
    "index_pack_contract",
    "contribution_pack_contract",
    "master_index_review_queue_contract",
    "pack_validator_aggregator",
    "validate_only_pack_import_tool",
    "pack_import_planning",
    "local_quarantine_staging_model",
    "staging_report_path_contract",
    "local_staging_manifest_format",
    "staged_pack_inspector",
    "pack_import_runtime",
    "local_staging_runtime",
    "ai_provider_contract",
    "typed_ai_output_validator",
    "ai_assisted_evidence_drafting_plan",
    "ai_runtime",
    "ai_public_search_integration",
    "query_observation_contract",
    "shared_query_result_cache",
    "miss_ledger",
    "search_need_record",
    "probe_queue",
    "candidate_index",
    "candidate_promotion_policy",
    "known_absence_page",
    "query_privacy_poisoning_guard",
    "demand_dashboard",
    "public_query_learning_runtime",
    "hosted_backend",
    "deployment_config",
    "production_ops",
    "dynamic_hosting",
    "live_probe_gateway",
    "ia_metadata_connector",
    "wayback_cdx_memento_connector",
    "github_releases_connector",
    "pypi_connector",
    "npm_connector",
    "software_heritage_connector",
    "wikidata_open_library_connector",
    "connector_health_quota_dashboard",
    "static_snapshot_format",
    "snapshot_consumer_contract",
    "snapshot_tooling",
    "native_client_contracts",
    "native_runtime",
    "windows_7_winforms_plan",
    "relay_design_prototype_plan",
    "relay_runtime",
    "offline_support",
    "rust_source_registry_parity",
    "rust_query_planner_parity",
    "rust_local_index_parity",
    "rust_runtime_wiring",
    "cargo_toolchain",
    "security_docs",
    "privacy_policy",
    "rights_takedown_process",
    "malware_risk_policy",
    "source_abuse_policy",
    "vulnerability_disclosure",
    "incident_response",
    "backup_restore_plan",
    "observability_plan",
    "deployment_rollback_plan",
    "cost_quota_governance",
    "governance_role_model",
]

FORBIDDEN_POSITIVE_CLAIMS = [
    "eureka is production ready",
    "eureka is production-ready",
    "production ready: true",
    "production_ready\": true",
    "github pages deployment succeeded",
    "github pages deployment success: true",
    "hosted public search is available",
    "hosted public search is live",
    "hosted search is live",
    "live probes are enabled",
    "live probe runtime is implemented",
    "ai runtime is implemented",
    "model calls are enabled",
    "external baselines were observed",
]


def _load_report(errors: list[str]) -> dict[str, Any]:
    if not REPORT_PATH.exists():
        errors.append("post_p49_platform_audit_report.json missing")
        return {}
    try:
        with REPORT_PATH.open("r", encoding="utf-8") as handle:
            report = json.load(handle)
    except Exception as exc:  # pragma: no cover - parser text is not stable
        errors.append(f"post_p49_platform_audit_report.json did not parse: {exc}")
        return {}
    if not isinstance(report, dict):
        errors.append("post_p49_platform_audit_report.json must contain an object")
        return {}
    return report


def _audit_text() -> str:
    if not AUDIT_ROOT.exists():
        return ""
    parts: list[str] = []
    for path in AUDIT_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".txt"}:
            parts.append(path.read_text(encoding="utf-8").lower())
    return "\n".join(parts)


def _walk_classifications(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            if key == "classification" or key.endswith("_classification"):
                if child not in CLASSIFICATIONS:
                    errors.append(f"invalid classification at {child_path}: {child!r}")
            _walk_classifications(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_classifications(child, f"{path}[{index}]", errors)


def validate() -> dict[str, Any]:
    errors: list[str] = []

    if not AUDIT_ROOT.exists():
        errors.append(f"audit pack missing: {AUDIT_ROOT.relative_to(ROOT)}")
    else:
        for name in REQUIRED_FILES:
            if not (AUDIT_ROOT / name).exists():
                errors.append(f"required audit file missing: {name}")

    report = _load_report(errors)
    if report:
        for key in REQUIRED_TOP_LEVEL_KEYS:
            if key not in report:
                errors.append(f"report missing top-level key: {key}")

        _walk_classifications(report, "", errors)

        subsystems = report.get("subsystem_status", {})
        if not isinstance(subsystems, dict):
            errors.append("subsystem_status must be an object")
        else:
            for key in REQUIRED_SUBSYSTEMS:
                if key not in subsystems:
                    errors.append(f"subsystem_status missing key: {key}")

        command_results = report.get("command_results")
        if not isinstance(command_results, list) or not command_results:
            errors.append("command_results must be a non-empty list")

        next_20 = report.get("next_20_milestones")
        if not isinstance(next_20, list) or len(next_20) != 20:
            errors.append("next_20_milestones must contain exactly 20 entries")

        for list_key in [
            "do_not_do_next",
            "human_operated_work",
            "approval_gated_work",
            "operator_gated_work",
        ]:
            if not isinstance(report.get(list_key), list) or not report.get(list_key):
                errors.append(f"{list_key} must be a non-empty list")

        external = report.get("external_baseline_summary", {})
        if external.get("global_observed_slots") != 0:
            errors.append("external_baseline_summary must record zero observed slots")
        if external.get("global_pending_slots", 0) <= 0:
            errors.append("external_baseline_summary must record pending slots")

        public_search = report.get("public_search_status", {})
        if public_search.get("hosted_public_search") is not False:
            errors.append("public_search_status must record hosted_public_search false")

        ai = report.get("ai_status", {})
        if ai.get("model_calls_performed") is not False:
            errors.append("ai_status must record model_calls_performed false")
        if ai.get("provider_runtime_implemented") is not False:
            errors.append("ai_status must record provider_runtime_implemented false")

        query_gap = report.get("query_intelligence_gap_status", {})
        if query_gap.get("public_query_learning_runtime") is not False:
            errors.append("query intelligence gap must record no public query learning runtime")

    text = _audit_text()
    for phrase in FORBIDDEN_POSITIVE_CLAIMS:
        if phrase in text:
            errors.append(f"forbidden positive claim found: {phrase}")

    return {
        "check_id": "post_p49_platform_audit_v0",
        "audit_root": str(AUDIT_ROOT.relative_to(ROOT)),
        "required_file_count": len(REQUIRED_FILES),
        "classification_values": sorted(CLASSIFICATIONS),
        "errors": errors,
        "status": "passed" if not errors else "failed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable validation result.")
    args = parser.parse_args()

    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["status"] == "passed":
        print(
            "post-p49 platform audit validation passed: "
            f"{result['required_file_count']} required files checked"
        )
    else:
        print("post-p49 platform audit validation failed:")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
