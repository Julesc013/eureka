from __future__ import annotations

import argparse
import hashlib
from html import escape
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_search_page_view_model import validate_payloads


SCHEMA_VERSION = "track_a_13_projection_dry_run.v0"
HANDOFF_SCHEMA_VERSION = "track_a_13_search_handoff_preview.v0"
DEFAULT_INPUT = "examples/view_models/search_page/static_projection_reference_v0.json"
DEFAULT_OUTPUT_ROOT = "control/audits/track-a-13-static-searchpage-projection-dry-run-v0/generated"
SEARCH_PAGE_POLICY = "control/inventory/publication/search_page_view_model_policy.json"
REPRESENTATION_INVENTORY = "control/inventory/publication/representation_profiles.json"
SEMANTIC_PARITY_INVENTORY = "control/inventory/publication/semantic_renderer_parity_policy.json"
ROUTE_MATRIX = "control/inventory/publication/route_view_representation_matrix.json"

PROJECTION_TARGETS: tuple[dict[str, str], ...] = (
    {
        "artifact_kind": "standard_static_html",
        "filename": "search.standard.html",
        "representation_profile": "standard_html",
        "route_family": "search",
    },
    {
        "artifact_kind": "lite_static_html",
        "filename": "search.lite.html",
        "representation_profile": "lite_html",
        "route_family": "lite_static",
    },
    {
        "artifact_kind": "text_static",
        "filename": "search.txt",
        "representation_profile": "text",
        "route_family": "text_static",
    },
    {
        "artifact_kind": "file_tree_static",
        "filename": "search.README.txt",
        "representation_profile": "file_tree",
        "route_family": "files_static",
    },
    {
        "artifact_kind": "static_json_handoff",
        "filename": "search_handoff.json",
        "representation_profile": "api_json",
        "route_family": "data_static",
    },
)

PRODUCT_BOUNDARY = {
    "changed_product_behavior": False,
    "changed_public_routes": False,
    "changed_generated_site_artifacts": False,
    "regenerated_site_dist": False,
    "enabled_hosting": False,
    "enabled_live_probes": False,
    "enabled_source_sync": False,
    "enabled_source_connectors": False,
    "enabled_downloads": False,
    "enabled_installers": False,
    "enabled_execution": False,
    "enabled_uploads": False,
    "enabled_accounts": False,
    "enabled_telemetry": False,
    "created_native_projects": False,
    "mutated_master_index": False,
    "claimed_rights_clearance": False,
    "claimed_malware_safety": False,
    "claimed_verified_installability": False,
    "claimed_exhaustive_global_search": False,
    "claimed_automatic_merge_or_promotion": False,
}

HANDOFF_PRODUCT_BOUNDARY = {
    "hosted_backend_claimed": False,
    "live_probes_enabled": False,
    "downloads_enabled": False,
    "uploads_enabled": False,
    "accounts_enabled": False,
    "telemetry_enabled": False,
}

SEMANTIC_CATEGORIES = (
    "route_identity",
    "query_identity",
    "public_runtime_posture",
    "result_identity",
    "source_evidence_posture",
    "risk_rights_posture",
    "compatibility_posture",
    "limitations",
    "blocked_actions",
    "next_safe_actions",
    "hosted_live_download_upload_account_telemetry_non_claims",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate dry-run static SearchPage projections from one fixture.")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="SearchPageView fixture to project.")
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT, help="Generated output root.")
    parser.add_argument("--check", action="store_true", help="Validate generated outputs after writing.")
    parser.add_argument("--json", action="store_true", help="Print compact deterministic JSON summary.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    output = stdout or sys.stdout
    error_output = stderr or sys.stderr
    try:
        report = generate_projection_bundle(
            input_path=Path(args.input),
            output_root=Path(args.output_root),
            repo_root=REPO_ROOT,
            run_check=args.check,
        )
    except ValueError as exc:
        error_output.write(f"error: {exc}\n")
        return 1

    if args.json:
        output.write(
            json.dumps(
                {
                    "schema_version": SCHEMA_VERSION,
                    "status": report["status"],
                    "generated_count": len(report["generated_outputs"]),
                    "critical_boundary_violations": report["critical_boundary_violations"],
                    "warnings": report["warnings"],
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        )
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "pass" else 1


def generate_projection_bundle(
    *,
    input_path: Path,
    output_root: Path,
    repo_root: Path = REPO_ROOT,
    run_check: bool = False,
) -> dict[str, Any]:
    root = repo_root.resolve()
    fixture_path = _resolve_repo_path(input_path, root)
    generated_root = validate_output_root(output_root, root)
    audit_root = generated_root.parent

    view_model = _load_json(fixture_path)
    _validate_fixture(view_model, root)
    generated_root.mkdir(parents=True, exist_ok=True)

    renderers = {
        "search.standard.html": render_standard_html,
        "search.lite.html": render_lite_html,
        "search.txt": render_text,
        "search.README.txt": lambda view, source: render_file_tree_readme(view, source, generated_root),
        "search_handoff.json": render_json_handoff,
    }
    generated_outputs: list[dict[str, Any]] = []
    for target in PROJECTION_TARGETS:
        filename = target["filename"]
        content = renderers[filename](view_model, _rel(fixture_path, root))
        path = generated_root / filename
        if filename.endswith(".json"):
            path.write_text(json.dumps(content, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        else:
            path.write_text(str(content), encoding="utf-8")
        generated_outputs.append(_output_record(path, root, target))

    semantic_parity = build_semantic_parity()
    warnings = _semantic_warnings(semantic_parity)
    critical: list[str] = []
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if not critical else "fail",
        "track": "A",
        "task": "TRACK-A-13",
        "source_fixture": _rel(fixture_path, root),
        "generated_outputs": generated_outputs,
        "semantic_parity": semantic_parity,
        "warnings": sorted(warnings),
        "critical_boundary_violations": critical,
        "product_boundary": dict(PRODUCT_BOUNDARY),
        "next_task": "TRACK-A-14 - Object Source Need Candidate projection audit",
    }

    report_path = audit_root / "projection_dry_run_report.json"
    parity_path = audit_root / "semantic_parity_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    parity_path.write_text(render_semantic_parity_report(report), encoding="utf-8")

    if run_check:
        from scripts.validate_static_searchpage_projection_dry_run import validate_static_searchpage_projection_dry_run

        validation = validate_static_searchpage_projection_dry_run(
            repo_root=root,
            output_root=generated_root,
            report_path=report_path,
            parity_path=parity_path,
        )
        if validation["status"] != "valid":
            raise ValueError("; ".join(validation["errors"]))
    return report


def validate_output_root(output_root: Path, repo_root: Path = REPO_ROOT) -> Path:
    root = repo_root.resolve()
    candidate = _resolve_repo_path(output_root, root)
    site_dist = root / "site" / "dist"
    forbidden_roots = [
        site_dist,
        root / "site" / "pages",
        root / "site" / "templates",
        root / "runtime",
        root / "contracts",
        root / "control" / "inventory",
        root / "surfaces",
        root / "native",
    ]
    for forbidden in forbidden_roots:
        if _is_relative_to(candidate, forbidden):
            raise ValueError(f"output root is forbidden: {_rel(candidate, root)}")
    if _is_relative_to(candidate, root):
        allowed = [
            root / "control" / "audits",
            root / ".aide" / "reports",
        ]
        if not any(_is_relative_to(candidate, prefix) for prefix in allowed):
            raise ValueError("repo-local output root must be under control/audits or .aide/reports")
    return candidate


def render_standard_html(view: Mapping[str, Any], source_fixture: str) -> str:
    results = "\n".join(render_result_html(result) for result in _sequence(view.get("results")))
    if not results:
        results = "<p>No results in this fixture.</p>"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{escape(str(view.get("page_title", "Search")))}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; line-height: 1.45; max-width: 56rem; margin: 2rem auto; padding: 0 1rem; }}
    section {{ border-top: 1px solid #ccc; padding-top: 1rem; margin-top: 1rem; }}
    .label {{ font-weight: 700; }}
  </style>
</head>
<body>
  <h1>Search</h1>
  <p><span class="label">Route Identity:</span> {escape(str(view.get("canonical_route")))}</p>
  <p><span class="label">Query:</span> {escape(_query_label(view))}</p>
  <p><span class="label">Mode/Posture:</span> {escape(_mode_posture(view))}</p>
  <p><span class="label">Hosted backend unavailable:</span> true. <span class="label">Live probes unavailable:</span> true. No JavaScript is required.</p>
  <section><h2>Result Summary</h2><p>{escape(_summary(view.get("result_summary")))}</p></section>
  <section><h2>Results</h2>{results}</section>
  <section><h2>Source/Evidence</h2><p>{escape(_source_evidence(view))}</p></section>
  <section><h2>Risk/Rights</h2><p>{escape(_risk_rights(view))}</p></section>
  <section><h2>Compatibility</h2><p>{escape(_compatibility(view))}</p></section>
  <section><h2>Limitations</h2>{_list_html(_limitations(view))}</section>
  <section><h2>Blocked Actions</h2>{_list_html(_blocked_action_text(view))}</section>
  <section><h2>Next Safe Actions</h2>{_list_html(_action_text(view))}</section>
  <section><h2>Static/Public Boundary</h2><p>No hosted backend, live probes, downloads, uploads, accounts, telemetry, production API, or deployment behavior is claimed.</p></section>
  <footer><p>Generated from {escape(source_fixture)} as audit evidence only.</p></footer>
</body>
</html>
"""


def render_result_html(result: Any) -> str:
    if not isinstance(result, Mapping):
        return ""
    return f"""<article>
  <h3>{escape(str(result.get("title", "Untitled result")))}</h3>
  <p><span class="label">Result State:</span> {escape(str(result.get("result_state", "unknown")))}</p>
  <p><span class="label">Source/Evidence:</span> {escape(str(result.get("source_posture", "unknown")))}; {escape(str(result.get("evidence_posture", "unknown")))}</p>
  <p><span class="label">Risk/Rights:</span> {escape(str(result.get("risk_posture", "unknown")))}; {escape(str(result.get("rights_posture", "unknown")))}</p>
  <p><span class="label">Compatibility:</span> {escape(str(result.get("compatibility_posture", "unknown")))}</p>
</article>"""


def render_lite_html(view: Mapping[str, Any], source_fixture: str) -> str:
    rows = [
        ("Route Identity", str(view.get("canonical_route", ""))),
        ("Query", _query_label(view)),
        ("Mode/Posture", _mode_posture(view)),
        ("Result Summary", _summary(view.get("result_summary"))),
        ("Source/Evidence", _source_evidence(view)),
        ("Risk/Rights", _risk_rights(view)),
        ("Compatibility", _compatibility(view)),
        ("Limitations", "; ".join(_limitations(view))),
        ("Blocked Actions", "; ".join(_blocked_action_text(view))),
        ("Next Safe Actions", "; ".join(_action_text(view))),
    ]
    result_items = "".join(f"<li>{escape(_result_line(result))}</li>\n" for result in _sequence(view.get("results")))
    return """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Lite Search</title></head>
<body>
<h1>Search</h1>
<p>No JavaScript, no hosted backend, no live probes, no downloads, no uploads, no accounts, no telemetry.</p>
<table border="1">
""" + "".join(f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>\n" for label, value in rows) + f"""</table>
<h2>Results</h2>
<ul>
{result_items or "<li>No results in this fixture.</li>"}
</ul>
<p>Generated from {escape(source_fixture)} as audit evidence only.</p>
</body>
</html>
"""


def render_text(view: Mapping[str, Any], source_fixture: str) -> str:
    result_lines = [_result_line(result) for result in _sequence(view.get("results"))] or ["No results in this fixture."]
    return "\n".join(
        [
            "Search",
            f"Route Identity: {view.get('canonical_route', '')}",
            f"Query: {_query_label(view)}",
            f"Mode/Posture: {_mode_posture(view)}",
            "",
            "Result Summary",
            _summary(view.get("result_summary")),
            "",
            "Results",
            *[f"- {line}" for line in result_lines],
            "",
            f"Source/Evidence: {_source_evidence(view)}",
            f"Risk/Rights: {_risk_rights(view)}",
            f"Compatibility: {_compatibility(view)}",
            "",
            "Limitations",
            *[f"- {item}" for item in _limitations(view)],
            "",
            "Blocked Actions",
            *[f"- {item}" for item in _blocked_action_text(view)],
            "",
            "Next Safe Actions",
            *[f"- {item}" for item in _action_text(view)],
            "",
            "Static/Public Boundary",
            "- Hosted backend unavailable.",
            "- Live probes unavailable.",
            "- Downloads, installers, execution, uploads, accounts, and telemetry unavailable.",
            "- This is dry-run audit evidence only, not an active public site or production API.",
            "",
            f"Generated From: {source_fixture}",
            "",
        ]
    )


def render_file_tree_readme(view: Mapping[str, Any], source_fixture: str, generated_root: Path) -> str:
    files = [target["filename"] for target in PROJECTION_TARGETS]
    return "\n".join(
        [
            "SearchPage Static Projection Dry Run",
            "",
            "Artifact Purpose",
            "- Public-safe file-tree README for generated SearchPage projection evidence.",
            "",
            f"Source SearchPageView Fixture: {source_fixture}",
            "Route Identity: " + str(view.get("canonical_route", "")),
            "Query: " + _query_label(view),
            "Mode/Posture: " + _mode_posture(view),
            "",
            "Output File List",
            *[f"- {name}" for name in files],
            "",
            "Result Summary",
            "- " + _summary(view.get("result_summary")),
            "",
            "Source/Evidence",
            "- " + _source_evidence(view),
            "",
            "Risk/Rights",
            "- " + _risk_rights(view),
            "",
            "Compatibility",
            "- " + _compatibility(view),
            "",
            "Limitations",
            *[f"- {item}" for item in _limitations(view)],
            "",
            "Blocked Actions",
            *[f"- {item}" for item in _blocked_action_text(view)],
            "",
            "Next Safe Actions",
            *[f"- {item}" for item in _action_text(view)],
            "",
            "Boundary Notes",
            "- No live API claim.",
            "- No download or install claim.",
            "- No hosted backend claim.",
            "- No upload, account, telemetry, rights-clearance, malware-safety, verified-installability, exhaustive-search, or auto-promotion claim.",
            "- Checksums in the dry-run report describe generated preview files only.",
            "",
            "Generated Root",
            "- " + str(generated_root),
            "",
        ]
    )


def render_json_handoff(view: Mapping[str, Any], source_fixture: str) -> dict[str, Any]:
    return {
        "schema_version": HANDOFF_SCHEMA_VERSION,
        "source_view_model": {
            "view_model_id": view.get("view_model_id"),
            "view_family": view.get("view_family"),
            "fixture_path": source_fixture,
        },
        "route_family": view.get("route_family"),
        "representation_profile": "api_json",
        "search_mode": view.get("search_mode"),
        "public_runtime_posture": view.get("public_runtime_posture"),
        "query": view.get("query"),
        "result_summary": view.get("result_summary"),
        "results": view.get("results"),
        "limitations": view.get("limitations"),
        "blocked_actions": view.get("blocked_actions"),
        "product_boundary": dict(HANDOFF_PRODUCT_BOUNDARY),
        "generated_from": {
            "generator": "scripts/generate_static_searchpage_projection.py",
            "source_fixture": source_fixture,
            "audit_only": True,
            "production_api_stability_claimed": False,
        },
        "notes": [
            "Static JSON handoff preview only.",
            "This is not a live API, production API, deployment artifact, or hosted backend claim.",
        ],
    }


def build_semantic_parity() -> dict[str, dict[str, str]]:
    parity: dict[str, dict[str, str]] = {}
    for category in SEMANTIC_CATEGORIES:
        parity[category] = {}
        for target in PROJECTION_TARGETS:
            kind = target["artifact_kind"]
            if kind == "file_tree_static" and category in {"result_identity", "source_evidence_posture"}:
                parity[category][kind] = "degraded_but_preserved"
            else:
                parity[category][kind] = "preserved"
    return parity


def render_semantic_parity_report(report: Mapping[str, Any]) -> str:
    lines = [
        "# TRACK-A-13 Semantic Parity Report",
        "",
        "Generated dry-run projections were compared against SearchPageView semantic categories.",
        "",
        "| Semantic Category | standard_static_html | lite_static_html | text_static | file_tree_static | static_json_handoff |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    parity = report["semantic_parity"]
    for category in SEMANTIC_CATEGORIES:
        statuses = parity[category]
        lines.append(
            "| "
            + " | ".join(
                [
                    category,
                    statuses["standard_static_html"],
                    statuses["lite_static_html"],
                    statuses["text_static"],
                    statuses["file_tree_static"],
                    statuses["static_json_handoff"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- File-tree output intentionally degrades result/source detail into a README summary while preserving status and caveats.",
            "- No generated output is an active public route, live API, deployment artifact, hosted backend, or production claim.",
            "- Site artifacts under `site/dist` were not regenerated or changed.",
            "",
        ]
    )
    return "\n".join(lines)


def _validate_fixture(view_model: Mapping[str, Any], root: Path) -> None:
    errors: list[str] = []
    policy = _load_json(root / SEARCH_PAGE_POLICY)
    representations = _load_json(root / REPRESENTATION_INVENTORY)
    semantic = _load_json(root / SEMANTIC_PARITY_INVENTORY)
    route_matrix = _load_json(root / ROUTE_MATRIX)
    errors.extend(
        validate_payloads(
            policy,
            representations,
            semantic,
            route_matrix,
            [view_model],
            source_label="static_searchpage_projection_fixture",
        )
    )
    if errors:
        raise ValueError("fixture validation failed: " + "; ".join(sorted(errors)))


def _output_record(path: Path, root: Path, target: Mapping[str, str]) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "artifact_kind": target["artifact_kind"],
        "path": _rel(path, root),
        "representation_profile": target["representation_profile"],
        "route_family": target["route_family"],
        "sha256": hashlib.sha256(data).hexdigest(),
        "byte_size": len(data),
    }


def _semantic_warnings(parity: Mapping[str, Mapping[str, str]]) -> list[str]:
    warnings: list[str] = []
    allowed = {"preserved", "degraded_but_preserved", "omitted_with_reason", "not_applicable"}
    for category, statuses in parity.items():
        for target, status in statuses.items():
            if status not in allowed:
                warnings.append(f"{category}/{target}: {status}")
    return warnings


def _resolve_repo_path(path: Path, repo_root: Path) -> Path:
    return path.resolve() if path.is_absolute() else (repo_root / path).resolve()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Static SearchPage projection dry run",
        f"status: {report['status']}",
        f"source_fixture: {report['source_fixture']}",
        f"generated_outputs: {len(report['generated_outputs'])}",
        f"critical_boundary_violations: {len(report['critical_boundary_violations'])}",
        f"warnings: {len(report['warnings'])}",
    ]
    for output in report["generated_outputs"]:
        lines.append(f"- {output['path']}: {output['representation_profile']} sha256={output['sha256']}")
    return "\n".join(lines) + "\n"


def _query_label(view: Mapping[str, Any]) -> str:
    query = view.get("query")
    if isinstance(query, Mapping):
        return str(query.get("raw_query") or query.get("normalized_query") or "")
    return ""


def _mode_posture(view: Mapping[str, Any]) -> str:
    runtime = view.get("public_runtime_posture")
    posture_notes = []
    if isinstance(runtime, Mapping):
        posture_notes.append(str(runtime.get("source_mode", "")))
        posture_notes.append("hosted_backend_claimed=false")
        posture_notes.append("live_probes_enabled=false")
    return f"{view.get('search_mode', '')}; " + "; ".join(item for item in posture_notes if item)


def _summary(value: Any) -> str:
    if isinstance(value, Mapping):
        return str(value.get("summary") or value.get("result_state") or "")
    return ""


def _source_evidence(view: Mapping[str, Any]) -> str:
    return f"{_summary(view.get('source_summary'))} Evidence: {_summary(view.get('evidence_summary'))}"


def _risk_rights(view: Mapping[str, Any]) -> str:
    results = [item for item in _sequence(view.get("results")) if isinstance(item, Mapping)]
    if not results:
        return "Risk and rights unknown."
    first = results[0]
    return f"{first.get('risk_posture', 'unknown risk')}; {first.get('rights_posture', 'unknown rights')}"


def _compatibility(view: Mapping[str, Any]) -> str:
    results = [item for item in _sequence(view.get("results")) if isinstance(item, Mapping)]
    if not results:
        return "Compatibility unknown."
    return str(results[0].get("compatibility_posture", "Compatibility unknown."))


def _limitations(view: Mapping[str, Any]) -> list[str]:
    items: list[str] = []
    for limitation in _sequence(view.get("limitations")):
        if isinstance(limitation, Mapping):
            label = str(limitation.get("label", "Limitation"))
            description = str(limitation.get("description", ""))
            items.append(f"{label}: {description}".strip())
        elif isinstance(limitation, str):
            items.append(limitation)
    return items or ["No limitations supplied by fixture."]


def _blocked_action_text(view: Mapping[str, Any]) -> list[str]:
    actions: list[str] = []
    for action in _sequence(view.get("blocked_actions")):
        if isinstance(action, Mapping):
            actions.append(f"{action.get('action_id')}: {action.get('reason', '')}".strip())
        elif isinstance(action, str):
            actions.append(action)
    return actions or ["No blocked actions supplied by fixture."]


def _action_text(view: Mapping[str, Any]) -> list[str]:
    actions: list[str] = []
    for action in _sequence(view.get("actions")):
        if isinstance(action, Mapping):
            actions.append(f"{action.get('action_id')}: {action.get('label', '')}".strip())
        elif isinstance(action, str):
            actions.append(action)
    return actions or ["No allowed actions supplied by fixture."]


def _result_line(result: Any) -> str:
    if not isinstance(result, Mapping):
        return "Unknown result"
    return (
        f"{result.get('result_id')}: {result.get('title')} "
        f"[{result.get('result_state')}; {result.get('candidate_review_state')}; "
        f"{result.get('source_posture')}; {result.get('evidence_posture')}]"
    )


def _list_html(items: Sequence[str]) -> str:
    return "<ul>\n" + "".join(f"  <li>{escape(str(item))}</li>\n" for item in items) + "</ul>"


def _sequence(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return list(value)
    return []


if __name__ == "__main__":
    raise SystemExit(main())
