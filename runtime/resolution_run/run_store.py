"""In-memory run store for the portable resolution-run foundation."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import re
from typing import Any, Mapping

from .errors import ResolutionRunNotFoundError


FIXED_CREATED_AT = "2026-05-22T00:00:00Z"


def stable_id(prefix: str, value: Any) -> str:
    text = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()[:32] or "record"
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}_{slug}_{digest}"


@dataclass
class InMemoryRunStore:
    """Store run packets without touching operator or public instance state."""

    runs: dict[str, dict[str, Any]] = field(default_factory=dict)

    def create(self, query: str, projection_profile: str = "operator_workbench") -> dict[str, Any]:
        request_id = stable_id("req", query)
        compiled_query_id = stable_id("compiled", {"query": query, "profile": projection_profile})
        run_id = stable_id("run", {"query": query, "profile": projection_profile})
        run = {
            "schema_version": "resolution_run.v0",
            "packet_type": "ResolutionRunPacket",
            "created_at": FIXED_CREATED_AT,
            "updated_at": FIXED_CREATED_AT,
            "run_id": run_id,
            "request_id": request_id,
            "compiled_query_id": compiled_query_id,
            "query": query,
            "projection_profile": projection_profile,
            "state": "created",
            "state_history": [
                {
                    "state": "created",
                    "at": FIXED_CREATED_AT,
                    "reason": "headless resolution run created",
                }
            ],
            "active_lanes": [],
            "controls_available": [
                "project_lanes",
                "request_ia_metadata_dry_run",
                "pause",
                "resume",
                "cancel",
            ],
            "coverage_report_id": stable_id("coverage", run_id),
            "dry_run": True,
            "accepted_truth": False,
            "review_required": False,
            "limitations": [
                "Foundation run store is in-memory and deterministic.",
                "No source, evidence, review, public, operator, or master store is mutated.",
            ],
        }
        self.runs[run_id] = run
        return dict(run)

    def get(self, run_id: str) -> dict[str, Any]:
        if run_id not in self.runs:
            raise ResolutionRunNotFoundError(f"resolution run not found: {run_id}")
        return dict(self.runs[run_id])

    def update(self, run: Mapping[str, Any]) -> dict[str, Any]:
        packet = dict(run)
        packet["updated_at"] = FIXED_CREATED_AT
        self.runs[str(packet["run_id"])] = packet
        return dict(packet)
