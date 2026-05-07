from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_search_page_view_model import validate_payloads


SCHEMA_VERSION = "0.1.0"
PLAN_PATH = "control/inventory/publication/search_page_static_projection_plan.json"
FIXTURE_PATH = "examples/view_models/search_page/static_projection_reference_v0.json"
DOC_PATH = "docs/operations/STATIC_SEARCHPAGE_PROJECTION_GENERATOR_PLAN.md"
A12_AUDIT_REPORT = "control/audits/track-a-12-static-searchpage-projection-plan-v0/track_a_12_report.json"
SEARCH_PAGE_POLICY = "control/inventory/publication/search_page_view_model_policy.json"
REPRESENTATION_INVENTORY = "control/inventory/publication/representation_profiles.json"
SEMANTIC_PARITY_INVENTORY = "control/inventory/publication/semantic_renderer_parity_policy.json"
ROUTE_MATRIX = "control/inventory/publication/route_view_representation_matrix.json"

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "plan_id",
    "label",
    "description",
    "track",
    "task",
    "status",
    "source_view_family",
    "source_fixture",
    "source_view_schema",
    "default_output_root",
    "projection_targets",
    "output_root_policy",
    "required_validators",
    "product_boundary",
    "deferred_work",
    "notes",
}
REQUIRED_TARGETS = {
    "standard_static_html": ("search.standard.html", "standard_html", "search"),
    "lite_static_html": ("search.lite.html", "lite_html", "lite_static"),
    "text_static": ("search.txt", "text", "text_static"),
    "file_tree_static": ("search.README.txt", "file_tree", "files_static"),
    "static_json_handoff": ("search_handoff.json", "api_json", "data_static"),
}
REQUIRED_PRODUCT_BOUNDARY_FALSE = {
    "changed_product_behavior",
    "changed_public_routes",
    "changed_generated_site_artifacts",
    "regenerated_site_dist",
    "enabled_hosting",
    "enabled_live_probes",
    "enabled_source_sync",
    "enabled_source_connectors",
    "enabled_downloads",
    "enabled_installers",
    "enabled_execution",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "created_native_projects",
    "mutated_master_index",
}
FORBIDDEN_PREFIXES = {
    "site/dist",
    "site/pages",
    "site/templates",
    "runtime",
    "contracts",
    "control/inventory",
    "surfaces",
    "native",
}
ALLOWED_PREFIXES = {"control/audits", ".aide/reports"}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the static SearchPage projection plan.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit deterministic JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_static_searchpage_projection_plan(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_static_searchpage_projection_plan(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    plan = _load_json(root / PLAN_PATH, errors, root)
    fixture = _load_json(root / FIXTURE_PATH, errors, root)
    policy = _load_json(root / SEARCH_PAGE_POLICY, errors, root)
    representations = _load_json(root / REPRESENTATION_INVENTORY, errors, root)
    semantic = _load_json(root / SEMANTIC_PARITY_INVENTORY, errors, root)
    route_matrix = _load_json(root / ROUTE_MATRIX, errors, root)
    audit = _load_json(root / A12_AUDIT_REPORT, errors, root)

    for relative in (DOC_PATH,):
        if not (root / relative).is_file():
            errors.append(f"{relative}: file not found")

    if isinstance(plan, Mapping):
        _validate_plan(plan, errors)
    if (
        isinstance(fixture, Mapping)
        and isinstance(policy, Mapping)
        and isinstance(representations, Mapping)
        and isinstance(semantic, Mapping)
        and isinstance(route_matrix, Mapping)
    ):
        errors.extend(
            validate_payloads(
                policy,
                representations,
                semantic,
                route_matrix,
                [fixture],
                source_label="static_projection_reference",
            )
        )
        if fixture.get("view_model_id") != "static_projection_reference_v0":
            errors.append(f"{FIXTURE_PATH}: view_model_id must be static_projection_reference_v0")
        if fixture.get("search_mode") != "static_handoff":
            errors.append(f"{FIXTURE_PATH}: search_mode must be static_handoff")

    if isinstance(audit, Mapping):
        boundary = audit.get("product_boundary")
        if not isinstance(boundary, Mapping):
            errors.append(f"{A12_AUDIT_REPORT}: product_boundary must be an object")
        else:
            for key in sorted(REQUIRED_PRODUCT_BOUNDARY_FALSE):
                if boundary.get(key) is not False:
                    errors.append(f"{A12_AUDIT_REPORT}: product_boundary.{key} must be false")

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "valid" if not errors else "invalid",
        "plan_checked": PLAN_PATH,
        "fixture_checked": FIXTURE_PATH,
        "audit_report_checked": A12_AUDIT_REPORT,
        "errors": sorted(errors),
        "warnings": sorted(warnings),
    }


def _validate_plan(plan: Mapping[str, Any], errors: list[str]) -> None:
    missing = REQUIRED_TOP_LEVEL - set(plan)
    if missing:
        errors.append(f"{PLAN_PATH}: missing top-level fields {sorted(missing)}")
    if plan.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{PLAN_PATH}: schema_version must be {SCHEMA_VERSION}")
    if plan.get("track") != "A":
        errors.append(f"{PLAN_PATH}: track must be A")
    if plan.get("task") != "TRACK-A-12":
        errors.append(f"{PLAN_PATH}: task must be TRACK-A-12")
    if plan.get("source_view_family") != "SearchPageView":
        errors.append(f"{PLAN_PATH}: source_view_family must be SearchPageView")
    if plan.get("source_fixture") != FIXTURE_PATH:
        errors.append(f"{PLAN_PATH}: source_fixture must be {FIXTURE_PATH}")

    default_root = str(plan.get("default_output_root", ""))
    if not default_root.startswith("control/audits/track-a-13-static-searchpage-projection-dry-run-v0"):
        errors.append(f"{PLAN_PATH}: default_output_root must be the A13 audit generated directory")

    targets = plan.get("projection_targets")
    if not isinstance(targets, Sequence) or isinstance(targets, (str, bytes)):
        errors.append(f"{PLAN_PATH}: projection_targets must be an array")
    else:
        by_id = {target.get("target_id"): target for target in targets if isinstance(target, Mapping)}
        for target_id, (filename, profile, route) in sorted(REQUIRED_TARGETS.items()):
            target = by_id.get(target_id)
            if not isinstance(target, Mapping):
                errors.append(f"{PLAN_PATH}: missing projection target {target_id}")
                continue
            if target.get("output_filename") != filename:
                errors.append(f"{PLAN_PATH}: {target_id}.output_filename must be {filename}")
            if target.get("representation_profile") != profile:
                errors.append(f"{PLAN_PATH}: {target_id}.representation_profile must be {profile}")
            if target.get("route_family") != route:
                errors.append(f"{PLAN_PATH}: {target_id}.route_family must be {route}")
            categories = target.get("required_semantic_categories")
            if not isinstance(categories, Sequence) or isinstance(categories, (str, bytes)) or not categories:
                errors.append(f"{PLAN_PATH}: {target_id}.required_semantic_categories must be non-empty")

    policy = plan.get("output_root_policy")
    if not isinstance(policy, Mapping):
        errors.append(f"{PLAN_PATH}: output_root_policy must be an object")
    else:
        forbidden = set(_string_items(policy.get("forbidden_repo_prefixes")))
        allowed = set(_string_items(policy.get("allowed_repo_prefixes")))
        if not FORBIDDEN_PREFIXES <= forbidden:
            errors.append(f"{PLAN_PATH}: forbidden_repo_prefixes missing {sorted(FORBIDDEN_PREFIXES - forbidden)}")
        if not ALLOWED_PREFIXES <= allowed:
            errors.append(f"{PLAN_PATH}: allowed_repo_prefixes missing {sorted(ALLOWED_PREFIXES - allowed)}")
        if policy.get("allowed_outside_repo") is not True:
            errors.append(f"{PLAN_PATH}: allowed_outside_repo must be true")

    boundary = plan.get("product_boundary")
    if not isinstance(boundary, Mapping):
        errors.append(f"{PLAN_PATH}: product_boundary must be an object")
    else:
        for key in sorted(REQUIRED_PRODUCT_BOUNDARY_FALSE):
            if boundary.get(key) is not False:
                errors.append(f"{PLAN_PATH}: product_boundary.{key} must be false")


def _load_json(path: Path, errors: list[str], repo_root: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path, repo_root)}: file not found")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path, repo_root)}: invalid JSON at line {exc.lineno}: {exc.msg}")
    return None


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
        f"validate_static_searchpage_projection_plan: {report['status']}",
        f"schema_version: {report['schema_version']}",
        f"plan: {report['plan_checked']}",
        f"fixture: {report['fixture_checked']}",
    ]
    errors = report.get("errors", [])
    if errors:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in errors)
    warnings = report.get("warnings", [])
    if warnings:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in warnings)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
