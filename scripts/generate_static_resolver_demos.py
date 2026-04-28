from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SITE_ROOT = REPO_ROOT / "public_site"
DEFAULT_OUTPUT_ROOT = PUBLIC_SITE_ROOT
DEFAULT_DATA_ROOT = PUBLIC_SITE_ROOT / "data"
GOLDEN_ROOT = REPO_ROOT / "tests" / "parity" / "golden" / "python_oracle" / "v0"

SCHEMA_VERSION = "0.1.0"
GENERATED_BY = "scripts/generate_static_resolver_demos.py"
SLICE_ID = "static_resolver_demo_snapshots_v0"

DEMO_FILES = (
    "demo/index.html",
    "demo/query-plan-windows-7-apps.html",
    "demo/result-member-driver-inside-support-cd.html",
    "demo/result-firefox-xp.html",
    "demo/result-article-scan.html",
    "demo/absence-example.html",
    "demo/comparison-example.html",
    "demo/source-example.html",
    "demo/eval-summary.html",
    "demo/README.txt",
    "demo/data/demo_snapshots.json",
)

PUBLIC_DATA_FILES = (
    "site_manifest.json",
    "page_registry.json",
    "source_summary.json",
    "eval_summary.json",
    "route_summary.json",
    "build_manifest.json",
)


class DemoGenerationError(RuntimeError):
    pass


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate static no-JS resolver demo snapshots."
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Static artifact root that receives demo/.",
    )
    parser.add_argument(
        "--data-root",
        default=None,
        help="Directory containing public data summaries. Defaults to <output-root>/data when present, otherwise public_site/data.",
    )
    parser.add_argument("--update", action="store_true", help="Write generated demo snapshots.")
    parser.add_argument("--check", action="store_true", help="Verify committed demo snapshots match generated output.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    output = stdout or sys.stdout
    output_root = Path(args.output_root)
    data_root = _resolve_data_root(output_root, args.data_root)

    try:
        if args.check:
            report = check_static_resolver_demos(output_root, data_root)
        elif args.update:
            report = write_static_resolver_demos(output_root, data_root)
        else:
            files = generate_static_resolver_demos(data_root)
            report = _summary_report(output_root, data_root, files, updated=False)
        if args.json:
            output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        else:
            output.write(_format_plain(report))
        return 0 if report["status"] == "valid" else 1
    except DemoGenerationError as exc:
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


def generate_static_resolver_demos(data_root: Path = DEFAULT_DATA_ROOT) -> dict[str, str]:
    data = _load_public_data(data_root)
    goldens = _load_golden_inputs()
    demos = _build_demo_models(data, goldens)
    manifest = _build_demo_manifest(demos)

    files: dict[str, str] = {
        "demo/index.html": _render_index(demos),
        "demo/README.txt": _readme_text(demos),
        "demo/data/demo_snapshots.json": _json_text(manifest),
    }
    for demo in demos:
        files[f"demo/{demo['page']}"] = _render_demo_page(demo)
    return files


def write_static_resolver_demos(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    data_root: Path | None = None,
) -> dict[str, Any]:
    output_root = output_root.resolve()
    data_root = _resolve_data_root(output_root, str(data_root) if data_root else None)
    files = generate_static_resolver_demos(data_root)
    demo_root = output_root / "demo"
    if demo_root.exists():
        shutil.rmtree(demo_root)
    for relative, text in files.items():
        path = output_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    return _summary_report(output_root, data_root, files, updated=True)


def check_static_resolver_demos(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    data_root: Path | None = None,
) -> dict[str, Any]:
    output_root = output_root.resolve()
    data_root = _resolve_data_root(output_root, str(data_root) if data_root else None)
    files = generate_static_resolver_demos(data_root)
    errors: list[str] = []
    for relative, expected in sorted(files.items()):
        path = output_root / relative
        if not path.exists():
            errors.append(f"{_display_path(path)}: generated demo snapshot is missing.")
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            errors.append(f"{_display_path(path)}: generated demo snapshot is stale.")
    return {
        **_summary_report(output_root, data_root, files, updated=False),
        "status": "valid" if not errors else "invalid",
        "check_mode": True,
        "errors": errors,
    }


def _load_public_data(data_root: Path) -> dict[str, Mapping[str, Any]]:
    data: dict[str, Mapping[str, Any]] = {}
    for name in PUBLIC_DATA_FILES:
        path = data_root / name
        payload = _load_json(path)
        if not isinstance(payload, Mapping):
            raise DemoGenerationError(f"{_display_path(path)} must contain a JSON object.")
        data[name] = payload
    return data


def _load_golden_inputs() -> dict[str, Mapping[str, Any]]:
    paths = {
        "plan_windows_7": GOLDEN_ROOT / "query_planner" / "windows_7_apps.json",
        "plan_firefox_xp": GOLDEN_ROOT / "query_planner" / "latest_firefox_before_xp_support_ended.json",
        "absence": GOLDEN_ROOT / "resolution_runs" / "exact_resolution_missing.json",
        "archive_search": GOLDEN_ROOT / "resolution_runs" / "deterministic_search_archive.json",
        "archive_eval": GOLDEN_ROOT / "archive_resolution_evals" / "full_report.json",
    }
    return {name: _load_json(path) for name, path in paths.items()}


def _build_demo_models(
    data: Mapping[str, Mapping[str, Any]],
    goldens: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    archive_eval = goldens["archive_eval"]
    tasks = archive_eval.get("tasks", [])
    if not isinstance(tasks, list):
        raise DemoGenerationError("archive eval golden must contain a tasks list.")

    windows_task = _task(tasks, "windows_7_apps")
    driver_task = _task(tasks, "driver_inside_support_cd")
    firefox_task = _task(tasks, "latest_firefox_before_xp_drop")
    article_task = _task(tasks, "article_inside_magazine_scan")

    plan = _mapping(_mapping(goldens["plan_windows_7"]).get("body")).get("query_plan")
    firefox_plan = _mapping(_mapping(goldens["plan_firefox_xp"]).get("body")).get("query_plan")
    absence_run = _first_run(goldens["absence"])
    absence = _mapping(absence_run.get("absence_report"))
    comparison_items = _comparison_items(goldens["archive_search"])
    source_summary = data["source_summary.json"]
    eval_summary = data["eval_summary.json"]

    return [
        _demo(
            "query-plan-windows-7-apps",
            "Query Plan: Windows 7 Apps",
            "query-plan-windows-7-apps.html",
            "Shows deterministic platform-scoped query interpretation and one source-backed local result.",
            ["query_planner/windows_7_apps.json", "archive_resolution_evals/full_report.json#windows_7_apps"],
            ["windows_7_apps"],
            [
                _kv("Raw query", _text(plan, "raw_query")),
                _kv("Task kind", _text(plan, "task_kind")),
                _kv("Object type", _text(plan, "object_type")),
                _kv("Planner confidence", _text(plan, "planner_confidence")),
                _kv("Platform as constraint", str(_mapping(plan.get("constraints")).get("platform_is_constraint"))),
                _kv("Platform", _text(_mapping(_mapping(plan.get("constraints")).get("platform")), "marketing_alias")),
                _kv("Prefer", ", ".join(_strings(plan.get("prefer")))),
                _kv("Exclude", ", ".join(_strings(plan.get("exclude")))),
            ],
            [
                "The planner treats Windows 7 as a compatibility constraint, not the requested object.",
                "The result count comes from the local fixture-backed archive eval golden.",
            ],
            [_result_summary(_first_result(windows_task), "Representative source-backed result")],
            related_links=[("Source summary JSON", "../data/source_summary.json")],
        ),
        _demo(
            "result-member-driver-inside-support-cd",
            "Member Result: Driver Inside Support CD",
            "result-member-driver-inside-support-cd.html",
            "Shows the smallest actionable unit inside a fixture support bundle.",
            ["archive_resolution_evals/full_report.json#driver_inside_support_cd"],
            ["driver_inside_support_cd"],
            [
                _kv("Raw query", _text(driver_task, "raw_query")),
                _kv("Search mode", _text(driver_task, "search_mode")),
                _kv("Observed results", str(driver_task.get("search_observed_result_count"))),
            ],
            [
                "The member target ref is synthetic and fixture-backed.",
                "Parent bundle lineage is preserved so the inner file does not lose context.",
            ],
            [_result_summary(_first_result(driver_task), "Primary member result")],
            related_links=[("Eval summary JSON", "../data/eval_summary.json")],
        ),
        _demo(
            "result-firefox-xp",
            "Result: Firefox XP Compatibility Evidence",
            "result-firefox-xp.html",
            "Shows latest-compatible planning with fixture-backed Firefox XP evidence.",
            [
                "query_planner/latest_firefox_before_xp_support_ended.json",
                "archive_resolution_evals/full_report.json#latest_firefox_before_xp_drop",
            ],
            ["latest_firefox_before_xp_drop"],
            [
                _kv("Raw query", _text(firefox_task, "raw_query")),
                _kv("Planner task", _text(firefox_plan, "task_kind")),
                _kv("Temporal goal", str(_mapping(firefox_plan.get("constraints")).get("temporal_goal"))),
                _kv("Support window hint", str(_mapping(firefox_plan.get("constraints")).get("support_window_hint"))),
            ],
            [
                "This is not a universal latest-version oracle.",
                "The page only demonstrates evidence present in the committed fixture corpus.",
            ],
            [_result_summary(_first_result(firefox_task), "Fixture-backed Firefox XP result")],
            related_links=[("Source summary JSON", "../data/source_summary.json")],
        ),
        _demo(
            "result-article-scan",
            "Result: Article Inside Scan Fixture",
            "result-article-scan.html",
            "Shows an article segment with parent issue lineage and page-range style evidence.",
            ["archive_resolution_evals/full_report.json#article_inside_magazine_scan"],
            ["article_inside_magazine_scan"],
            [
                _kv("Raw query", _text(article_task, "raw_query")),
                _kv("Planner task", _text(_mapping(article_task.get("planner_observed")), "task_kind")),
                _kv("Topic hint", str(_mapping(_mapping(article_task.get("planner_observed")).get("constraints")).get("topic_hint"))),
                _kv("Page/member preference", ", ".join(_strings(_mapping(article_task.get("planner_observed")).get("prefer")))),
            ],
            [
                "The article text is OCR-like synthetic fixture text.",
                "No real scan parsing, OCR engine, copyrighted article body, or live Internet Archive call is included.",
            ],
            [_result_summary(_first_result(article_task), "Article segment result")],
            related_links=[("Source summary JSON", "../data/source_summary.json")],
        ),
        _demo(
            "absence-example",
            "Absence Example: Missing Target",
            "absence-example.html",
            "Shows bounded absence reasoning for a target outside the committed corpus.",
            ["resolution_runs/exact_resolution_missing.json"],
            ["missing_synthetic_target_absence"],
            [
                _kv("Requested value", _text(absence, "requested_value")),
                _kv("Status", _text(absence, "status")),
                _kv("Reason code", _text(absence, "likely_reason_code")),
                _kv("Checked records", str(absence.get("checked_record_count"))),
                _kv("Checked subjects", str(absence.get("checked_subject_count"))),
                _kv("Checked source families", ", ".join(_strings(absence.get("checked_source_families")))),
            ],
            [
                _text(absence, "reason_message"),
                "This absence is bounded to the current local corpus and is not a global non-existence claim.",
            ],
            [_list_block("Next steps", _strings(absence.get("next_steps")))],
            related_links=[("Limitations", "../limitations.html")],
        ),
        _demo(
            "comparison-example",
            "Comparison Example: ArchiveBox Fixture Records",
            "comparison-example.html",
            "Shows side-by-side evidence without merging or truth selection.",
            ["resolution_runs/deterministic_search_archive.json"],
            ["archivebox_release_085"],
            [
                _kv("Comparison subject", "ArchiveBox-like records from deterministic search results"),
                _kv("Agreement", "Both sides are software records with source-backed ArchiveBox labels."),
                _kv("Disagreement", "Version labels, source family, source locator, and trust lane differ."),
            ],
            [
                "The comparison preserves disagreement instead of merging records.",
                "This is a static example, not a live compare route.",
            ],
            [
                _result_summary(comparison_items[0], "Left record"),
                _result_summary(comparison_items[1], "Right record"),
            ],
            related_links=[("Route summary JSON", "../data/route_summary.json")],
        ),
        _demo(
            "source-example",
            "Source Example: Fixture and Placeholder Honesty",
            "source-example.html",
            "Shows source coverage, capability metadata, and placeholder posture.",
            ["public_site/data/source_summary.json"],
            [],
            [
                _kv("Source count", str(source_summary.get("source_count"))),
                _kv("Contains live data", str(source_summary.get("contains_live_data"))),
                _kv("Contains live probes", str(source_summary.get("contains_live_probes"))),
            ],
            [
                "Active fixture-backed sources and future placeholder sources are intentionally separate.",
                "Placeholder sources do not imply implemented connectors.",
            ],
            [_source_table(source_summary)],
            related_links=[("Source summary JSON", "../data/source_summary.json")],
        ),
        _demo(
            "eval-summary",
            "Eval Summary Demo",
            "eval-summary.html",
            "Shows archive hard eval status, search usefulness counts, and pending manual baselines.",
            ["public_site/data/eval_summary.json", "archive_resolution_evals/full_report.json"],
            [],
            [
                _kv("Archive hard eval tasks", str(_mapping(eval_summary.get("archive_resolution")).get("task_count"))),
                _kv("Archive hard eval status counts", _json_inline(_mapping(eval_summary.get("archive_resolution")).get("status_counts"))),
                _kv("Search audit queries", str(_mapping(eval_summary.get("search_usefulness")).get("query_count"))),
                _kv("Search audit status counts", _json_inline(_mapping(eval_summary.get("search_usefulness")).get("status_counts"))),
                _kv("Manual baseline pending", str(_mapping(eval_summary.get("manual_external_baselines")).get("global_pending_count"))),
                _kv("Manual baseline observed", str(_mapping(eval_summary.get("manual_external_baselines")).get("global_observed_count"))),
            ],
            [
                "Archive hard eval satisfaction is local and fixture-backed.",
                "Manual external baselines remain pending until a human records observations.",
            ],
            [_eval_task_table(archive_eval)],
            related_links=[("Eval summary JSON", "../data/eval_summary.json")],
        ),
    ]


def _demo(
    demo_id: str,
    title: str,
    page: str,
    summary: str,
    source_data: list[str],
    related_query_ids: list[str],
    facts: list[Mapping[str, str]],
    limitations: list[str],
    blocks: list[str],
    *,
    related_links: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    return {
        "id": demo_id,
        "title": title,
        "page": page,
        "status": "static_demo",
        "stability": "stable_draft",
        "summary": summary,
        "source_data": source_data,
        "fixture_backed": True,
        "live_backend_required": False,
        "external_observation_required": False,
        "limitations": [
            "Static demo snapshot.",
            "Fixture-backed.",
            "Not live search.",
            "Not production.",
            *limitations,
        ],
        "related_query_ids": related_query_ids,
        "facts": facts,
        "blocks": blocks,
        "related_links": related_links or [],
    }


def _build_demo_manifest(demos: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "demo_count": len(demos),
        "demos": [
            {
                "id": demo["id"],
                "title": demo["title"],
                "page": f"/demo/{demo['page']}",
                "status": demo["status"],
                "stability": demo["stability"],
                "source_data": demo["source_data"],
                "fixture_backed": demo["fixture_backed"],
                "live_backend_required": False,
                "external_observation_required": False,
                "limitations": demo["limitations"],
                "related_query_ids": demo["related_query_ids"],
            }
            for demo in demos
        ],
        "no_live_backend": True,
        "no_external_observations": True,
        "no_deployment_claim": True,
        "contains_live_data": False,
        "contains_live_probes": False,
        "source_inputs": [
            "tests/parity/golden/python_oracle/v0/query_planner/*.json",
            "tests/parity/golden/python_oracle/v0/resolution_runs/*.json",
            "tests/parity/golden/python_oracle/v0/archive_resolution_evals/full_report.json",
            "public_site/data/*.json",
        ],
    }


def _render_index(demos: Sequence[Mapping[str, Any]]) -> str:
    items = "\n".join(
        f'      <li><a href="{escape(str(demo["page"]))}">{escape(str(demo["title"]))}</a>: {escape(str(demo["summary"]))}</li>'
        for demo in demos
    )
    body = [
        "<p>These are static resolver demo snapshots generated from committed Python-oracle fixture outputs and public data summaries.</p>",
        "<p>They are not live search, not a live API, not backend hosting, and not production.</p>",
        "<p>The reserved /api/v1 route family belongs to future live backend handoff work and is not live from these demo pages.</p>",
        "<ul>",
        items,
        "</ul>",
        '<p>Machine-readable demo data: <a href="data/demo_snapshots.json">data/demo_snapshots.json</a></p>',
    ]
    return _html_page("Static Resolver Demo Snapshots", "Static Resolver Demo Snapshots", body, current="index.html")


def _render_demo_page(demo: Mapping[str, Any]) -> str:
    facts = "\n".join(
        f"      <dt>{escape(str(item['label']))}</dt><dd>{escape(str(item['value']))}</dd>"
        for item in demo["facts"]
    )
    sources = "\n".join(f"      <li>{escape(str(source))}</li>" for source in demo["source_data"])
    limitations = "\n".join(f"      <li>{escape(str(item))}</li>" for item in demo["limitations"])
    links = "\n".join(
        f'      <li><a href="{escape(href)}">{escape(label)}</a></li>'
        for label, href in demo["related_links"]
    )
    blocks = "\n".join(str(block) for block in demo["blocks"])
    body = [
        "<p><strong>Static demo snapshot.</strong> Fixture-backed. Not live search. Not production.</p>",
        f"<p>{escape(str(demo['summary']))}</p>",
        "<h2>Snapshot Facts</h2>",
        "    <dl>",
        facts,
        "    </dl>",
        "<h2>Details</h2>",
        blocks,
        "<h2>Source Data</h2>",
        "    <ul>",
        sources,
        "    </ul>",
        "<h2>Limitations</h2>",
        "    <ul>",
        limitations,
        "    </ul>",
        "<h2>Related Static Data</h2>",
        "    <ul>",
        links or '      <li><a href="data/demo_snapshots.json">Demo snapshot data</a></li>',
        '      <li><a href="../limitations.html">Public limitations</a></li>',
        "    </ul>",
    ]
    return _html_page(str(demo["title"]), str(demo["title"]), body, current=str(demo["page"]))


def _html_page(title: str, heading: str, body: Sequence[str], *, current: str) -> str:
    nav = [
        ("index.html", "Demo index"),
        ("query-plan-windows-7-apps.html", "Query plan"),
        ("result-member-driver-inside-support-cd.html", "Member result"),
        ("result-firefox-xp.html", "Firefox XP"),
        ("result-article-scan.html", "Article scan"),
        ("absence-example.html", "Absence"),
        ("comparison-example.html", "Comparison"),
        ("source-example.html", "Source"),
        ("eval-summary.html", "Evals"),
        ("../index.html", "Main site"),
    ]
    nav_html = "\n".join(
        f'      <a href="{escape(href)}">{escape(label)}</a>'
        for href, label in nav
        if href != current
    )
    html = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        f"  <title>{escape(title)}</title>",
        "</head>",
        "<body>",
        "  <header>",
        f"    <h1>{escape(heading)}</h1>",
        "    <nav>",
        nav_html,
        "    </nav>",
        "  </header>",
        "  <main>",
        *body,
        "  </main>",
        "  <footer>",
        "    Static demo snapshot. Fixture-backed. Not live search. Not production. No live backend, live probes, or external observations are included.",
        "  </footer>",
        "</body>",
        "</html>",
        "",
    ]
    return "\n".join(line.rstrip() for line in html)


def _readme_text(demos: Sequence[Mapping[str, Any]]) -> str:
    lines = [
        "Eureka Static Resolver Demo Snapshots",
        "",
        "These files are generated static publication examples.",
        "They are not live search, not a live API, not backend hosting, and not production.",
        "The reserved /api/v1 route family is future handoff contract only and is not live here.",
        "",
        "Pages:",
    ]
    lines.extend(f"- {demo['page']}: {demo['title']}" for demo in demos)
    lines.extend(
        [
            "",
            "Machine-readable data: data/demo_snapshots.json",
            "",
        ]
    )
    return "\n".join(lines)


def _result_summary(result: Mapping[str, Any], heading: str) -> str:
    fields = [
        ("Label", result.get("label")),
        ("Record kind", result.get("record_kind")),
        ("Target ref", result.get("target_ref")),
        ("Member path", result.get("member_path")),
        ("Parent target ref", result.get("parent_target_ref")),
        ("Parent object", result.get("parent_object_label")),
        ("Source id", result.get("source_id")),
        ("Source family", result.get("source_family")),
        ("Primary lane", result.get("primary_lane")),
        ("Result lanes", ", ".join(_strings(result.get("result_lanes")))),
        ("User cost", result.get("user_cost_score")),
        ("User-cost reasons", ", ".join(_strings(result.get("user_cost_reasons")))),
        ("Usefulness", result.get("usefulness_summary")),
        ("Compatibility", result.get("compatibility_summary")),
        ("Summary", result.get("summary")),
    ]
    rows = "\n".join(
        f"      <dt>{escape(label)}</dt><dd>{escape(str(value))}</dd>"
        for label, value in fields
        if value not in (None, "", [])
    )
    evidence = _evidence_lines(result)
    evidence_html = "\n".join(f"      <li>{escape(line)}</li>" for line in evidence[:6])
    return "\n".join(
        [
            f"    <section><h3>{escape(heading)}</h3>",
            "    <dl>",
            rows,
            "    </dl>",
            "    <h4>Evidence Summary</h4>",
            "    <ul>",
            evidence_html or "      <li>No compact evidence summary available in this snapshot.</li>",
            "    </ul></section>",
        ]
    )


def _list_block(title: str, values: Sequence[str]) -> str:
    items = "\n".join(f"      <li>{escape(value)}</li>" for value in values)
    return "\n".join([f"    <section><h3>{escape(title)}</h3>", "    <ul>", items, "    </ul></section>"])


def _source_table(source_summary: Mapping[str, Any]) -> str:
    rows = []
    for source in source_summary.get("sources", []):
        if not isinstance(source, Mapping):
            continue
        if source.get("source_id") not in {
            "local-bundle-fixtures",
            "article-scan-recorded-fixtures",
            "internet-archive-placeholder",
        }:
            continue
        rows.append(
            [
                str(source.get("source_id")),
                str(source.get("label")),
                str(source.get("status")),
                str(source.get("coverage_depth")),
                str(source.get("placeholder")),
                str(source.get("live_supported")),
                str(source.get("posture")),
            ]
        )
    return _table(
        ["source_id", "label", "status", "coverage", "placeholder", "live_supported", "posture"],
        rows,
    )


def _eval_task_table(archive_eval: Mapping[str, Any]) -> str:
    rows = []
    for task in archive_eval.get("task_summaries", []):
        if not isinstance(task, Mapping):
            continue
        rows.append(
            [
                str(task.get("task_id")),
                str(task.get("overall_status")),
                str(task.get("planner_observed_task_kind")),
                str(task.get("search_observed_result_count")),
            ]
        )
    return _table(["task_id", "status", "planner", "results"], rows)


def _table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    head = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body = "\n".join(
        "      <tr>" + "".join(f"<td>{escape(value)}</td>" for value in row) + "</tr>"
        for row in rows
    )
    return "\n".join(["    <table>", f"      <tr>{head}</tr>", body, "    </table>"])


def _kv(label: str, value: str) -> dict[str, str]:
    return {"label": label, "value": value}


def _first_result(task: Mapping[str, Any]) -> Mapping[str, Any]:
    results = task.get("top_results")
    if not isinstance(results, list) or not results or not isinstance(results[0], Mapping):
        raise DemoGenerationError(f"task {task.get('task_id')} does not have a first top result.")
    return results[0]


def _first_run(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    runs = _mapping(payload.get("body")).get("runs")
    if not isinstance(runs, list) or not runs or not isinstance(runs[0], Mapping):
        raise DemoGenerationError("golden run payload does not contain a first run.")
    return runs[0]


def _comparison_items(payload: Mapping[str, Any]) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    items = _mapping(_first_run(payload).get("result_summary")).get("items")
    if not isinstance(items, list):
        raise DemoGenerationError("comparison search golden does not contain result items.")
    synthetic = None
    github = None
    for item in items:
        if not isinstance(item, Mapping):
            continue
        obj = _mapping(item.get("object"))
        source = _mapping(item.get("source"))
        flattened = {
            **obj,
            "source_id": source.get("source_id"),
            "source_family": source.get("family"),
            "source_label": source.get("label"),
            "target_ref": item.get("target_ref"),
            "resolved_resource_id": item.get("resolved_resource_id"),
            "record_kind": obj.get("kind"),
        }
        label = str(obj.get("label", ""))
        if synthetic is None and label == "ArchiveBox 0.8.5":
            synthetic = flattened
        if github is None and label == "ArchiveBox v0.8.5":
            github = flattened
    if synthetic is None or github is None:
        raise DemoGenerationError("could not find ArchiveBox comparison pair in deterministic search golden.")
    return synthetic, github


def _task(tasks: Sequence[Any], task_id: str) -> Mapping[str, Any]:
    for task in tasks:
        if isinstance(task, Mapping) and task.get("task_id") == task_id:
            return task
    raise DemoGenerationError(f"archive eval task missing: {task_id}")


def _evidence_lines(result: Mapping[str, Any]) -> list[str]:
    lines: list[str] = []
    evidence = result.get("evidence")
    if isinstance(evidence, list):
        for item in evidence:
            if isinstance(item, Mapping):
                claim = item.get("claim_kind")
                value = item.get("claim_value")
                source = item.get("asserted_by_label") or item.get("asserted_by_family")
                if claim and value:
                    lines.append(f"{claim}: {value} ({source})")
            elif isinstance(item, str):
                lines.append(item)
    compat = result.get("compatibility_evidence")
    if isinstance(compat, list):
        for item in compat[:3]:
            if isinstance(item, Mapping):
                text = item.get("evidence_text") or item.get("claim_type")
                source = item.get("source_label") or item.get("source_id")
                if text:
                    lines.append(f"compatibility evidence: {text} ({source})")
    return lines


def _resolve_data_root(output_root: Path, requested: str | None) -> Path:
    if requested:
        return Path(requested).resolve()
    output_data = output_root.resolve() / "data"
    if output_data.exists():
        return output_data
    return DEFAULT_DATA_ROOT.resolve()


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DemoGenerationError(f"missing input file: {_display_path(path)}") from exc
    except json.JSONDecodeError as exc:
        raise DemoGenerationError(f"invalid JSON in {_display_path(path)}: {exc}") from exc


def _json_text(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _json_inline(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _text(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    return "" if value is None else str(value)


def _summary_report(
    output_root: Path,
    data_root: Path,
    files: Mapping[str, str],
    *,
    updated: bool,
) -> dict[str, Any]:
    return {
        "status": "valid",
        "created_by": SLICE_ID,
        "generated_by": GENERATED_BY,
        "output_root": _display_path(output_root),
        "data_root": _display_path(data_root),
        "demo_root": _display_path(output_root / "demo"),
        "files": sorted(files),
        "file_count": len(files),
        "demo_count": len([name for name in files if name.startswith("demo/") and name.endswith(".html")]) - 1,
        "contains_live_backend": False,
        "contains_live_probes": False,
        "contains_external_observations": False,
        "updated": updated,
        "errors": [],
    }


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Static resolver demo snapshot generation",
        f"status: {report.get('status')}",
        f"output_root: {report.get('output_root', '<unknown>')}",
        f"demo_count: {report.get('demo_count', '<unknown>')}",
    ]
    if report.get("check_mode"):
        lines.append("check_mode: true")
    errors = report.get("errors") or []
    if errors:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in errors)
    return "\n".join(lines) + "\n"


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
