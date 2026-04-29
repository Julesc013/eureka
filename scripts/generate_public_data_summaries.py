from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "public_site" / "data"
PUBLIC_SITE_ROOT = REPO_ROOT / "public_site"
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
SOURCE_INVENTORY_DIR = REPO_ROOT / "control" / "inventory" / "sources"
PUBLIC_ALPHA_ROUTES = REPO_ROOT / "control" / "inventory" / "public_alpha_routes.json"

SCHEMA_VERSION = "0.1.0"
GENERATED_BY = "scripts/generate_public_data_summaries.py"
SLICE_ID = "generated_public_data_summaries_v0"
REPO_ID = "Julesc013/eureka"
REQUIRED_DATA_FILES = (
    "site_manifest.json",
    "page_registry.json",
    "source_summary.json",
    "eval_summary.json",
    "route_summary.json",
    "build_manifest.json",
)
PUBLIC_DATA_PATHS = tuple(f"/data/{name}" for name in REQUIRED_DATA_FILES)


class PublicDataGenerationError(RuntimeError):
    pass


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate deterministic static public data summaries."
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Directory that receives generated public data JSON files.",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Write generated summaries into the output root.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify committed/generated summaries match current repo inputs.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    output = stdout or sys.stdout
    try:
        if args.check:
            report = check_public_data_summaries(Path(args.output_root))
        elif args.update:
            report = write_public_data_summaries(Path(args.output_root))
        else:
            payloads = generate_public_data_summaries()
            report = _summary_report(Path(args.output_root), payloads, updated=False)
        if args.json:
            output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        else:
            output.write(_format_plain(report))
        return 0 if report["status"] == "valid" else 1
    except PublicDataGenerationError as exc:
        report = {
            "status": "invalid",
            "created_by": SLICE_ID,
            "errors": [str(exc)],
        }
        if args.json:
            output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        else:
            output.write(_format_plain(report))
        return 1


def generate_public_data_summaries() -> dict[str, dict[str, Any]]:
    publication_contract = _load_json(PUBLICATION_DIR / "publication_contract.json")
    action_policy = _load_json(PUBLICATION_DIR / "action_policy.json")
    local_cache_privacy_policy = _load_json(
        PUBLICATION_DIR / "local_cache_privacy_policy.json"
    )
    page_registry = _load_json(PUBLICATION_DIR / "page_registry.json")
    deployment_targets = _load_json(PUBLICATION_DIR / "deployment_targets.json")
    domain_plan = _load_json(PUBLICATION_DIR / "domain_plan.json")
    live_backend_handoff = _load_json(PUBLICATION_DIR / "live_backend_handoff.json")
    live_backend_routes = _load_json(PUBLICATION_DIR / "live_backend_routes.json")
    live_probe_gateway = _load_json(PUBLICATION_DIR / "live_probe_gateway.json")
    public_data_contract = _load_json(PUBLICATION_DIR / "public_data_contract.json")
    relay_surface = _load_json(PUBLICATION_DIR / "relay_surface.json")
    snapshot_contract = _load_json(PUBLICATION_DIR / "snapshot_contract.json")
    static_hosting_targets = _load_json(PUBLICATION_DIR / "static_hosting_targets.json")
    surface_capabilities = _load_json(PUBLICATION_DIR / "surface_capabilities.json")
    source_records = _load_source_records()
    route_inventory = _load_json(PUBLIC_ALPHA_ROUTES)

    page_registry_summary = _build_page_registry_summary(page_registry)
    source_summary = _build_source_summary(source_records)
    eval_summary = _build_eval_summary()
    route_summary = _build_route_summary(route_inventory)
    build_manifest = _build_build_manifest(
        public_data_contract, action_policy, local_cache_privacy_policy
    )
    site_manifest = _build_data_site_manifest(
        publication_contract,
        action_policy,
        local_cache_privacy_policy,
        page_registry_summary,
        deployment_targets,
        domain_plan,
        live_backend_handoff,
        live_backend_routes,
        live_probe_gateway,
        public_data_contract,
        relay_surface,
        snapshot_contract,
        static_hosting_targets,
        surface_capabilities,
    )

    return {
        "site_manifest.json": site_manifest,
        "page_registry.json": page_registry_summary,
        "source_summary.json": source_summary,
        "eval_summary.json": eval_summary,
        "route_summary.json": route_summary,
        "build_manifest.json": build_manifest,
    }


def write_public_data_summaries(output_root: Path = DEFAULT_OUTPUT_ROOT) -> dict[str, Any]:
    payloads = generate_public_data_summaries()
    output_root.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for name, payload in payloads.items():
        path = output_root / name
        path.write_text(_json_text(payload), encoding="utf-8")
        written.append(_display_path(path))
    report = _summary_report(output_root, payloads, updated=True)
    report["written_files"] = written
    return report


def check_public_data_summaries(output_root: Path = DEFAULT_OUTPUT_ROOT) -> dict[str, Any]:
    payloads = generate_public_data_summaries()
    errors: list[str] = []
    existing_files: list[str] = []
    for name, payload in payloads.items():
        path = output_root / name
        expected = _json_text(payload)
        try:
            actual = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            errors.append(f"{_display_path(path)}: generated public data file is missing.")
            continue
        existing_files.append(_display_path(path))
        if actual != expected:
            errors.append(
                f"{_display_path(path)}: generated public data is stale; run "
                "python scripts/generate_public_data_summaries.py --update."
            )
        try:
            parsed = json.loads(actual)
        except json.JSONDecodeError as exc:
            errors.append(f"{_display_path(path)}: invalid JSON: {exc}.")
            continue
        _validate_static_safety(path, parsed, errors)

    report = _summary_report(output_root, payloads, updated=False)
    report["check_mode"] = True
    report["existing_files"] = sorted(existing_files)
    report["errors"] = errors
    report["status"] = "valid" if not errors else "invalid"
    return report


def _build_data_site_manifest(
    publication_contract: Mapping[str, Any],
    action_policy: Mapping[str, Any],
    local_cache_privacy_policy: Mapping[str, Any],
    page_registry_summary: Mapping[str, Any],
    deployment_targets: Mapping[str, Any],
    domain_plan: Mapping[str, Any],
    live_backend_handoff: Mapping[str, Any],
    live_backend_routes: Mapping[str, Any],
    live_probe_gateway: Mapping[str, Any],
    public_data_contract: Mapping[str, Any],
    relay_surface: Mapping[str, Any],
    snapshot_contract: Mapping[str, Any],
    static_hosting_targets: Mapping[str, Any],
    surface_capabilities: Mapping[str, Any],
) -> dict[str, Any]:
    targets = [
        {
            "id": target.get("id"),
            "kind": target.get("kind"),
            "status": target.get("status"),
            "artifact_root": target.get("artifact_root"),
            "base_path": target.get("base_path"),
            "no_backend": target.get("no_backend", target.get("kind") != "backend"),
            "no_live_probes": target.get("no_live_probes", target.get("no_live_probes_by_default", True)),
            "deployment_success_claimed": target.get("deployment_success_claimed", False),
        }
        for target in deployment_targets.get("targets", [])
        if isinstance(target, Mapping)
    ]
    base_paths = sorted(
        {
            str(target["base_path"])
            for target in targets
            if isinstance(target.get("base_path"), str)
        }
    )
    public_data_files = [
        entry.get("path")
        for entry in public_data_contract.get("entries", [])
        if isinstance(entry, Mapping) and str(entry.get("path", "")).startswith("/data/")
    ]
    host_targets = [
        {
            "id": target.get("id"),
            "status": target.get("status"),
            "base_path": target.get("base_path"),
            "artifact_root": target.get("artifact_root"),
            "backend_supported": target.get("backend_supported", target.get("backend_supported_by_this_repo", False)),
            "live_probes_supported": target.get("live_probes_supported", False),
            "provider_config_committed": target.get("provider_config_committed", False),
        }
        for target in static_hosting_targets.get("targets", [])
        if isinstance(target, Mapping)
    ]
    capabilities = [
        {
            "id": capability.get("id"),
            "status": capability.get("status"),
            "enabled_by_default": capability.get("enabled_by_default"),
            "requires_backend": capability.get("requires_backend"),
            "safe_for_static_hosting": capability.get("safe_for_static_hosting"),
        }
        for capability in surface_capabilities.get("capabilities", [])
        if isinstance(capability, Mapping)
    ]
    live_routes = [
        {
            "path_template": route.get("path_template"),
            "method": route.get("method"),
            "status": route.get("status"),
            "static_handoff_allowed": route.get("static_handoff_allowed"),
            "public_alpha_allowed": route.get("public_alpha_allowed"),
            "live_probe_related": route.get("live_probe_related"),
        }
        for route in live_backend_routes.get("routes", [])
        if isinstance(route, Mapping)
    ]
    live_probe_candidates = [
        {
            "id": source.get("id"),
            "status": source.get("status"),
            "live_supported_now": source.get("live_supported_now"),
            "requires_operator_enable": source.get("requires_operator_enable"),
            "allowed_modes": source.get("allowed_modes", []),
            "default_result_cap": source.get("default_result_cap"),
            "default_timeout_ms": source.get("default_timeout_ms"),
            "cache_required": source.get("cache_required"),
            "evidence_required": source.get("evidence_required"),
        }
        for source in live_probe_gateway.get("future_candidate_sources", [])
        if isinstance(source, Mapping)
    ]
    relay_protocol_candidates = [
        {
            "id": candidate.get("id"),
            "status": candidate.get("status"),
            "implemented": candidate.get("implemented"),
            "default_scope": candidate.get("default_scope"),
            "allowed_data": candidate.get("allowed_data"),
        }
        for candidate in relay_surface.get("future_protocol_candidates", [])
        if isinstance(candidate, Mapping)
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "artifact": "public_site/data",
        "current_static_artifact": publication_contract.get("current_static_artifact", "public_site"),
        "publication_contract_id": publication_contract.get("contract_id"),
        "publication_contract_version": publication_contract.get("schema_version"),
        "pages": page_registry_summary.get("pages", []),
        "public_data_files": sorted(public_data_files),
        "deployment_targets": targets,
        "static_hosting_targets": host_targets,
        "custom_domain_readiness": {
            "status": "implemented",
            "plan_id": domain_plan.get("plan_id"),
            "no_domain_configured": domain_plan.get("no_domain_configured"),
            "no_dns_changes_performed": domain_plan.get("no_dns_changes_performed"),
            "no_cname_file_committed": domain_plan.get("no_cname_file_committed"),
            "custom_domain_status": domain_plan.get("custom_domain_status"),
            "custom_domain_static_status": domain_plan.get("custom_domain_static_status"),
            "domain_verification_required": domain_plan.get("domain_verification_required"),
        },
        "live_backend_handoff": {
            "status": "implemented_contract_only",
            "handoff_id": live_backend_handoff.get("handoff_id"),
            "route_prefix": live_backend_routes.get("route_prefix"),
            "no_live_backend_implemented": live_backend_handoff.get("no_live_backend_implemented"),
            "no_deployment_performed": live_backend_handoff.get("no_deployment_performed"),
            "public_alpha_backend_future": live_backend_handoff.get("public_alpha_backend_future"),
            "cors_policy_status": live_backend_handoff.get("cors_policy_status"),
            "auth_policy_status": live_backend_handoff.get("auth_policy_status"),
            "rate_limit_policy_status": live_backend_handoff.get("rate_limit_policy_status"),
            "live_probe_dependency_status": live_backend_handoff.get("live_probe_dependency_status"),
            "reserved_endpoint_count": len(live_routes),
            "reserved_endpoints": live_routes,
        },
        "live_probe_gateway": {
            "status": "implemented_contract_only_runtime_disabled",
            "gateway_id": live_probe_gateway.get("gateway_id"),
            "no_live_probes_implemented": live_probe_gateway.get("no_live_probes_implemented"),
            "no_network_calls_performed": live_probe_gateway.get("no_network_calls_performed"),
            "enabled_by_default": live_probe_gateway.get("enabled_by_default"),
            "public_alpha_default_enabled": live_probe_gateway.get("public_alpha_default_enabled"),
            "allow_arbitrary_url_fetch": _mapping(live_probe_gateway.get("global_limits")).get(
                "allow_arbitrary_url_fetch"
            ),
            "allow_downloads": _mapping(live_probe_gateway.get("global_limits")).get("allow_downloads"),
            "candidate_source_count": len(live_probe_candidates),
            "candidate_sources": live_probe_candidates,
            "manual_only_sources": live_probe_gateway.get("manual_only_sources", []),
        },
        "relay_surface": {
            "status": "implemented_contract_only_runtime_absent",
            "relay_surface_id": relay_surface.get("relay_surface_id"),
            "no_relay_implemented": relay_surface.get("no_relay_implemented"),
            "no_network_services_implemented": relay_surface.get("no_network_services_implemented"),
            "no_protocol_servers_implemented": relay_surface.get("no_protocol_servers_implemented"),
            "default_scope": relay_surface.get("default_scope"),
            "default_mode": relay_surface.get("default_mode"),
            "public_data_only_by_default": relay_surface.get("public_data_only_by_default"),
            "private_data_disabled_by_default": relay_surface.get("private_data_disabled_by_default"),
            "write_actions_disabled_by_default": relay_surface.get("write_actions_disabled_by_default"),
            "live_probes_disabled_by_default": relay_surface.get("live_probes_disabled_by_default"),
            "admin_routes_disabled_for_old_clients": relay_surface.get(
                "admin_routes_disabled_for_old_clients"
            ),
            "protocol_candidate_count": len(relay_protocol_candidates),
            "protocol_candidates": relay_protocol_candidates,
        },
        "snapshot_format": {
            "status": "implemented_contract_seed_example",
            "snapshot_contract_id": snapshot_contract.get("snapshot_contract_id"),
            "snapshot_format_version": snapshot_contract.get("snapshot_format_version"),
            "production_signed_release": snapshot_contract.get("production_signed_release"),
            "real_signing_keys_present": snapshot_contract.get("real_signing_keys_present"),
            "contains_real_binaries": snapshot_contract.get("contains_real_binaries"),
            "seed_example_root": _mapping(snapshot_contract.get("file_tree_policy")).get(
                "snapshot_example_root"
            ),
            "public_snapshots_route_status": _mapping(snapshot_contract.get("file_tree_policy")).get(
                "public_snapshots_route_status"
            ),
        },
        "action_policy": {
            "status": "implemented_policy_only",
            "action_policy_id": action_policy.get("action_policy_id"),
            "no_install_automation_implemented": action_policy.get(
                "no_install_automation_implemented"
            ),
            "no_download_surface_implemented": action_policy.get(
                "no_download_surface_implemented"
            ),
            "no_malware_scanning_claim": action_policy.get("no_malware_scanning_claim"),
            "no_rights_clearance_claim": action_policy.get("no_rights_clearance_claim"),
            "future_gated_actions": action_policy.get("future_gated_actions", []),
            "prohibited_until_policy": action_policy.get("prohibited_until_policy", []),
            "public_alpha_defaults": action_policy.get("public_alpha_defaults", {}),
            "static_site_defaults": action_policy.get("static_site_defaults", {}),
        },
        "local_cache_privacy_policy": {
            "status": "implemented_policy_only",
            "policy_id": local_cache_privacy_policy.get("policy_id"),
            "privacy_default": local_cache_privacy_policy.get("privacy_default"),
            "no_cache_runtime_implemented": local_cache_privacy_policy.get(
                "no_cache_runtime_implemented"
            ),
            "no_private_ingestion_implemented": local_cache_privacy_policy.get(
                "no_private_ingestion_implemented"
            ),
            "no_telemetry_implemented": local_cache_privacy_policy.get(
                "no_telemetry_implemented"
            ),
            "no_accounts_implemented": local_cache_privacy_policy.get(
                "no_accounts_implemented"
            ),
            "no_cloud_sync_implemented": local_cache_privacy_policy.get(
                "no_cloud_sync_implemented"
            ),
            "prohibited_behaviors": local_cache_privacy_policy.get(
                "prohibited_behaviors", []
            ),
            "telemetry_policy": local_cache_privacy_policy.get("telemetry_policy", {}),
            "relay_policy": local_cache_privacy_policy.get("relay_policy", {}),
            "snapshot_policy": local_cache_privacy_policy.get("snapshot_policy", {}),
        },
        "surface_capabilities": capabilities,
        "base_path_targets": base_paths,
        "contains_live_backend": False,
        "contains_live_probes": False,
        "contains_external_observations": False,
        "no_deployment_claim": True,
        "limitations": [
            "Static data summaries only; not a live API.",
            "No live backend or live source probes are represented.",
            "Manual external baselines remain pending unless human observations are recorded later.",
            "Public JSON is stable_draft for pre-alpha clients, not a production API promise.",
            "Custom-domain and alternate-host readiness is policy only; no DNS, CNAME, or alternate host is configured.",
            "Live Backend Handoff Contract v0 is contract-only; /api/v1 is reserved but not live.",
            "Live Probe Gateway Contract v0 is contract-only; live probes, downloads, arbitrary URL fetching, and network calls remain disabled.",
            "Google remains manual-baseline only and is not a live probe source.",
            "Relay Surface Design v0 is contract-only; no relay runtime, protocol server, network listener, private data exposure, write/admin route exposure, or live-probe passthrough is implemented.",
            "Compatibility Surface Strategy v0 is contract and inventory only; snapshots, relay, native clients, live API behavior, and new runtime product behavior remain future/deferred.",
            "Signed Snapshot Format v0 is a contract and seed example only; real signing keys, production signatures, executable downloads, public /snapshots/ route, relay behavior, native-client runtime, live backend behavior, and live probes remain absent.",
            "Native Action / Download / Install Policy v0 is policy-only; downloads, mirrors, install handoff, package-manager handoff, execute, restore, uninstall, rollback, malware scanning, rights clearance, native clients, relay runtime, and executable trust claims remain absent.",
            "Native Local Cache / Privacy Policy v0 is policy-only; local cache runtime, private file ingestion, local archive scanning, telemetry, accounts, cloud sync, uploads, native clients, relay runtime, and private-data relay behavior remain absent.",
        ],
        "source_inputs": [
            "control/inventory/publication/publication_contract.json",
            "control/inventory/publication/action_policy.json",
            "control/inventory/publication/local_cache_privacy_policy.json",
            "control/inventory/publication/page_registry.json",
            "control/inventory/publication/deployment_targets.json",
            "control/inventory/publication/domain_plan.json",
            "control/inventory/publication/live_backend_handoff.json",
            "control/inventory/publication/live_backend_routes.json",
            "control/inventory/publication/live_probe_gateway.json",
            "control/inventory/publication/public_data_contract.json",
            "control/inventory/publication/relay_surface.json",
            "control/inventory/publication/snapshot_contract.json",
            "control/inventory/publication/static_hosting_targets.json",
            "control/inventory/publication/surface_capabilities.json",
            "control/inventory/publication/surface_route_matrix.json",
        ],
    }


def _build_page_registry_summary(page_registry: Mapping[str, Any]) -> dict[str, Any]:
    pages: list[dict[str, Any]] = []
    for route in page_registry.get("routes", []):
        if not isinstance(route, Mapping):
            continue
        pages.append(
            {
                "path": route.get("path"),
                "title": route.get("title"),
                "status": route.get("status"),
                "stability": route.get("stability"),
                "source_file": route.get("source_file"),
                "client_profiles": list(route.get("client_profiles", [])),
                "requires_javascript": route.get("requires_javascript"),
                "works_under_project_base_path": route.get("works_under_project_base_path"),
                "safe_for_static_hosting": route.get("safe_for_static_hosting"),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "registry_id": page_registry.get("registry_id"),
        "artifact_root": page_registry.get("artifact_root"),
        "pages": pages,
        "route_count": len(pages),
        "implemented_route_count": sum(1 for page in pages if page.get("status") == "implemented"),
        "reserved_route_count": sum(1 for page in pages if page.get("status") != "implemented"),
        "contains_live_backend": False,
        "contains_live_probes": False,
        "source_inputs": [
            "control/inventory/publication/page_registry.json",
        ],
        "limitations": [
            "Future reserved routes are included so clients can avoid assuming implementation.",
            "This is a static route summary, not a live router or API discovery document.",
        ],
    }


def _build_source_summary(source_records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    sources = [_summarize_source_record(record) for record in source_records]
    status_counts = Counter(str(source["status"]) for source in sources)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "source_count": len(sources),
        "status_counts": dict(sorted(status_counts.items())),
        "sources": sources,
        "contains_live_data": False,
        "contains_live_probes": False,
        "contains_external_observations": False,
        "source_inputs": [
            "control/inventory/sources/*.source.json",
        ],
        "limitations": [
            "Source records are governed inventory summaries, not live source health checks.",
            "Placeholder sources are planning records and do not imply implemented connectors.",
            "Private local filesystem paths are not exposed in this public summary.",
        ],
    }


def _summarize_source_record(record: Mapping[str, Any]) -> dict[str, Any]:
    capabilities = _mapping(record.get("capabilities"))
    coverage = _mapping(record.get("coverage"))
    live_access = _mapping(record.get("live_access"))
    status = str(record.get("status", "unknown"))
    supported_capabilities = sorted(
        key for key, value in capabilities.items() if isinstance(value, bool) and value
    )
    fixture_backed = bool(capabilities.get("fixture_backed"))
    recorded_fixture_backed = bool(capabilities.get("recorded_fixture_backed"))
    live_supported = bool(capabilities.get("live_supported") or capabilities.get("supports_live_probe"))
    live_deferred = bool(capabilities.get("live_deferred") or live_access.get("mode") == "deferred")
    return {
        "source_id": record.get("source_id"),
        "label": record.get("name", record.get("source_id")),
        "family": record.get("source_family"),
        "status": status,
        "posture": _source_posture(status, fixture_backed, recorded_fixture_backed, live_deferred),
        "coverage_depth": coverage.get("coverage_depth"),
        "capabilities": {
            "supported": supported_capabilities,
            "supports_search": bool(capabilities.get("supports_search")),
            "supports_item_metadata": bool(capabilities.get("supports_item_metadata")),
            "supports_file_listing": bool(capabilities.get("supports_file_listing")),
            "supports_member_listing": bool(capabilities.get("supports_member_listing")),
            "supports_content_text": bool(capabilities.get("supports_content_text")),
            "supports_hashes": bool(capabilities.get("supports_hashes")),
            "supports_action_paths": bool(capabilities.get("supports_action_paths")),
            "supports_live_probe": bool(capabilities.get("supports_live_probe")),
        },
        "live_supported": live_supported,
        "live_deferred": live_deferred,
        "fixture_backed": fixture_backed,
        "recorded_fixture_backed": recorded_fixture_backed,
        "placeholder": status == "placeholder",
        "future_marker": status in {"placeholder", "local_private_future", "future"},
        "limitations": _string_list(coverage.get("current_limitations")),
        "next_step": coverage.get("next_coverage_step"),
    }


def _source_posture(
    status: str, fixture_backed: bool, recorded_fixture_backed: bool, live_deferred: bool
) -> str:
    if status == "placeholder":
        return "placeholder_not_implemented"
    if status == "local_private_future":
        return "future_local_private_not_ingested"
    if recorded_fixture_backed:
        return "recorded_fixture_backed_no_live_probe"
    if fixture_backed:
        return "fixture_backed_no_live_probe"
    if live_deferred:
        return "live_access_deferred"
    return status


def _build_eval_summary() -> dict[str, Any]:
    archive = _run_json_script("scripts/run_archive_resolution_evals.py")
    search = _run_json_script("scripts/run_search_usefulness_audit.py")
    baselines = _run_json_script("scripts/report_external_baseline_status.py")

    batch_0 = _mapping(_mapping(baselines.get("batches")).get("batch_0"))
    global_counts = _mapping(baselines.get("global_slot_counts"))
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "archive_resolution": {
            "task_count": archive.get("total_task_count"),
            "status_counts": archive.get("status_counts", {}),
            "source_command": "python scripts/run_archive_resolution_evals.py --json",
            "fixture_backed": True,
            "notes": [
                "Internal hard eval satisfaction is fixture-backed local regression evidence.",
                "This summary does not claim production relevance or global recall.",
            ],
        },
        "search_usefulness": {
            "query_count": search.get("total_query_count"),
            "status_counts": search.get("eureka_status_counts", {}),
            "failure_mode_counts": search.get("failure_mode_counts", {}),
            "source_gap_count": _mapping(search.get("eureka_status_counts")).get("source_gap"),
            "capability_gap_count": _mapping(search.get("eureka_status_counts")).get("capability_gap"),
            "external_baseline_pending_counts": search.get("external_baseline_pending_counts", {}),
            "source_command": "python scripts/run_search_usefulness_audit.py --json",
        },
        "manual_external_baselines": {
            "global_pending_count": global_counts.get("pending_manual_observation", 0),
            "global_observed_count": global_counts.get("observed", 0),
            "batch_0_pending_count": batch_0.get("pending_observation_count", 0),
            "batch_0_observed_count": batch_0.get("observed_observation_count", 0),
            "batch_0_expected_observation_count": batch_0.get("expected_observation_count", 0),
            "source_command": "python scripts/report_external_baseline_status.py --json",
        },
        "contains_live_data": False,
        "contains_live_probes": False,
        "contains_external_observations": False,
        "source_inputs": [
            "scripts/run_archive_resolution_evals.py --json",
            "scripts/run_search_usefulness_audit.py --json",
            "scripts/report_external_baseline_status.py --json",
        ],
        "limitations": [
            "No external searches are run by this generator.",
            "Manual baseline slots remain pending unless human observations are committed.",
            "Eval counts summarize local deterministic scripts and omit volatile run timestamps.",
        ],
    }


def _build_route_summary(route_inventory: Mapping[str, Any]) -> dict[str, Any]:
    routes = [
        route for route in route_inventory.get("routes", []) if isinstance(route, Mapping)
    ]
    counts = Counter(str(route.get("classification", "unknown")) for route in routes)
    review_required = [
        _route_projection(route)
        for route in routes
        if route.get("classification") == "review_required"
    ]
    blocked = [
        _route_projection(route)
        for route in routes
        if route.get("classification") == "blocked_public_alpha"
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "route_counts": {
            "total": len(routes),
            "safe_public_alpha": counts.get("safe_public_alpha", 0),
            "blocked_public_alpha": counts.get("blocked_public_alpha", 0),
            "local_dev_only": counts.get("local_dev_only", 0),
            "review_required": counts.get("review_required", 0),
            "deferred": counts.get("deferred", 0),
        },
        "classification_counts": dict(sorted(counts.items())),
        "review_required_routes": review_required,
        "blocked_routes": blocked,
        "public_alpha_not_production": True,
        "contains_live_backend": False,
        "contains_live_probes": False,
        "source_inputs": [
            "control/inventory/public_alpha_routes.json",
        ],
        "limitations": [
            "Route inventory describes public-alpha route posture for the backend wrapper, not GitHub Pages routing.",
            "Safe public-alpha routes are constrained demo posture and not production readiness.",
            "Local filesystem route variants remain blocked for public alpha.",
        ],
    }


def _route_projection(route: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "method": route.get("method"),
        "route_pattern": route.get("route_pattern"),
        "classification": route.get("classification"),
        "surface_type": route.get("surface_type"),
        "reason": route.get("reason"),
        "local_path_parameters": list(route.get("local_path_parameters", [])),
    }


def _build_build_manifest(
    public_data_contract: Mapping[str, Any],
    action_policy: Mapping[str, Any],
    local_cache_privacy_policy: Mapping[str, Any],
) -> dict[str, Any]:
    data_files = [
        entry.get("path")
        for entry in public_data_contract.get("entries", [])
        if isinstance(entry, Mapping) and str(entry.get("path", "")).startswith("/data/")
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "repo": REPO_ID,
        "branch": "main",
        "commit": "UNKNOWN_UNTIL_CI",
        "source": SLICE_ID,
        "built_at": "UNKNOWN_UNTIL_CI",
        "contains_live_backend": False,
        "contains_live_probes": False,
        "contains_external_observations": False,
        "deployment_performed": False,
        "downloads_enabled": False,
        "install_automation_enabled": False,
        "malware_scanning_claimed": False,
        "rights_clearance_claimed": False,
        "local_cache_runtime_implemented": False,
        "private_ingestion_implemented": False,
        "telemetry_implemented": False,
        "accounts_implemented": False,
        "cloud_sync_implemented": False,
        "artifact_root": "public_site",
        "data_files": sorted(data_files),
        "action_policy": {
            "status": "implemented_policy_only",
            "action_policy_id": action_policy.get("action_policy_id"),
            "future_gated_actions": action_policy.get("future_gated_actions", []),
            "prohibited_until_policy": action_policy.get("prohibited_until_policy", []),
        },
        "local_cache_privacy_policy": {
            "status": "implemented_policy_only",
            "policy_id": local_cache_privacy_policy.get("policy_id"),
            "privacy_default": local_cache_privacy_policy.get("privacy_default"),
            "prohibited_behaviors": local_cache_privacy_policy.get(
                "prohibited_behaviors", []
            ),
        },
        "validations_expected": [
            "python scripts/generate_public_data_summaries.py --check",
            "python scripts/validate_public_static_site.py",
            "python scripts/validate_publication_inventory.py",
            "python scripts/check_github_pages_static_artifact.py",
            "python scripts/validate_static_host_readiness.py",
            "python scripts/validate_live_backend_handoff.py",
            "python scripts/validate_live_probe_gateway.py",
            "python scripts/validate_relay_surface_design.py",
            "python scripts/validate_action_policy.py",
            "python scripts/validate_local_cache_privacy_policy.py",
            "python scripts/generate_static_snapshot.py --check",
            "python scripts/validate_static_snapshot.py",
        ],
        "source_inputs": [
            "control/inventory/publication/public_data_contract.json",
            "control/inventory/publication/action_policy.json",
            "control/inventory/publication/local_cache_privacy_policy.json",
            "control/inventory/publication/publication_contract.json",
            "control/inventory/publication/page_registry.json",
            "control/inventory/publication/domain_plan.json",
            "control/inventory/publication/live_backend_handoff.json",
            "control/inventory/publication/live_backend_routes.json",
            "control/inventory/publication/live_probe_gateway.json",
            "control/inventory/publication/relay_surface.json",
            "control/inventory/publication/snapshot_contract.json",
            "control/inventory/publication/static_hosting_targets.json",
            "control/inventory/publication/surface_capabilities.json",
            "control/inventory/publication/surface_route_matrix.json",
            "control/inventory/sources/*.source.json",
            "control/inventory/public_alpha_routes.json",
            "scripts/run_archive_resolution_evals.py --json",
            "scripts/run_search_usefulness_audit.py --json",
            "scripts/report_external_baseline_status.py --json",
        ],
    }


def _run_json_script(relative_script: str) -> Mapping[str, Any]:
    script = REPO_ROOT / relative_script
    completed = subprocess.run(
        [sys.executable, str(script), "--json"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    if not isinstance(payload, Mapping):
        raise PublicDataGenerationError(f"{relative_script} --json did not return an object.")
    return payload


def _load_source_records() -> list[Mapping[str, Any]]:
    records: list[Mapping[str, Any]] = []
    for path in sorted(SOURCE_INVENTORY_DIR.glob("*.source.json")):
        payload = _load_json(path)
        if not isinstance(payload, Mapping):
            raise PublicDataGenerationError(f"{_display_path(path)} must contain a JSON object.")
        records.append(payload)
    return sorted(records, key=lambda record: str(record.get("source_id", "")))


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PublicDataGenerationError(f"missing JSON input: {_display_path(path)}") from exc
    except json.JSONDecodeError as exc:
        raise PublicDataGenerationError(f"invalid JSON input {_display_path(path)}: {exc}") from exc


def _validate_static_safety(path: Path, payload: Any, errors: list[str]) -> None:
    text = json.dumps(payload, sort_keys=True)
    for needle in ("contains_live_backend", "contains_live_probes", "deployment_performed"):
        if needle in text and f'"{needle}": true' in text.casefold():
            errors.append(f"{_display_path(path)}: {needle} must not be true.")
    for private_marker in ("D:\\", "C:\\", "/Users/", "/home/"):
        if private_marker in text:
            errors.append(f"{_display_path(path)}: private/local filesystem path marker leaked.")


def _summary_report(
    output_root: Path, payloads: Mapping[str, Mapping[str, Any]], *, updated: bool
) -> dict[str, Any]:
    return {
        "status": "valid",
        "created_by": SLICE_ID,
        "generated_by": GENERATED_BY,
        "output_root": _display_path(output_root),
        "updated": updated,
        "data_files": sorted(payloads),
        "public_data_paths": sorted(PUBLIC_DATA_PATHS),
        "contains_live_backend": False,
        "contains_live_probes": False,
        "contains_external_observations": False,
        "deployment_performed": False,
        "errors": [],
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        return [value]
    return []


def _json_text(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Generated public data summaries",
        f"status: {report['status']}",
    ]
    if report.get("output_root"):
        lines.append(f"output_root: {report['output_root']}")
    if report.get("data_files"):
        lines.append(f"data_files: {len(report['data_files'])}")
    if report.get("updated"):
        lines.append("updated: true")
    if report.get("check_mode"):
        lines.append("check_mode: true")
    if report.get("errors"):
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
