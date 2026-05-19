from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path
import subprocess
import sys
import tomllib
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = REPO_ROOT / "contracts" / "repo"
ROOT_ALLOWLIST = CONTRACT_ROOT / "root_allowlist.contract.toml"
NAMING = CONTRACT_ROOT / "naming.contract.toml"
GENERATED_EXCEPTIONS = CONTRACT_ROOT / "generated_artifact_exceptions.contract.toml"
ROOT_OWNERSHIP = CONTRACT_ROOT / "root_ownership.contract.toml"

REQUIRED_CONTRACTS = (
    ROOT_ALLOWLIST,
    NAMING,
    GENERATED_EXCEPTIONS,
    ROOT_OWNERSHIP,
)

KNOWN_DEBT_PATHS = (
    {
        "path": "control/prototypes/legacy_runtime",
        "debt_id": "control_prototypes_legacy_runtime",
        "class": "prototype_runtime_under_control",
        "required_disposition": "move_to_archive_legacy_or_promote_selected_runtime_slices",
    },
    {
        "path": "runtime/local_workbench",
        "debt_id": "runtime_local_workbench_presentation",
        "class": "presentation_under_runtime",
        "required_disposition": "move_presentation_to_surfaces_web_workbench_after_workbench_foundation",
    },
    {
        "path": "control/schemas",
        "debt_id": "control_schemas_contract_authority_overlap",
        "class": "duplicate_contract_authority_risk",
        "required_disposition": "eliminate_or_scope_against_contracts_repo_authority",
    },
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Eureka repository root and naming canon without moving files."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings as well as errors. Known debt remains non-fatal.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_repo_structure_canon(strict=args.strict)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_repo_structure_canon(*, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    contracts = _load_contracts(errors)
    tracked_files = _git_ls_files()
    tracked_set = set(tracked_files)
    top_level = _top_level_entries(tracked_files)

    root_report = _validate_top_level_roots(top_level, contracts, errors)
    _validate_required_roots(top_level, contracts, errors)
    _validate_native_surface_rule(contracts, errors)
    generated_report = _validate_generated_artifact_exceptions(tracked_set, tracked_files, contracts, errors)
    naming_report = _validate_naming_rules(top_level, tracked_files, contracts, errors, warnings)
    debt = _collect_known_debt(top_level, tracked_files, contracts)

    if strict and warnings:
        errors.extend(f"strict warning: {warning}" for warning in warnings)

    return {
        "schema_version": "repo_structure_canon_validation.v0",
        "status": "valid" if not errors else "invalid",
        "created_by": "REPO-LAYOUT-CANON-01",
        "contracts": {key: _rel(path) for key, path in _contract_paths().items()},
        "top_level": root_report,
        "generated_artifacts": generated_report,
        "naming": naming_report,
        "known_debt": debt,
        "native_root": {
            "root": "native",
            "status": "canonical" if _root_class(contracts, "native") == "native_client_project" else "invalid",
            "surfaces_native": "projection_adapter_only",
        },
        "native_root_canonical": _root_class(contracts, "native") == "native_client_project",
        "surfaces_native_supersedes_native": False,
        "tools_root_allowed": _root_known(contracts, "tools"),
        "release_root_allowed": _root_known(contracts, "release"),
        "archive_root_allowed": _root_known(contracts, "archive"),
        "strict": strict,
        "warnings": warnings,
        "errors": errors,
        "network_used": False,
        "runtime_behavior_changed": False,
        "files_moved": False,
        "production_or_public_launch_claim": False,
    }


def _load_contracts(errors: list[str]) -> dict[str, Any]:
    contracts: dict[str, Any] = {}
    for label, path in _contract_paths().items():
        if not path.is_file():
            errors.append(f"{_rel(path)}: required repo canon contract is missing.")
            contracts[label] = {}
            continue
        try:
            contracts[label] = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"{_rel(path)}: invalid TOML: {exc}.")
            contracts[label] = {}
    return contracts


def _validate_top_level_roots(
    top_level: Mapping[str, str],
    contracts: Mapping[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    allowlist = contracts.get("root_allowlist", {})
    root_entries = _table_list(allowlist, "roots")
    allowed_roots = {str(root.get("name")) for root in root_entries}
    optional_roots = sorted(str(root.get("name")) for root in root_entries if root.get("required") is False)
    conventional_files = set(_string_list(allowlist.get("conventional_root_files")))
    classified_exceptions = {
        str(item.get("name")): str(item.get("class"))
        for item in _table_list(allowlist, "classified_top_level_exceptions")
    }
    classified_debt = {
        str(item.get("name")): str(item.get("class"))
        for item in _table_list(allowlist, "classified_top_level_debt")
    }

    unexpected: list[str] = []
    active_roots: list[str] = []
    root_files: list[str] = []
    for name, kind in sorted(top_level.items()):
        if kind == "file":
            root_files.append(name)
            if name not in conventional_files:
                unexpected.append(name)
            continue
        active_roots.append(name)
        if name in allowed_roots or name in classified_exceptions or name in classified_debt:
            continue
        unexpected.append(name)

    for name in unexpected:
        errors.append(f"{name}: top-level entry is not allowed or explicitly classified.")

    return {
        "active_roots": active_roots,
        "allowed_roots": sorted(allowed_roots),
        "optional_roots": optional_roots,
        "optional_roots_absent": [name for name in optional_roots if name not in top_level],
        "conventional_root_files": sorted(root_files),
        "classified_exceptions": classified_exceptions,
        "classified_debt": classified_debt,
        "unexpected": unexpected,
    }


def _validate_required_roots(top_level: Mapping[str, str], contracts: Mapping[str, Any], errors: list[str]) -> None:
    allowlist = contracts.get("root_allowlist", {})
    for root in _table_list(allowlist, "roots"):
        name = str(root.get("name", ""))
        if root.get("required") is True and name not in top_level:
            errors.append(f"{name}: required top-level root is absent.")


def _validate_native_surface_rule(contracts: Mapping[str, Any], errors: list[str]) -> None:
    if _root_class(contracts, "native") != "native_client_project":
        errors.append("native: root must remain classified as native_client_project.")
    surfaces_ownership = _ownership_for_root(contracts, "surfaces")
    native_ownership = _ownership_for_root(contracts, "native")
    if "native_project_authority" not in _string_list(surfaces_ownership.get("must_not_own")):
        errors.append("surfaces: ownership contract must forbid native_project_authority.")
    if "native_client_projects" not in _string_list(native_ownership.get("owns")):
        errors.append("native: ownership contract must own native_client_projects.")


def _validate_generated_artifact_exceptions(
    tracked_set: set[str],
    tracked_files: Sequence[str],
    contracts: Mapping[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    contract = contracts.get("generated_artifact_exceptions", {})
    exact = {str(item.get("path")): item for item in _table_list(contract, "exceptions")}
    patterns = _table_list(contract, "pattern_exceptions")
    required_paths = (
        "site/dist",
        "snapshots/examples/static_snapshot_v0",
        "data/public_index",
        ".aide/generated",
        ".aide/cache",
        ".aide/export",
        ".aide/reports",
    )

    accepted: list[str] = []
    for path in required_paths:
        if not _has_tracked_path(path, tracked_set, tracked_files):
            continue
        item = exact.get(path)
        if not isinstance(item, Mapping):
            errors.append(f"{path}: generated artifact path is tracked without an exact exception.")
            continue
        if item.get("manual_edits_allowed") is not False:
            errors.append(f"{path}: generated artifact exception must set manual_edits_allowed=false.")
        if not item.get("check_command"):
            errors.append(f"{path}: generated artifact exception must declare check_command.")
        accepted.append(path)

    audit_generated_count = sum(1 for path in tracked_files if "/generated/" in path and path.startswith("control/audits/"))
    if audit_generated_count:
        has_audit_pattern = any(str(item.get("path_pattern")) == "control/audits/*/generated" for item in patterns)
        if not has_audit_pattern:
            errors.append("control/audits/*/generated: tracked generated audit material lacks a pattern exception.")

    return {
        "accepted_exact_exceptions": sorted(accepted),
        "pattern_exception_count": len(patterns),
        "control_audits_generated_file_count": audit_generated_count,
        "data_public_index_status": str(exact.get("data/public_index", {}).get("status", "missing")),
        "site_dist_exception": "site/dist" in accepted,
        "snapshot_seed_exception": "snapshots/examples/static_snapshot_v0" in accepted,
    }


def _validate_naming_rules(
    top_level: Mapping[str, str],
    tracked_files: Sequence[str],
    contracts: Mapping[str, Any],
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    contract = contracts.get("naming", {})
    directories = _mapping(contract.get("directories"))
    allowed_src = _string_list(directories.get("allowed_src_exceptions"))
    forbidden_vague = set(_string_list(directories.get("forbidden_vague_terms")))
    forbidden_status = set(_string_list(directories.get("forbidden_status_terms")))
    allowlist = contracts.get("root_allowlist", {})
    classified_top_level = {
        str(item.get("name"))
        for item in _table_list(allowlist, "classified_top_level_exceptions")
    } | {
        str(item.get("name"))
        for item in _table_list(allowlist, "classified_top_level_debt")
    }

    src_hits = [path for path in tracked_files if "/src/" in f"/{path}/"]
    unclassified_src = [
        path for path in src_hits if not any(fnmatch.fnmatchcase(path, pattern) for pattern in allowed_src)
    ]
    for path in unclassified_src:
        errors.append(f"{path}: nested src path is not documented as an ecosystem exception.")

    unsafe_top_level_names = []
    for name, kind in top_level.items():
        if kind != "dir":
            continue
        if any(ord(char) > 127 for char in name) or " " in name:
            unsafe_top_level_names.append(name)
        if name not in classified_top_level and (name in forbidden_vague or name in forbidden_status):
            unsafe_top_level_names.append(name)
    for name in sorted(set(unsafe_top_level_names)):
        errors.append(f"{name}: top-level root violates naming canon.")

    contract_files = [path for path in tracked_files if path.startswith("contracts/repo/")]
    bad_contract_suffixes = [path for path in contract_files if not path.endswith(".contract.toml")]
    for path in bad_contract_suffixes:
        if path.endswith("/README.md"):
            continue
        errors.append(f"{path}: repo contract file must use .contract.toml suffix.")

    if "scripts" in top_level:
        warnings.append("scripts: allowed as a transitional thin-wrapper root; substantial tools should move to tools/.")

    return {
        "src_exception_count": len(src_hits),
        "unclassified_src_paths": unclassified_src,
        "allowed_src_exceptions": allowed_src,
        "forbidden_vague_terms": sorted(forbidden_vague),
        "forbidden_status_terms": sorted(forbidden_status),
        "repo_contract_files": sorted(contract_files),
    }


def _collect_known_debt(
    top_level: Mapping[str, str],
    tracked_files: Sequence[str],
    contracts: Mapping[str, Any],
) -> list[dict[str, str]]:
    debt: list[dict[str, str]] = []
    allowlist = contracts.get("root_allowlist", {})
    for item in _table_list(allowlist, "classified_top_level_debt"):
        name = str(item.get("name", ""))
        if name in top_level:
            debt.append(
                {
                    "debt_id": f"top_level_{name}",
                    "path": name,
                    "class": str(item.get("class", "classified_debt")),
                    "required_disposition": str(item.get("future_disposition", "classify_or_move_later")),
                }
            )
    tracked_set = set(tracked_files)
    for item in KNOWN_DEBT_PATHS:
        path = item["path"]
        if _has_tracked_path(path, tracked_set, tracked_files):
            debt.append(dict(item))
    if sum(1 for path in tracked_files if path.startswith("scripts/")) > 100:
        debt.append(
            {
                "debt_id": "scripts_large_tool_tree",
                "path": "scripts",
                "class": "thin_wrapper_root_with_substantive_tools",
                "required_disposition": "move_substantive_implementations_to_tools_in_phases",
            }
        )
    return debt


def _git_ls_files() -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted(line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip())


def _top_level_entries(tracked_files: Sequence[str]) -> dict[str, str]:
    entries: dict[str, str] = {}
    for path in tracked_files:
        parts = path.split("/")
        name = parts[0]
        kind = "dir" if len(parts) > 1 else "file"
        entries[name] = "dir" if entries.get(name) == "dir" or kind == "dir" else kind
    return entries


def _has_tracked_path(path: str, tracked_set: set[str], tracked_files: Sequence[str]) -> bool:
    normalized = path.rstrip("/")
    return normalized in tracked_set or any(item.startswith(normalized + "/") for item in tracked_files)


def _root_known(contracts: Mapping[str, Any], name: str) -> bool:
    return _root_class(contracts, name) != ""


def _root_class(contracts: Mapping[str, Any], name: str) -> str:
    allowlist = contracts.get("root_allowlist", {})
    for root in _table_list(allowlist, "roots"):
        if root.get("name") == name:
            return str(root.get("class", ""))
    return ""


def _ownership_for_root(contracts: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    ownership = contracts.get("root_ownership", {})
    for item in _table_list(ownership, "ownership"):
        if item.get("root") == name:
            return item
    return {}


def _contract_paths() -> dict[str, Path]:
    return {
        "root_allowlist": ROOT_ALLOWLIST,
        "naming": NAMING,
        "generated_artifact_exceptions": GENERATED_EXCEPTIONS,
        "root_ownership": ROOT_OWNERSHIP,
    }


def _table_list(payload: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    value = payload.get(key)
    if isinstance(value, list):
        return [item for item in value if isinstance(item, Mapping)]
    return []


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Repository structure canon validation",
        f"status: {report['status']}",
        f"allowed_top_level_roots: {len(report['top_level']['allowed_roots'])}",
        f"active_top_level_roots: {len(report['top_level']['active_roots'])}",
        f"known_debt_count: {len(report['known_debt'])}",
        f"generated_exception_count: {len(report['generated_artifacts']['accepted_exact_exceptions'])}",
        f"native_root: {report['native_root']['status']}",
        f"native_root_canonical: {str(report['native_root_canonical']).lower()}",
    ]
    if report["known_debt"]:
        lines.append("")
        lines.append("Known debt")
        lines.extend(f"- {item['path']}: {item['class']}" for item in report["known_debt"])
    if report["warnings"]:
        lines.append("")
        lines.append("Warnings")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    if report["errors"]:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
