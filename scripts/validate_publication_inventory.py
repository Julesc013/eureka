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
    "domain_plan.json",
    "live_backend_handoff.json",
    "live_backend_routes.json",
    "live_probe_gateway.json",
    "public_data_contract.json",
    "redirects.json",
    "static_hosting_targets.json",
    "surface_capabilities.json",
    "surface_route_matrix.json",
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
    "/api/v1/",
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
    "/files/manifest.json",
    "/files/index.txt",
    "/files/SHA256SUMS",
    "/demo/data/demo_snapshots.json",
}
REQUIRED_GENERATED_PUBLIC_DATA_PATHS = {
    "/data/site_manifest.json",
    "/data/page_registry.json",
    "/data/source_summary.json",
    "/data/eval_summary.json",
    "/data/route_summary.json",
    "/data/build_manifest.json",
}
REQUIRED_FILE_SURFACE_PATHS = {
    "/files/manifest.json",
    "/files/index.txt",
    "/files/SHA256SUMS",
}
REQUIRED_DEMO_ROUTES = {
    "/demo/",
    "/demo/query-plan-windows-7-apps.html",
    "/demo/result-member-driver-inside-support-cd.html",
    "/demo/result-firefox-xp.html",
    "/demo/result-article-scan.html",
    "/demo/absence-example.html",
    "/demo/comparison-example.html",
    "/demo/source-example.html",
    "/demo/eval-summary.html",
}
REQUIRED_DEMO_DATA_PATHS = {
    "/demo/data/demo_snapshots.json",
}
REQUIRED_LIVE_BACKEND_ENDPOINTS = {
    "/api/v1/status",
    "/api/v1/search",
    "/api/v1/query-plan",
    "/api/v1/sources",
    "/api/v1/source/{source_id}",
    "/api/v1/evidence/{evidence_id}",
    "/api/v1/object/{object_id}",
    "/api/v1/result/{result_id}",
    "/api/v1/absence",
    "/api/v1/compare",
    "/api/v1/live-probe",
}
REQUIRED_SURFACE_CAPABILITIES = {
    "static_site",
    "generated_public_data",
    "lite_surface",
    "text_surface",
    "files_surface",
    "demo_snapshots",
    "public_alpha_wrapper",
    "live_backend",
    "live_search",
    "live_probe_gateway",
    "internet_archive_live_probe",
    "external_baseline_observations",
    "native_clients",
    "rust_runtime",
}
REQUIRED_LIVE_PROBE_CANDIDATE_SOURCES = {
    "internet_archive_metadata",
    "internet_archive_item_metadata",
    "wayback_availability",
    "wayback_cdx_metadata",
    "github_releases_metadata",
    "software_heritage_metadata",
    "pypi_package_metadata",
    "npm_package_metadata",
    "wikidata_metadata",
}
DISABLED_LIVE_CAPABILITIES = {
    "live_backend",
    "live_search",
    "live_probe_gateway",
    "internet_archive_live_probe",
}
IMPLEMENTED_ROUTE_STATUSES = {
    "implemented",
    "static_demo",
}
SEEDED_COMPATIBILITY_ROUTES = {
    "/lite/",
    "/text/",
    "/files/",
}
REQUIRED_PUBLIC_DATA_FIELDS = {
    "path",
    "status",
    "stability",
    "schema_version",
    "producer",
    "source_inputs",
    "consumer_profiles",
    "contains_live_data",
    "contains_external_observations",
    "safe_for_static_hosting",
    "generated_by",
    "notes",
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
        "domain_plan.json": _load_json(
            inventory_dir / "domain_plan.json", errors, repo_root
        ),
        "live_backend_handoff.json": _load_json(
            inventory_dir / "live_backend_handoff.json", errors, repo_root
        ),
        "live_backend_routes.json": _load_json(
            inventory_dir / "live_backend_routes.json", errors, repo_root
        ),
        "live_probe_gateway.json": _load_json(
            inventory_dir / "live_probe_gateway.json", errors, repo_root
        ),
        "public_data_contract.json": _load_json(
            inventory_dir / "public_data_contract.json", errors, repo_root
        ),
        "redirects.json": _load_json(inventory_dir / "redirects.json", errors, repo_root),
        "static_hosting_targets.json": _load_json(
            inventory_dir / "static_hosting_targets.json", errors, repo_root
        ),
        "surface_capabilities.json": _load_json(
            inventory_dir / "surface_capabilities.json", errors, repo_root
        ),
        "surface_route_matrix.json": _load_json(
            inventory_dir / "surface_route_matrix.json", errors, repo_root
        ),
    }

    _validate_contract(payloads["publication_contract.json"], errors)
    page_summary = _validate_page_registry(
        payloads["page_registry.json"], site_dir, repo_root, errors
    )
    _validate_client_profiles(payloads["client_profiles.json"], errors)
    _validate_deployment_targets(payloads["deployment_targets.json"], errors)
    _validate_domain_plan(payloads["domain_plan.json"], errors)
    _validate_live_backend_handoff(payloads["live_backend_handoff.json"], errors)
    _validate_live_backend_routes(payloads["live_backend_routes.json"], errors)
    _validate_live_probe_gateway(payloads["live_probe_gateway.json"], errors)
    _validate_public_data_contract(payloads["public_data_contract.json"], site_dir, errors)
    _validate_redirects(payloads["redirects.json"], errors)
    _validate_static_hosting_targets(payloads["static_hosting_targets.json"], errors)
    _validate_surface_capabilities(payloads["surface_capabilities.json"], errors)
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
        "domain_plan_checked": "domain_plan.json" in existing_files,
        "live_backend_handoff_checked": "live_backend_handoff.json" in existing_files,
        "live_backend_routes_checked": "live_backend_routes.json" in existing_files,
        "live_probe_gateway_checked": "live_probe_gateway.json" in existing_files,
        "static_hosting_targets_checked": "static_hosting_targets.json" in existing_files,
        "surface_capabilities_checked": "surface_capabilities.json" in existing_files,
        "surface_route_matrix_checked": "surface_route_matrix.json" in existing_files,
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
    if payload.get("generator_status") != "implemented":
        errors.append("publication_contract.json: generator_status must be implemented.")
    if payload.get("generated_artifact_deployed") is not False:
        errors.append(
            "publication_contract.json: generated_artifact_deployed must be false."
        )
    if payload.get("deploy_artifact_current") != "public_site":
        errors.append("publication_contract.json: deploy_artifact_current must be public_site.")
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
            if status in IMPLEMENTED_ROUTE_STATUSES and not (repo_root / source_file).exists():
                errors.append(
                    f"page_registry.json: implemented route {path} source_file is missing: {source_file}."
                )

    for reserved in sorted(REQUIRED_RESERVED_ROUTES):
        route = route_by_path.get(reserved)
        if route is None:
            errors.append(f"page_registry.json: missing reserved route {reserved}.")
            continue
        if reserved in SEEDED_COMPATIBILITY_ROUTES:
            if route.get("status") not in IMPLEMENTED_ROUTE_STATUSES:
                errors.append(
                    f"page_registry.json: seeded compatibility route {reserved} must be implemented or static_demo."
                )
            if not isinstance(route.get("source_file"), str):
                errors.append(
                    f"page_registry.json: seeded compatibility route {reserved} must claim a source_file."
                )
        else:
            if route.get("status") in IMPLEMENTED_ROUTE_STATUSES:
                errors.append(f"page_registry.json: reserved route {reserved} is marked implemented.")
            if route.get("source_file") is not None:
                errors.append(f"page_registry.json: reserved route {reserved} must not claim a source_file.")

    for demo_route in sorted(REQUIRED_DEMO_ROUTES):
        route = route_by_path.get(demo_route)
        if route is None:
            errors.append(f"page_registry.json: missing static demo route {demo_route}.")
            continue
        if route.get("status") != "static_demo":
            errors.append(f"page_registry.json: demo route {demo_route} must be static_demo.")
        if route.get("stability") != "stable_draft":
            errors.append(f"page_registry.json: demo route {demo_route} must be stable_draft.")
        if route.get("requires_javascript") is not False:
            errors.append(f"page_registry.json: demo route {demo_route} must not require JavaScript.")
        if route.get("safe_for_static_hosting") is not True:
            errors.append(f"page_registry.json: demo route {demo_route} must be safe for static hosting.")
        if not isinstance(route.get("source_file"), str):
            errors.append(f"page_registry.json: demo route {demo_route} must claim a source_file.")

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
        "generated_artifact_root": "site/dist",
        "generated_artifact_deployed": False,
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


def _validate_domain_plan(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("domain_plan.json: must be a JSON object.")
        return
    expected = {
        "schema_version": "0.1.0",
        "plan_id": "eureka-custom-domain-alternate-host-readiness",
        "status": "planned",
        "no_domain_configured": True,
        "no_dns_changes_performed": True,
        "no_cname_file_committed": True,
        "custom_domain_status": "future",
        "github_pages_project_status": "implemented",
        "custom_domain_static_status": "future",
        "domain_verification_required": True,
        "created_by_slice": "custom_domain_alternate_host_readiness_v0",
    }
    _expect_mapping_values("domain_plan.json", payload, expected, errors)
    transition = payload.get("base_path_transition")
    if not isinstance(transition, Mapping):
        errors.append("domain_plan.json: base_path_transition must be an object.")
    else:
        if transition.get("from") != "/eureka/":
            errors.append("domain_plan.json: base_path_transition.from must be /eureka/.")
        if transition.get("to") != "/":
            errors.append("domain_plan.json: base_path_transition.to must be /.")
        if transition.get("status") != "future":
            errors.append("domain_plan.json: base_path_transition.status must be future.")


def _validate_live_backend_handoff(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("live_backend_handoff.json: must be a JSON object.")
        return
    expected = {
        "schema_version": "0.1.0",
        "handoff_id": "eureka-live-backend-handoff",
        "status": "planned",
        "stability": "experimental",
        "no_live_backend_implemented": True,
        "no_deployment_performed": True,
        "static_site_current": True,
        "public_alpha_backend_future": True,
        "created_by_slice": "live_backend_handoff_contract_v0",
    }
    _expect_mapping_values("live_backend_handoff.json", payload, expected, errors)
    endpoints = set(_string_list(payload.get("endpoint_prefixes_reserved")))
    missing = sorted(REQUIRED_LIVE_BACKEND_ENDPOINTS - endpoints)
    if missing:
        errors.append(f"live_backend_handoff.json: missing reserved endpoints {missing}.")
    for key in ("cors_policy_status", "auth_policy_status", "rate_limit_policy_status"):
        if payload.get(key) != "unresolved":
            errors.append(f"live_backend_handoff.json: {key} must be unresolved.")
    if payload.get("live_probe_dependency_status") != "requires_live_probe_gateway_contract_v0":
        errors.append(
            "live_backend_handoff.json: live_probe_dependency_status must require Live Probe Gateway Contract v0."
        )


def _validate_live_backend_routes(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("live_backend_routes.json: must be a JSON object.")
        return
    expected = {
        "schema_version": "0.1.0",
        "registry_id": "eureka-live-backend-routes",
        "status": "planned",
        "stability": "experimental",
        "route_prefix": "/api/v1",
        "no_live_backend_implemented": True,
        "current_local_api_public_contract": False,
    }
    _expect_mapping_values("live_backend_routes.json", payload, expected, errors)
    routes = payload.get("routes")
    if not isinstance(routes, list):
        errors.append("live_backend_routes.json: routes must be a list.")
        return
    by_path = {
        route.get("path_template"): route
        for route in routes
        if isinstance(route, Mapping) and isinstance(route.get("path_template"), str)
    }
    missing = sorted(REQUIRED_LIVE_BACKEND_ENDPOINTS - set(by_path))
    if missing:
        errors.append(f"live_backend_routes.json: missing endpoints {missing}.")
    for path, route in by_path.items():
        if route.get("status") in IMPLEMENTED_ROUTE_STATUSES:
            errors.append(f"live_backend_routes.json: {path} must not be implemented.")
        if route.get("requires_live_backend") is not True:
            errors.append(f"live_backend_routes.json: {path} must require live backend.")
    live_probe = by_path.get("/api/v1/live-probe")
    if isinstance(live_probe, Mapping):
        if live_probe.get("status") not in {"blocked", "deferred", "unsafe_for_public_alpha"}:
            errors.append("live_backend_routes.json: /api/v1/live-probe must be blocked/deferred.")
        if live_probe.get("public_alpha_allowed") is not False:
            errors.append("live_backend_routes.json: /api/v1/live-probe must not be public-alpha allowed.")
        if live_probe.get("static_handoff_allowed") is not False:
            errors.append("live_backend_routes.json: /api/v1/live-probe must not allow static handoff.")


def _validate_live_probe_gateway(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("live_probe_gateway.json: must be a JSON object.")
        return
    expected = {
        "schema_version": "0.1.0",
        "gateway_id": "eureka-live-probe-gateway",
        "status": "planned",
        "stability": "experimental",
        "no_live_probes_implemented": True,
        "no_network_calls_performed": True,
        "enabled_by_default": False,
        "public_alpha_default_enabled": False,
        "requires_live_backend_handoff": True,
        "requires_operator_signoff": True,
        "requires_abuse_controls": True,
        "requires_source_policy_review": True,
        "created_by_slice": "live_probe_gateway_contract_v0",
    }
    _expect_mapping_values("live_probe_gateway.json", payload, expected, errors)
    global_limits = payload.get("global_limits")
    if not isinstance(global_limits, Mapping):
        errors.append("live_probe_gateway.json: global_limits must be an object.")
    else:
        for key in (
            "allow_arbitrary_url_fetch",
            "allow_downloads",
            "allow_write_actions",
            "allow_auth_user_credentials",
        ):
            if global_limits.get(key) is not False:
                errors.append(f"live_probe_gateway.json: global_limits.{key} must be false.")
    candidates = payload.get("future_candidate_sources")
    if not isinstance(candidates, list):
        errors.append("live_probe_gateway.json: future_candidate_sources must be a list.")
        return
    by_id = {
        item.get("id"): item
        for item in candidates
        if isinstance(item, Mapping) and isinstance(item.get("id"), str)
    }
    missing = sorted(REQUIRED_LIVE_PROBE_CANDIDATE_SOURCES - set(by_id))
    if missing:
        errors.append(f"live_probe_gateway.json: missing candidate sources {missing}.")
    if "google_web_search" in by_id:
        errors.append("live_probe_gateway.json: google_web_search must not be a live probe candidate.")
    disabled = set(_string_list(payload.get("disabled_sources")))
    missing_disabled = sorted(REQUIRED_LIVE_PROBE_CANDIDATE_SOURCES - disabled)
    if missing_disabled:
        errors.append(f"live_probe_gateway.json: disabled_sources missing {missing_disabled}.")
    for source_id, candidate in by_id.items():
        if candidate.get("status") != "future_disabled":
            errors.append(f"live_probe_gateway.json: {source_id}.status must be future_disabled.")
        if candidate.get("live_supported_now") is not False:
            errors.append(f"live_probe_gateway.json: {source_id}.live_supported_now must be false.")
        if candidate.get("requires_operator_enable") is not True:
            errors.append(f"live_probe_gateway.json: {source_id}.requires_operator_enable must be true.")
        if candidate.get("cache_required") is not True:
            errors.append(f"live_probe_gateway.json: {source_id}.cache_required must be true.")
        if candidate.get("evidence_required") is not True:
            errors.append(f"live_probe_gateway.json: {source_id}.evidence_required must be true.")
    manual = payload.get("manual_only_sources")
    if not isinstance(manual, list):
        errors.append("live_probe_gateway.json: manual_only_sources must be a list.")
    elif not any(
        isinstance(item, Mapping)
        and item.get("id") == "google_web_search"
        and item.get("status") == "manual_external_baseline"
        and item.get("live_probe_candidate") is False
        for item in manual
    ):
        errors.append("live_probe_gateway.json: google_web_search manual-only baseline record is required.")


def _validate_public_data_contract(payload: Any, site_dir: Path, errors: list[str]) -> None:
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
        if not isinstance(entry.get("source_inputs"), list) or not entry.get("source_inputs"):
            errors.append(f"public_data_contract.json: entry {path} must name source_inputs.")
        if not isinstance(entry.get("generated_by"), str) or not entry.get("generated_by"):
            errors.append(f"public_data_contract.json: entry {path} must name generated_by.")

    missing_paths = sorted(REQUIRED_PUBLIC_DATA_PATHS - set(by_path))
    if missing_paths:
        errors.append(f"public_data_contract.json: missing required paths {missing_paths}.")

    for required_path in sorted(REQUIRED_GENERATED_PUBLIC_DATA_PATHS):
        entry = by_path.get(required_path)
        if not entry:
            continue
        if entry.get("status") != "implemented":
            errors.append(
                f"public_data_contract.json: generated data path {required_path} must be implemented."
            )
        if entry.get("stability") != "stable_draft":
            errors.append(
                f"public_data_contract.json: generated data path {required_path} must be stable_draft."
            )
        generated_file = site_dir / required_path.removeprefix("/")
        if not generated_file.exists():
            errors.append(
                f"public_data_contract.json: generated data path {required_path} is missing from public_site."
            )

    for required_path in sorted(REQUIRED_FILE_SURFACE_PATHS):
        entry = by_path.get(required_path)
        if not entry:
            continue
        if entry.get("status") not in IMPLEMENTED_ROUTE_STATUSES:
            errors.append(
                f"public_data_contract.json: file surface path {required_path} must be implemented or static_demo."
            )
        if entry.get("stability") != "stable_draft":
            errors.append(
                f"public_data_contract.json: file surface path {required_path} must be stable_draft."
            )
        generated_file = site_dir / required_path.removeprefix("/")
        if not generated_file.exists():
            errors.append(
                f"public_data_contract.json: file surface path {required_path} is missing from public_site."
            )

    for required_path in sorted(REQUIRED_DEMO_DATA_PATHS):
        entry = by_path.get(required_path)
        if not entry:
            continue
        if entry.get("status") != "static_demo":
            errors.append(
                f"public_data_contract.json: demo data path {required_path} must be static_demo."
            )
        if entry.get("stability") != "stable_draft":
            errors.append(
                f"public_data_contract.json: demo data path {required_path} must be stable_draft."
            )
        if entry.get("generated_by") != "scripts/generate_static_resolver_demos.py":
            errors.append(
                f"public_data_contract.json: demo data path {required_path} must be generated by scripts/generate_static_resolver_demos.py."
            )
        generated_file = site_dir / required_path.removeprefix("/")
        if not generated_file.exists():
            errors.append(
                f"public_data_contract.json: demo data path {required_path} is missing from public_site."
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


def _validate_static_hosting_targets(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("static_hosting_targets.json: must be a JSON object.")
        return
    if payload.get("schema_version") != "0.1.0":
        errors.append("static_hosting_targets.json: schema_version must be 0.1.0.")
    targets = payload.get("targets")
    if not isinstance(targets, list):
        errors.append("static_hosting_targets.json: targets must be a list.")
        return
    by_id = {
        target.get("id"): target
        for target in targets
        if isinstance(target, Mapping) and isinstance(target.get("id"), str)
    }
    required = {
        "github_pages_project",
        "github_pages_custom_domain",
        "cloudflare_pages_static",
        "generic_static_host",
        "local_file_preview",
    }
    missing = sorted(required - set(by_id))
    if missing:
        errors.append(f"static_hosting_targets.json: missing targets {missing}.")
    project = by_id.get("github_pages_project")
    if isinstance(project, Mapping):
        expected = {
            "status": "implemented",
            "kind": "static",
            "base_path": "/eureka/",
            "artifact_root": "public_site",
            "workflow_configured": True,
            "deployment_success_claimed": False,
            "backend_supported": False,
            "live_probes_supported": False,
            "custom_domain_status": "future",
        }
        _expect_mapping_values(
            "static_hosting_targets.json: github_pages_project", project, expected, errors
        )
    custom = by_id.get("github_pages_custom_domain")
    if isinstance(custom, Mapping):
        expected = {
            "status": "future",
            "kind": "static",
            "base_path": "/",
            "artifact_root": "public_site",
            "requires_domain_verification": True,
            "dns_config_not_in_repo": True,
            "backend_supported": False,
            "live_probes_supported": False,
            "provider_config_committed": False,
        }
        _expect_mapping_values(
            "static_hosting_targets.json: github_pages_custom_domain", custom, expected, errors
        )
    for target_id in ("cloudflare_pages_static", "generic_static_host"):
        target = by_id.get(target_id)
        if isinstance(target, Mapping):
            if target.get("status") != "future":
                errors.append(f"static_hosting_targets.json: {target_id}.status must be future.")
            if target.get("base_path") != "/":
                errors.append(f"static_hosting_targets.json: {target_id}.base_path must be /.")
            if target.get("provider_config_committed") is not False:
                errors.append(
                    f"static_hosting_targets.json: {target_id}.provider_config_committed must be false."
                )


def _validate_surface_capabilities(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("surface_capabilities.json: must be a JSON object.")
        return
    if payload.get("schema_version") != "0.1.0":
        errors.append("surface_capabilities.json: schema_version must be 0.1.0.")
    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, list):
        errors.append("surface_capabilities.json: capabilities must be a list.")
        return
    by_id = {
        item.get("id"): item
        for item in capabilities
        if isinstance(item, Mapping) and isinstance(item.get("id"), str)
    }
    missing = sorted(REQUIRED_SURFACE_CAPABILITIES - set(by_id))
    if missing:
        errors.append(f"surface_capabilities.json: missing capabilities {missing}.")
    for capability_id in ("static_site", "generated_public_data"):
        capability = by_id.get(capability_id)
        if isinstance(capability, Mapping):
            if capability.get("status") != "implemented":
                errors.append(f"surface_capabilities.json: {capability_id}.status must be implemented.")
            if capability.get("enabled_by_default") is not True:
                errors.append(
                    f"surface_capabilities.json: {capability_id}.enabled_by_default must be true."
                )
    for capability_id in DISABLED_LIVE_CAPABILITIES:
        capability = by_id.get(capability_id)
        if isinstance(capability, Mapping):
            if capability.get("enabled_by_default") is not False:
                errors.append(
                    f"surface_capabilities.json: {capability_id}.enabled_by_default must be false."
                )
            if capability.get("requires_backend") is not True:
                errors.append(f"surface_capabilities.json: {capability_id}.requires_backend must be true.")
            if capability.get("status") in IMPLEMENTED_ROUTE_STATUSES:
                errors.append(
                    f"surface_capabilities.json: {capability_id}.status must remain future/deferred/blocked."
                )


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


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


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
