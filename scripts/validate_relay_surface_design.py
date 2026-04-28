from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
RELAY_SURFACE = PUBLICATION_DIR / "relay_surface.json"
SURFACE_CAPABILITIES = PUBLICATION_DIR / "surface_capabilities.json"
SURFACE_ROUTE_MATRIX = PUBLICATION_DIR / "surface_route_matrix.json"

REQUIRED_FIELDS = {
    "schema_version",
    "relay_surface_id",
    "status",
    "stability",
    "no_relay_implemented",
    "no_network_services_implemented",
    "no_protocol_servers_implemented",
    "default_scope",
    "default_mode",
    "public_data_only_by_default",
    "private_data_disabled_by_default",
    "write_actions_disabled_by_default",
    "live_probes_disabled_by_default",
    "admin_routes_disabled_for_old_clients",
    "supported_future_modes",
    "forbidden_v0_behaviors",
    "future_protocol_candidates",
    "data_sources",
    "trust_and_integrity_model",
    "snapshot_dependency",
    "operator_controls_required",
    "security_requirements",
    "privacy_requirements",
    "client_profiles",
    "next_milestones",
    "created_by_slice",
    "notes",
}
REQUIRED_PROTOCOL_CANDIDATES = {
    "local_static_http",
    "local_text_http",
    "local_file_tree_http",
    "read_only_ftp_mirror",
    "webdav_read_only",
    "smb_read_only",
    "afp_read_only",
    "nfs_read_only",
    "gopher_experimental",
    "native_sidecar",
    "snapshot_mount",
}
FUTURE_STATUSES = {"future", "deferred", "planned", "design_only", "future_deferred"}
REQUIRED_DOCS = {
    "docs/architecture/RELAY_SURFACE.md": [
        "design, contract, inventory",
        "No relay runtime is implemented",
        "No network listeners",
        "public_site/data/",
        "public_site/lite/",
        "public_site/text/",
        "public_site/files/",
        "snapshots/examples/static_snapshot_v0/",
    ],
    "docs/reference/RELAY_SURFACE_CONTRACT.md": [
        "design contract only",
        "future/deferred",
        "read-only by default",
        "Live probes are disabled by default",
    ],
    "docs/reference/RELAY_SECURITY_AND_PRIVACY.md": [
        "future-only",
        "No public internet exposure by default",
        "No credentials to old clients",
        "No write or admin endpoints to old clients",
        "Future threat model",
    ],
    "docs/operations/RELAY_OPERATOR_CHECKLIST.md": [
        "future/unsigned",
        "confirm read-only mode",
        "confirm no private data exposure",
        "confirm rollback or disable procedure",
    ],
}
SUSPECT_FILENAMES = {
    "relay_server.py",
    "ftp_server.py",
    "smb_server.py",
    "webdav_server.py",
    "gopher_server.py",
    "local_http_relay.py",
    "protocol_proxy.py",
}
POSITIVE_RELAY_CLAIMS = (
    re.compile(r"\brelay runtime (is )?(available|enabled|running)\b", re.IGNORECASE),
    re.compile(r"\brelay server (is )?(available|enabled|running)\b", re.IGNORECASE),
    re.compile(r"\bproduction relay\b", re.IGNORECASE),
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Eureka Relay Surface Design v0.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_relay_surface_design(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_relay_surface_design(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    publication_dir = repo_root / "control" / "inventory" / "publication"

    relay = _load_json(publication_dir / "relay_surface.json", repo_root, errors)
    capabilities = _load_json(publication_dir / "surface_capabilities.json", repo_root, errors)
    route_matrix = _load_json(publication_dir / "surface_route_matrix.json", repo_root, errors)

    protocol_ids = _validate_relay_inventory(relay, errors)
    _validate_surface_capabilities(capabilities, errors)
    _validate_route_matrix(route_matrix, errors)
    _validate_docs(repo_root, errors)
    _validate_no_server_code(repo_root, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "relay_surface_design_validator_v0",
        "relay_surface": "control/inventory/publication/relay_surface.json",
        "protocol_candidate_count": len(protocol_ids),
        "protocol_candidates": sorted(protocol_ids),
        "no_relay_implemented": _mapping(relay).get("no_relay_implemented"),
        "no_network_services_implemented": _mapping(relay).get("no_network_services_implemented"),
        "no_protocol_servers_implemented": _mapping(relay).get("no_protocol_servers_implemented"),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_relay_inventory(payload: Any, errors: list[str]) -> set[str]:
    protocol_ids: set[str] = set()
    if not isinstance(payload, Mapping):
        errors.append("relay_surface.json: must be a JSON object.")
        return protocol_ids
    missing = sorted(REQUIRED_FIELDS - set(payload))
    if missing:
        errors.append(f"relay_surface.json: missing fields {missing}.")
    expected = {
        "schema_version": "0.1.0",
        "relay_surface_id": "eureka-local-relay-surface",
        "status": "design_only",
        "stability": "experimental",
        "no_relay_implemented": True,
        "no_network_services_implemented": True,
        "no_protocol_servers_implemented": True,
        "public_data_only_by_default": True,
        "private_data_disabled_by_default": True,
        "write_actions_disabled_by_default": True,
        "live_probes_disabled_by_default": True,
        "admin_routes_disabled_for_old_clients": True,
        "created_by_slice": "relay_surface_design_v0",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append(f"relay_surface.json: {key} must be {value!r}.")

    candidates = payload.get("future_protocol_candidates")
    if not isinstance(candidates, list):
        errors.append("relay_surface.json: future_protocol_candidates must be a list.")
        return protocol_ids
    for item in candidates:
        if not isinstance(item, Mapping):
            errors.append("relay_surface.json: each protocol candidate must be an object.")
            continue
        candidate_id = item.get("id")
        if not isinstance(candidate_id, str):
            errors.append("relay_surface.json: protocol candidate id must be a string.")
            continue
        protocol_ids.add(candidate_id)
        if item.get("status") not in FUTURE_STATUSES:
            errors.append(f"relay_surface.json: {candidate_id}.status must remain future/deferred.")
        if item.get("implemented") is not False:
            errors.append(f"relay_surface.json: {candidate_id}.implemented must be false.")
    missing_protocols = sorted(REQUIRED_PROTOCOL_CANDIDATES - protocol_ids)
    if missing_protocols:
        errors.append(f"relay_surface.json: missing protocol candidates {missing_protocols}.")

    forbidden = {str(item).casefold() for item in _list(payload.get("forbidden_v0_behaviors"))}
    for required in (
        "relay runtime",
        "network listener",
        "ftp server",
        "smb server",
        "webdav server",
        "gopher server",
        "private user data exposure",
        "live source probing",
    ):
        if required not in forbidden:
            errors.append(f"relay_surface.json: forbidden_v0_behaviors missing {required!r}.")

    data_source_paths = {str(item.get("path")) for item in _mapping_list(payload.get("data_sources"))}
    for required_path in (
        "public_site/data/",
        "public_site/lite/",
        "public_site/text/",
        "public_site/files/",
        "snapshots/examples/static_snapshot_v0/",
    ):
        if required_path not in data_source_paths:
            errors.append(f"relay_surface.json: data_sources missing {required_path}.")

    trust = payload.get("trust_and_integrity_model")
    if not isinstance(trust, Mapping):
        errors.append("relay_surface.json: trust_and_integrity_model must be an object.")
    else:
        if trust.get("relay_is_not_trust_oracle") is not True:
            errors.append("relay_surface.json: relay_is_not_trust_oracle must be true.")
        if trust.get("requires_future_signature_policy_for_authenticity") is not True:
            errors.append(
                "relay_surface.json: future signature policy must be required for authenticity claims."
            )
    return protocol_ids


def _validate_surface_capabilities(payload: Any, errors: list[str]) -> None:
    relay = _by_id(_mapping(payload).get("capabilities")).get("relay")
    if not relay:
        errors.append("surface_capabilities.json: relay capability is missing.")
        return
    if relay.get("status") not in {"planned", "deferred", "blocked", "design_only"}:
        errors.append("surface_capabilities.json: relay status must remain future/deferred/design-only.")
    if relay.get("enabled_by_default") is not False:
        errors.append("surface_capabilities.json: relay.enabled_by_default must be false.")
    if relay.get("supports_live_data") is not False:
        errors.append("surface_capabilities.json: relay.supports_live_data must be false.")
    if relay.get("supports_private_user_state") is not False:
        errors.append("surface_capabilities.json: relay.supports_private_user_state must be false.")
    if relay.get("supports_downloads") is not False:
        errors.append("surface_capabilities.json: relay.supports_downloads must be false.")


def _validate_route_matrix(payload: Any, errors: list[str]) -> None:
    relay = _by_id(_mapping(payload).get("surfaces")).get("relay")
    if not relay:
        errors.append("surface_route_matrix.json: relay route entry is missing.")
        return
    if relay.get("implemented_now") is not False:
        errors.append("surface_route_matrix.json: relay.implemented_now must be false.")
    if relay.get("route_roots") != []:
        errors.append("surface_route_matrix.json: relay.route_roots must remain empty.")
    if relay.get("implemented_paths") != []:
        errors.append("surface_route_matrix.json: relay.implemented_paths must remain empty.")
    if relay.get("status") not in {"planned", "deferred", "blocked", "design_only"}:
        errors.append("surface_route_matrix.json: relay.status must remain future/deferred/design-only.")


def _validate_docs(repo_root: Path, errors: list[str]) -> None:
    for relative, phrases in REQUIRED_DOCS.items():
        path = repo_root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            errors.append(f"{relative}: required relay document is missing.")
            continue
        lowered = text.casefold()
        for phrase in phrases:
            if phrase.casefold() not in lowered:
                errors.append(f"{relative}: missing phrase {phrase!r}.")
        for pattern in POSITIVE_RELAY_CLAIMS:
            for match in pattern.finditer(text):
                context = text[max(0, match.start() - 80) : match.end() + 80].casefold()
                if any(token in context for token in ("no ", "not ", "future", "deferred", "design")):
                    continue
                errors.append(f"{relative}: prohibited relay claim {match.group(0)!r}.")


def _validate_no_server_code(repo_root: Path, errors: list[str]) -> None:
    for filename in SUSPECT_FILENAMES:
        for path in repo_root.rglob(filename):
            if ".git" in path.parts:
                continue
            errors.append(f"{_rel(path, repo_root)}: relay/protocol server filename is not allowed in v0.")


def _load_json(path: Path, repo_root: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path, repo_root)}: file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path, repo_root)}: invalid JSON: {exc}.")
    return {}


def _by_id(value: Any) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    if not isinstance(value, list):
        return result
    for item in value:
        if isinstance(item, Mapping) and isinstance(item.get("id"), str):
            result[item["id"]] = item
    return result


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay surface design validation",
        f"status: {report['status']}",
        f"protocol_candidates: {report['protocol_candidate_count']}",
        f"no_relay_implemented: {report['no_relay_implemented']}",
        f"no_network_services_implemented: {report['no_network_services_implemented']}",
        f"no_protocol_servers_implemented: {report['no_protocol_servers_implemented']}",
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


if __name__ == "__main__":
    raise SystemExit(main())
