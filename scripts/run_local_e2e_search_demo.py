#!/usr/bin/env python3
"""Run the deterministic local E2E search demo.

This demo is a local product proof over repo-local hard-query fixtures. It does
not call live source providers, download files, mutate indexes, or create
reviewed/verified artifact claims.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from html import escape
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evals.hard_queries import (
    BASELINE_PROFILES,
    REQUIRED_HARD_QUERY_IDS,
    SYNTHETIC_FIXTURE_DISCLAIMER,
    evaluate_fixture_case,
    fixture_case_by_query_id,
    render_fixture_case,
)


DEMO_TASK_ID = "LOCAL-E2E-SEARCH-DEMO-00"
DEMO_ROOT = Path("evals/hard_queries/local_e2e_demo/demo_00")

REQUIRED_QUERY_TEXTS = (
    "Windows 7 apps",
    "driver for Win98",
    "old blue FTP client for XP",
    "manual for Sound Blaster CT1740",
    "latest Firefox before XP support ended",
    "article about ray tracing in a 1994 magazine",
)

STATUS_CONCEPTS = {
    "hq_windows_7_apps": "candidate",
    "hq_driver_win98": "blocked_for_user_details",
    "hq_blue_ftp_client_xp": "near_miss",
    "hq_sound_blaster_ct1740_manual": "candidate",
    "hq_firefox_last_xp": "policy_blocked",
    "hq_ray_tracing_1994_magazine": "unavailable",
}

ARTIFACT_GATE_PATHS = (
    Path("evals/hard_queries/artifact_record_gate/gate_02/public_alpha_artifact_gate.json"),
    Path("evals/hard_queries/artifact_record_gate/gate_00/public_alpha_artifact_gate.json"),
)

FORBIDDEN_PUBLIC_ACTIONS = (
    "review_candidate",
    "promote",
    "reject",
    "supersede",
    "request_more_evidence",
    "rebuild_index",
    "freeze_review",
    "download",
    "install",
    "launch_emulator",
    "run_extraction",
    "submit_direct_evidence",
    "crawl_source",
    "arbitrary_live_lookup",
)


def build_demo_suite(root: Path = REPO_ROOT) -> dict[str, Any]:
    gate = load_artifact_gate(root)
    results: dict[str, dict[str, Any]] = {}
    queries: list[dict[str, Any]] = []
    evaluations: list[dict[str, Any]] = []

    for query_id in REQUIRED_HARD_QUERY_IDS:
        fixture = fixture_case_by_query_id(query_id)
        rendered = render_fixture_case(fixture)
        profile_results: dict[str, dict[str, Any]] = {}
        for profile in BASELINE_PROFILES:
            projection = deepcopy(rendered[profile])
            profile_results[profile] = {
                "schema_version": "local_e2e_search_demo_profile_result.v0",
                "query_id": query_id,
                "query_text": fixture["query_text"],
                "expected_status": fixture["expected_status"],
                "status_concept": STATUS_CONCEPTS[query_id],
                "artifact_gate": gate,
                "renderer_output": projection["renderer_result"]["renderer_output"],
                "view_model": projection["view_model"],
                "surface_flags": _surface_flags(projection),
                "renderer_flags": _renderer_flags(projection["renderer_result"]),
                "truth_boundary": _truth_boundary(fixture, gate),
            }
        results[query_id] = profile_results
        queries.append(
            {
                "query_id": query_id,
                "query_text": fixture["query_text"],
                "expected_status": fixture["expected_status"],
                "status_concept": STATUS_CONCEPTS[query_id],
                "reason_codes": list(fixture["fallback_summary"].get("reason_codes") or []),
            }
        )
        evaluations.append(evaluate_fixture_case(fixture))

    return {
        "schema_version": "local_e2e_search_demo_suite.v0",
        "task_id": DEMO_TASK_ID,
        "fixture_disclaimer": SYNTHETIC_FIXTURE_DISCLAIMER,
        "profiles": list(BASELINE_PROFILES),
        "queries": queries,
        "artifact_gate": gate,
        "results": results,
        "evaluations": evaluations,
        "live_source_calls": False,
        "source_provider_calls": False,
        "downloads_performed": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "verified_artifacts_created": 0,
        "reviewed_artifact_records_created": 0,
    }


def load_artifact_gate(root: Path = REPO_ROOT) -> dict[str, Any]:
    for rel in ARTIFACT_GATE_PATHS:
        path = root / rel
        if path.is_file():
            payload = json.loads(path.read_text(encoding="utf-8"))
            reviewed = int(payload.get("reviewed_artifact_record_count", 0))
            threshold = int(
                payload.get("minimum_public_alpha_reviewed_artifact_records")
                or payload.get("threshold_reviewed_artifact_records")
                or 25
            )
            verified = int(payload.get("verified_artifact_count", 0))
            return {
                "schema_version": "local_e2e_artifact_gate_snapshot.v0",
                "source_path": rel.as_posix(),
                "status": str(payload.get("status", "unknown")),
                "public_alpha_blocked": bool(payload.get("public_alpha_blocked", True)),
                "dev_to_main_promotion_blocked": bool(payload.get("dev_to_main_promotion_blocked", True)),
                "reviewed_artifact_record_count": reviewed,
                "minimum_public_alpha_reviewed_artifact_records": threshold,
                "reviewed_artifact_record_gap": int(payload.get("reviewed_artifact_record_gap", max(threshold - reviewed, 0))),
                "verified_artifact_count": verified,
                "external_artifact_evidence": "absent",
                "hardware_details": "absent",
            }
    return {
        "schema_version": "local_e2e_artifact_gate_snapshot.v0",
        "source_path": "",
        "status": "unknown",
        "public_alpha_blocked": True,
        "dev_to_main_promotion_blocked": True,
        "reviewed_artifact_record_count": 0,
        "minimum_public_alpha_reviewed_artifact_records": 25,
        "reviewed_artifact_record_gap": 25,
        "verified_artifact_count": 0,
        "external_artifact_evidence": "absent",
        "hardware_details": "absent",
    }


def build_profile_output(suite: Mapping[str, Any], profile: str, query: str | None = None) -> dict[str, Any]:
    if profile not in BASELINE_PROFILES:
        raise ValueError(f"unsupported profile: {profile}")
    selected = _select_query_ids(suite, query)
    return {
        "schema_version": "local_e2e_search_demo_profile_output.v0",
        "task_id": DEMO_TASK_ID,
        "profile": profile,
        "fixture_disclaimer": suite["fixture_disclaimer"],
        "artifact_gate": suite["artifact_gate"],
        "queries": [
            {
                "query_id": query_id,
                "query_text": suite["results"][query_id][profile]["query_text"],
                "expected_status": suite["results"][query_id][profile]["expected_status"],
                "status_concept": suite["results"][query_id][profile]["status_concept"],
                "renderer_output": suite["results"][query_id][profile]["renderer_output"],
                "truth_boundary": suite["results"][query_id][profile]["truth_boundary"],
                "surface_flags": suite["results"][query_id][profile]["surface_flags"],
                "renderer_flags": suite["results"][query_id][profile]["renderer_flags"],
            }
            for query_id in selected
        ],
        "live_source_calls": False,
        "downloads_performed": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def write_demo_fixtures(output_root: Path = REPO_ROOT / DEMO_ROOT, root: Path = REPO_ROOT) -> dict[str, str]:
    suite = build_demo_suite(root)
    output_root.mkdir(parents=True, exist_ok=True)

    files = {
        "query_inputs.json": _query_inputs(suite),
        "expected_statuses.json": _expected_statuses(suite),
        "surface_view_models.json": _surface_view_models(suite),
        "rendered_json_v0.json": build_profile_output(suite, "json_v0"),
        "rendered_text_v0.txt": render_profile_text(build_profile_output(suite, "text_v0")),
        "rendered_html_basic_v0.html": render_profile_html(build_profile_output(suite, "html_basic_v0")),
        "snapshot_v0.json": build_profile_output(suite, "snapshot_v0"),
        "demo_report.md": render_demo_report(suite),
    }

    written: dict[str, str] = {}
    for name, payload in files.items():
        path = output_root / name
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8")
        else:
            path.write_text(_stable_json_pretty(payload) + "\n", encoding="utf-8")
        written[name] = path.as_posix()
    return written


def render_profile_text(profile_output: Mapping[str, Any]) -> str:
    gate = profile_output["artifact_gate"]
    lines = [
        "LOCAL-E2E-SEARCH-DEMO-00",
        f"Profile: {profile_output['profile']}",
        f"Artifact gate: {gate['status']}",
        f"Reviewed artifacts: {gate['reviewed_artifact_record_count']}/{gate['minimum_public_alpha_reviewed_artifact_records']}",
        f"Verified artifacts: {gate['verified_artifact_count']}",
        "",
    ]
    for item in profile_output["queries"]:
        content = item["renderer_output"]["content"]
        lines.extend(
            [
                f"Query: {item['query_text']}",
                f"Expected status: {item['expected_status']}",
                f"Status concept: {item['status_concept']}",
                str(content),
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_profile_html(profile_output: Mapping[str, Any]) -> str:
    gate = profile_output["artifact_gate"]
    body = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        "<title>LOCAL-E2E-SEARCH-DEMO-00</title>",
        "</head>",
        "<body>",
        "<main>",
        "<h1>LOCAL-E2E-SEARCH-DEMO-00</h1>",
        f"<p>Profile: {_e(profile_output['profile'])}</p>",
        f"<p>Artifact gate: {_e(gate['status'])}</p>",
        f"<p>Reviewed artifacts: {gate['reviewed_artifact_record_count']}/{gate['minimum_public_alpha_reviewed_artifact_records']}</p>",
        f"<p>Verified artifacts: {gate['verified_artifact_count']}</p>",
    ]
    for item in profile_output["queries"]:
        body.extend(
            [
                "<section>",
                f"<h2>{_e(item['query_text'])}</h2>",
                f"<p>Status: {_e(item['expected_status'])}</p>",
                f"<p>Status concept: {_e(item['status_concept'])}</p>",
                "<pre>",
                _e(str(item["renderer_output"]["content"])),
                "</pre>",
                "</section>",
            ]
        )
    body.extend(["</main>", "</body>", "</html>"])
    return "\n".join(body) + "\n"


def render_demo_report(suite: Mapping[str, Any]) -> str:
    gate = suite["artifact_gate"]
    lines = [
        "# Local E2E Search Demo 00",
        "",
        "This is a local product-proof demo over repo-local hard-query fixtures and SurfaceKernel baseline renderers.",
        "",
        "It is not public-alpha readiness evidence and it is not artifact evidence.",
        "",
        "## Gate Snapshot",
        "",
        "```text",
        f"artifact gate: {gate['status']}",
        f"reviewed artifact records: {gate['reviewed_artifact_record_count']}/{gate['minimum_public_alpha_reviewed_artifact_records']}",
        f"verified artifacts: {gate['verified_artifact_count']}",
        "public alpha: blocked",
        "dev -> main: blocked",
        "external artifact evidence: absent",
        "hardware details: absent",
        "```",
        "",
        "## Queries",
        "",
        "| Query | Status | Concept |",
        "| --- | --- | --- |",
    ]
    for item in suite["queries"]:
        lines.append(f"| {item['query_text']} | {item['expected_status']} | {item['status_concept']} |")
    lines.extend(
        [
            "",
            "## Renderers",
            "",
            "```text",
            "\n".join(BASELINE_PROFILES),
            "```",
            "",
            "## Truth Boundary",
            "",
            "```text",
            "live_source_calls: false",
            "downloads_performed: false",
            "reviewed_index_mutated: false",
            "public_index_mutated: false",
            "master_index_mutated: false",
            "reviewed_artifact_records_created: 0",
            "verified_artifacts_created: 0",
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="Render all demo hard queries.")
    parser.add_argument("--query", help="Render one query by id or text.")
    parser.add_argument("--profile", choices=BASELINE_PROFILES, default="json_v0")
    parser.add_argument("--write-fixtures", action="store_true", help="Write deterministic demo fixture files.")
    parser.add_argument("--output-root", default=str(REPO_ROOT / DEMO_ROOT))
    args = parser.parse_args(argv)

    if not args.all and not args.query and not args.write_fixtures:
        parser.error("use --all, --query, or --write-fixtures")

    if args.write_fixtures:
        written = write_demo_fixtures(Path(args.output_root))
        print(_stable_json_pretty({"schema_version": "local_e2e_fixture_write_result.v0", "written": written}), file=stdout)
        return 0

    suite = build_demo_suite()
    output = build_profile_output(suite, args.profile, None if args.all else args.query)
    if args.profile == "text_v0":
        print(render_profile_text(output), end="", file=stdout)
    elif args.profile == "html_basic_v0":
        print(render_profile_html(output), end="", file=stdout)
    else:
        print(_stable_json_pretty(output), file=stdout)
    return 0


def _query_inputs(suite: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "local_e2e_query_inputs.v0",
        "task_id": DEMO_TASK_ID,
        "queries": suite["queries"],
    }


def _expected_statuses(suite: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "local_e2e_expected_statuses.v0",
        "task_id": DEMO_TASK_ID,
        "statuses": {
            item["query_id"]: {
                "query_text": item["query_text"],
                "expected_status": item["expected_status"],
                "status_concept": item["status_concept"],
            }
            for item in suite["queries"]
        },
    }


def _surface_view_models(suite: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "local_e2e_surface_view_models.v0",
        "task_id": DEMO_TASK_ID,
        "artifact_gate": suite["artifact_gate"],
        "view_models": {
            query_id: {
                profile: profile_result["view_model"]
                for profile, profile_result in profile_results.items()
            }
            for query_id, profile_results in suite["results"].items()
        },
    }


def _select_query_ids(suite: Mapping[str, Any], query: str | None) -> list[str]:
    if not query:
        return [item["query_id"] for item in suite["queries"]]
    normalized = query.strip().lower()
    matches = [
        item["query_id"]
        for item in suite["queries"]
        if normalized in {item["query_id"].lower(), item["query_text"].lower()}
    ]
    if not matches:
        raise ValueError(f"unknown query: {query}")
    return matches


def _surface_flags(projection: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "surface_kernel_called_source_provider": bool(projection.get("surface_kernel_called_source_provider")),
        "surface_kernel_mutated_reviewed_index": bool(projection.get("surface_kernel_mutated_reviewed_index")),
        "surface_kernel_mutated_public_index": bool(projection.get("surface_kernel_mutated_public_index")),
        "surface_kernel_mutated_master_index": bool(projection.get("surface_kernel_mutated_master_index")),
    }


def _renderer_flags(renderer_result: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "renderer_called_source_provider": bool(renderer_result.get("renderer_called_source_provider")),
        "renderer_created_verified_state": bool(renderer_result.get("renderer_created_verified_state")),
        "renderer_mutated_reviewed_index": bool(renderer_result.get("renderer_mutated_reviewed_index")),
        "renderer_mutated_public_index": bool(renderer_result.get("renderer_mutated_public_index")),
        "renderer_mutated_master_index": bool(renderer_result.get("renderer_mutated_master_index")),
    }


def _truth_boundary(fixture: Mapping[str, Any], gate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "reviewed_support_fact_is_not_reviewed_artifact_record": True,
        "reviewed_artifact_record_is_not_verified_artifact": True,
        "candidate_is_not_reviewed_truth": True,
        "need_is_not_reviewed_truth": True,
        "near_miss_is_not_reviewed_truth": True,
        "blocked_for_user_details_is_not_failed_search": True,
        "unavailable_is_not_absence": True,
        "fixture_is_evidence": False,
        "verified": False,
        "accepted_truth": False,
        "reviewed_artifact_record_created": False,
        "verified_artifact_created": False,
        "reviewed_artifact_record_count": gate["reviewed_artifact_record_count"],
        "verified_artifact_count": gate["verified_artifact_count"],
        "fixture_reviewed_record_created": bool(fixture.get("reviewed_record_created")),
    }


def _stable_json_pretty(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)


def _e(value: Any) -> str:
    return escape(str(value), quote=True)


if __name__ == "__main__":
    raise SystemExit(main())
