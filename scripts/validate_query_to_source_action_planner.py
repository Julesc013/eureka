#!/usr/bin/env python3
"""Validate QUERY-TO-SOURCE-ACTION-PLANNER-00 artifacts and runtime behavior."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.search.query_plan import DOMAIN_PACKS, INTENTS, SOURCE_FAMILIES, plan_query_to_source_actions


TASK = "QUERY-TO-SOURCE-ACTION-PLANNER-00"
REQUIRED_FILES = (
    "contracts/search/query_plan/README.md",
    "contracts/search/query_plan/query_to_source_action_plan.v0.json",
    "runtime/search/__init__.py",
    "runtime/search/query_plan/__init__.py",
    "runtime/search/query_plan/planner.py",
    "scripts/eureka_query_plan.py",
    "scripts/validate_query_to_source_action_planner.py",
    "examples/query_plans/new_york_1993_d_theater_hd_demo_tape_original_source.json",
    "examples/query_plans/windows_7_compatible_portable_utilities_not_windows_7_iso.json",
    "examples/query_plans/stylewriter_2500_mac_os_8_driver.json",
    "examples/query_plans/directx_sdk_june_2010_offline_installer.json",
    "examples/query_plans/ambiguous_query_example.json",
    "docs/architecture/QUERY_TO_SOURCE_ACTION_PLANNER.md",
    "control/audits/query-to-source-action-planner-00-v0/README.md",
    "control/audits/query-to-source-action-planner-00-v0/query_to_source_action_planner_report.json",
)

EXAMPLE_EXPECTATIONS = {
    "New York 1993 D-Theater HD demo tape original source": (
        "find_frontier_resolution_media",
        "frontier_resolution_media",
        ("internet_archive_metadata", "wayback_cdx_metadata", "wikidata_metadata"),
    ),
    "Windows 7-compatible portable utilities, not Windows 7 ISO": (
        "find_software",
        "legacy_software",
        ("internet_archive_metadata", "github_releases_metadata", "package_registry_metadata"),
    ),
    "StyleWriter 2500 Mac OS 8 driver": (
        "find_driver_or_support_media",
        "driver_support_media",
        ("internet_archive_metadata", "wayback_cdx_metadata"),
    ),
    "DirectX SDK June 2010 offline installer": (
        "find_exact_artifact",
        "legacy_software",
        ("internet_archive_metadata",),
    ),
    "best apps": (
        "ambiguous_query",
        "general_archive_metadata",
        ("internet_archive_metadata",),
    ),
}

FALSE_SAFETY_FIELDS = (
    "accepted_truth_created",
    "source_cache_mutated",
    "candidate_index_mutated",
    "reviewed_index_mutated",
    "master_index_mutated",
    "public_index_mutated",
    "download_performed",
    "upload_performed",
    "extraction_executed",
    "install_handoff_enabled",
    "model_provider_used",
    "deployment_performed",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = validate(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"query-to-source-action planner validation: {report['status']}", file=stdout)
        for error in report["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if report["status"] == "pass" else 1


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"{rel}: required file is missing")

    contract = _load_json(root / "contracts/search/query_plan/query_to_source_action_plan.v0.json", errors)
    if contract.get("contract_id") != "query_to_source_action_plan.v0":
        errors.append("query_to_source_action_plan contract_id must be query_to_source_action_plan.v0")
    _require_enum(contract, ("properties", "intent", "enum"), INTENTS, errors, "intent enum")
    _require_enum(contract, ("properties", "domain_pack", "enum"), DOMAIN_PACKS, errors, "domain_pack enum")
    _require_enum(
        contract,
        ("properties", "source_families", "items", "enum"),
        SOURCE_FAMILIES,
        errors,
        "source_families enum",
    )

    plans: dict[str, Mapping[str, Any]] = {}
    for query, (intent, domain_pack, source_families) in EXAMPLE_EXPECTATIONS.items():
        plan = plan_query_to_source_actions(query)
        plans[query] = plan
        _validate_plan_shape(plan, errors)
        if plan.get("intent") != intent:
            errors.append(f"{query}: expected intent {intent}, got {plan.get('intent')}")
        if plan.get("domain_pack") != domain_pack:
            errors.append(f"{query}: expected domain_pack {domain_pack}, got {plan.get('domain_pack')}")
        missing_sources = set(source_families) - set(plan.get("source_families", []))
        if missing_sources:
            errors.append(f"{query}: missing source families {sorted(missing_sources)}")
        _validate_example_file(root, query, plan, errors)

    windows_plan = plans["Windows 7-compatible portable utilities, not Windows 7 ISO"]
    windows_rewrite = str(windows_plan.get("source_query_rewrites", {}).get("archive_org_metadata", ""))
    if "-iso" not in windows_rewrite and '-"iso"' not in windows_rewrite:
        errors.append("Windows 7 utility rewrite must suppress ISO results")
    if "portable" not in windows_rewrite.casefold():
        errors.append("Windows 7 utility rewrite must preserve portable utility intent")

    frontier_rewrite = str(
        plans["New York 1993 D-Theater HD demo tape original source"]
        .get("source_query_rewrites", {})
        .get("archive_org_metadata", "")
    )
    for term in ("D-Theater", "D-VHS", "JVC", "Hi-Vision", "MUSE"):
        if term.casefold() not in frontier_rewrite.casefold():
            errors.append(f"frontier media rewrite missing {term}")

    return {
        "schema_version": "query_to_source_action_planner_validation.v0",
        "task": TASK,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "intent_count": len(INTENTS),
        "domain_pack_count": len(DOMAIN_PACKS),
        "source_family_count": len(SOURCE_FAMILIES),
        "example_count": len(EXAMPLE_EXPECTATIONS),
        "accepted_truth_created": False,
        "candidate_index_mutated": False,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
    }


def _validate_plan_shape(plan: Mapping[str, Any], errors: list[str]) -> None:
    required = (
        "schema_version",
        "planner_id",
        "plan_id",
        "normalized_query",
        "intent",
        "domain_pack",
        "source_families",
        "source_query_rewrites",
        "candidate_suppressions",
        "candidate_lane_expectations",
        "source_actions",
        "work_units",
        "result_lane_plans",
        "review_handoff_plans",
        "explanation",
        "safety",
        "non_claims",
    )
    for field in required:
        if field not in plan:
            errors.append(f"{plan.get('normalized_query', '<unknown>')}: missing {field}")
    if plan.get("schema_version") != "query_to_source_action_plan.v0":
        errors.append(f"{plan.get('normalized_query', '<unknown>')}: invalid schema_version")
    if not plan.get("source_query_rewrites", {}).get("archive_org_metadata"):
        errors.append(f"{plan.get('normalized_query', '<unknown>')}: missing Archive.org metadata rewrite")
    safety = plan.get("safety")
    if not isinstance(safety, Mapping):
        errors.append(f"{plan.get('normalized_query', '<unknown>')}: safety must be an object")
        return
    if safety.get("candidate_only") is not True or safety.get("review_required") is not True:
        errors.append(f"{plan.get('normalized_query', '<unknown>')}: safety must be candidate-only and review-required")
    for field in FALSE_SAFETY_FIELDS:
        if safety.get(field) is not False:
            errors.append(f"{plan.get('normalized_query', '<unknown>')}: safety.{field} must be false")


def _validate_example_file(
    root: Path,
    query: str,
    plan: Mapping[str, Any],
    errors: list[str],
) -> None:
    file_name = _example_file_name(query)
    payload = _load_json(root / "examples" / "query_plans" / file_name, errors)
    if not payload:
        return
    if payload.get("example_query") != query:
        errors.append(f"{file_name}: example_query mismatch")
    if payload.get("expected_intent") != plan.get("intent"):
        errors.append(f"{file_name}: expected_intent does not match runtime planner")
    if payload.get("expected_domain_pack") != plan.get("domain_pack"):
        errors.append(f"{file_name}: expected_domain_pack does not match runtime planner")
    if set(payload.get("expected_source_families", [])) != set(plan.get("source_families", [])):
        errors.append(f"{file_name}: expected_source_families do not match runtime planner")
    if payload.get("archive_org_metadata_query") != plan.get("source_query_rewrites", {}).get("archive_org_metadata"):
        errors.append(f"{file_name}: archive_org_metadata_query does not match runtime planner")
    runtime_suppressions = {
        str(item.get("suppression_id"))
        for item in plan.get("candidate_suppressions", [])
        if isinstance(item, Mapping)
    }
    if set(payload.get("expected_candidate_suppressions", [])) != runtime_suppressions:
        errors.append(f"{file_name}: expected_candidate_suppressions do not match runtime planner")
    for field in (
        "candidate_only",
        "review_required",
    ):
        if payload.get(field) is not True:
            errors.append(f"{file_name}: {field} must be true")
    for field in (
        "accepted_truth_created",
        "download_performed",
        "extraction_executed",
        "model_provider_used",
        "index_mutation_performed",
    ):
        if payload.get(field) is not False:
            errors.append(f"{file_name}: {field} must be false")


def _example_file_name(query: str) -> str:
    mapping = {
        "New York 1993 D-Theater HD demo tape original source": "new_york_1993_d_theater_hd_demo_tape_original_source.json",
        "Windows 7-compatible portable utilities, not Windows 7 ISO": "windows_7_compatible_portable_utilities_not_windows_7_iso.json",
        "StyleWriter 2500 Mac OS 8 driver": "stylewriter_2500_mac_os_8_driver.json",
        "DirectX SDK June 2010 offline installer": "directx_sdk_june_2010_offline_installer.json",
        "best apps": "ambiguous_query_example.json",
    }
    return mapping[query]


def _require_enum(
    payload: Mapping[str, Any],
    path: tuple[str, ...],
    expected: Sequence[str],
    errors: list[str],
    label: str,
) -> None:
    value: Any = payload
    for key in path:
        value = value.get(key) if isinstance(value, Mapping) else None
    if set(value or []) != set(expected):
        errors.append(f"contract {label} must match runtime constants")


def _load_json(path: Path, errors: list[str]) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{path}: missing")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"{path}: JSON root must be object")
        return {}
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
