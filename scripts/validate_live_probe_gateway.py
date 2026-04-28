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
PUBLIC_SITE_DIR = REPO_ROOT / "public_site"

REQUIRED_CANDIDATE_SOURCES = {
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
REQUIRED_FORBIDDEN_MODES = {
    "downloads",
    "scraping",
    "bulk crawling",
    "arbitrary URL fetching",
    "account/private data",
}
REQUIRED_GLOBAL_LIMITS = {
    "max_query_length": 160,
    "max_total_results": 20,
    "max_results_per_source": 10,
    "global_timeout_ms": 10000,
    "source_timeout_ms": 5000,
    "max_sources_per_request": 2,
    "allow_arbitrary_url_fetch": False,
    "allow_downloads": False,
    "allow_write_actions": False,
    "allow_auth_user_credentials": False,
}
REQUIRED_POLICY_KEYS = {
    "cache_policy",
    "evidence_policy",
    "user_agent_policy",
    "retry_policy",
    "circuit_breaker_policy",
    "download_policy",
    "privacy_policy",
    "logging_policy",
}
LIVE_PROBE_DISABLED_CAPABILITIES = {
    "live_probe_gateway",
    "internet_archive_live_probe",
}
POSITIVE_LIVE_PROBE_PATTERNS = (
    re.compile(r"\blive probes (are )?(available|enabled|implemented|running)\b", re.IGNORECASE),
    re.compile(r"\blive probe gateway (is )?(available|enabled|implemented|running)\b", re.IGNORECASE),
    re.compile(r"\binternet archive live probe (is )?(available|enabled|implemented|running)\b", re.IGNORECASE),
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key.lower() in {"href", "src", "action"} and value:
                self.references.append((key.lower(), value))


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Eureka's disabled live probe gateway contract without network access."
    )
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_live_probe_gateway(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_live_probe_gateway(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    publication_dir = repo_root / "control" / "inventory" / "publication"
    public_site = repo_root / "public_site"
    errors: list[str] = []
    warnings: list[str] = []

    gateway = _load_json(publication_dir / "live_probe_gateway.json", errors, repo_root)
    capabilities = _load_json(publication_dir / "surface_capabilities.json", errors, repo_root)
    handoff = _load_json(publication_dir / "live_backend_handoff.json", errors, repo_root)
    routes = _load_json(publication_dir / "live_backend_routes.json", errors, repo_root)

    source_report = _validate_gateway_inventory(gateway, errors)
    _validate_surface_capabilities(capabilities, errors)
    _validate_live_backend_handoff(handoff, errors)
    _validate_live_backend_routes(routes, errors)
    wrapper_report = _validate_public_alpha_wrapper(repo_root, errors)
    static_hits = _validate_static_pages(public_site, repo_root, errors)
    _validate_docs(repo_root, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "live_probe_gateway_validator_v0",
        "repo_root": str(repo_root),
        "gateway_inventory": _rel(publication_dir / "live_probe_gateway.json", repo_root),
        "candidate_sources": source_report["candidate_sources"],
        "disabled_sources": source_report["disabled_sources"],
        "manual_only_sources": source_report["manual_only_sources"],
        "wrapper_live_probes_enabled": wrapper_report.get("live_probes_enabled"),
        "wrapper_live_internet_archive_enabled": wrapper_report.get("live_internet_archive_enabled"),
        "positive_live_probe_claims": static_hits,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_gateway_inventory(payload: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        errors.append("live_probe_gateway.json: must be a JSON object.")
        return {"candidate_sources": [], "disabled_sources": [], "manual_only_sources": []}
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
        for key, expected_value in REQUIRED_GLOBAL_LIMITS.items():
            if global_limits.get(key) != expected_value:
                errors.append(f"live_probe_gateway.json: global_limits.{key} must be {expected_value!r}.")

    for key in REQUIRED_POLICY_KEYS:
        value = payload.get(key)
        if not isinstance(value, Mapping):
            errors.append(f"live_probe_gateway.json: {key} must be an object.")
    _validate_policy_flags(payload, errors)

    source_limits = payload.get("source_limits")
    if not isinstance(source_limits, Mapping):
        errors.append("live_probe_gateway.json: source_limits must be an object.")
    disabled_sources = set(_string_list(payload.get("disabled_sources")))
    missing_disabled = sorted(REQUIRED_CANDIDATE_SOURCES - disabled_sources)
    if missing_disabled:
        errors.append(f"live_probe_gateway.json: disabled_sources missing {missing_disabled}.")

    candidates = payload.get("future_candidate_sources")
    if not isinstance(candidates, list):
        errors.append("live_probe_gateway.json: future_candidate_sources must be a list.")
        candidates = []
    by_id = {
        candidate.get("id"): candidate
        for candidate in candidates
        if isinstance(candidate, Mapping) and isinstance(candidate.get("id"), str)
    }
    missing = sorted(REQUIRED_CANDIDATE_SOURCES - set(by_id))
    if missing:
        errors.append(f"live_probe_gateway.json: missing candidate sources {missing}.")
    if "google" in " ".join(str(key).casefold() for key in by_id):
        errors.append("live_probe_gateway.json: Google must not be a live probe candidate.")
    for source_id, candidate in sorted(by_id.items()):
        _validate_candidate_source(str(source_id), candidate, source_limits, errors)

    manual_only_sources = payload.get("manual_only_sources")
    manual_ids: list[str] = []
    if isinstance(manual_only_sources, list):
        for source in manual_only_sources:
            if not isinstance(source, Mapping):
                continue
            source_id = source.get("id")
            if isinstance(source_id, str):
                manual_ids.append(source_id)
            if source_id == "google_web_search":
                if source.get("status") != "manual_external_baseline":
                    errors.append("live_probe_gateway.json: google_web_search must be manual_external_baseline.")
                if source.get("live_probe_candidate") is not False:
                    errors.append("live_probe_gateway.json: google_web_search must not be a live probe candidate.")
    else:
        errors.append("live_probe_gateway.json: manual_only_sources must be a list.")
    if "google_web_search" not in manual_ids:
        errors.append("live_probe_gateway.json: google_web_search manual-only record is required.")

    prohibited = set(_string_list(payload.get("prohibited_behaviors")))
    for required in ("network calls", "URL fetching", "downloads", "scraping", "bulk crawling"):
        if required not in prohibited:
            errors.append(f"live_probe_gateway.json: prohibited_behaviors must include {required!r}.")

    return {
        "candidate_sources": sorted(by_id),
        "disabled_sources": sorted(disabled_sources),
        "manual_only_sources": sorted(manual_ids),
    }


def _validate_policy_flags(payload: Mapping[str, Any], errors: list[str]) -> None:
    cache_policy = payload.get("cache_policy")
    if isinstance(cache_policy, Mapping) and cache_policy.get("cache_required") is not True:
        errors.append("live_probe_gateway.json: cache_policy.cache_required must be true.")
    evidence_policy = payload.get("evidence_policy")
    if isinstance(evidence_policy, Mapping) and evidence_policy.get("evidence_required") is not True:
        errors.append("live_probe_gateway.json: evidence_policy.evidence_required must be true.")
    download_policy = payload.get("download_policy")
    if isinstance(download_policy, Mapping):
        if download_policy.get("allow_downloads") is not False:
            errors.append("live_probe_gateway.json: download_policy.allow_downloads must be false.")
        if download_policy.get("allow_executable_downloads") is not False:
            errors.append("live_probe_gateway.json: download_policy.allow_executable_downloads must be false.")
    privacy_policy = payload.get("privacy_policy")
    if isinstance(privacy_policy, Mapping):
        if privacy_policy.get("allow_auth_user_credentials") is not False:
            errors.append("live_probe_gateway.json: privacy_policy.allow_auth_user_credentials must be false.")
        if privacy_policy.get("allow_private_account_data") is not False:
            errors.append("live_probe_gateway.json: privacy_policy.allow_private_account_data must be false.")


def _validate_candidate_source(
    source_id: str,
    candidate: Mapping[str, Any],
    source_limits: Any,
    errors: list[str],
) -> None:
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
    if not isinstance(candidate.get("default_result_cap"), int):
        errors.append(f"live_probe_gateway.json: {source_id}.default_result_cap must be an integer.")
    if not isinstance(candidate.get("default_timeout_ms"), int):
        errors.append(f"live_probe_gateway.json: {source_id}.default_timeout_ms must be an integer.")
    forbidden = set(_string_list(candidate.get("forbidden_modes")))
    missing_forbidden = sorted(REQUIRED_FORBIDDEN_MODES - forbidden)
    if missing_forbidden:
        errors.append(f"live_probe_gateway.json: {source_id}.forbidden_modes missing {missing_forbidden}.")
    allowed = _string_list(candidate.get("allowed_modes"))
    if not allowed:
        errors.append(f"live_probe_gateway.json: {source_id}.allowed_modes must not be empty.")
    if isinstance(source_limits, Mapping):
        limits = source_limits.get(source_id)
        if not isinstance(limits, Mapping):
            errors.append(f"live_probe_gateway.json: source_limits.{source_id} must exist.")
        else:
            if limits.get("default_result_cap") != candidate.get("default_result_cap"):
                errors.append(f"live_probe_gateway.json: source_limits.{source_id}.default_result_cap mismatch.")
            if limits.get("default_timeout_ms") != candidate.get("default_timeout_ms"):
                errors.append(f"live_probe_gateway.json: source_limits.{source_id}.default_timeout_ms mismatch.")


def _validate_surface_capabilities(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("surface_capabilities.json: must be a JSON object.")
        return
    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, list):
        errors.append("surface_capabilities.json: capabilities must be a list.")
        return
    by_id = {
        item.get("id"): item
        for item in capabilities
        if isinstance(item, Mapping) and isinstance(item.get("id"), str)
    }
    for capability_id in LIVE_PROBE_DISABLED_CAPABILITIES:
        item = by_id.get(capability_id)
        if not isinstance(item, Mapping):
            errors.append(f"surface_capabilities.json: missing {capability_id}.")
            continue
        if item.get("enabled_by_default") is not False:
            errors.append(f"surface_capabilities.json: {capability_id}.enabled_by_default must be false.")
        if item.get("requires_operator_signoff") is not True:
            errors.append(f"surface_capabilities.json: {capability_id}.requires_operator_signoff must be true.")
        if item.get("status") in {"implemented", "static_demo", "recorded_fixture"}:
            errors.append(f"surface_capabilities.json: {capability_id}.status must remain future/disabled.")


def _validate_live_backend_handoff(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("live_backend_handoff.json: must be a JSON object.")
        return
    if payload.get("no_live_backend_implemented") is not True:
        errors.append("live_backend_handoff.json: no_live_backend_implemented must remain true.")
    flags = set(_string_list(payload.get("capability_flags_required")))
    for capability_id in LIVE_PROBE_DISABLED_CAPABILITIES:
        if capability_id not in flags:
            errors.append(f"live_backend_handoff.json: capability_flags_required missing {capability_id}.")


def _validate_live_backend_routes(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("live_backend_routes.json: must be a JSON object.")
        return
    routes = payload.get("routes")
    if not isinstance(routes, list):
        errors.append("live_backend_routes.json: routes must be a list.")
        return
    by_path = {
        route.get("path_template"): route
        for route in routes
        if isinstance(route, Mapping) and isinstance(route.get("path_template"), str)
    }
    live_probe = by_path.get("/api/v1/live-probe")
    if not isinstance(live_probe, Mapping):
        errors.append("live_backend_routes.json: /api/v1/live-probe is required.")
        return
    if live_probe.get("status") not in {"blocked", "deferred", "planned"}:
        errors.append("live_backend_routes.json: /api/v1/live-probe must remain blocked/deferred/planned.")
    if live_probe.get("public_alpha_allowed") is not False:
        errors.append("live_backend_routes.json: /api/v1/live-probe must not be public-alpha allowed.")
    if live_probe.get("static_handoff_allowed") is not False:
        errors.append("live_backend_routes.json: /api/v1/live-probe must not allow static handoff.")


def _validate_public_alpha_wrapper(repo_root: Path, errors: list[str]) -> dict[str, Any]:
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    try:
        from surfaces.web.server.public_alpha_config import load_public_alpha_wrapper_config
    except Exception as error:  # pragma: no cover - defensive import reporting
        errors.append(f"public_alpha_config.py: failed to import wrapper config: {error}")
        return {}
    try:
        config = load_public_alpha_wrapper_config(environ={})
        summary = config.to_summary_dict()
    except Exception as error:  # pragma: no cover - defensive config reporting
        errors.append(f"public_alpha_config.py: failed to load default wrapper config: {error}")
        return {}
    if summary.get("live_probes_enabled") is not False:
        errors.append("public_alpha wrapper: live_probes_enabled must default to false.")
    if summary.get("live_internet_archive_enabled") is not False:
        errors.append("public_alpha wrapper: live_internet_archive_enabled must default to false.")
    return summary


def _validate_static_pages(public_site: Path, repo_root: Path, errors: list[str]) -> list[str]:
    hits: list[str] = []
    if not public_site.exists():
        errors.append("public_site: static artifact is missing.")
        return hits
    for path in sorted(public_site.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".html", ".txt", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        _validate_no_positive_live_probe_claims(path, text, repo_root, errors, hits)
        if path.suffix.lower() == ".html":
            parser = LinkParser()
            parser.feed(text)
            for attr, value in parser.references:
                if "/api/v1/live-probe" in value:
                    hit = f"{_rel(path, repo_root)}: {attr}={value!r}"
                    hits.append(hit)
                    errors.append(f"{hit}: static artifact must not link to live-probe routes.")
    return hits


def _validate_docs(repo_root: Path, errors: list[str]) -> None:
    required_docs = {
        "docs/reference/LIVE_PROBE_GATEWAY_CONTRACT.md": [
            "disabled by default",
            "not a probe implementation",
            "Google is not a live probe candidate",
        ],
        "docs/architecture/LIVE_PROBE_GATEWAY.md": [
            "static publication plane",
            "live backend handoff",
            "Google web search remains",
        ],
        "docs/operations/LIVE_PROBE_POLICY.md": [
            "No live probe is implemented",
            "Google remains manual-baseline only",
        ],
    }
    for relative, phrases in required_docs.items():
        path = repo_root / relative
        if not path.exists():
            errors.append(f"{relative}: required live probe gateway doc is missing.")
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.casefold()
        for phrase in phrases:
            if phrase.casefold() not in lowered:
                errors.append(f"{relative}: missing phrase {phrase!r}.")


def _validate_no_positive_live_probe_claims(
    path: Path,
    text: str,
    repo_root: Path,
    errors: list[str],
    hits: list[str],
) -> None:
    for pattern in POSITIVE_LIVE_PROBE_PATTERNS:
        for match in pattern.finditer(text):
            before = text[max(0, match.start() - 120) : match.start()].casefold()
            context = text[max(0, match.start() - 32) : match.end() + 32].casefold()
            if "no " in before[-40:] or "not " in before[-40:] or "does not " in before[-96:]:
                continue
            if "future" in before[-80:] or "disabled" in before[-80:] or "reserved" in before[-80:]:
                continue
            if "not " in context or "disabled" in context or "no live" in context:
                continue
            hit = f"{_rel(path, repo_root)}: {match.group(0)!r}"
            hits.append(hit)
            errors.append(f"{hit}: prohibited positive live-probe claim.")


def _expect_mapping_values(
    label: str, payload: Mapping[str, Any], expected: Mapping[str, Any], errors: list[str]
) -> None:
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append(f"{label}: {key} must be {value!r}.")


def _load_json(path: Path, errors: list[str], repo_root: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path, repo_root)}: missing required JSON file.")
    except json.JSONDecodeError as error:
        errors.append(f"{_rel(path, repo_root)}: invalid JSON: {error}")
    return {}


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Live probe gateway validation",
        f"status: {report['status']}",
        f"candidate_sources: {len(report['candidate_sources'])}",
        f"disabled_sources: {len(report['disabled_sources'])}",
        f"wrapper_live_probes_enabled: {report.get('wrapper_live_probes_enabled')}",
        f"wrapper_live_internet_archive_enabled: {report.get('wrapper_live_internet_archive_enabled')}",
    ]
    errors = report.get("errors")
    if isinstance(errors, list) and errors:
        lines.extend(["", "Errors"])
        lines.extend(f"- {error}" for error in errors)
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.extend(["", "Warnings"])
        lines.extend(f"- {warning}" for warning in warnings)
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
