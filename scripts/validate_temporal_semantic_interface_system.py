from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]

SEMANTIC_CONTRACTS = [
    "contracts/semantic/entity.v0.json",
    "contracts/semantic/status.v0.json",
    "contracts/semantic/affordance.v0.json",
    "contracts/semantic/badge.v0.json",
    "contracts/semantic/navigation.v0.json",
    "contracts/semantic/relationship.v0.json",
]
REPRESENTATION_CONTRACTS = [
    "contracts/representation/representation_profile.v0.json",
    "contracts/representation/renderer_contract.v0.json",
    "contracts/representation/skin_contract.v0.json",
    "contracts/representation/compatibility_budget.v0.json",
    "contracts/representation/fallback_rule.v0.json",
    "contracts/representation/cache_key.v0.json",
]
VIEW_CONTRACTS = [
    "contracts/view/search_page/search_page.v0.json",
    "contracts/view/result_card/result_card.v0.json",
    "contracts/view/object_page/object_page.v0.json",
    "contracts/view/need_page/need_page.v0.json",
    "contracts/view/candidate_page/candidate_page.v0.json",
    "contracts/view/source_page/source_page.v0.json",
    "contracts/view/evidence_page/evidence_page.v0.json",
    "contracts/view/status_page/status_page.v0.json",
]
SUPPORTING_CONTRACTS = [
    "contracts/action/action_registry.v0.json",
    "contracts/route/route_model.v0.json",
    "contracts/surface/surface_projection.v0.json",
    "contracts/policy/surface_kernel_policy.v0.json",
]
REQUIRED_DOCS = [
    "docs/architecture/TEMPORAL_SEMANTIC_INTERFACE_SYSTEM.md",
    "docs/architecture/SURFACE_KERNEL.md",
    "docs/architecture/RENDERER_POLICY.md",
    "docs/reference/TEMPORAL_SEMANTIC_INTERFACE_CONTRACTS.md",
    "docs/operations/TSIS_00_RUNBOOK.md",
]
REQUIRED_POLICIES = [
    "control/policies/temporal_semantic_interface_policy.json",
    "control/policies/surface_kernel_policy.json",
]
REQUIRED_INVENTORY = [
    "control/inventory/semantic_status_registry.json",
    "control/inventory/semantic_affordance_registry.json",
    "control/inventory/representation_profile_registry.json",
    "control/inventory/tsis_00_semantic_inventory.json",
    "control/inventory/tsis_00_surface_kernel_matrix.json",
    "control/inventory/tsis_00_validation_matrix.json",
    "control/inventory/tsis_00_result.json",
    "control/inventory/tsis_00_next_task_decision.json",
]

FORBIDDEN_RUNTIME_PHASE_FILES = [
    "runtime/surface/kernel.py",
    "runtime/surface/route_resolver.py",
    "runtime/surface/capability_negotiator.py",
    "runtime/surface/view_model_loader.py",
    "runtime/surface/renderer_dispatch.py",
    "runtime/surface/cache_key.py",
    "runtime/surface/output_policy.py",
    "runtime/surface/fallback.py",
    "scripts/eureka_surface_kernel.py",
]

FORBIDDEN_TRUE_BOUNDARIES = {
    "new_top_level_roots_added",
    "runtime_behavior_changed",
    "surface_kernel_runtime_added",
    "renderer_implementation_added",
    "renderer_mutated_truth",
    "renderer_called_sources",
    "renderer_changed_policy",
    "public_index_mutated",
    "master_index_mutated",
    "download_performed",
    "file_fetch_performed",
    "ocr_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "public_launch_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the TSIS-00 contract foundation.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_temporal_semantic_interface_system(Path(args.repo_root))
    output = stdout or None
    text = json.dumps(report, indent=2, sort_keys=True) + "\n" if args.json else _plain(report)
    if output is None:
        print(text, end="")
    else:
        output.write(text)
    return 0 if report["status"] == "pass" else 1


def validate_temporal_semantic_interface_system(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    checked_paths = (
        SEMANTIC_CONTRACTS
        + REPRESENTATION_CONTRACTS
        + VIEW_CONTRACTS
        + SUPPORTING_CONTRACTS
        + REQUIRED_DOCS
        + REQUIRED_POLICIES
        + REQUIRED_INVENTORY
    )
    for relative in checked_paths:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    for relative in SEMANTIC_CONTRACTS + REPRESENTATION_CONTRACTS + VIEW_CONTRACTS + SUPPORTING_CONTRACTS:
        payload = _load_json(root / relative, errors)
        if isinstance(payload, Mapping):
            _validate_contract(relative, payload, errors)

    semantic_inventory = _load_json(root / "control/inventory/tsis_00_semantic_inventory.json", errors)
    if isinstance(semantic_inventory, Mapping):
        _validate_semantic_inventory(semantic_inventory, errors)

    status_registry = _load_json(root / "control/inventory/semantic_status_registry.json", errors)
    if isinstance(status_registry, Mapping):
        _validate_status_registry(status_registry, errors)

    affordance_registry = _load_json(root / "control/inventory/semantic_affordance_registry.json", errors)
    if isinstance(affordance_registry, Mapping):
        _validate_affordance_registry(affordance_registry, errors)

    representation_registry = _load_json(root / "control/inventory/representation_profile_registry.json", errors)
    if isinstance(representation_registry, Mapping):
        _validate_representation_registry(representation_registry, errors)

    for relative in REQUIRED_POLICIES:
        payload = _load_json(root / relative, errors)
        if isinstance(payload, Mapping):
            _validate_policy(relative, payload, errors)

    result = _load_json(root / "control/inventory/tsis_00_result.json", errors)
    boundary_flags = _boundary_flags(result if isinstance(result, Mapping) else {})
    _validate_boundaries(boundary_flags, errors)
    _validate_runtime_not_added(root, errors)

    return {
        "schema_version": "tsis_00_validation.v0",
        "task": "TSIS-00",
        "status": "pass" if not errors else "fail",
        "semantic_contract_count": len(SEMANTIC_CONTRACTS),
        "representation_contract_count": len(REPRESENTATION_CONTRACTS),
        "view_contract_count": len(VIEW_CONTRACTS),
        "supporting_contract_count": len(SUPPORTING_CONTRACTS),
        "registries_added": True,
        "surface_kernel_runtime_added": False,
        "surface_kernel_cli_added": False,
        **boundary_flags,
        "errors": sorted(errors),
    }


def _validate_contract(relative: str, payload: Mapping[str, Any], errors: list[str]) -> None:
    for field in ("$schema", "$id", "title", "type", "required", "properties"):
        if field not in payload:
            errors.append(f"{relative}: missing schema field {field}")
    if payload.get("type") != "object":
        errors.append(f"{relative}: schema type must be object")
    required = payload.get("required")
    if not isinstance(required, list) or not required:
        errors.append(f"{relative}: required must be a non-empty list")
    if payload.get("x-tsis_contract") is not True:
        errors.append(f"{relative}: x-tsis_contract must be true")


def _validate_semantic_inventory(payload: Mapping[str, Any], errors: list[str]) -> None:
    expected_refs = set(SEMANTIC_CONTRACTS)
    actual_refs = set(_strings(payload.get("semantic_contract_refs")))
    missing_refs = expected_refs - actual_refs
    for ref in sorted(missing_refs):
        errors.append(f"semantic inventory missing contract ref {ref}")
    statuses = set(_strings(payload.get("canonical_status_vocabulary")))
    for status in _required_statuses():
        if status not in statuses:
            errors.append(f"semantic inventory missing status {status}")
    affordances = set(_strings(payload.get("canonical_affordances")))
    for affordance in _required_affordances():
        if affordance not in affordances:
            errors.append(f"semantic inventory missing affordance {affordance}")
    for field in (
        "machine_status_synonyms_allowed",
        "color_only_status_allowed",
        "renderer_fact_invention_allowed",
        "renderer_policy_decision_allowed",
        "route_identity_changes_allowed",
    ):
        if payload.get(field) is not False:
            errors.append(f"semantic inventory field {field} must be false")


def _validate_status_registry(payload: Mapping[str, Any], errors: list[str]) -> None:
    statuses = {str(item.get("status_id")) for item in _objects(payload.get("statuses"))}
    for status in _required_statuses():
        if status not in statuses:
            errors.append(f"status registry missing {status}")
    if payload.get("machine_status_synonyms_allowed") is not False:
        errors.append("status registry machine_status_synonyms_allowed must be false")
    if payload.get("color_only_status_allowed") is not False:
        errors.append("status registry color_only_status_allowed must be false")


def _validate_affordance_registry(payload: Mapping[str, Any], errors: list[str]) -> None:
    affordances = {str(item.get("affordance_id")) for item in _objects(payload.get("affordances"))}
    for affordance in _required_affordances():
        if affordance not in affordances:
            errors.append(f"affordance registry missing {affordance}")
    if payload.get("renderer_policy_decision_allowed") is not False:
        errors.append("affordance registry renderer_policy_decision_allowed must be false")


def _validate_representation_registry(payload: Mapping[str, Any], errors: list[str]) -> None:
    profiles = {str(item.get("profile_id")) for item in _objects(payload.get("profiles"))}
    for profile in ("json", "text", "terminal", "html2", "html32", "rich", "native_card", "agent_context"):
        if profile not in profiles:
            errors.append(f"representation profile registry missing {profile}")
    if payload.get("unknown_profile_fallback_required") is not True:
        errors.append("representation registry unknown_profile_fallback_required must be true")
    if payload.get("profile_selection_may_change_route_identity") is not False:
        errors.append("representation registry profile_selection_may_change_route_identity must be false")


def _validate_policy(relative: str, payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("schema_version") != "tsis_policy.v0":
        errors.append(f"{relative}: schema_version must be tsis_policy.v0")
    required_true = (
        "one_semantic_product_language",
        "contracts_own_meaning",
        "renderers_are_pure",
        "capability_negotiation_preserves_identity",
        "unknown_fields_are_forward_compatible",
    )
    for field in required_true:
        if payload.get(field) is not True:
            errors.append(f"{relative}: {field} must be true")
    for field in ("deployment_enabled", "public_launch_enabled", "source_calls_enabled", "downloads_enabled", "model_provider_enabled"):
        if payload.get(field) is not False:
            errors.append(f"{relative}: {field} must be false")


def _validate_boundaries(boundary_flags: Mapping[str, bool], errors: list[str]) -> None:
    for field in FORBIDDEN_TRUE_BOUNDARIES:
        if boundary_flags.get(field) is not False:
            errors.append(f"boundary flag {field} must be false")


def _validate_runtime_not_added(root: Path, errors: list[str]) -> None:
    for relative in FORBIDDEN_RUNTIME_PHASE_FILES:
        if (root / relative).exists():
            errors.append(f"TSIS-00 must not add runtime phase file: {relative}")


def _boundary_flags(result: Mapping[str, Any]) -> dict[str, bool]:
    return {field: bool(result.get(field)) for field in FORBIDDEN_TRUE_BOUNDARIES}


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {path.as_posix()}")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path.as_posix()}:{exc.lineno}: {exc.msg}")
    return None


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _objects(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _required_statuses() -> tuple[str, ...]:
    return (
        "verified",
        "candidate",
        "need",
        "near_miss",
        "mention_only",
        "policy_blocked",
        "private_local",
        "superseded",
        "rejected",
        "unknown",
    )


def _required_affordances() -> tuple[str, ...]:
    return (
        "open",
        "inspect",
        "compare",
        "cite",
        "download_manifest",
        "review_candidate",
        "promote",
        "reject",
        "report_risk",
        "preserve",
    )


def _plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"validate_temporal_semantic_interface_system: {report['status']}",
        f"semantic_contract_count: {report['semantic_contract_count']}",
        f"representation_contract_count: {report['representation_contract_count']}",
        f"view_contract_count: {report['view_contract_count']}",
        f"supporting_contract_count: {report['supporting_contract_count']}",
    ]
    if report["errors"]:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
