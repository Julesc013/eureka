"""WorkUnit scheduling adapters for resolution runs."""

from __future__ import annotations

from typing import Any, Mapping

from runtime.search.hunt.ia_bridge import plan_ia_hunt_pipeline


def schedule_ia_hunt_workunits(
    query: str,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Plan IA-Hunt WorkUnits without executing source access or store writes."""
    plan = plan_ia_hunt_pipeline(query, policy or {})
    workunits = [dict(item) for item in plan.get("workunits", []) or []]
    return {
        "schema_version": "resolution_run_workunit_schedule.v0",
        "source_family": "internet_archive_metadata",
        "dry_run": True,
        "workunits": workunits,
        "workunit_count": len(workunits),
        "blocked_actions": list(plan.get("blocked_actions", [])),
        "plan": plan,
    }
