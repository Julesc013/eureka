#!/usr/bin/env python3
"""Validate P56 Static Site Search Integration v0 without network access."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "static-site-search-integration-v0"
REPORT_PATH = AUDIT_ROOT / "static_site_search_integration_report.json"
SITE_ROOT = REPO_ROOT / "site" / "dist"
SEARCH_CONFIG = SITE_ROOT / "data" / "search_config.json"
INDEX_SUMMARY = SITE_ROOT / "data" / "public_index_summary.json"
PUBLIC_INDEX_STATS = REPO_ROOT / "data" / "public_index" / "index_stats.json"

REQUIRED_AUDIT_FILES = {
    "README.md",
    "INTEGRATION_SUMMARY.md",
    "SEARCH_PAGE_REVIEW.md",
    "LITE_TEXT_FILES_REVIEW.md",
    "SEARCH_CONFIG_REVIEW.md",
    "PUBLIC_INDEX_SUMMARY_REVIEW.md",
    "STATIC_TO_DYNAMIC_HANDOFF.md",
    "BACKEND_CONFIGURATION_STATUS.md",
    "NO_JS_AND_OLD_CLIENT_REVIEW.md",
    "PUBLIC_CLAIM_REVIEW.md",
    "GENERATED_ARTIFACT_REVIEW.md",
    "COMMAND_RESULTS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "static_site_search_integration_report.json",
}
REQUIRED_STATIC_FILES = {
    "search.html",
    "lite/search.html",
    "text/search.txt",
    "files/search.README.txt",
    "data/search_config.json",
    "data/public_index_summary.json",
}
REQUIRED_DOCS = {
    "docs/operations/STATIC_SITE_SEARCH_INTEGRATION.md",
}
HARD_FALSE_REPORT_FIELDS = {
    "hosted_backend_verified",
    "live_probes_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "local_paths_enabled",
    "arbitrary_url_fetch_enabled",
    "production_claimed",
    "dynamic_backend_deployed_by_this_milestone",
}
HARD_FALSE_CONFIG_FIELDS = {
    "hosted_backend_verified",
    "search_form_enabled",
    "live_probes_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "local_paths_enabled",
    "arbitrary_url_fetch_enabled",
    "contains_live_backend",
    "contains_live_probes",
    "contains_live_data",
    "contains_external_observations",
    "deployment_performed",
}
PROHIBITED_CLAIMS = (
    "hosted public search is live",
    "public search is hosted",
    "hosted backend is live",
    "production-ready public search",
    "production ready public search",
    "github pages runs python",
    "live probes are enabled",
    "downloads are enabled",
    "uploads are enabled",
)
PRIVATE_PATH_RE = re.compile(r"([A-Za-z]:\\|/Users/|/home/|/tmp/|/var/)")


class _SearchFormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.script_count = 0
        self.form_actions: list[str] = []
        self.q_maxlengths: list[int] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        folded = tag.casefold()
        attr = {name.casefold(): value for name, value in attrs}
        if folded == "script":
            self.script_count += 1
        if folded == "form":
            self.form_actions.append(attr.get("action") or "")
        if folded == "input" and attr.get("name") == "q":
            try:
                self.q_maxlengths.append(int(attr.get("maxlength") or "0"))
            except ValueError:
                self.q_maxlengths.append(0)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate P56 static search integration.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_static_site_search_integration()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_static_site_search_integration() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    _validate_audit_pack(errors)
    report = _load_json(REPORT_PATH, errors)
    config = _load_json(SEARCH_CONFIG, errors)
    index_summary = _load_json(INDEX_SUMMARY, errors)
    index_stats = _load_json(PUBLIC_INDEX_STATS, errors)

    _validate_report(report, errors)
    _validate_static_files(config, index_summary, errors)
    _validate_search_config(config, errors)
    _validate_public_index_summary(index_summary, index_stats, errors)
    _validate_docs(errors)
    _validate_no_private_paths(errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "static_site_search_integration_validator_v0",
        "report_id": _mapping(report).get("report_id"),
        "backend_status": _mapping(report).get("backend_status"),
        "hosted_backend_verified": _mapping(config).get("hosted_backend_verified"),
        "search_form_enabled": _mapping(config).get("search_form_enabled"),
        "document_count": _mapping(index_summary).get("document_count"),
        "checked_static_files": sorted(REQUIRED_STATIC_FILES),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_audit_pack(errors: list[str]) -> None:
    if not AUDIT_ROOT.is_dir():
        errors.append(f"{_rel(AUDIT_ROOT)}: audit directory is missing.")
        return
    present = {path.name for path in AUDIT_ROOT.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_AUDIT_FILES - present)
    if missing:
        errors.append(f"{_rel(AUDIT_ROOT)}: missing audit files {missing}.")


def _validate_report(report: Any, errors: list[str]) -> None:
    if not isinstance(report, Mapping):
        errors.append("static_site_search_integration_report.json must be an object.")
        return
    if report.get("report_id") != "static_site_search_integration_v0":
        errors.append("report_id must be static_site_search_integration_v0.")
    if report.get("backend_status") not in {"backend_unconfigured", "backend_configured_unverified"}:
        errors.append("report backend_status must stay unconfigured or unverified without evidence.")
    if report.get("hosted_backend_url") is not None:
        errors.append("report hosted_backend_url must be null without verified evidence.")
    if report.get("search_form_enabled") is not False:
        errors.append("report search_form_enabled must be false without verified evidence.")
    if report.get("no_js_required") is not True:
        errors.append("report no_js_required must be true.")
    for field in HARD_FALSE_REPORT_FIELDS:
        if report.get(field) is not False:
            errors.append(f"report {field} must be false.")
    if not isinstance(report.get("command_results"), list) or not report["command_results"]:
        errors.append("report command_results must be a non-empty list.")
    if "production ready" in json.dumps(report).casefold():
        errors.append("report must not claim production readiness.")


def _validate_static_files(config: Any, index_summary: Any, errors: list[str]) -> None:
    for relative in sorted(REQUIRED_STATIC_FILES):
        if not (SITE_ROOT / relative).is_file():
            errors.append(f"site/dist/{relative}: required static search integration file is missing.")

    combined = ""
    for relative in ("search.html", "lite/search.html", "text/search.txt", "files/search.README.txt"):
        path = SITE_ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        combined += "\n" + text
        lowered = text.casefold()
        for phrase in ("hosted public search is not configured", "local_index_only", "no live probes"):
            if phrase not in lowered:
                errors.append(f"site/dist/{relative}: missing required phrase {phrase!r}.")
        for claim in PROHIBITED_CLAIMS:
            if claim in lowered:
                errors.append(f"site/dist/{relative}: prohibited claim {claim!r}.")
        parser = _SearchFormParser()
        parser.feed(text)
        if parser.script_count:
            errors.append(f"site/dist/{relative}: no script tags are allowed for P56 search surfaces.")
        if relative.endswith(".html") and _mapping(config).get("hosted_backend_verified") is not True:
            for action in parser.form_actions:
                if action not in ("", "#"):
                    errors.append(f"site/dist/{relative}: form action must be empty while backend is unverified.")
        for maxlength in parser.q_maxlengths:
            if maxlength <= 0 or maxlength > int(_mapping(config).get("max_query_length", 160)):
                errors.append(f"site/dist/{relative}: q maxlength exceeds search_config max.")

    if "data/search_config.json" not in combined or "data/public_index_summary.json" not in combined:
        errors.append("static search surfaces must link or reference search_config and public_index_summary data.")
    if _mapping(index_summary).get("document_count") is None:
        errors.append("public_index_summary document_count must be present.")


def _validate_search_config(config: Any, errors: list[str]) -> None:
    if not isinstance(config, Mapping):
        errors.append("data/search_config.json must be an object.")
        return
    expected = {
        "schema_version": "0.1.0",
        "generated_by": "scripts/generate_public_data_summaries.py",
        "hosted_backend_status": "backend_unconfigured",
        "hosted_backend_url": None,
        "mode": "local_index_only",
        "no_js_required": True,
    }
    for key, value in expected.items():
        if config.get(key) != value:
            errors.append(f"data/search_config.json {key} must be {value!r}.")
    for field in HARD_FALSE_CONFIG_FIELDS:
        if config.get(field) is not False:
            errors.append(f"data/search_config.json {field} must be false.")
    max_query = config.get("max_query_length")
    if not isinstance(max_query, int) or max_query <= 0 or max_query > 160:
        errors.append("data/search_config.json max_query_length must be an integer <= 160.")


def _validate_public_index_summary(summary: Any, stats: Any, errors: list[str]) -> None:
    if not isinstance(summary, Mapping):
        errors.append("data/public_index_summary.json must be an object.")
        return
    if not isinstance(stats, Mapping):
        errors.append("data/public_index/index_stats.json must be an object.")
        return
    for key in ("schema_version", "generated_by", "artifact_root", "document_count", "source_count"):
        if key not in summary:
            errors.append(f"data/public_index_summary.json missing {key}.")
    if summary.get("schema_version") != "0.1.0":
        errors.append("data/public_index_summary.json schema_version must be 0.1.0.")
    if summary.get("generated_by") != "scripts/generate_public_data_summaries.py":
        errors.append("data/public_index_summary.json generated_by mismatch.")
    if summary.get("artifact_root") != "data/public_index":
        errors.append("data/public_index_summary.json artifact_root must be data/public_index.")
    if summary.get("document_count") != stats.get("document_count"):
        errors.append("data/public_index_summary.json document_count must match index_stats.json.")
    if summary.get("record_kind_counts") != stats.get("record_kind_counts"):
        errors.append("data/public_index_summary.json record_kind_counts must match index_stats.json.")
    if summary.get("source_family_counts") != stats.get("source_family_counts"):
        errors.append("data/public_index_summary.json source_family_counts must match index_stats.json.")
    for field in (
        "contains_live_data",
        "contains_private_data",
        "contains_executables",
        "external_calls_performed",
        "live_sources_used",
    ):
        if summary.get(field) is not False:
            errors.append(f"data/public_index_summary.json {field} must be false.")


def _validate_docs(errors: list[str]) -> None:
    for relative in sorted(REQUIRED_DOCS):
        path = REPO_ROOT / relative
        if not path.is_file():
            errors.append(f"{relative}: required documentation is missing.")
            continue
        text = path.read_text(encoding="utf-8").casefold()
        for phrase in (
            "backend unconfigured",
            "no-js",
            "search_config.json",
            "public_index_summary.json",
            "no live probes",
        ):
            if phrase not in text:
                errors.append(f"{relative}: missing phrase {phrase!r}.")


def _validate_no_private_paths(errors: list[str]) -> None:
    for relative in sorted(REQUIRED_STATIC_FILES):
        path = SITE_ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for match in PRIVATE_PATH_RE.finditer(text):
            errors.append(f"site/dist/{relative}: private/local filesystem marker leaked: {match.group(0)!r}.")


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
    return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Static Site Search Integration validation",
        f"status: {report['status']}",
        f"report_id: {report.get('report_id')}",
        f"backend_status: {report.get('backend_status')}",
        f"document_count: {report.get('document_count')}",
    ]
    if report.get("errors"):
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("Warnings")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
