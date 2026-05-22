"""Command handling for the headless resolution-run kernel."""

from __future__ import annotations

from typing import Any, Mapping

from .errors import ResolutionRunPolicyError, ResolutionRunValidationError
from .event_log import InMemoryRunEventLog
from .policy_gate import evaluate_run_policy
from .run_store import FIXED_CREATED_AT, stable_id


STATE_COMMAND_TARGETS = {
    "start": "running",
    "pause": "paused",
    "resume": "running",
    "cancel": "cancelled",
    "project_lanes": "running",
    "request_ia_metadata_dry_run": "running",
}


def handle_run_command(
    run: Mapping[str, Any],
    command: Mapping[str, Any],
    event_log: InMemoryRunEventLog,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Apply a safe command to a run packet and append an event."""
    command_type = str(command.get("command_type") or "")
    if not command_type:
        raise ResolutionRunValidationError("command_type is required")
    decision = evaluate_run_policy(command_type, policy)
    command_packet = {
        "schema_version": "run_command.v0",
        "command_id": str(command.get("command_id") or stable_id("runcmd", {"run": run.get("run_id"), "type": command_type})),
        "run_id": str(command.get("run_id") or run.get("run_id")),
        "command_type": command_type,
        "created_at": FIXED_CREATED_AT,
        "payload": dict(command.get("payload", {}) or {}),
        "dry_run": True,
        "allowed": decision["allowed"],
        "blocked_reasons": list(decision["blocked_reasons"]),
    }
    if not decision["allowed"]:
        event_log.append(str(run.get("run_id")), "command_blocked", {"command": command_packet, "policy_decision": decision})
        raise ResolutionRunPolicyError("; ".join(decision["blocked_reasons"]))
    updated = dict(run)
    target = STATE_COMMAND_TARGETS.get(command_type)
    if target:
        updated["state"] = target
        updated.setdefault("state_history", [])
        updated["state_history"] = list(updated.get("state_history", [])) + [
            {"state": target, "at": FIXED_CREATED_AT, "reason": f"command:{command_type}"}
        ]
    event_log.append(str(run.get("run_id")), "command_applied", {"command": command_packet})
    return updated
