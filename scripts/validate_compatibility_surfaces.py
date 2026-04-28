from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
PUBLIC_SITE = REPO_ROOT / "public_site"

CAPABILITIES_PATH = PUBLICATION_DIR / "surface_capabilities.json"
ROUTE_MATRIX_PATH = PUBLICATION_DIR / "surface_route_matrix.json"
CLIENT_PROFILES_PATH = PUBLICATION_DIR / "client_profiles.json"

REQUIRED_SURFACE_IDS = {
    "app",
    "web",
    "lite",
    "text",
    "files",
    "data",
    "api",
    "snapshots",
    "relay",
    "cli",
    "native_client",
    "public_static_site",
    "public_alpha_wrapper",
    "live_backend",
    "live_probe_gateway",
}
REQUIRED_ROUTE_SURFACES = {
    "public_static_site",
    "lite",
    "text",
    "files",
    "data",
    "demo",
    "app",
    "web",
    "api",
    "snapshots",
    "relay",
    "native_client",
    "cli",
}
REQUIRED_FIELDS = {
    "id",
    "label",
    "status",
    "stability",
    "client_profiles",
    "implemented_paths",
    "reserved_paths",
    "requires_backend",
    "requires_javascript",
    "safe_for_static_hosting",
    "supports_static_data",
    "supports_live_data",
    "supports_downloads",
    "supports_private_user_state",
    "supports_external_sources",
    "enabled_by_default",
    "current_limitations",
    "next_step",
}
IMPLEMENTED_STATUSES = {"implemented", "static_demo", "recorded_fixture"}
FUTURE_STATUSES = {"planned", "deferred", "blocked", "placeholder", "unsafe_for_public_alpha"}
STATIC_SEED_SURFACES = {"lite", "text", "files", "data", "demo", "public_static_site"}
FUTURE_DISABLED_SURFACES = {"app", "api", "snapshots", "relay", "native_client", "live_backend", "live_probe_gateway"}
PROFILE_REQUIRED = {
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
PROHIBITED_POSITIVE_PATTERNS = (
    re.compile(r"\bsnapshots? (are|is) (implemented|available|ready)\b", re.IGNORECASE),
    re.compile(r"\brelay (is )?(implemented|available|ready|enabled)\b", re.IGNORECASE),
    re.compile(r"\bnative (clients?|apps?) (are|is) (implemented|available|ready)\b", re.IGNORECASE),
    re.compile(r"\blive backend (is )?(available|enabled|running|deployed|exists)\b", re.IGNORECASE),
    re.compile(r"\blive probes (are )?(available|enabled|implemented|running)\b", re.IGNORECASE),
    re.compile(r"\bproduction[- ]ready\b", re.IGNORECASE),
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []
        self.script_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "script":
            self.script_count += 1
        for key, value in attrs:
            if key.lower() in {"href", "src", "action"} and value:
                self.references.append(value)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Eureka compatibility-surface strategy inventories and docs."
    )
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_compatibility_surfaces(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_compatibility_surfaces(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    publication_dir = repo_root / "control" / "inventory" / "publication"
    public_site = repo_root / "public_site"
    errors: list[str] = []
    warnings: list[str] = []

    capabilities = _load_json(publication_dir / "surface_capabilities.json", repo_root, errors)
    route_matrix = _load_json(publication_dir / "surface_route_matrix.json", repo_root, errors)
    client_profiles = _load_json(publication_dir / "client_profiles.json", repo_root, errors)

    profile_ids = _validate_client_profiles(client_profiles, errors)
    capability_summary = _validate_capabilities(capabilities, profile_ids, repo_root, errors)
    route_summary = _validate_route_matrix(route_matrix, profile_ids, repo_root, errors)
    _validate_static_surfaces(public_site, repo_root, errors)
    _validate_docs(repo_root, errors)
    _validate_static_pages_claims(public_site, repo_root, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "compatibility_surface_strategy_validator_v0",
        "repo_root": str(repo_root),
        "surface_capabilities": _rel(publication_dir / "surface_capabilities.json", repo_root),
        "surface_route_matrix": _rel(publication_dir / "surface_route_matrix.json", repo_root),
        "surface_count": capability_summary["surface_count"],
        "route_surface_count": route_summary["surface_count"],
        "implemented_static_surfaces": route_summary["implemented_static_surfaces"],
        "future_disabled_surfaces": capability_summary["future_disabled_surfaces"],
        "errors": errors,
        "warnings": warnings,
    }


def _validate_client_profiles(payload: Any, errors: list[str]) -> set[str]:
    if not isinstance(payload, Mapping):
        errors.append("client_profiles.json: must be a JSON object.")
        return set()
    profiles = payload.get("profiles")
    if not isinstance(profiles, list):
        errors.append("client_profiles.json: profiles must be a list.")
        return set()
    profile_ids = {
        item.get("id")
        for item in profiles
        if isinstance(item, Mapping) and isinstance(item.get("id"), str)
    }
    missing = sorted(PROFILE_REQUIRED - profile_ids)
    if missing:
        errors.append(f"client_profiles.json: missing profiles {missing}.")
    return set(profile_ids)


def _validate_capabilities(
    payload: Any,
    profile_ids: set[str],
    repo_root: Path,
    errors: list[str],
) -> dict[str, Any]:
    future_disabled: list[str] = []
    if not isinstance(payload, Mapping):
        errors.append("surface_capabilities.json: must be a JSON object.")
        return {"surface_count": 0, "future_disabled_surfaces": future_disabled}
    if payload.get("schema_version") != "0.1.0":
        errors.append("surface_capabilities.json: schema_version must be 0.1.0.")
    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, list):
        errors.append("surface_capabilities.json: capabilities must be a list.")
        return {"surface_count": 0, "future_disabled_surfaces": future_disabled}

    by_id = {
        item.get("id"): item
        for item in capabilities
        if isinstance(item, Mapping) and isinstance(item.get("id"), str)
    }
    missing = sorted(REQUIRED_SURFACE_IDS - set(by_id))
    if missing:
        errors.append(f"surface_capabilities.json: missing surface ids {missing}.")

    for capability_id, item in sorted(by_id.items()):
        if not isinstance(item, Mapping):
            continue
        missing_fields = sorted(REQUIRED_FIELDS - set(item))
        if missing_fields:
            errors.append(f"surface_capabilities.json: {capability_id} missing fields {missing_fields}.")
        for profile in _string_list(item.get("client_profiles")):
            if profile not in profile_ids:
                errors.append(f"surface_capabilities.json: {capability_id} references unknown client profile {profile}.")
        for relative in _string_list(item.get("implemented_paths")):
            path = repo_root / relative
            if not path.exists():
                errors.append(f"surface_capabilities.json: {capability_id} implemented path missing: {relative}.")
        if capability_id in STATIC_SEED_SURFACES:
            if item.get("requires_backend") is not False:
                errors.append(f"surface_capabilities.json: {capability_id}.requires_backend must be false.")
            if item.get("requires_javascript") is not False:
                errors.append(f"surface_capabilities.json: {capability_id}.requires_javascript must be false.")
            if item.get("safe_for_static_hosting") is not True:
                errors.append(f"surface_capabilities.json: {capability_id}.safe_for_static_hosting must be true.")
            if item.get("supports_live_data") is not False:
                errors.append(f"surface_capabilities.json: {capability_id}.supports_live_data must be false.")
            if item.get("supports_private_user_state") is not False:
                errors.append(f"surface_capabilities.json: {capability_id}.supports_private_user_state must be false.")
        if capability_id in FUTURE_DISABLED_SURFACES:
            if item.get("status") not in FUTURE_STATUSES:
                errors.append(f"surface_capabilities.json: {capability_id}.status must remain future/deferred/blocked.")
            if item.get("enabled_by_default") is not False:
                errors.append(f"surface_capabilities.json: {capability_id}.enabled_by_default must be false.")
            if item.get("supports_live_data") is not False:
                errors.append(f"surface_capabilities.json: {capability_id}.supports_live_data must be false until implemented.")
            future_disabled.append(str(capability_id))
        if capability_id in {"live_backend", "live_probe_gateway", "api"}:
            if item.get("requires_backend") is not True:
                errors.append(f"surface_capabilities.json: {capability_id}.requires_backend must be true.")
        if capability_id in {"snapshots", "relay", "native_client"} and item.get("status") in IMPLEMENTED_STATUSES:
            errors.append(f"surface_capabilities.json: {capability_id} must not be implemented in v0.")
    return {
        "surface_count": len(by_id),
        "future_disabled_surfaces": sorted(future_disabled),
    }


def _validate_route_matrix(
    payload: Any,
    profile_ids: set[str],
    repo_root: Path,
    errors: list[str],
) -> dict[str, Any]:
    implemented_static: list[str] = []
    if not isinstance(payload, Mapping):
        errors.append("surface_route_matrix.json: must be a JSON object.")
        return {"surface_count": 0, "implemented_static_surfaces": implemented_static}
    if payload.get("schema_version") != "0.1.0":
        errors.append("surface_route_matrix.json: schema_version must be 0.1.0.")
    surfaces = payload.get("surfaces")
    if not isinstance(surfaces, list):
        errors.append("surface_route_matrix.json: surfaces must be a list.")
        return {"surface_count": 0, "implemented_static_surfaces": implemented_static}
    by_id = {
        item.get("id"): item
        for item in surfaces
        if isinstance(item, Mapping) and isinstance(item.get("id"), str)
    }
    missing = sorted(REQUIRED_ROUTE_SURFACES - set(by_id))
    if missing:
        errors.append(f"surface_route_matrix.json: missing surface route ids {missing}.")
    for surface_id, item in sorted(by_id.items()):
        if not isinstance(item, Mapping):
            continue
        for field in (
            "route_roots",
            "status",
            "stability",
            "implemented_now",
            "implemented_paths",
            "live_backend_required",
            "static_host_safe",
            "client_profiles",
            "notes",
        ):
            if field not in item:
                errors.append(f"surface_route_matrix.json: {surface_id} missing {field}.")
        for profile in _string_list(item.get("client_profiles")):
            if profile not in profile_ids:
                errors.append(f"surface_route_matrix.json: {surface_id} references unknown client profile {profile}.")
        if item.get("implemented_now") is True:
            for relative in _string_list(item.get("implemented_paths")):
                if not (repo_root / relative).exists():
                    errors.append(f"surface_route_matrix.json: {surface_id} implemented path missing: {relative}.")
            if item.get("static_host_safe") is True:
                implemented_static.append(str(surface_id))
        if surface_id in {"app", "api", "snapshots", "relay", "native_client"}:
            if item.get("implemented_now") is not False:
                errors.append(f"surface_route_matrix.json: {surface_id}.implemented_now must be false.")
            if item.get("status") not in FUTURE_STATUSES:
                errors.append(f"surface_route_matrix.json: {surface_id}.status must be future/deferred.")
    return {
        "surface_count": len(by_id),
        "implemented_static_surfaces": sorted(implemented_static),
    }


def _validate_static_surfaces(public_site: Path, repo_root: Path, errors: list[str]) -> None:
    for relative in (
        "lite/index.html",
        "text/index.txt",
        "files/index.html",
        "files/SHA256SUMS",
        "data/site_manifest.json",
        "demo/index.html",
    ):
        if not (public_site / relative).exists():
            errors.append(f"public_site/{relative}: required compatibility surface artifact is missing.")
    for html_path in sorted((public_site / "lite").glob("*.html")):
        parser = LinkParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        if parser.script_count:
            errors.append(f"{_rel(html_path, repo_root)}: lite pages must not contain script tags.")
        for link in parser.references:
            if link.startswith("/"):
                errors.append(f"{_rel(html_path, repo_root)}: root-relative link is not base-path safe: {link}")


def _validate_docs(repo_root: Path, errors: list[str]) -> None:
    required_docs = {
        "docs/architecture/COMPATIBILITY_SURFACES.md": [
            "same resolver truth, multiple projections",
            "do not make one modern web app serve every old client",
            "does not implement new runtime product behavior",
        ],
        "docs/reference/OLD_CLIENT_DEGRADATION_POLICY.md": [
            "multiple read-only projections",
            "must not require JavaScript",
            "Trust must come from future signed manifests",
        ],
        "docs/reference/NATIVE_CLIENT_READINESS_POLICY.md": [
            "Native app projects remain deferred",
            "no dependency on private engine internals",
        ],
    }
    for relative, phrases in required_docs.items():
        path = repo_root / relative
        if not path.exists():
            errors.append(f"{relative}: required compatibility-surface doc is missing.")
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.casefold()
        for phrase in phrases:
            if phrase.casefold() not in lowered:
                errors.append(f"{relative}: missing phrase {phrase!r}.")


def _validate_static_pages_claims(public_site: Path, repo_root: Path, errors: list[str]) -> None:
    for path in sorted(public_site.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".html", ".txt", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in PROHIBITED_POSITIVE_PATTERNS:
            for match in pattern.finditer(text):
                before = text[max(0, match.start() - 120) : match.start()].casefold()
                context = text[max(0, match.start() - 48) : match.end() + 48].casefold()
                if any(
                    token in before[-100:]
                    for token in ("no ", "not ", "does not ", "future", "deferred", "reserved", "prohibited")
                ):
                    continue
                if any(
                    token in context
                    for token in ("not implemented", "not available", "not live", "remain future", "prohibited")
                ):
                    continue
                errors.append(f"{_rel(path, repo_root)}: prohibited compatibility-surface claim {match.group(0)!r}.")


def _load_json(path: Path, repo_root: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path, repo_root)}: file is missing.")
    except json.JSONDecodeError as error:
        errors.append(f"{_rel(path, repo_root)}: invalid JSON: {error}.")
    return {}


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Compatibility surface validation",
        f"status: {report['status']}",
        f"surface_count: {report['surface_count']}",
        f"route_surface_count: {report['route_surface_count']}",
        f"implemented_static_surfaces: {len(report['implemented_static_surfaces'])}",
        f"future_disabled_surfaces: {len(report['future_disabled_surfaces'])}",
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
