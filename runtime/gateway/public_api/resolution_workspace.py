from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.gateway.public_api.action_plan_boundary import (
    ActionPlanEvaluationRequest,
    ActionPlanPublicApi,
)
from runtime.gateway.public_api.action_plan_view_models import (
    action_plan_envelope_to_view_model,
)
from runtime.gateway.public_api.representation_selection_boundary import (
    RepresentationSelectionEvaluationRequest,
    RepresentationSelectionPublicApi,
)
from runtime.gateway.public_api.representation_selection_view_models import (
    representation_selection_envelope_to_view_model,
)
from runtime.gateway.public_api.resolution_actions import (
    ResolutionActionRequest,
    ResolutionActionsPublicApi,
)
from runtime.gateway.public_api.resolution_actions_view_models import (
    resolution_actions_envelope_to_view_model,
)
from runtime.gateway.public_api.resolution_boundary import ResolutionJobsPublicApi
from runtime.gateway.public_api.resolution_jobs import SubmitResolutionJobRequest
from runtime.gateway.public_api.stored_exports import (
    StoredExportsPublicApi,
    StoredExportsTargetRequest,
)
from runtime.gateway.public_api.stored_exports_view_models import (
    stored_exports_envelope_to_view_model,
)
from runtime.gateway.public_api.workbench_sessions import (
    resolution_job_envelope_to_workbench_session,
)


@dataclass(frozen=True)
class ResolutionWorkspaceViewModels:
    workbench_session: dict[str, Any]
    action_plan: dict[str, Any] | None = None
    handoff: dict[str, Any] | None = None
    resolution_actions: dict[str, Any] | None = None
    stored_exports: dict[str, Any] | None = None


class ResolutionWorkspaceReadError(LookupError):
    """Raised when a submitted resolution job cannot be read back."""


def build_resolution_workspace_view_models(
    resolution_public_api: ResolutionJobsPublicApi,
    target_ref: str,
    *,
    action_plan_public_api: ActionPlanPublicApi | None = None,
    handoff_public_api: RepresentationSelectionPublicApi | None = None,
    actions_public_api: ResolutionActionsPublicApi | None = None,
    stored_exports_public_api: StoredExportsPublicApi | None = None,
    session_id: str,
    host_profile_id: str | None = None,
    strategy_id: str | None = None,
) -> ResolutionWorkspaceViewModels:
    submit_response = resolution_public_api.submit_resolution_job(
        SubmitResolutionJobRequest.from_parts(target_ref),
    )
    job_id = _require_non_empty_string(submit_response.body.get("job_id"), "job_id")
    read_response = resolution_public_api.read_resolution_job(job_id)
    if read_response.status_code != 200:
        message = read_response.body.get("message")
        if not isinstance(message, str) or not message:
            message = "No job state was available for the requested work."
        raise ResolutionWorkspaceReadError(message)

    action_plan = None
    if action_plan_public_api is not None:
        action_plan = action_plan_envelope_to_view_model(
            action_plan_public_api.plan_actions(
                ActionPlanEvaluationRequest.from_parts(
                    target_ref,
                    host_profile_id,
                    strategy_id,
                    store_actions_enabled=stored_exports_public_api is not None,
                )
            ).body
        )

    handoff = None
    if handoff_public_api is not None:
        handoff = representation_selection_envelope_to_view_model(
            handoff_public_api.select_representation(
                RepresentationSelectionEvaluationRequest.from_parts(
                    target_ref,
                    host_profile_id,
                    strategy_id,
                )
            ).body
        )

    resolution_actions = None
    if actions_public_api is not None:
        resolution_actions = resolution_actions_envelope_to_view_model(
            actions_public_api.list_resolution_actions(
                ResolutionActionRequest.from_parts(target_ref),
            ).body
        )

    stored_exports = None
    if stored_exports_public_api is not None:
        stored_exports = stored_exports_envelope_to_view_model(
            stored_exports_public_api.list_stored_exports(
                StoredExportsTargetRequest.from_parts(target_ref),
            ).body
        )

    return ResolutionWorkspaceViewModels(
        workbench_session=resolution_job_envelope_to_workbench_session(
            read_response.body,
            session_id=session_id,
        ),
        action_plan=action_plan,
        handoff=handoff,
        resolution_actions=resolution_actions,
        stored_exports=stored_exports,
    )


def _require_non_empty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value
