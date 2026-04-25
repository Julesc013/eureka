from __future__ import annotations

import argparse
from copy import deepcopy
import filecmp
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
DEFAULT_OUTPUT_ROOT = (
    REPO_ROOT / "tests" / "parity" / "golden" / "python_oracle" / "v0"
)
CREATED_BY_SLICE = "rust_parity_fixture_pack_v0"
FIXTURE_PACK_ID = "python_oracle_golden_v0"
FIXTURE_PACK_VERSION = "0.1.0"
DETERMINISTIC_PLACEHOLDER = "<DETERMINISTIC_PLACEHOLDER>"
COMMIT_PLACEHOLDER = "<GENERATED_FROM_COMMIT>"
TIMESTAMP_PLACEHOLDER = "<PYTHON_ORACLE_TIMESTAMP>"
LOCAL_INDEX_PATH_PLACEHOLDER = "<PYTHON_ORACLE_LOCAL_INDEX_PATH>"
FTS_MODE_PLACEHOLDER = "<PYTHON_ORACLE_FTS_MODE_NORMALIZED>"


QUERY_PLANNER_FIXTURES = {
    "windows_7_apps": "Windows 7 apps",
    "latest_firefox_before_xp_support_ended": "latest Firefox before XP support ended",
    "old_blue_ftp_client_xp": "old blue FTP client for XP",
    "driver_thinkpad_t42_wifi_windows_2000": "ThinkPad T42 wifi driver Windows 2000",
    "article_ray_tracing_1994_magazine": "article about ray tracing in 1994 magazine",
    "generic_unknown_query": "obscure utility with no known fixture",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate stable Python-oracle golden outputs for future Rust parity.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Directory where the Python-oracle v0 fixture pack should be written.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Regenerate into a temporary directory and compare with committed golden files.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON summary.",
    )
    args = parser.parse_args(argv)

    output_root = Path(args.output_root)
    if args.check:
        return _run_check(output_root, emit_json=args.json)

    written_files = generate_fixture_pack(output_root)
    summary = _summary("generated", output_root, written_files)
    _emit_summary(summary, emit_json=args.json)
    return 0


def generate_fixture_pack(output_root: Path) -> list[Path]:
    pack = build_fixture_pack()
    written_files: list[Path] = []
    for relative_path, payload in sorted(pack.items()):
        output_path = output_root / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(_json_dumps(payload), encoding="utf-8")
        written_files.append(output_path)
    return written_files


def build_fixture_pack() -> dict[Path, Any]:
    return {
        Path("manifest.json"): _manifest(),
        Path("source_registry/sources_list.json"): _source_registry_list(),
        Path("source_registry/source_synthetic_fixtures.json"): _source_registry_source(
            "synthetic-fixtures"
        ),
        Path("source_registry/source_github_releases_recorded_fixtures.json"): (
            _source_registry_source("github-releases-recorded-fixtures")
        ),
        **_query_planner_outputs(),
        **_resolution_run_outputs(),
        **_local_index_outputs(),
        **_resolution_memory_outputs(),
        **_archive_resolution_eval_outputs(),
    }


def _manifest() -> dict[str, Any]:
    return {
        "fixture_pack_id": FIXTURE_PACK_ID,
        "fixture_pack_version": FIXTURE_PACK_VERSION,
        "created_by_slice": CREATED_BY_SLICE,
        "python_oracle_status": "authoritative_reference_lane",
        "generated_from_commit": COMMIT_PLACEHOLDER,
        "generated_at": DETERMINISTIC_PLACEHOLDER,
        "included_seams": [
            "source_registry",
            "query_planner",
            "resolution_runs",
            "local_index",
            "resolution_memory",
            "archive_resolution_evals",
        ],
        "commands_to_regenerate": [
            "python scripts/generate_python_oracle_golden.py",
            "python scripts/generate_python_oracle_golden.py --check",
        ],
        "normalization_policy": {
            "timestamps": TIMESTAMP_PLACEHOLDER,
            "local_index_paths": LOCAL_INDEX_PATH_PLACEHOLDER,
            "local_index_fts_mode": FTS_MODE_PLACEHOLDER,
            "generated_from_commit": COMMIT_PLACEHOLDER,
            "generated_at": DETERMINISTIC_PLACEHOLDER,
        },
        "notes": [
            "Python remains the executable oracle for these fixtures.",
            "Rust candidate seams must match these outputs before replacement unless an allowed divergence is explicitly recorded.",
            "This fixture pack captures current bounded behavior only; it does not implement Rust behavior.",
        ],
        "limitations": [
            "No Rust parity runner is implemented in this milestone.",
            "Golden outputs are v0 and may evolve through explicit migration updates.",
            "Local Index FTS mode is normalized because SQLite FTS5 availability can vary by environment.",
            "Archive-resolution eval outputs intentionally preserve capability gaps and hard-query misses.",
        ],
    }


def _source_registry_list() -> dict[str, Any]:
    from runtime.gateway.public_api import (
        SourceCatalogRequest,
        build_demo_source_registry_public_api,
    )

    response = build_demo_source_registry_public_api().list_sources(
        SourceCatalogRequest.from_parts()
    )
    return _public_response(response)


def _source_registry_source(source_id: str) -> dict[str, Any]:
    from runtime.gateway.public_api import (
        SourceReadRequest,
        build_demo_source_registry_public_api,
    )

    response = build_demo_source_registry_public_api().get_source(
        SourceReadRequest.from_parts(source_id)
    )
    return _public_response(response)


def _query_planner_outputs() -> dict[Path, Any]:
    from runtime.gateway.public_api import build_demo_query_planner_public_api

    api = build_demo_query_planner_public_api()
    outputs: dict[Path, Any] = {}
    for fixture_id, query in QUERY_PLANNER_FIXTURES.items():
        outputs[Path(f"query_planner/{fixture_id}.json")] = _public_response(
            api.plan_query_text(query)
        )
    return outputs


def _resolution_run_outputs() -> dict[Path, Any]:
    from runtime.gateway.public_api import (
        DeterministicSearchRunRequest,
        ExactResolutionRunRequest,
        PlannedSearchRunRequest,
        build_demo_resolution_runs_public_api,
    )

    outputs: dict[Path, Any] = {}
    with tempfile.TemporaryDirectory() as temp_dir:
        api = build_demo_resolution_runs_public_api(temp_dir)
        outputs[Path("resolution_runs/exact_resolution_known.json")] = _public_response(
            api.start_exact_resolution_run(
                ExactResolutionRunRequest.from_parts(
                    "fixture:software/synthetic-demo-app@1.0.0"
                )
            )
        )
    with tempfile.TemporaryDirectory() as temp_dir:
        api = build_demo_resolution_runs_public_api(temp_dir)
        outputs[Path("resolution_runs/exact_resolution_missing.json")] = _public_response(
            api.start_exact_resolution_run(
                ExactResolutionRunRequest.from_parts(
                    "fixture:software/missing-demo-app@0.0.1"
                )
            )
        )
    with tempfile.TemporaryDirectory() as temp_dir:
        api = build_demo_resolution_runs_public_api(temp_dir)
        outputs[Path("resolution_runs/deterministic_search_archive.json")] = _public_response(
            api.start_deterministic_search_run(
                DeterministicSearchRunRequest.from_parts("archive")
            )
        )
    with tempfile.TemporaryDirectory() as temp_dir:
        api = build_demo_resolution_runs_public_api(temp_dir)
        outputs[Path("resolution_runs/planned_search_latest_firefox_xp.json")] = (
            _public_response(
                api.start_planned_search_run(
                    PlannedSearchRunRequest.from_parts(
                        "latest Firefox before XP support ended"
                    )
                )
            )
        )
    return {path: normalize_for_golden(payload) for path, payload in outputs.items()}


def _local_index_outputs() -> dict[Path, Any]:
    from runtime.gateway.public_api import (
        LocalIndexBuildRequest,
        LocalIndexQueryRequest,
        LocalIndexStatusRequest,
        build_demo_local_index_public_api,
    )

    outputs: dict[Path, Any] = {}
    with tempfile.TemporaryDirectory() as temp_dir:
        index_path = str(Path(temp_dir) / "python-oracle-index.sqlite3")
        api = build_demo_local_index_public_api()
        api.build_index(LocalIndexBuildRequest.from_parts(index_path))
        outputs[Path("local_index/status_after_build.json")] = _public_response(
            api.get_index_status(LocalIndexStatusRequest.from_parts(index_path))
        )
        outputs[Path("local_index/query_synthetic.json")] = _public_response(
            api.query_index(LocalIndexQueryRequest.from_parts(index_path, "synthetic"))
        )
        outputs[Path("local_index/query_archive.json")] = _public_response(
            api.query_index(LocalIndexQueryRequest.from_parts(index_path, "archive"))
        )
        outputs[Path("local_index/query_no_result.json")] = _public_response(
            api.query_index(LocalIndexQueryRequest.from_parts(index_path, "no-such-record"))
        )
    return {path: normalize_for_golden(payload) for path, payload in outputs.items()}


def _resolution_memory_outputs() -> dict[Path, Any]:
    from runtime.gateway.public_api import (
        ExactResolutionRunRequest,
        PlannedSearchRunRequest,
        ResolutionMemoryCreateRequest,
        build_demo_resolution_memory_public_api,
        build_demo_resolution_runs_public_api,
    )

    outputs: dict[Path, Any] = {}
    with tempfile.TemporaryDirectory() as temp_dir:
        run_api = build_demo_resolution_runs_public_api(temp_dir)
        run_response = run_api.start_exact_resolution_run(
            ExactResolutionRunRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0"
            )
        )
        run_id = str(run_response.body["selected_run_id"])
        memory_api = build_demo_resolution_memory_public_api(
            temp_dir,
            run_store_root=temp_dir,
        )
        outputs[Path("resolution_memory/memory_from_exact_resolution.json")] = (
            _public_response(
                memory_api.create_memory_from_run(
                    ResolutionMemoryCreateRequest.from_parts(run_id)
                )
            )
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        run_api = build_demo_resolution_runs_public_api(temp_dir)
        run_response = run_api.start_planned_search_run(
            PlannedSearchRunRequest.from_parts(
                "latest Firefox before XP support ended"
            )
        )
        run_id = str(run_response.body["selected_run_id"])
        memory_api = build_demo_resolution_memory_public_api(
            temp_dir,
            run_store_root=temp_dir,
        )
        outputs[Path("resolution_memory/memory_from_planned_search.json")] = (
            _public_response(
                memory_api.create_memory_from_run(
                    ResolutionMemoryCreateRequest.from_parts(run_id)
                )
            )
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        run_api = build_demo_resolution_runs_public_api(temp_dir)
        run_response = run_api.start_exact_resolution_run(
            ExactResolutionRunRequest.from_parts(
                "fixture:software/missing-demo-app@0.0.1"
            )
        )
        run_id = str(run_response.body["selected_run_id"])
        memory_api = build_demo_resolution_memory_public_api(
            temp_dir,
            run_store_root=temp_dir,
        )
        outputs[Path("resolution_memory/memory_from_absence.json")] = _public_response(
            memory_api.create_memory_from_run(
                ResolutionMemoryCreateRequest.from_parts(run_id)
            )
        )

    return {path: normalize_for_golden(payload) for path, payload in outputs.items()}


def _archive_resolution_eval_outputs() -> dict[Path, Any]:
    from runtime.gateway.public_api import build_demo_archive_resolution_evals_public_api

    api = build_demo_archive_resolution_evals_public_api()
    response = _public_response(api.run_suite())
    full_report = normalize_for_golden(response["body"]["eval_suite"])
    suite_summary = {
        "status": "evaluated",
        "total_task_count": full_report["total_task_count"],
        "status_counts": full_report["status_counts"],
        "task_summaries": full_report["task_summaries"],
        "created_at": full_report["created_at"],
        "created_by_slice": full_report["created_by_slice"],
        "notices": full_report["notices"],
    }
    return {
        Path("archive_resolution_evals/full_report.json"): full_report,
        Path("archive_resolution_evals/suite_summary.json"): suite_summary,
    }


def normalize_for_golden(value: Any) -> Any:
    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if key in {"started_at", "completed_at", "created_at"}:
                normalized[str(key)] = TIMESTAMP_PLACEHOLDER
            elif key == "index_path":
                normalized[str(key)] = LOCAL_INDEX_PATH_PLACEHOLDER
            elif key == "fts_mode":
                normalized[str(key)] = FTS_MODE_PLACEHOLDER
            elif key == "generated_from_commit":
                normalized[str(key)] = COMMIT_PLACEHOLDER
            elif key == "generated_at":
                normalized[str(key)] = DETERMINISTIC_PLACEHOLDER
            else:
                normalized[str(key)] = normalize_for_golden(item)
        return normalized
    if isinstance(value, list):
        return [normalize_for_golden(item) for item in value]
    if isinstance(value, tuple):
        return [normalize_for_golden(item) for item in value]
    return value


def _public_response(response: Any) -> dict[str, Any]:
    return normalize_for_golden(response.to_dict())


def _run_check(committed_root: Path, *, emit_json: bool) -> int:
    if not committed_root.exists():
        summary = _summary("failed", committed_root, [], error="Committed golden root is missing.")
        _emit_summary(summary, emit_json=emit_json, stderr=True)
        return 1

    with tempfile.TemporaryDirectory() as temp_dir:
        generated_root = Path(temp_dir) / "generated"
        generated_files = generate_fixture_pack(generated_root)
        comparison = _compare_directories(committed_root, generated_root)

    if comparison["status"] != "passed":
        _emit_summary(comparison, emit_json=emit_json, stderr=True)
        return 1

    summary = _summary("passed", committed_root, generated_files)
    _emit_summary(summary, emit_json=emit_json)
    return 0


def _compare_directories(left: Path, right: Path) -> dict[str, Any]:
    left_files = _relative_json_files(left)
    right_files = _relative_json_files(right)
    missing = sorted(str(path) for path in right_files - left_files)
    extra = sorted(str(path) for path in left_files - right_files)
    changed = sorted(
        str(path)
        for path in left_files & right_files
        if not filecmp.cmp(left / path, right / path, shallow=False)
    )
    status = "passed" if not missing and not extra and not changed else "failed"
    return {
        "status": status,
        "committed_root": str(left),
        "missing_files": missing,
        "extra_files": extra,
        "changed_files": changed,
    }


def _relative_json_files(root: Path) -> set[Path]:
    return {
        path.relative_to(root)
        for path in root.rglob("*.json")
        if path.is_file()
    }


def _summary(
    status: str,
    output_root: Path,
    written_files: Sequence[Path],
    *,
    error: str | None = None,
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "status": status,
        "fixture_pack_id": FIXTURE_PACK_ID,
        "fixture_pack_version": FIXTURE_PACK_VERSION,
        "output_root": str(output_root),
        "file_count": len(written_files),
        "created_by_slice": CREATED_BY_SLICE,
    }
    if error is not None:
        summary["error"] = error
    return summary


def _emit_summary(summary: Mapping[str, Any], *, emit_json: bool, stderr: bool = False) -> None:
    output = sys.stderr if stderr else sys.stdout
    if emit_json:
        output.write(_json_dumps(dict(summary)))
        return
    output.write("Python oracle golden fixture pack\n")
    output.write(f"status: {summary['status']}\n")
    output.write(f"fixture_pack_id: {summary['fixture_pack_id']}\n")
    output.write(f"fixture_pack_version: {summary['fixture_pack_version']}\n")
    output.write(f"output_root: {summary['output_root']}\n")
    output.write(f"file_count: {summary['file_count']}\n")
    if "error" in summary:
        output.write(f"error: {summary['error']}\n")


def _json_dumps(payload: Any) -> str:
    return json.dumps(deepcopy(payload), indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
