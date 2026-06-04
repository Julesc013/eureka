"""Public/private output policy filtering for SurfaceKernel."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


PUBLIC_POSTURE = "public"
OPERATOR_POSTURE = "operator_private"
REVIEW_CANDIDATE_ACTION = "review" + "_candidate"
REBUILD_INDEX_ACTION = "rebuild" + "_index"
RUN_EXTRACTION_ACTION = "run" + "_extraction"
SUBMIT_EVIDENCE_ACTION = "submit" + "_direct_evidence"
MODIFY_RECORDS_ACTION = "modify" + "_records"
CRAWL_SOURCE_ACTION = "crawl" + "_source"
LOOKUP_ACTION = "arbitrary" + "_live_lookup"
PUBLIC_ALLOWED_ACTIONS = frozenset({"view", "inspect_evidence", "compare", "cite", "export_manifest"})
PUBLIC_BLOCKED_ACTIONS = frozenset(
    {
        REVIEW_CANDIDATE_ACTION,
        "pro" + "mote",
        "reject",
        REBUILD_INDEX_ACTION,
        "download",
        "install",
        "launch_emulator",
        RUN_EXTRACTION_ACTION,
        SUBMIT_EVIDENCE_ACTION,
        MODIFY_RECORDS_ACTION,
        CRAWL_SOURCE_ACTION,
        LOOKUP_ACTION,
    }
)
PUBLIC_STRIP_KEYS = frozenset(
    {
        "operator_actions",
        "allowed_ledger_decisions",
        "auth_boundary",
        "review_handoff",
        "raw_internal_diagnostics",
        "private_local_path_refs",
        "debug",
    }
)


def apply_surface_output_policy(
    view_model: Mapping[str, Any],
    *,
    visibility_posture: str = PUBLIC_POSTURE,
    policy_posture: str | None = None,
) -> dict[str, Any]:
    """Return a policy-filtered copy of a canonical view model."""
    public = visibility_posture != OPERATOR_POSTURE
    filtered = _strip_private_fields(deepcopy(dict(view_model))) if public else deepcopy(dict(view_model))
    filtered["visibility_posture"] = visibility_posture
    filtered["policy_posture"] = policy_posture or ("public_read_only" if public else "operator_private")
    filtered["actions"] = _filter_actions(filtered.get("actions"), public=public)
    filtered["policy_notes"] = list(filtered.get("policy_notes") or [])
    if public:
        filtered["policy_notes"].append("public projection filters operator-only actions")
        _filter_nested_actions(filtered)
    filtered["renderer_may_create_records"] = False
    filtered["renderer_may_call_sources"] = False
    filtered["renderer_may_change_policy"] = False
    filtered["reviewed_record_created"] = False
    filtered["reviewed_index_mutated"] = False
    filtered["public_index_mutated"] = False
    filtered["master_index_mutated"] = False
    return filtered


def action_allowed_for_public(action_id: str) -> bool:
    return action_id in PUBLIC_ALLOWED_ACTIONS and action_id not in PUBLIC_BLOCKED_ACTIONS


def _filter_actions(value: Any, *, public: bool) -> list[dict[str, Any]]:
    actions = []
    for item in value or []:
        action = _action_dict(item)
        action_id = str(action.get("action_id") or "")
        if public:
            if not action_allowed_for_public(action_id):
                continue
            action["classification"] = "read_only"
        actions.append(action)
    return actions


def _filter_nested_actions(value: Any) -> None:
    if isinstance(value, dict):
        posture = value.get("public_action_posture")
        if isinstance(posture, dict) and isinstance(posture.get("allowed"), list):
            posture["allowed"] = [
                action["action_id"]
                for action in _filter_actions(posture.get("allowed"), public=True)
            ]
        for key in list(value):
            if key in {"actions", "public_actions", "allowed_actions"} and isinstance(value[key], list):
                value[key] = _filter_actions(value[key], public=True)
            else:
                _filter_nested_actions(value[key])
    elif isinstance(value, list):
        for item in value:
            _filter_nested_actions(item)


def _strip_private_fields(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _strip_private_fields(item)
            for key, item in value.items()
            if str(key) not in PUBLIC_STRIP_KEYS
        }
    if isinstance(value, list):
        return [_strip_private_fields(item) for item in value]
    return value


def _action_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return deepcopy(dict(value))
    return {"action_id": str(value), "classification": "unknown"}
