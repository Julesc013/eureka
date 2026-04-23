from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from runtime.engine.action_routing.action_plan import (
    ACCESS_REPRESENTATION_ACTION_ID,
    COMPARE_TARGET_ACTION_ID,
    EXPORT_RESOLUTION_BUNDLE_ACTION_ID,
    EXPORT_RESOLUTION_MANIFEST_ACTION_ID,
    INSPECT_BUNDLE_ACTION_ID,
    INSPECT_PRIMARY_REPRESENTATION_ACTION_ID,
    LIST_SUBJECT_STATES_ACTION_ID,
    STORE_RESOLUTION_BUNDLE_ACTION_ID,
    STORE_RESOLUTION_MANIFEST_ACTION_ID,
)
from runtime.engine.interfaces.public import ActionPlanRequest, ActionPlanResult
from runtime.engine.interfaces.service import ActionPlanService
from runtime.engine.strategy import bootstrap_strategy_profiles
from runtime.gateway.public_api.resolution_actions import (
    EXPORT_RESOLUTION_BUNDLE_ROUTE,
    EXPORT_RESOLUTION_MANIFEST_ROUTE,
)
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse
from runtime.gateway.public_api.stored_exports import (
    STORE_RESOLUTION_BUNDLE_ROUTE,
    STORE_RESOLUTION_MANIFEST_ROUTE,
)

BOOTSTRAP_STRATEGY_PROFILES = tuple(
    strategy_profile.to_dict() for strategy_profile in bootstrap_strategy_profiles()
)


@dataclass(frozen=True)
class ActionPlanEvaluationRequest:
    target_ref: str
    host_profile_id: str | None = None
    strategy_id: str | None = None
    store_actions_enabled: bool = False

    @classmethod
    def from_parts(
        cls,
        target_ref: str,
        host_profile_id: str | None = None,
        strategy_id: str | None = None,
        *,
        store_actions_enabled: bool = False,
    ) -> "ActionPlanEvaluationRequest":
        engine_request = ActionPlanRequest.from_parts(
            target_ref,
            host_profile_id,
            strategy_id,
            store_actions_enabled=store_actions_enabled,
        )
        return cls(
            target_ref=engine_request.target_ref,
            host_profile_id=engine_request.host_profile_id,
            strategy_id=engine_request.strategy_id,
            store_actions_enabled=engine_request.store_actions_enabled,
        )

    def to_engine_request(self) -> ActionPlanRequest:
        return ActionPlanRequest.from_parts(
            self.target_ref,
            self.host_profile_id,
            self.strategy_id,
            store_actions_enabled=self.store_actions_enabled,
        )


class ActionPlanPublicApi:
    def __init__(self, action_plan_service: ActionPlanService) -> None:
        self._action_plan_service = action_plan_service

    def plan_actions(self, request: ActionPlanEvaluationRequest) -> PublicApiResponse:
        result = self._action_plan_service.plan_actions(request.to_engine_request())
        return PublicApiResponse(
            status_code=200 if result.status == "planned" else 404,
            body=action_plan_result_to_public_envelope(result),
        )


def action_plan_result_to_public_envelope(result: ActionPlanResult) -> dict[str, Any]:
    envelope = result.to_dict()
    actions = envelope.get("actions")
    if isinstance(actions, list):
        for action in actions:
            if not isinstance(action, dict):
                continue
            route_hint = _route_hint_for_action(action, target_ref=result.target_ref)
            if route_hint is not None:
                action["route_hint"] = route_hint
    return envelope


def _route_hint_for_action(action: dict[str, Any], *, target_ref: str) -> str | None:
    action_id = action.get("action_id")
    action_status = action.get("status")
    if action_id in {INSPECT_PRIMARY_REPRESENTATION_ACTION_ID, ACCESS_REPRESENTATION_ACTION_ID}:
        locator = action.get("access_locator")
        if isinstance(locator, str) and locator:
            return locator
        return None
    if action_id == LIST_SUBJECT_STATES_ACTION_ID:
        subject_key = action.get("subject_key")
        if isinstance(subject_key, str) and subject_key:
            return f"/subject?key={quote(subject_key, safe='')}"
        return None
    if action_id == COMPARE_TARGET_ACTION_ID:
        return f"/compare?left={quote(target_ref, safe='')}"
    if action_id == EXPORT_RESOLUTION_MANIFEST_ACTION_ID:
        return f"{EXPORT_RESOLUTION_MANIFEST_ROUTE}?target_ref={quote(target_ref, safe='')}"
    if action_id == EXPORT_RESOLUTION_BUNDLE_ACTION_ID:
        return f"{EXPORT_RESOLUTION_BUNDLE_ROUTE}?target_ref={quote(target_ref, safe='')}"
    if action_id == INSPECT_BUNDLE_ACTION_ID:
        return "/inspect/bundle"
    if action_id == STORE_RESOLUTION_MANIFEST_ACTION_ID:
        if action_status == "unavailable":
            return None
        return f"{STORE_RESOLUTION_MANIFEST_ROUTE}?target_ref={quote(target_ref, safe='')}"
    if action_id == STORE_RESOLUTION_BUNDLE_ACTION_ID:
        if action_status == "unavailable":
            return None
        return f"{STORE_RESOLUTION_BUNDLE_ROUTE}?target_ref={quote(target_ref, safe='')}"
    return None
