from __future__ import annotations

import argparse
import hashlib
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

SCHEMA_VERSION = "0.1.0"
GENERATED_BY = "scripts/generate_compatibility_surfaces.py"
SLICE_ID = "lite_text_files_seed_surfaces_v0"
SURFACE_DIRS = ("lite", "text", "files")
PUBLIC_DATA_FILES = (
    "site_manifest.json",
    "page_registry.json",
    "source_summary.json",
    "eval_summary.json",
    "route_summary.json",
    "build_manifest.json",
)
CHECKSUM_PATHS = (
    "data/site_manifest.json",
    "data/page_registry.json",
    "data/source_summary.json",
    "data/eval_summary.json",
    "data/route_summary.json",
    "data/build_manifest.json",
    "files/manifest.json",
    "files/index.txt",
    "files/README.txt",
)
DEMO_QUERIES = (
    "Windows 7 apps",
    "latest Firefox before XP support ended",
    "old blue FTP client for XP",
    "Windows 98 registry repair",
    "driver inside support CD",
    "driver for ThinkPad T42 Wi-Fi Windows 2000",
    "PC Magazine July 1994 ray tracing",
    "Mac OS 9 browser",
    "PowerPC Mac OS X 10.4 browser",
    "Creative CT1740 driver Windows 98",
    "3Com 3C905 Windows 95 driver",
)


class CompatibilitySurfaceError(RuntimeError):
    pass


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate static lite/text/files compatibility surfaces."
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Static artifact root that receives lite/, text/, and files/.",
    )
    parser.add_argument(
        "--data-root",
        default=None,
        help="Directory containing generated public data JSON. Defaults to <output-root>/data when present, otherwise public_site/data.",
    )
    parser.add_argument("--update", action="store_true", help="Write generated surfaces.")
    parser.add_argument("--check", action="store_true", help="Verify committed surfaces match generated output.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    output = stdout or sys.stdout
    output_root = Path(args.output_root)
    data_root = _resolve_data_root(output_root, args.data_root)

    try:
        if args.check:
            report = check_compatibility_surfaces(output_root, data_root)
        elif args.update:
            report = write_compatibility_surfaces(output_root, data_root)
        else:
            files = generate_compatibility_surfaces(data_root)
            report = _summary_report(output_root, data_root, files, updated=False)
        if args.json:
            output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        else:
            output.write(_format_plain(report))
        return 0 if report["status"] == "valid" else 1
    except CompatibilitySurfaceError as exc:
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


def generate_compatibility_surfaces(data_root: Path = DEFAULT_DATA_ROOT) -> dict[str, str]:
    data = _load_public_data(data_root)
    files: dict[str, str] = {}

    files.update(_build_lite_surface(data))
    files.update(_build_text_surface(data))
    files.update(_build_files_surface(data))
    files["files/SHA256SUMS"] = _build_sha256sums(files, data_root)
    return files


def write_compatibility_surfaces(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    data_root: Path | None = None,
) -> dict[str, Any]:
    output_root = output_root.resolve()
    data_root = _resolve_data_root(output_root, str(data_root) if data_root else None)
    files = generate_compatibility_surfaces(data_root)
    _clean_surface_dirs(output_root)
    for relative, text in files.items():
        path = output_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    return _summary_report(output_root, data_root, files, updated=True)


def check_compatibility_surfaces(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    data_root: Path | None = None,
) -> dict[str, Any]:
    output_root = output_root.resolve()
    data_root = _resolve_data_root(output_root, str(data_root) if data_root else None)
    files = generate_compatibility_surfaces(data_root)
    errors: list[str] = []
    for relative, expected in sorted(files.items()):
        path = output_root / relative
        if not path.exists():
            errors.append(f"{_display_path(path)}: generated compatibility file is missing.")
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            errors.append(f"{_display_path(path)}: generated compatibility file is stale.")
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
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise CompatibilitySurfaceError(f"missing public data file: {_display_path(path)}") from exc
        except json.JSONDecodeError as exc:
            raise CompatibilitySurfaceError(f"invalid public data file {_display_path(path)}: {exc}") from exc
        if not isinstance(payload, Mapping):
            raise CompatibilitySurfaceError(f"{_display_path(path)} must contain a JSON object.")
        data[name] = payload
    return data


def _build_lite_surface(data: Mapping[str, Mapping[str, Any]]) -> dict[str, str]:
    site = data["site_manifest.json"]
    source = data["source_summary.json"]
    evals = data["eval_summary.json"]
    route = data["route_summary.json"]
    sources = list(source.get("sources", []))

    index_body = [
        "<p>This is Eureka's lite static surface for old and low-capability browsers. It is a set of fixed pages generated from public data summaries.</p>",
        "<ul>",
        '<li><a href="sources.html">Lite source summary</a></li>',
        '<li><a href="evals.html">Lite eval summary</a></li>',
        '<li><a href="demo-queries.html">Lite demo query list</a></li>',
        '<li><a href="limitations.html">Lite limitations</a></li>',
        '<li><a href="../text/index.txt">Plain text surface</a></li>',
        '<li><a href="../files/index.html">Static files surface</a></li>',
        '<li><a href="../demo/index.html">Static resolver demos</a></li>',
        "</ul>",
        "<h2>Current static status</h2>",
        "<ul>",
        f"<li>Source records summarized: {escape(str(source.get('source_count', 'unknown')))}</li>",
        f"<li>Archive hard eval tasks: {escape(str(_mapping(evals.get('archive_resolution')).get('task_count', 'unknown')))}</li>",
        f"<li>Search audit queries: {escape(str(_mapping(evals.get('search_usefulness')).get('query_count', 'unknown')))}</li>",
        f"<li>Public-alpha routes summarized: {escape(str(_mapping(route.get('route_counts')).get('total', 'unknown')))}</li>",
        f"<li>Future live backend endpoints reserved: {escape(str(_mapping(site.get('live_backend_handoff')).get('reserved_endpoint_count', 0)))}</li>",
        "</ul>",
        "<p>The reserved /api/v1 route family is not live in this static artifact.</p>",
        "<p>Machine-readable summaries: <a href=\"../data/site_manifest.json\">site</a>, <a href=\"../data/source_summary.json\">sources</a>, <a href=\"../data/eval_summary.json\">evals</a>, <a href=\"../data/route_summary.json\">routes</a>.</p>",
    ]

    source_rows = []
    for item in sources:
        if not isinstance(item, Mapping):
            continue
        source_rows.append(
            [
                str(item.get("source_id", "")),
                str(item.get("label", "")),
                str(item.get("status", "")),
                str(item.get("coverage_depth", "")),
                str(item.get("posture", "")),
            ]
        )
    sources_body = [
        "<p>Source records come from the static source summary. Placeholder records remain placeholders and live probes remain disabled.</p>",
        _simple_table(["source_id", "label", "status", "coverage", "posture"], source_rows),
        '<p>Machine-readable summary: <a href="../data/source_summary.json">../data/source_summary.json</a></p>',
    ]

    archive = _mapping(evals.get("archive_resolution"))
    search = _mapping(evals.get("search_usefulness"))
    baselines = _mapping(evals.get("manual_external_baselines"))
    eval_body = [
        "<p>These are local deterministic summaries, not production benchmarks.</p>",
        "<ul>",
        f"<li>Archive hard eval tasks: {escape(str(archive.get('task_count', 'unknown')))}</li>",
        f"<li>Archive satisfied count: {escape(str(_mapping(archive.get('status_counts')).get('satisfied', 'unknown')))}</li>",
        f"<li>Search audit queries: {escape(str(search.get('query_count', 'unknown')))}</li>",
        f"<li>Search status counts: {escape(_status_counts(_mapping(search.get('status_counts'))))}</li>",
        f"<li>Manual external baseline slots pending: {escape(str(baselines.get('global_pending_count', 'unknown')))}</li>",
        f"<li>Manual external baseline observations recorded: {escape(str(baselines.get('global_observed_count', 'unknown')))}</li>",
        "</ul>",
        '<p>Machine-readable summary: <a href="../data/eval_summary.json">../data/eval_summary.json</a></p>',
    ]

    demo_body = [
        "<p>These are example local prototype queries only. They are not links to live hosted search.</p>",
        "<ul>",
        *(f"<li>{escape(query)}</li>" for query in DEMO_QUERIES),
        "</ul>",
        '<p>Standard page: <a href="../demo-queries.html">../demo-queries.html</a></p>',
    ]

    limitations = list(site.get("limitations", []))
    limitations_body = [
        "<p>The lite surface is static. It does not search, crawl, probe, download, authenticate, or execute code.</p>",
        "<ul>",
        *(f"<li>{escape(str(item))}</li>" for item in limitations),
        "<li>No public executable downloads or mirrors are provided by this seed surface.</li>",
        "<li>Snapshots, relay behavior, native clients, and live APIs remain future work.</li>",
        "<li>/api/v1 is reserved by contract only and is not a live backend on the static site.</li>",
        "</ul>",
    ]

    readme = "\n".join(
        [
            "Eureka lite surface",
            "===================",
            "",
            "Static old-browser HTML seed surface generated from public data summaries.",
            "No JavaScript, no live search, no live probes, and no executable downloads.",
            "",
            "Start with index.html.",
        ]
    ) + "\n"

    return {
        "lite/index.html": _lite_html("Eureka Lite", "Eureka Lite Surface", index_body),
        "lite/sources.html": _lite_html("Eureka Lite Sources", "Lite Source Summary", sources_body),
        "lite/evals.html": _lite_html("Eureka Lite Evals", "Lite Eval Summary", eval_body),
        "lite/demo-queries.html": _lite_html("Eureka Lite Demo Queries", "Lite Demo Queries", demo_body),
        "lite/limitations.html": _lite_html("Eureka Lite Limitations", "Lite Limitations", limitations_body),
        "lite/README.txt": readme,
    }


def _build_text_surface(data: Mapping[str, Mapping[str, Any]]) -> dict[str, str]:
    source = data["source_summary.json"]
    evals = data["eval_summary.json"]
    route = data["route_summary.json"]
    build = data["build_manifest.json"]
    sources = [item for item in source.get("sources", []) if isinstance(item, Mapping)]
    archive = _mapping(evals.get("archive_resolution"))
    search = _mapping(evals.get("search_usefulness"))
    baselines = _mapping(evals.get("manual_external_baselines"))

    index = _text_page(
        "Eureka Text Surface",
        [
            "Eureka is a Python reference backend prototype, not production.",
            "This is a plain-text static seed surface generated from public data summaries.",
            "It is not command-line interactivity and it is not live search.",
            "The /api/v1 route family is reserved for future live backend handoff only; it is not live here.",
            "",
            "Files:",
            "- sources.txt",
            "- evals.txt",
            "- demo-queries.txt",
            "- limitations.txt",
            "- ../files/index.txt",
            "- ../demo/index.html",
            "",
            "Machine-readable data:",
            "- ../data/site_manifest.json",
            "- ../data/source_summary.json",
            "- ../data/eval_summary.json",
            "- ../data/route_summary.json",
        ],
    )
    source_lines = [
        f"source_count: {source.get('source_count', 'unknown')}",
        "",
    ]
    for item in sources:
        source_lines.append(
            f"- {item.get('source_id')}: {item.get('status')} / {item.get('posture')} / {item.get('coverage_depth')}"
        )
    source_lines.extend(
        [
            "",
            "Placeholders remain placeholders. No live source probes are enabled.",
            "No live search is performed by this static text file.",
            "machine_readable: ../data/source_summary.json",
        ]
    )
    eval_lines = [
        f"archive_task_count: {archive.get('task_count', 'unknown')}",
        f"archive_status_counts: {_status_counts(_mapping(archive.get('status_counts')))}",
        f"search_query_count: {search.get('query_count', 'unknown')}",
        f"search_status_counts: {_status_counts(_mapping(search.get('status_counts')))}",
        f"manual_external_baselines_pending: {baselines.get('global_pending_count', 'unknown')}",
        f"manual_external_baselines_observed: {baselines.get('global_observed_count', 'unknown')}",
        "",
        "No live search is performed by this static text file.",
        "External observations remain manual and pending unless human evidence is committed.",
        "machine_readable: ../data/eval_summary.json",
    ]
    demo_lines = [
        "Demo queries are examples for local prototype behavior only.",
        "They do not invoke live hosted search.",
        "No live search is performed by this static text file.",
        "Static demo snapshots: ../demo/index.html",
        "",
        *(f"- {query}" for query in DEMO_QUERIES),
    ]
    limitation_lines = [
        "Limitations:",
        "- not production",
        "- no live search",
        "- no live source probes",
        "- /api/v1 reserved only, not live",
        "- no scraping",
        "- no executable downloads or mirrors",
        "- no snapshots yet",
        "- no relay or native-client runtime behavior",
        "- public JSON remains pre-alpha stable_draft, not a production API",
        "",
        f"route_count_summarized: {_mapping(route.get('route_counts')).get('total', 'unknown')}",
        f"build_source: {build.get('source', 'unknown')}",
    ]
    readme = _text_page(
        "README",
        [
            "Plain text static files for text browsers, terminals, screen readers, and simple automation.",
            "These files are generated from public_site/data summaries.",
            "No live search, live backend, live probes, external observations, or downloads are added.",
        ],
    )
    return {
        "text/index.txt": index,
        "text/sources.txt": _text_page("Sources", source_lines),
        "text/evals.txt": _text_page("Evals", eval_lines),
        "text/demo-queries.txt": _text_page("Demo Queries", demo_lines),
        "text/limitations.txt": _text_page("Limitations", limitation_lines),
        "text/README.txt": readme,
    }


def _build_files_surface(data: Mapping[str, Mapping[str, Any]]) -> dict[str, str]:
    evals = data["eval_summary.json"]
    baselines = _mapping(evals.get("manual_external_baselines"))
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "surface_id": "eureka-files-seed",
        "status": "static_demo",
        "stability": "stable_draft",
        "artifact_root": "public_site",
        "surface_root": "public_site/files",
        "contains_live_backend": False,
        "contains_live_probes": False,
        "contains_live_data": False,
        "contains_external_observations": False,
        "contains_executable_downloads": False,
        "downloads_available": False,
        "checksum_file": "files/SHA256SUMS",
        "public_data_files": [f"data/{name}" for name in PUBLIC_DATA_FILES],
        "files": [
            "files/index.html",
            "files/index.txt",
            "files/README.txt",
            "files/manifest.json",
            "files/SHA256SUMS",
            "files/data/README.txt",
            "demo/index.html",
            "demo/data/demo_snapshots.json",
        ],
        "manual_external_baselines": {
            "global_pending_count": baselines.get("global_pending_count", 0),
            "global_observed_count": baselines.get("global_observed_count", 0),
        },
        "source_inputs": [
            "public_site/data/site_manifest.json",
            "public_site/data/page_registry.json",
            "public_site/data/source_summary.json",
            "public_site/data/eval_summary.json",
            "public_site/data/route_summary.json",
            "public_site/data/build_manifest.json",
        ],
        "limitations": [
            "Static file-tree seed surface only.",
            "No executable downloads, mirrors, snapshots, relay runtime, or native-client runtime behavior.",
            "Future download or snapshot surfaces require rights and security policy first.",
        ],
    }
    manifest_text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    index_txt = _text_page(
        "Eureka Files Surface",
        [
            "Static file-tree seed surface.",
            "No public executable downloads are present in v0.",
            "No live backend, live probes, crawling, scraping, or external observations are included.",
            "The /api/v1 route family is reserved for future backend handoff only and is not live.",
            "",
            "Public data summaries:",
            *(f"- ../data/{name}" for name in PUBLIC_DATA_FILES),
            "",
            "Files:",
            "- manifest.json",
            "- SHA256SUMS",
            "- README.txt",
            "- data/README.txt",
            "- ../demo/index.html",
            "- ../demo/data/demo_snapshots.json",
            "",
            "Future files, snapshots, or downloads require rights and security policy first.",
        ],
    )
    readme = _text_page(
        "README",
        [
            "This directory is a static file-tree seed surface.",
            "It contains manifests and checksums for public data summaries.",
            "It does not contain software downloads, executable mirrors, private stores, or live source output.",
            "It does not expose a live /api/v1 backend.",
        ],
    )
    data_readme = _text_page(
        "Data README",
        [
            "The public data files are stored at ../data/ from this directory's parent artifact root.",
            "This subdirectory is only an explanatory placeholder for file-tree readers.",
            "Use ../../data/*.json from files/data/ or ../data/*.json from files/.",
        ],
    )
    index_html = _lite_html(
        "Eureka Files",
        "Eureka Files Surface",
        [
            "<p>This is a static file-tree seed surface. It contains manifests, checksums, and links to public data summaries.</p>",
            "<p>No public executable downloads, mirrors, snapshots, live backend calls, or live source probes are provided in v0.</p>",
            "<p>The reserved /api/v1 route family is contract-only and not live on this static surface.</p>",
            "<ul>",
            '<li><a href="index.txt">index.txt</a></li>',
            '<li><a href="manifest.json">manifest.json</a></li>',
            '<li><a href="SHA256SUMS">SHA256SUMS</a></li>',
            '<li><a href="README.txt">README.txt</a></li>',
            '<li><a href="data/README.txt">data/README.txt</a></li>',
            '<li><a href="../data/site_manifest.json">../data/site_manifest.json</a></li>',
            '<li><a href="../data/source_summary.json">../data/source_summary.json</a></li>',
            '<li><a href="../demo/index.html">Static resolver demos</a></li>',
            '<li><a href="../demo/data/demo_snapshots.json">Demo snapshot data</a></li>',
            '<li><a href="../lite/index.html">Lite surface</a></li>',
            '<li><a href="../text/index.txt">Text surface</a></li>',
            "</ul>",
        ],
        nav_prefix="../",
    )
    return {
        "files/index.html": index_html,
        "files/index.txt": index_txt,
        "files/README.txt": readme,
        "files/manifest.json": manifest_text,
        "files/data/README.txt": data_readme,
    }


def _build_sha256sums(files: Mapping[str, str], data_root: Path) -> str:
    lines: list[str] = []
    for relative in CHECKSUM_PATHS:
        if relative.startswith("data/"):
            content = (data_root / relative.removeprefix("data/")).read_bytes()
        else:
            content = files[relative].encode("utf-8")
        digest = hashlib.sha256(content).hexdigest()
        lines.append(f"{digest}  {relative}")
    return "\n".join(lines) + "\n"


def _lite_html(
    title: str,
    heading: str,
    body_lines: Sequence[str],
    *,
    nav_prefix: str = "",
) -> str:
    if nav_prefix:
        nav_targets = (
            ("index.html", "Overview"),
            ("status.html", "Status"),
            ("sources.html", "Sources"),
            ("evals.html", "Evals"),
            ("demo-queries.html", "Demo Queries"),
            ("limitations.html", "Limitations"),
            ("roadmap.html", "Roadmap"),
        )
    else:
        nav_targets = (
            ("index.html", "Lite Overview"),
            ("sources.html", "Sources"),
            ("evals.html", "Evals"),
            ("demo-queries.html", "Demo Queries"),
            ("limitations.html", "Limitations"),
        )
    nav = "\n".join(
        f'    <a href="{nav_prefix}{href}">{label}</a>' for href, label in nav_targets
    )
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            f"  <title>{escape(title)}</title>",
            "</head>",
            "<body>",
            f"  <h1>{escape(heading)}</h1>",
            "  <p><strong>Static seed surface.</strong> No JavaScript, no live search, no live source probes, no downloads.</p>",
            "  <nav>",
            nav,
            "  </nav>",
            "  <hr>",
            *body_lines,
            "  <hr>",
            "  <p>Eureka is a Python reference backend prototype, not production. This surface uses no scraping, performs no live source probes, and makes no external search calls. external baselines pending/manual; source placeholders remain placeholders.</p>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _simple_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    header_html = "".join(f"<th>{escape(header)}</th>" for header in headers)
    row_html = []
    for row in rows:
        cells = "".join(f"<td>{escape(cell)}</td>" for cell in row)
        row_html.append(f"<tr>{cells}</tr>")
    return "<table border=\"1\"><thead><tr>" + header_html + "</tr></thead><tbody>" + "".join(row_html) + "</tbody></table>"


def _text_page(title: str, lines: Sequence[str]) -> str:
    underline = "=" * len(title)
    return "\n".join([title, underline, "", *lines, ""]) + "\n"


def _status_counts(counts: Mapping[str, Any]) -> str:
    if not counts:
        return "unknown"
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def _clean_surface_dirs(output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    for name in SURFACE_DIRS:
        path = output_root / name
        if path.exists() and path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()


def _resolve_data_root(output_root: Path, data_root: str | None) -> Path:
    if data_root:
        return Path(data_root).resolve()
    candidate = output_root.resolve() / "data"
    if candidate.exists():
        return candidate
    return DEFAULT_DATA_ROOT.resolve()


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
        "surface_roots": list(SURFACE_DIRS),
        "files": sorted(files),
        "file_count": len(files),
        "checksum_paths": list(CHECKSUM_PATHS),
        "contains_live_backend": False,
        "contains_live_probes": False,
        "contains_external_observations": False,
        "contains_executable_downloads": False,
        "updated": updated,
        "errors": [],
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Compatibility surface generation",
        f"status: {report['status']}",
        f"output_root: {report.get('output_root', 'public_site')}",
        f"surface_roots: {', '.join(report.get('surface_roots', []))}",
    ]
    if report.get("check_mode"):
        lines.append("check_mode: true")
    if report.get("file_count") is not None:
        lines.append(f"files: {report['file_count']}")
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
