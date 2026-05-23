#!/usr/bin/env python3
"""Run the local IA Hunt bridge in dry-run or temp-instance mode."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.search.hunt.ia_bridge import (  # noqa: E402
    build_ia_hunt_boundary_report,
    build_ia_hunt_result_lanes,
    plan_ia_hunt_pipeline,
    run_ia_hunt_pipeline_dry_run,
    run_ia_hunt_pipeline_temp_instance,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="sampleproject")
    parser.add_argument("--need-id")
    parser.add_argument("--hunt-id")
    parser.add_argument("--instance")
    parser.add_argument("--operator-token")
    parser.add_argument("--use-temp-instance", action="store_true")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply-to-temp", action="store_true")
    parser.add_argument(
        "--projection",
        choices=("operator_workbench", "public_web", "native_desktop_read_only"),
        default="operator_workbench",
    )
    parser.add_argument("--from-fixtures", action="store_true")
    parser.add_argument("--from-ia-live-preview", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--boundary-output")
    args = parser.parse_args(argv)

    if args.apply_to_temp and not args.use_temp_instance:
        print("error: --apply-to-temp requires --use-temp-instance", file=stderr)
        return 2
    if args.from_ia_live_preview:
        print("error: --from-ia-live-preview is accepted but blocked by IA Hunt bridge policy", file=stderr)
        return 2

    need = {
        "query": args.query,
        "need_id": args.need_id or "",
        "hunt_id": args.hunt_id or "",
    }
    try:
        plan = plan_ia_hunt_pipeline(need)
        plan["from_fixtures"] = bool(args.from_fixtures or not args.from_ia_live_preview)
        if args.apply_to_temp:
            if args.instance:
                outputs = run_ia_hunt_pipeline_temp_instance(plan, args.instance, args.operator_token)
            else:
                with TemporaryDirectory(prefix="eureka-ia-hunt-bridge-") as tmp:
                    outputs = run_ia_hunt_pipeline_temp_instance(plan, tmp, args.operator_token)
        else:
            outputs = run_ia_hunt_pipeline_dry_run(plan)
        result_lanes = build_ia_hunt_result_lanes(outputs, args.projection)
        boundary_report = build_ia_hunt_boundary_report(outputs)
        payload = {
            "schema_version": "ia_hunt_bridge_cli_result.v0",
            "task": "IA-HUNT-BRIDGE-00",
            "mode": outputs.get("mode", "dry_run"),
            "query": args.query,
            "projection_profile": args.projection,
            "plan": plan,
            "workunits": outputs.get("workunits", []),
            "outputs": _summarize_outputs(outputs),
            "result_lane_page": result_lanes,
            "boundary_report": boundary_report,
        }
    except Exception as exc:
        print(f"error: {exc}", file=stderr)
        return 1

    if args.output:
        _write_json(Path(args.output), payload)
    if args.boundary_output:
        _write_json(Path(args.boundary_output), boundary_report)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print("IA Hunt bridge", file=stdout)
        print(f"mode: {payload['mode']}", file=stdout)
        print(f"workunit_count: {len(payload['workunits'])}", file=stdout)
        print(f"result_lanes_emitted: {str(bool(result_lanes.get('lanes'))).lower()}", file=stdout)
    return 0


def _summarize_outputs(outputs: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": "ia_hunt_bridge_output_summary.v0",
        "source_cache_record_count": len(outputs.get("source_cache_records", []) or []),
        "evidence_candidate_count": len(outputs.get("evidence_candidates", []) or []),
        "candidate_count": len(outputs.get("candidate_records", []) or []),
        "review_item_count": len(outputs.get("review_items", []) or []),
        "reviewed_record_count": len(outputs.get("reviewed_records", []) or []),
        "source_cache_report": _summarize_report(outputs.get("source_cache_report", {})),
        "evidence_report": _summarize_report(outputs.get("evidence_report", {})),
        "candidate_report": _summarize_report(outputs.get("candidate_report", {})),
        "review_report": _summarize_report(outputs.get("review_report", {})),
        "reviewed_index_report": _summarize_report(outputs.get("reviewed_index_report", {})),
    }


def _summarize_report(value: object) -> dict[str, object]:
    report = dict(value or {}) if isinstance(value, dict) else {}
    summary_keys = (
        "schema_version",
        "status",
        "dry_run",
        "write_scope",
        "record_count",
        "candidate_count",
        "review_item_count",
        "review_decision_count",
        "reviewed_record_count",
        "source_cache_write_performed",
        "evidence_ledger_write_performed",
        "candidate_index_mutated",
        "review_queue_mutated",
        "reviewed_index_mutated",
        "accepted_truth_created",
        "master_index_mutated",
        "download_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
    )
    return {key: report[key] for key in summary_keys if key in report}


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
