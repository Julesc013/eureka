from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
HANDOFF = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_handoff.json"
SAFETY = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_safety.json"
GENERATED_ARTIFACTS = (
    REPO_ROOT / "control" / "inventory" / "generated_artifacts" / "generated_artifacts.json"
)
SITE_ROOT = REPO_ROOT / "site" / "dist"

REQUIRED_OUTPUTS = {
    "search.html": "standard",
    "lite/search.html": "lite",
    "text/search.txt": "text",
    "files/search.README.txt": "files",
    "data/search_handoff.json": "data",
}
REQUIRED_LANGUAGE = (
    "hosted public search is not configured",
    "does not run python",
    "local_index_only",
    "no live probes",
    "downloads",
    "installs",
    "uploads",
    "local path search",
)
SAMPLE_QUERIES = (
    "windows 7 apps",
    "latest firefox before xp support ended",
    "driver.inf",
    "thinkpad t42 wifi windows 2000",
    "pc magazine ray tracing",
)
PROHIBITED_LIVE_CLAIMS = (
    "hosted public search is live",
    "public search is hosted",
    "production-ready public search",
    "github pages runs python",
    "live probes are enabled",
    "downloads are enabled",
    "installs are enabled",
    "uploads are enabled",
)


class _SearchFormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.script_count = 0
        self.q_maxlengths: list[int] = []
        self.form_actions: list[str] = []
        self.disabled_submit_seen = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        folded_tag = tag.casefold()
        attr = {name.casefold(): value for name, value in attrs}
        if folded_tag == "script":
            self.script_count += 1
        if folded_tag == "form":
            self.form_actions.append(attr.get("action") or "")
        if folded_tag == "input" and attr.get("name") == "q":
            raw_max = attr.get("maxlength")
            try:
                self.q_maxlengths.append(int(raw_max or "0"))
            except ValueError:
                self.q_maxlengths.append(0)
        if folded_tag == "button" and "disabled" in attr:
            self.disabled_submit_seen = True


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Public Search Static Handoff v0 without network access."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_public_search_static_handoff()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_public_search_static_handoff() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    handoff = _load_json(HANDOFF, errors)
    safety = _load_json(SAFETY, errors)
    data_summary = _load_json(SITE_ROOT / "data" / "search_handoff.json", errors)
    generated_artifacts = _load_json(GENERATED_ARTIFACTS, errors)

    _validate_inventory(handoff, errors)
    _validate_safety_alignment(handoff, safety, errors)
    _validate_outputs(handoff, safety, data_summary, errors)
    _validate_generated_artifact_ownership(generated_artifacts, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "public_search_static_handoff_validator_v0",
        "handoff_id": _mapping(handoff).get("handoff_id"),
        "static_artifact": _mapping(handoff).get("static_artifact"),
        "hosted_backend_status": _mapping(handoff).get("hosted_backend_status"),
        "default_backend_mode": _mapping(handoff).get("default_backend_mode"),
        "outputs": sorted(REQUIRED_OUTPUTS),
        "q_maxlength": _mapping(_mapping(handoff).get("form_policy")).get("query_maxlength"),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_inventory(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("public_search_handoff.json: must be a JSON object.")
        return
    expected = {
        "schema_version": "0.1.0",
        "handoff_id": "eureka-public-search-static-handoff-v0",
        "status": "implemented_static_handoff",
        "stability": "experimental",
        "static_artifact": "site/dist",
        "runtime_dependency": "local_public_search_runtime_v0",
        "hosted_backend_status": "unavailable",
        "default_backend_mode": "not_configured",
        "no_js_required": True,
    }
    _expect_values("public_search_handoff.json", payload, expected, errors)

    backend_policy = _mapping(payload.get("backend_url_policy"))
    for flag in ("hosted_backend_url_configured", "hosted_backend_url_verified"):
        if backend_policy.get(flag) is not False:
            errors.append(f"public_search_handoff.json: backend_url_policy.{flag} must be false.")
    if backend_policy.get("hosted_backend_url") is not None:
        errors.append("public_search_handoff.json: hosted_backend_url must be null.")
    if backend_policy.get("fake_hosted_urls_allowed") is not False:
        errors.append("public_search_handoff.json: fake hosted backend URLs must not be allowed.")

    form_policy = _mapping(payload.get("form_policy"))
    expected_form = {
        "method": "get",
        "query_parameter": "q",
        "mode": "local_index_only",
        "hosted_form_enabled": False,
        "disabled_static_form_rendered": True,
        "no_js_required": True,
    }
    _expect_values("public_search_handoff.json: form_policy", form_policy, expected_form, errors)
    if not isinstance(form_policy.get("query_maxlength"), int):
        errors.append("public_search_handoff.json: form_policy.query_maxlength must be an integer.")

    disabled = _mapping(payload.get("disabled_behaviors"))
    for key in (
        "live_probes_enabled",
        "downloads_enabled",
        "installs_enabled",
        "uploads_enabled",
        "accounts_enabled",
        "telemetry_enabled",
        "local_path_search_enabled",
        "arbitrary_url_fetch_enabled",
        "scraping_enabled",
        "crawling_enabled",
    ):
        if disabled.get(key) is not False:
            errors.append(f"public_search_handoff.json: disabled_behaviors.{key} must be false.")


def _validate_safety_alignment(handoff: Any, safety: Any, errors: list[str]) -> None:
    if not isinstance(handoff, Mapping) or not isinstance(safety, Mapping):
        return
    form_policy = _mapping(handoff.get("form_policy"))
    safety_limits = _mapping(safety.get("request_limits"))
    max_query_length = safety_limits.get("max_query_length")
    if form_policy.get("query_maxlength") != max_query_length:
        errors.append("public_search_handoff.json: form query_maxlength must match safety max_query_length.")
    if form_policy.get("default_limit") != _mapping(safety.get("result_limits")).get(
        "default_result_limit"
    ):
        errors.append("public_search_handoff.json: default_result_limit must match safety policy.")
    static_defaults = _mapping(safety.get("static_site_defaults"))
    if static_defaults.get("search_form_added") is not True:
        errors.append("public_search_safety.json: search_form_added must be true.")
    if static_defaults.get("static_search_handoff_added") is not True:
        errors.append("public_search_safety.json: static_search_handoff_added must be true.")
    if static_defaults.get("hosted_form_enabled") is not False:
        errors.append("public_search_safety.json: hosted_form_enabled must be false.")


def _validate_outputs(handoff: Any, safety: Any, data_summary: Any, errors: list[str]) -> None:
    max_query_length = _mapping(_mapping(handoff).get("form_policy")).get("query_maxlength")
    if not isinstance(max_query_length, int):
        max_query_length = _mapping(_mapping(safety).get("request_limits")).get("max_query_length", 160)
    static_routes = _route_outputs(_mapping(handoff).get("static_routes"))
    for relative, route_key in REQUIRED_OUTPUTS.items():
        path = SITE_ROOT / relative
        if not path.exists():
            errors.append(f"site/dist/{relative}: required search handoff output is missing.")
            continue
        if static_routes.get(route_key) != f"site/dist/{relative}":
            errors.append(
                f"public_search_handoff.json: static_routes.{route_key} must be site/dist/{relative}."
            )

    search_html = _read_text(SITE_ROOT / "search.html", errors)
    lite_html = _read_text(SITE_ROOT / "lite" / "search.html", errors)
    text_handoff = _read_text(SITE_ROOT / "text" / "search.txt", errors)
    files_handoff = _read_text(SITE_ROOT / "files" / "search.README.txt", errors)

    for label, text in {
        "search.html": search_html,
        "lite/search.html": lite_html,
        "text/search.txt": text_handoff,
        "files/search.README.txt": files_handoff,
    }.items():
        folded = text.casefold()
        for phrase in REQUIRED_LANGUAGE:
            if phrase not in folded:
                errors.append(f"site/dist/{label}: missing required phrase {phrase!r}.")
        for query in SAMPLE_QUERIES:
            if query not in folded:
                errors.append(f"site/dist/{label}: missing sample query {query!r}.")
        for prohibited in PROHIBITED_LIVE_CLAIMS:
            if prohibited in folded:
                errors.append(f"site/dist/{label}: contains prohibited claim {prohibited!r}.")
        if "https://" in folded and _mapping(handoff).get("hosted_backend_status") != "verified":
            errors.append(f"site/dist/{label}: must not include fake hosted HTTPS backend links.")

    for relative, text in {
        "search.html": search_html,
        "lite/search.html": lite_html,
        "files/search.README.txt": files_handoff,
    }.items():
        if "<script" in text.casefold():
            errors.append(f"site/dist/{relative}: must not include script tags.")

    parser = _SearchFormParser()
    parser.feed(search_html)
    if parser.script_count:
        errors.append("site/dist/search.html: must not include script tags.")
    if not parser.q_maxlengths:
        errors.append("site/dist/search.html: missing q input maxlength.")
    for maxlength in parser.q_maxlengths:
        if maxlength <= 0 or maxlength > max_query_length:
            errors.append("site/dist/search.html: q maxlength exceeds safety policy.")
    if parser.form_actions and any(action not in ("", "#") for action in parser.form_actions):
        errors.append("site/dist/search.html: disabled hosted form must not point at a backend URL.")
    if not parser.disabled_submit_seen:
        errors.append("site/dist/search.html: disabled submit button is required while backend is unconfigured.")

    _validate_data_summary(data_summary, max_query_length, errors)


def _validate_data_summary(payload: Any, max_query_length: int, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("site/dist/data/search_handoff.json: must be a JSON object.")
        return
    expected = {
        "schema_version": "0.1.0",
        "generated_by": "scripts/generate_public_data_summaries.py",
        "search_handoff_status": "implemented_static_handoff",
        "hosted_backend_status": "unavailable",
        "default_backend_mode": "not_configured",
        "first_mode": "local_index_only",
        "backend_url": None,
        "local_runtime_available": True,
        "contains_live_backend": False,
        "contains_live_probes": False,
        "contains_external_observations": False,
        "deployment_performed": False,
        "no_hosted_search_claim": True,
    }
    _expect_values("site/dist/data/search_handoff.json", payload, expected, errors)
    if payload.get("max_query_length") != max_query_length:
        errors.append("site/dist/data/search_handoff.json: max_query_length must match handoff policy.")
    disabled = _mapping(payload.get("disabled_behaviors"))
    for key in (
        "live_probes_enabled",
        "downloads_enabled",
        "installs_enabled",
        "uploads_enabled",
        "local_path_search_enabled",
        "arbitrary_url_fetch_enabled",
        "telemetry_enabled",
    ):
        if disabled.get(key) is not False:
            errors.append(f"site/dist/data/search_handoff.json: disabled_behaviors.{key} must be false.")


def _validate_generated_artifact_ownership(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("generated_artifacts.json: must be a JSON object.")
        return
    artifacts = payload.get("artifact_groups")
    if not isinstance(artifacts, list):
        artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list):
        errors.append("generated_artifacts.json: artifact_groups must be a list.")
        return
    by_id = {
        artifact.get("artifact_id"): artifact
        for artifact in artifacts
        if isinstance(artifact, Mapping) and isinstance(artifact.get("artifact_id"), str)
    }
    static_site = _mapping(by_id.get("static_site_dist"))
    if not static_site:
        errors.append("generated_artifacts.json: missing static_site_dist artifact.")
        return
    if "site/dist" not in _string_list(static_site.get("artifact_paths")):
        errors.append("generated_artifacts.json: static_site_dist must own site/dist.")
    if static_site.get("manual_edits_allowed") is not False:
        errors.append("generated_artifacts.json: static_site_dist must disallow manual edits.")


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON at line {exc.lineno}: {exc.msg}.")
    return None


def _read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: missing.")
        return ""


def _expect_values(
    label: str,
    payload: Mapping[str, Any],
    expected: Mapping[str, Any],
    errors: list[str],
) -> None:
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            errors.append(f"{label}: {key} must be {expected_value!r}.")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _route_outputs(value: Any) -> Mapping[str, str]:
    routes: dict[str, str] = {}
    if not isinstance(value, list):
        return routes
    for item in value:
        if not isinstance(item, Mapping):
            continue
        profile = item.get("profile")
        output_path = item.get("output_path")
        if isinstance(profile, str) and isinstance(output_path, str):
            key = {
                "standard_web": "standard",
                "lite_html": "lite",
                "text": "text",
                "file_tree": "files",
                "api_client": "data",
            }.get(profile)
            if key:
                routes[key] = output_path
    return routes


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Public Search Static Handoff validation",
        f"status: {report['status']}",
        f"handoff_id: {report.get('handoff_id')}",
        f"static_artifact: {report.get('static_artifact')}",
        f"hosted_backend_status: {report.get('hosted_backend_status')}",
        f"default_backend_mode: {report.get('default_backend_mode')}",
        f"outputs: {len(report['outputs'])}",
    ]
    if report["errors"]:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
