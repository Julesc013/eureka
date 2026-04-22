from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from runtime.engine.interfaces.service import ResolutionBundleService, ResolutionManifestService
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


EXPORT_RESOLUTION_MANIFEST_ACTION_ID = "export_resolution_manifest"
EXPORT_RESOLUTION_MANIFEST_LABEL = "Export resolution manifest"
EXPORT_RESOLUTION_MANIFEST_ROUTE = "/actions/export-resolution-manifest"
EXPORT_RESOLUTION_BUNDLE_ACTION_ID = "export_resolution_bundle"
EXPORT_RESOLUTION_BUNDLE_LABEL = "Export resolution bundle"
EXPORT_RESOLUTION_BUNDLE_ROUTE = "/actions/export-resolution-bundle"


@dataclass(frozen=True)
class ResolutionActionRequest:
    target_ref: str

    @classmethod
    def from_parts(cls, target_ref: str) -> "ResolutionActionRequest":
        normalized_target_ref = target_ref.strip()
        if not normalized_target_ref:
            raise ValueError("target_ref must be a non-empty string.")
        return cls(target_ref=normalized_target_ref)


@dataclass(frozen=True)
class PublicArtifactResponse:
    status_code: int
    content_type: str
    payload: bytes
    filename: str | None = None

    def json_body(self) -> dict[str, Any]:
        return json.loads(self.payload.decode("utf-8"))


class ResolutionActionsPublicApi:
    def __init__(
        self,
        *,
        manifest_service: ResolutionManifestService,
        bundle_service: ResolutionBundleService,
    ) -> None:
        self._manifest_service = manifest_service
        self._bundle_service = bundle_service

    def list_resolution_actions(self, request: ResolutionActionRequest) -> PublicApiResponse:
        manifest_available = self._manifest_service.has_manifest_available(request.target_ref)
        bundle_available = self._bundle_service.has_bundle_available(request.target_ref)
        manifest = self._manifest_service.export_manifest(request.target_ref) if manifest_available else None
        return PublicApiResponse(
            status_code=200,
            body=resolution_actions_to_public_envelope(
                request.target_ref,
                manifest_available=manifest_available,
                bundle_available=bundle_available,
                resolved_resource_id=_manifest_resolved_resource_id(manifest),
            ),
        )

    def export_resolution_manifest(self, request: ResolutionActionRequest) -> PublicApiResponse:
        manifest = self._manifest_service.export_manifest(request.target_ref)
        if manifest is None:
            return PublicApiResponse(
                status_code=404,
                body=resolution_manifest_not_available_error(request.target_ref),
            )
        return PublicApiResponse(status_code=200, body=manifest)

    def export_resolution_bundle(self, request: ResolutionActionRequest) -> PublicArtifactResponse:
        bundle = self._bundle_service.export_bundle(request.target_ref)
        if bundle is None:
            return PublicArtifactResponse(
                status_code=404,
                content_type="application/json; charset=utf-8",
                payload=_json_bytes(resolution_bundle_not_available_error(request.target_ref)),
            )
        return PublicArtifactResponse(
            status_code=200,
            content_type=bundle.content_type,
            payload=bundle.payload,
            filename=bundle.filename,
        )

def resolution_actions_to_public_envelope(
    target_ref: str,
    *,
    manifest_available: bool,
    bundle_available: bool,
    resolved_resource_id: str | None = None,
) -> dict[str, Any]:
    actions = [
        _manifest_action_entry(target_ref, available=manifest_available),
        _bundle_action_entry(target_ref, available=bundle_available),
    ]
    notices: list[dict[str, str]] = []
    if not manifest_available:
        notices.append(_manifest_not_available_notice(target_ref))
    if not bundle_available:
        notices.append(_bundle_not_available_notice(target_ref))
    envelope = {
        "target_ref": target_ref,
        "actions": actions,
        "notices": notices,
    }
    if resolved_resource_id is not None:
        envelope["resolved_resource_id"] = resolved_resource_id
    return envelope


def available_resolution_actions_to_public_envelope(target_ref: str) -> dict[str, Any]:
    return resolution_actions_to_public_envelope(
        target_ref,
        manifest_available=True,
        bundle_available=True,
    )


def unavailable_resolution_actions_to_public_envelope(target_ref: str) -> dict[str, Any]:
    return resolution_actions_to_public_envelope(
        target_ref,
        manifest_available=False,
        bundle_available=False,
    )


def resolution_manifest_not_available_error(target_ref: str) -> dict[str, str]:
    return {
        "action_id": EXPORT_RESOLUTION_MANIFEST_ACTION_ID,
        "status": "blocked",
        "target_ref": target_ref,
        "code": "resolution_manifest_not_available",
        "message": f"No resolved bounded record matched target_ref '{target_ref}'.",
    }


def resolution_bundle_not_available_error(target_ref: str) -> dict[str, str]:
    return {
        "action_id": EXPORT_RESOLUTION_BUNDLE_ACTION_ID,
        "status": "blocked",
        "target_ref": target_ref,
        "code": "resolution_bundle_not_available",
        "message": f"No resolved bounded record matched target_ref '{target_ref}'.",
    }


def _manifest_export_href(target_ref: str) -> str:
    return f"{EXPORT_RESOLUTION_MANIFEST_ROUTE}?target_ref={quote(target_ref, safe='')}"


def _bundle_export_href(target_ref: str) -> str:
    return f"{EXPORT_RESOLUTION_BUNDLE_ROUTE}?target_ref={quote(target_ref, safe='')}"


def _manifest_action_entry(target_ref: str, *, available: bool) -> dict[str, str]:
    action = {
        "action_id": EXPORT_RESOLUTION_MANIFEST_ACTION_ID,
        "label": EXPORT_RESOLUTION_MANIFEST_LABEL,
        "availability": "available" if available else "unavailable",
    }
    if available:
        action["href"] = _manifest_export_href(target_ref)
    return action


def _bundle_action_entry(target_ref: str, *, available: bool) -> dict[str, str]:
    action = {
        "action_id": EXPORT_RESOLUTION_BUNDLE_ACTION_ID,
        "label": EXPORT_RESOLUTION_BUNDLE_LABEL,
        "availability": "available" if available else "unavailable",
    }
    if available:
        action["href"] = _bundle_export_href(target_ref)
    return action


def _manifest_not_available_notice(target_ref: str) -> dict[str, str]:
    return {
        "code": "resolution_manifest_not_available",
        "severity": "warning",
        "message": f"No resolved bounded record matched target_ref '{target_ref}'.",
    }


def _bundle_not_available_notice(target_ref: str) -> dict[str, str]:
    return {
        "code": "resolution_bundle_not_available",
        "severity": "warning",
        "message": f"No resolved bounded record matched target_ref '{target_ref}'.",
    }


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return f"{json.dumps(payload, indent=2, sort_keys=True)}\n".encode("utf-8")


def _manifest_resolved_resource_id(manifest: dict[str, Any] | None) -> str | None:
    if not isinstance(manifest, dict):
        return None
    resolved_resource_id = manifest.get("resolved_resource_id")
    if not isinstance(resolved_resource_id, str) or not resolved_resource_id:
        return None
    return resolved_resource_id
