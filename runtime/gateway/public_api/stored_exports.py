from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from runtime.engine.interfaces.public.resolution import Notice
from runtime.engine.interfaces.service import ExportStoreService, StoredArtifactMetadata
from runtime.gateway.public_api.resolution_actions import PublicArtifactResponse
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


STORE_RESOLUTION_MANIFEST_ACTION_ID = "store_resolution_manifest"
STORE_RESOLUTION_MANIFEST_LABEL = "Store resolution manifest locally"
STORE_RESOLUTION_MANIFEST_ROUTE = "/store/manifest"
STORE_RESOLUTION_BUNDLE_ACTION_ID = "store_resolution_bundle"
STORE_RESOLUTION_BUNDLE_LABEL = "Store resolution bundle locally"
STORE_RESOLUTION_BUNDLE_ROUTE = "/store/bundle"
STORED_ARTIFACT_ROUTE = "/stored/artifact"


@dataclass(frozen=True)
class StoredExportsTargetRequest:
    target_ref: str

    @classmethod
    def from_parts(cls, target_ref: str) -> "StoredExportsTargetRequest":
        normalized_target_ref = target_ref.strip()
        if not normalized_target_ref:
            raise ValueError("target_ref must be a non-empty string.")
        return cls(target_ref=normalized_target_ref)


@dataclass(frozen=True)
class StoredArtifactRequest:
    artifact_id: str

    @classmethod
    def from_parts(cls, artifact_id: str) -> "StoredArtifactRequest":
        normalized_artifact_id = artifact_id.strip()
        if not normalized_artifact_id:
            raise ValueError("artifact_id must be a non-empty string.")
        return cls(artifact_id=normalized_artifact_id)


class StoredExportsPublicApi:
    def __init__(self, store_service: ExportStoreService) -> None:
        self._store_service = store_service

    def list_stored_exports(self, request: StoredExportsTargetRequest) -> PublicApiResponse:
        result = self._store_service.list_artifacts(request.target_ref)
        status_code = 200 if result.status == "available" else 404
        body = stored_exports_to_public_envelope(
            request.target_ref,
            manifest_store_available=self._store_service.has_manifest_store_available(request.target_ref),
            bundle_store_available=self._store_service.has_bundle_store_available(request.target_ref),
            artifacts=result.artifacts,
            notices=result.notices,
        )
        return PublicApiResponse(status_code=status_code, body=body)

    def store_resolution_manifest(self, request: StoredExportsTargetRequest) -> PublicApiResponse:
        result = self._store_service.store_manifest(request.target_ref)
        if result.artifact is None:
            return PublicApiResponse(
                status_code=404,
                body=_blocked_store_action_envelope(
                    action_id=STORE_RESOLUTION_MANIFEST_ACTION_ID,
                    target_ref=request.target_ref,
                    notices=result.notices,
                ),
            )
        return PublicApiResponse(
            status_code=200,
            body={
                "status": "stored",
                "artifact": result.artifact.to_dict(),
                "notices": [notice.to_dict() for notice in result.notices],
            },
        )

    def store_resolution_bundle(self, request: StoredExportsTargetRequest) -> PublicApiResponse:
        result = self._store_service.store_bundle(request.target_ref)
        if result.artifact is None:
            return PublicApiResponse(
                status_code=404,
                body=_blocked_store_action_envelope(
                    action_id=STORE_RESOLUTION_BUNDLE_ACTION_ID,
                    target_ref=request.target_ref,
                    notices=result.notices,
                ),
            )
        return PublicApiResponse(
            status_code=200,
            body={
                "status": "stored",
                "artifact": result.artifact.to_dict(),
                "notices": [notice.to_dict() for notice in result.notices],
            },
        )

    def get_stored_artifact_metadata(self, request: StoredArtifactRequest) -> PublicApiResponse:
        result = self._store_service.get_artifact_metadata(request.artifact_id)
        if result.artifact is None:
            return PublicApiResponse(
                status_code=404,
                body=stored_artifact_not_found_envelope(request.artifact_id, result.notices),
            )
        return PublicApiResponse(
            status_code=200,
            body={
                "status": "available",
                "artifact": result.artifact.to_dict(),
                "notices": [notice.to_dict() for notice in result.notices],
            },
        )

    def get_stored_artifact_content(self, request: StoredArtifactRequest) -> PublicArtifactResponse:
        result = self._store_service.get_artifact_content(request.artifact_id)
        if result.artifact is None or result.payload is None:
            return PublicArtifactResponse(
                status_code=404,
                content_type="application/json; charset=utf-8",
                payload=_json_bytes(stored_artifact_not_found_envelope(request.artifact_id, result.notices)),
            )
        return PublicArtifactResponse(
            status_code=200,
            content_type=result.artifact.content_type,
            payload=result.payload,
            filename=result.artifact.filename,
        )


def stored_exports_to_public_envelope(
    target_ref: str,
    *,
    manifest_store_available: bool,
    bundle_store_available: bool,
    artifacts: tuple[StoredArtifactMetadata, ...],
    notices: tuple[Notice, ...],
) -> dict[str, Any]:
    envelope_notices = [notice.to_dict() for notice in notices]
    if not manifest_store_available:
        envelope_notices.append(_store_manifest_not_available_notice(target_ref).to_dict())
    if not bundle_store_available:
        envelope_notices.append(_store_bundle_not_available_notice(target_ref).to_dict())

    envelope = {
        "target_ref": target_ref,
        "store_actions": [
            _store_manifest_action_entry(target_ref, available=manifest_store_available),
            _store_bundle_action_entry(target_ref, available=bundle_store_available),
        ],
        "artifacts": [_stored_artifact_entry(artifact) for artifact in artifacts],
        "notices": envelope_notices,
    }
    resolved_resource_id = _resolved_resource_id_for_artifacts(artifacts)
    if resolved_resource_id is not None:
        envelope["resolved_resource_id"] = resolved_resource_id
    return envelope


def stored_artifact_not_found_envelope(
    artifact_id: str,
    notices: tuple[Notice, ...],
) -> dict[str, Any]:
    primary_notice = notices[0] if notices else Notice(
        code="stored_artifact_not_found",
        severity="error",
        message=f"Unknown stored artifact_id '{artifact_id}'.",
    )
    return {
        "artifact_id": artifact_id,
        "status": "blocked",
        "code": primary_notice.code,
        "message": primary_notice.message,
        "notices": [notice.to_dict() for notice in notices],
    }


def _blocked_store_action_envelope(
    *,
    action_id: str,
    target_ref: str,
    notices: tuple[Notice, ...],
) -> dict[str, Any]:
    primary_notice = notices[0] if notices else Notice(
        code=f"{action_id}_not_available",
        severity="warning",
        message=f"No resolved synthetic record matched target_ref '{target_ref}'.",
    )
    return {
        "action_id": action_id,
        "status": "blocked",
        "target_ref": target_ref,
        "code": primary_notice.code,
        "message": primary_notice.message,
        "notices": [notice.to_dict() for notice in notices],
    }


def _store_manifest_action_entry(target_ref: str, *, available: bool) -> dict[str, str]:
    action = {
        "action_id": STORE_RESOLUTION_MANIFEST_ACTION_ID,
        "label": STORE_RESOLUTION_MANIFEST_LABEL,
        "availability": "available" if available else "unavailable",
    }
    if available:
        action["href"] = f"{STORE_RESOLUTION_MANIFEST_ROUTE}?target_ref={quote(target_ref, safe='')}"
    return action


def _store_bundle_action_entry(target_ref: str, *, available: bool) -> dict[str, str]:
    action = {
        "action_id": STORE_RESOLUTION_BUNDLE_ACTION_ID,
        "label": STORE_RESOLUTION_BUNDLE_LABEL,
        "availability": "available" if available else "unavailable",
    }
    if available:
        action["href"] = f"{STORE_RESOLUTION_BUNDLE_ROUTE}?target_ref={quote(target_ref, safe='')}"
    return action


def _stored_artifact_entry(artifact: StoredArtifactMetadata) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "artifact_id": artifact.artifact_id,
        "artifact_kind": artifact.artifact_kind,
        "content_type": artifact.content_type,
        "byte_length": artifact.byte_length,
        "availability": "available",
        "href": f"{STORED_ARTIFACT_ROUTE}?artifact_id={quote(artifact.artifact_id, safe='')}",
    }
    if artifact.resolved_resource_id is not None:
        entry["resolved_resource_id"] = artifact.resolved_resource_id
    if artifact.filename is not None:
        entry["filename"] = artifact.filename
    return entry


def _store_manifest_not_available_notice(target_ref: str) -> Notice:
    return Notice(
        code="store_resolution_manifest_not_available",
        severity="warning",
        message=f"No resolved synthetic record matched target_ref '{target_ref}'.",
    )


def _store_bundle_not_available_notice(target_ref: str) -> Notice:
    return Notice(
        code="store_resolution_bundle_not_available",
        severity="warning",
        message=f"No resolved synthetic record matched target_ref '{target_ref}'.",
    )


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return f"{json.dumps(payload, indent=2, sort_keys=True)}\n".encode("utf-8")


def _resolved_resource_id_for_artifacts(artifacts: tuple[StoredArtifactMetadata, ...]) -> str | None:
    for artifact in artifacts:
        if artifact.resolved_resource_id is not None:
            return artifact.resolved_resource_id
    return None
