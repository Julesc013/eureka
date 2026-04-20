from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from runtime.engine.interfaces.service import ResolutionManifestService
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


EXPORT_RESOLUTION_MANIFEST_ACTION_ID = "export_resolution_manifest"
EXPORT_RESOLUTION_MANIFEST_LABEL = "Export resolution manifest"
EXPORT_RESOLUTION_MANIFEST_ROUTE = "/actions/export-resolution-manifest"


@dataclass(frozen=True)
class ResolutionActionRequest:
    target_ref: str

    @classmethod
    def from_parts(cls, target_ref: str) -> "ResolutionActionRequest":
        normalized_target_ref = target_ref.strip()
        if not normalized_target_ref:
            raise ValueError("target_ref must be a non-empty string.")
        return cls(target_ref=normalized_target_ref)


class ResolutionActionsPublicApi:
    def __init__(self, manifest_service: ResolutionManifestService) -> None:
        self._manifest_service = manifest_service

    def list_resolution_actions(self, request: ResolutionActionRequest) -> PublicApiResponse:
        if self._manifest_service.has_manifest_available(request.target_ref):
            return PublicApiResponse(
                status_code=200,
                body=available_resolution_actions_to_public_envelope(request.target_ref),
            )

        return PublicApiResponse(
            status_code=200,
            body=unavailable_resolution_actions_to_public_envelope(request.target_ref),
        )

    def export_resolution_manifest(self, request: ResolutionActionRequest) -> PublicApiResponse:
        manifest = self._manifest_service.export_manifest(request.target_ref)
        if manifest is None:
            return PublicApiResponse(
                status_code=404,
                body=resolution_manifest_not_available_error(request.target_ref),
            )
        return PublicApiResponse(status_code=200, body=manifest)


def available_resolution_actions_to_public_envelope(target_ref: str) -> dict[str, Any]:
    return {
        "target_ref": target_ref,
        "actions": [
            {
                "action_id": EXPORT_RESOLUTION_MANIFEST_ACTION_ID,
                "label": EXPORT_RESOLUTION_MANIFEST_LABEL,
                "availability": "available",
                "href": _manifest_export_href(target_ref),
            }
        ],
        "notices": [],
    }


def unavailable_resolution_actions_to_public_envelope(target_ref: str) -> dict[str, Any]:
    return {
        "target_ref": target_ref,
        "actions": [
            {
                "action_id": EXPORT_RESOLUTION_MANIFEST_ACTION_ID,
                "label": EXPORT_RESOLUTION_MANIFEST_LABEL,
                "availability": "unavailable",
            }
        ],
        "notices": [
            {
                "code": "resolution_manifest_not_available",
                "severity": "warning",
                "message": f"No resolved synthetic record matched target_ref '{target_ref}'.",
            }
        ],
    }


def resolution_manifest_not_available_error(target_ref: str) -> dict[str, str]:
    return {
        "action_id": EXPORT_RESOLUTION_MANIFEST_ACTION_ID,
        "status": "blocked",
        "target_ref": target_ref,
        "code": "resolution_manifest_not_available",
        "message": f"No resolved synthetic record matched target_ref '{target_ref}'.",
    }


def _manifest_export_href(target_ref: str) -> str:
    return f"{EXPORT_RESOLUTION_MANIFEST_ROUTE}?target_ref={quote(target_ref, safe='')}"
