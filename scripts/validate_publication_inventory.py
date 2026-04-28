from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY_DIR = REPO_ROOT / "control" / "inventory" / "publication"
DEFAULT_SITE_DIR = REPO_ROOT / "public_site"

REQUIRED_FILES = {
    "README.md",
    "publication_contract.json",
    "page_registry.json",
    "client_profiles.json",
    "deployment_targets.json",
    "public_data_contract.json",
    "redirects.json",
}
REQUIRED_CONTRACT_FIELDS = {
    "schema_version",
    "contract_id",
    "status",
    "stability",
    "current_static_artifact",
    "future_generator_root",
    "future_generated_artifact",
    "base_path_policy",
    "publication_scope",
    "no_live_backend",
    "no_deployment_performed",
    "no_external_observations",
    "public_claim_source_policy",
    "public_status_taxonomy",
    "route_stability_levels",
    "next_expected_milestones",
    "created_by_slice",
    "notes",
}
REQUIRED_STATUS_VALUES = {
    "implemented",
    "recorded_fixture",
    "static_demo",
    "placeholder",
    "planned",
    "deferred",
    "blocked",
    "unsafe_for_public_alpha",
    "removed",
}
REQUIRED_ROUTE_STABILITY_VALUES = {
    "experimental",
    "stable_draft",
    "stable",
    "deprecated",
    "removed",
}
REQUIRED_PAGE_FIELDS = {
    "path",
    "title",
    "status",
    "stability",
    "source_file",
    "client_profiles",
    "requires_javascript",
    "requires_css",
    "works_under_project_base_path",
    "safe_for_static_hosting",
    "public_claim_scope",
    "notes",
}
REQUIRED_RESERVED_ROUTES = {
    "/app/",
    "/web/",
    "/lite/",
    "/text/",
    "/files/",
    "/data/",
    "/api/",
    "/snapshots/",
    "/source-policy.html",
    "/rights-and-access.html",
    "/security.html",
    "/downloads.html",
    "/404.html",
    "/robots.txt",
}
REQUIRED_CLIENT_PROFILES = {
    "modern_web",
    "standard_web",
    "lite_html",
    "text",
    "file_tree",
    "snapshot",
    "native_client",
    "relay",
    "api_client",
}
REQUIRED_CLIENT_PROFILE_FIELDS = {
    "id",
    "status",
    "intended_clients",
    "requires_javascript",
    "requires_css",
    "requires_https",
    "intended_path_prefixes",
    "must_support",
    "prohibited_dependencies",
    "current_support_level",
    "notes",
}
REQUIRED_PUBLIC_DATA_PATHS = {
    "/data/site_manifest.json",
    "/data/page_registry.json",
    "/data/source_summary.json",
    "/data/eval_summary.json",
    "/data/route_summary.json",
    "/data/build_manifest.json",
    "/files/index.txt",
    "/files/SHA256SUMS",
}
REQUIRED_PUBLIC_DATA_FIELDS = {
    "path",
    "status",
    "stability",
    "schema_version",
    "producer",
    "consumer_profiles",
    "contains_live_data",
    "contains_external_observations",
    "safe_for_static_hosting",
    "notes",
}
NON_IMPLEMENTED_STATUSES = {
    "planned",
    "deferred",
    "blocked",
    "placeholder",
    "unsafe_for_public_alpha",
    "removed",
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Eureka publication-plane contracts without network access."
    )
    parser.add_argument(
        "--inventory-dir",
        default=str(DEFAULT_INVENTORY_DIR),
        help="Publication inventory directory to validate.",
    )
    parser.add_argument(
        "--site-dir",
        default=str(DEFAULT_SITE_DIR),
        help="Current static public artifact directory.",
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root used for relative source_file checks.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_publication_inventory(
        Path(args.inventory_dir),
        Path(args.site_dir),
        Path(args.repo_root),
    )
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_publication_inventory(
    inventory_dir: Path = DEFAULT_INVENTORY_DIR,
    site_dir: Path = DEFAULT_SITE_DIR,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    existing_files: list[str] = []
    for relative in sorted(REQUIRED_FILES):
        path = inventory_dir / relative
        if path.exists():
            existing_files.append(relative)
        else:
            errors.append(f"{_rel(path, repo_root)}: required file is missing.")

    payloads = {
        "publication_contract.json": _load_json(
            inventory_dir / "publication_contract.json", errors, repo_root
        ),
        "page_registry.json": _load_json(
            inventory_dir / "page_registry.json", errors, repo_root
        ),
        "client_profiles.json": _load_json(
            inventory_dir / "client_profiles.json", errors, repo_root
        ),
        "deployment_targets.json": _load_json(
            inventory_dir / "deployment_targets.json", errors, repo_root
        ),
        "public_data_contract.json": _load_json(
            inventory_dir / "public_data_contract.json", errors, repo_root
        ),
        "redirects.json": _load_json(inventory_dir / "redirects.json", errors, repo_root),
    }

    _validate_contract(payloads["publication_contract.json"], errors)
    page_summary = _validate_page_registry(
        payloads["page_registry.json"], site_dir, repo_root, errors
    )
    _validate_client_profiles(payloads["client_profiles.json"], errors)
    _validate_deployment_targets(payloads["deployment_targets.json"], errors)
    _validate_public_data_contract(payloads["public_data_contract.json"], errors)
    _validate_redirects(payloads["redirects.json"], errors)
    _validate_claim_traceability_doc(repo_root, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "publication_inventory_validator_v0",
        "inventory_dir": str(inventory_dir),
        "site_dir": str(site_dir),
        "required_files": sorted(REQUIRED_FILES),
        "existing_files": sorted(existing_files),
        "current_public_site_pages": page_summary["current_public_site_pages"],
        "covered_public_site_pages": page_summary["covered_public_site_pages"],
        "registered_routes": page_summary["registered_routes"],
        "reserved_routes": sorted(REQUIRED_RESERVED_ROUTES),
        "required_client_profiles": sorted(REQUIRED_CLIENT_PROFILES),
        "required_public_data_paths": sorted(REQUIRED_PUBLIC_DATA_PATHS),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_contract(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("publication_contract.json: must be a JSON object.")
        return
    missing = sorted(REQUIRED_CONTRACT_FIELDS - set(payload))
    if missing:
        errors.append(f"publication_contract.json: missing fields {missing}.")
    if payload.get("schema_version") != "0.1.0":
        errors.append("publication_contract.json: schema_version must be 0.1.0.")
    if payload.get("contract_id") != "eureka-publication-plane":
        errors.append("publication_contract.json: unexpected contract_id.")
    if payload.get("current_static_artifact") != "public_site":
        errors.append("publication_contract.json: current_static_artifact must be public_site.")
    if payload.get("future_generator_root") != "site":
        errors.append("publication_contract.json: future_generator_root must be site.")
    if payload.get("future_generated_artifact") != "site/dist":
        errors.append(
            "publication_contract.json: future_generated_artifact must be site/dist."
        )
    if payload.get("base_path_policy") != "deployment_target_defined":
        errors.append(
            "publication_contract.json: base_path_policy must be deployment_target_defined."
        )
    for flag in (
        "no_live_backend",
        "no_deployment_performed",
        "no_external_observations",
    ):
        if payload.get(flag) is not True:
            errors.append(f"publication_contract.json: {flag} must be true.")

    status_ids = _ids(payload.get("public_status_taxonomy"))
    missing_statuses = sorted(REQUIRED_STATUS_VALUES - status_ids)
    if missing_statuses:
        errors.append(
            f"publication_contract.json: public_status_taxonomy missing {missing_statuses}."
        )

    stability_ids = _ids(payload.get("route_stability_levels"))
    missing_stability = sorted(REQUIRED_ROUTE_STABILITY_VALUES - stability_ids)
    if missing_stability:
        errors.append(
            f"publication_contract.json: route_stability_levels missing {missing_stability}."
        )

    policy = payload.get("public_claim_source_policy")
    if not isinstance(policy, Mapping):
        errors.append("publication_contract.json: public_claim_source_policy must be an object.")
    elif policy.get("rule") != "No public claim without a repo source.":
        errors.append("publication_contract.json: claim source rule is missing.")


def _validate_page_registry(
    payload: Any, site_dir: Path, repo_root: Path, errors: list[str]
) -> dict[str, list[str]]:
    summary = {
        "current_public_site_pages": [],
        "covered_public_site_pages": [],
        "registered_routes": [],
    }
    if not isinstance(payload, Mapping):
        errors.append("page_registry.json: must be a JSON object.")
        return summary
    routes = payload.get("routes")
    if not isinstance(routes, list):
        errors.append("page_registry.json: routes must be a list.")
        return summary

    route_by_path: dict[str, Mapping[str, Any]] = {}
    source_files: set[str] = set()
    for index, route in enumerate(routes):
        if not isinstance(route, Mapping):
            errors.append(f"page_registry.json: routes[{index}] must be an object.")
            continue
        missing = sorted(REQUIRED_PAGE_FIELDS - set(route))
        if missing:
            errors.append(f"page_registry.json: route {route.get('path', index)} missing {missing}.")
        path = route.get("path")
        if isinstance(path, str):
            summary["registered_routes"].append(path)
            if path in route_by_path:
                errors.append(f"page_registry.json: duplicate route path {path}.")
            route_by_path[path] = route
        else:
            errors.append(f"page_registry.json: routes[{index}].path must be a string.")

        status = route.get("status")
        stability = route.get("stability")
        if status not in REQUIRED_STATUS_VALUES:
            errors.append(f"page_registry.json: route {path} has unknown status {status!r}.")
        if stability not in REQUIRED_ROUTE_STABILITY_VALUES:
            errors.append(
                f"page_registry.json: route {path} has unknown stability {stability!r}."
            )
        if not isinstance(route.get("client_profiles"), list) or not route.get(
            "client_profiles"
        ):
            errors.append(f"page_registry.json: route {path} must name client_profiles.")
        for bool_field in (
            "requires_javascript",
            "requires_css",
            "works_under_project_base_path",
            "safe_for_static_hosting",
        ):
            if not isinstance(route.get(bool_field), bool):
                errors.append(f"page_registry.json: route {path}.{bool_field} must be bool.")

        source_file = route.get("source_file")
        if isinstance(source_file, str):
            source_files.add(source_file.replace("\\", "/"))
            if status == "implemented" and not (repo_root / source_file).exists():
                errors.append(
                    f"page_registry.json: implemented route {path} source_file is missing: {source_file}."
                )

    for reserved in sorted(REQUIRED_RESERVED_ROUTES):
        route = route_by_path.get(reserved)
        if route is None:
            errors.append(f"page_registry.json: missing reserved route {reserved}.")
            continue
        if route.get("status") == "implemented":
            errors.append(f"page_registry.json: reserved route {reserved} is marked implemented.")
        if route.get("source_file") is not None:
            errors.append(f"page_registry.json: reserved route {reserved} must not claim a source_file.")

    current_pages = sorted(
        _to_posix(path.relative_to(repo_root))
        for path in site_dir.glob("*.html")
        if path.is_file()
    )
    summary["current_public_site_pages"] = current_pages
    covered = sorted(page for page in current_pages if page in source_files)
    summary["covered_public_site_pages"] = covered
    missing_pages = sorted(set(current_pages) - source_files)
    if missing_pages:
        errors.append(f"page_registry.json: current public_site pages are not covered: {missing_pages}.")

    return summary


def _validate_client_profiles(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("client_profiles.json: must be a JSON object.")
        return
    profiles = payload.get("profiles")
    if not isinstance(profiles, list):
        errors.append("client_profiles.json: profiles must be a list.")
        return
    profile_by_id: dict[str, Mapping[str, Any]] = {}
    for index, profile in enumerate(profiles):
        if not isinstance(profile, Mapping):
            errors.append(f"client_profiles.json: profiles[{index}] must be an object.")
            continue
        missing = sorted(REQUIRED_CLIENT_PROFILE_FIELDS - set(profile))
        if missing:
            errors.append(
                f"client_profiles.json: profile {profile.get('id', index)} missing {missing}."
            )
        profile_id = profile.get("id")
        if isinstance(profile_id, str):
            profile_by_id[profile_id] = profile
        for bool_field in ("requires_javascript", "requires_css", "requires_https"):
            if not isinstance(profile.get(bool_field), bool):
                errors.append(
                    f"client_profiles.json: profile {profile_id}.{bool_field} must be bool."
                )
    missing_profiles = sorted(REQUIRED_CLIENT_PROFILES - set(profile_by_id))
    if missing_profiles:
        errors.append(f"client_profiles.json: missing profiles {missing_profiles}.")


def _validate_deployment_targets(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("deployment_targets.json: must be a JSON object.")
        return
    targets = payload.get("targets")
    if not isinstance(targets, list):
        errors.append("deployment_targets.json: targets must be a list.")
        return
    by_id = {
        target.get("id"): target
        for target in targets
        if isinstance(target, Mapping) and isinstance(target.get("id"), str)
    }
    github_pages = by_id.get("github_pages_project")
    if not isinstance(github_pages, Mapping):
        errors.append("deployment_targets.json: missing github_pages_project target.")
    else:
        expected = {
            "kind": "static",
            "status": "implemented",
            "artifact_root": "public_site",
            "base_path": "/eureka/",
            "canonical_base_url": "https://julesc013.github.io/eureka/",
            "requires_base_path_safe_links": True,
            "no_backend": True,
            "no_live_probes": True,
            "no_secrets": True,
            "deployment_workflow_path": ".github/workflows/pages.yml",
            "workflow_configured": True,
            "deployment_success_claimed": False,
            "deployment_status": "workflow_configured_deployment_unverified",
        }
        _expect_mapping_values("deployment_targets.json: github_pages_project", github_pages, expected, errors)

    custom_domain = by_id.get("custom_domain_static")
    if not isinstance(custom_domain, Mapping):
        errors.append("deployment_targets.json: missing custom_domain_static target.")
    else:
        expected = {
            "kind": "static",
            "status": "future",
            "artifact_root": "public_site",
            "base_path": "/",
            "requires_domain_verification": True,
            "no_backend": True,
            "no_live_probes": True,
        }
        _expect_mapping_values("deployment_targets.json: custom_domain_static", custom_domain, expected, errors)

    backend = by_id.get("hosted_public_alpha_backend")
    if not isinstance(backend, Mapping):
        errors.append("deployment_targets.json: missing hosted_public_alpha_backend target.")
    else:
        if backend.get("kind") != "backend":
            errors.append("deployment_targets.json: hosted_public_alpha_backend.kind must be backend.")
        if backend.get("status") != "future":
            errors.append("deployment_targets.json: hosted_public_alpha_backend.status must be future.")
        if backend.get("no_live_probes_by_default") is not True:
            errors.append(
                "deployment_targets.json: hosted_public_alpha_backend.no_live_probes_by_default must be true."
            )


def _validate_public_data_contract(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("public_data_contract.json: must be a JSON object.")
        return
    entries = payload.get("entries")
    if not isinstance(entries, list):
        errors.append("public_data_contract.json: entries must be a list.")
        return
    by_path: dict[str, Mapping[str, Any]] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            errors.append(f"public_data_contract.json: entries[{index}] must be an object.")
            continue
        missing = sorted(REQUIRED_PUBLIC_DATA_FIELDS - set(entry))
        if missing:
            errors.append(
                f"public_data_contract.json: entry {entry.get('path', index)} missing {missing}."
            )
        path = entry.get("path")
        if isinstance(path, str):
            by_path[path] = entry
        else:
            errors.append(f"public_data_contract.json: entries[{index}].path must be a string.")
        if entry.get("stability") not in REQUIRED_ROUTE_STABILITY_VALUES:
            errors.append(
                f"public_data_contract.json: entry {path} has unknown stability {entry.get('stability')!r}."
            )
        if entry.get("status") not in REQUIRED_STATUS_VALUES:
            errors.append(
                f"public_data_contract.json: entry {path} has unknown status {entry.get('status')!r}."
            )
        if entry.get("contains_live_data") is not False:
            errors.append(f"public_data_contract.json: entry {path} must not contain live data.")
        if entry.get("contains_external_observations") is not False:
            errors.append(
                f"public_data_contract.json: entry {path} must not contain external observations."
            )
        if entry.get("safe_for_static_hosting") is not True:
            errors.append(f"public_data_contract.json: entry {path} must be safe for static hosting.")

    missing_paths = sorted(REQUIRED_PUBLIC_DATA_PATHS - set(by_path))
    if missing_paths:
        errors.append(f"public_data_contract.json: missing required paths {missing_paths}.")

    for required_path in sorted(REQUIRED_PUBLIC_DATA_PATHS):
        entry = by_path.get(required_path)
        if entry and entry.get("status") not in NON_IMPLEMENTED_STATUSES:
            errors.append(
                f"public_data_contract.json: future data path {required_path} must not be implemented in v0."
            )


def _validate_redirects(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("redirects.json: must be a JSON object.")
        return
    redirects = payload.get("redirects")
    if redirects != []:
        errors.append("redirects.json: redirects must start as an empty list.")
    if payload.get("supports_server_side_redirects") is not False:
        errors.append("redirects.json: supports_server_side_redirects must be false.")


def _validate_claim_traceability_doc(repo_root: Path, errors: list[str]) -> None:
    doc_path = repo_root / "docs" / "architecture" / "PUBLICATION_PLANE.md"
    try:
        text = doc_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append("docs/architecture/PUBLICATION_PLANE.md: file is missing.")
        return
    if "No public claim without a repo source." not in text:
        errors.append("docs/architecture/PUBLICATION_PLANE.md: claim traceability rule is missing.")
    for phrase in (
        "README/status docs",
        "source inventory",
        "route inventory",
        "eval/audit outputs",
        "manual baseline records",
        "static site manifest",
        "publication inventory",
    ):
        if phrase not in text:
            errors.append(
                f"docs/architecture/PUBLICATION_PLANE.md: allowed source phrase missing: {phrase}."
            )


def _expect_mapping_values(
    label: str, payload: Mapping[str, Any], expected: Mapping[str, Any], errors: list[str]
) -> None:
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append(f"{label}.{key} must be {value!r}.")


def _ids(value: Any) -> set[str]:
    ids: set[str] = set()
    if not isinstance(value, list):
        return ids
    for item in value:
        if isinstance(item, str):
            ids.add(item)
        elif isinstance(item, Mapping) and isinstance(item.get("id"), str):
            ids.add(item["id"])
    return ids


def _load_json(path: Path, errors: list[str], repo_root: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path, repo_root)}: file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path, repo_root)}: invalid JSON: {exc}.")
    return None


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Publication inventory validation",
        f"status: {report['status']}",
        f"registered_routes: {len(report['registered_routes'])}",
        f"current_public_site_pages: {len(report['current_public_site_pages'])}",
        f"required_client_profiles: {len(report['required_client_profiles'])}",
        f"required_public_data_paths: {len(report['required_public_data_paths'])}",
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


def _to_posix(path: Path) -> str:
    return str(path).replace("\\", "/")


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
