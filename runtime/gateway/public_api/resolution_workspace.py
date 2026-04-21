from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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
    resolution_actions: dict[str, Any] | None = None
    stored_exports: dict[str, Any] | None = None


class ResolutionWorkspaceReadError(LookupError):
    """Raised when a submitted resolution job cannot be read back."""


def build_resolution_workspace_view_models(
    resolution_public_api: ResolutionJobsPublicApi,
    target_ref: str,
    *,
    actions_public_api: ResolutionActionsPublicApi | None = None,
    stored_exports_public_api: StoredExportsPublicApi | None = None,
    session_id: str,
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
        resolution_actions=resolution_actions,
        stored_exports=stored_exports,
    )


def _require_non_empty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value
