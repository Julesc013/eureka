"""Lane snapshot assembly for headless resolution runs."""

from __future__ import annotations

from typing import Any, Mapping

from runtime.local_service.workbench_result_lanes import (
    build_absence_lane,
    build_blocked_action_lane,
    build_demo_lane_page,
    build_result_lane_page_view,
    build_result_lane_packet,
)
from runtime.search_hunt.ia_bridge import build_ia_hunt_result_lanes, run_ia_hunt_pipeline_dry_run

from .run_store import FIXED_CREATED_AT, stable_id


def build_run_lane_snapshot(
    run: Mapping[str, Any],
    workunit_schedule: Mapping[str, Any] | None = None,
    *,
    projection_profile: str = "operator_workbench",
    run_ia_dry_run: bool = True,
) -> dict[str, Any]:
    """Build a projection-safe lane snapshot from local/demo and IA dry-run records."""
    query = str(run.get("query") or "")
    schedule = dict(workunit_schedule or {})
    base_page = build_demo_lane_page(query or "sampleproject", "operator_workbench", from_play_demo=True, from_ia_examples=False)
    lanes = list(base_page.get("lanes", []))
    if schedule.get("workunits"):
        lanes.append(
            build_result_lane_packet(
                "running_workunits",
                [
                    {
                        "item_id": str(item.get("workunit_id")),
                        "title": str(item.get("workunit_type", "IA metadata WorkUnit")).replace("_", " "),
                        "summary": "IA-Hunt WorkUnit planned by the headless run kernel; no live source call executed.",
                        "workunit_refs": [str(item.get("workunit_id"))],
                        "operator_notes": "Scheduled as dry-run orchestration only.",
                    }
                    for item in schedule.get("workunits", [])
                ],
            )
        )
    if run_ia_dry_run and schedule.get("plan"):
        outputs = run_ia_hunt_pipeline_dry_run(schedule["plan"])
        ia_page = build_ia_hunt_result_lanes(outputs, "operator_workbench")
        lanes.extend([dict(lane) for lane in ia_page.get("lanes", []) if lane.get("lane_kind") == "ia_metadata_candidates"])
    lanes.append(build_absence_lane(query or "sampleproject"))
    lanes.append(build_blocked_action_lane())
    page = build_result_lane_page_view(query or "sampleproject", lanes, projection_profile)
    return {
        "schema_version": "run_lane_snapshot.v0",
        "snapshot_id": stable_id("run_lane_snapshot", {"run_id": run.get("run_id"), "projection": projection_profile}),
        "run_id": str(run.get("run_id")),
        "created_at": FIXED_CREATED_AT,
        "projection_profile": projection_profile,
        "lane_page": page,
        "lane_count": page.get("lane_count", 0),
        "visible_lane_count": page.get("visible_lane_count", 0),
        "accepted_truth": False,
        "review_required": True,
    }
