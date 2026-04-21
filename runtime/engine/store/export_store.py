from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from runtime.engine.interfaces.public.resolution import Notice, ObjectSummary
from runtime.engine.interfaces.service.action_service import ResolutionManifestService
from runtime.engine.interfaces.service.bundle_service import ResolutionBundleService
from runtime.engine.interfaces.service.export_store_service import (
    StoredArtifactContentResult,
    StoredArtifactListResult,
    StoredArtifactLookupResult,
    StoredArtifactMetadata,
    StoredArtifactWriteResult,
)
from runtime.engine.store.artifact_identity import (
    artifact_id_for_bytes,
    artifact_id_to_metadata_relpath,
    artifact_id_to_object_relpath,
    target_ref_to_index_relpath,
)


class ExportStoreDataError(RuntimeError):
    def __init__(self, *, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class LocalExportStore:
    def __init__(self, store_root: Path | str) -> None:
        root = Path(store_root)
        self._store_root = root.resolve()

    @property
    def store_root(self) -> Path:
        return self._store_root

    def store_artifact(
        self,
        *,
        artifact_kind: str,
        target_ref: str,
        resolved_resource_id: str | None = None,
        content_type: str,
        payload: bytes,
        source_action: str,
        filename: str | None = None,
        primary_object: ObjectSummary | None = None,
    ) -> StoredArtifactMetadata:
        if not artifact_kind:
            raise ValueError("artifact_kind must be a non-empty string.")
        if not target_ref.strip():
            raise ValueError("target_ref must be a non-empty string.")
        if not content_type.strip():
            raise ValueError("content_type must be a non-empty string.")
        if not source_action.strip():
            raise ValueError("source_action must be a non-empty string.")

        artifact_id = artifact_id_for_bytes(payload)
        object_relpath = artifact_id_to_object_relpath(artifact_id)
        object_path = self._store_root / Path(object_relpath)
        metadata = StoredArtifactMetadata(
            artifact_id=artifact_id,
            artifact_kind=artifact_kind,
            target_ref=target_ref,
            resolved_resource_id=resolved_resource_id,
            content_type=content_type,
            byte_length=len(payload),
            store_path=object_relpath.replace("\\", "/"),
            created_by_slice="local_export_store",
            source_action=source_action,
            filename=filename,
            primary_object=primary_object,
        )

        _write_bytes_if_missing(object_path, payload)
        self._write_metadata(metadata)
        self._write_target_index(target_ref, artifact_id)
        return metadata

    def get_artifact_metadata(self, artifact_id: str) -> StoredArtifactMetadata | None:
        metadata_path = self._store_root / Path(artifact_id_to_metadata_relpath(artifact_id))
        object_path = self._store_root / Path(artifact_id_to_object_relpath(artifact_id))
        if not metadata_path.exists():
            if object_path.exists():
                raise ExportStoreDataError(
                    code="stored_artifact_metadata_missing",
                    message=f"Store metadata for artifact_id '{artifact_id}' is missing.",
                )
            return None
        payload = _load_json(metadata_path, code="stored_artifact_metadata_invalid")
        metadata = _stored_artifact_metadata_from_dict(payload)
        if metadata.artifact_id != artifact_id:
            raise ExportStoreDataError(
                code="stored_artifact_metadata_invalid",
                message=f"Store metadata for artifact_id '{artifact_id}' did not round-trip cleanly.",
            )
        return metadata

    def get_artifact_bytes(self, artifact_id: str) -> bytes | None:
        metadata = self.get_artifact_metadata(artifact_id)
        if metadata is None:
            return None
        object_path = self._store_root / Path(metadata.store_path)
        if not object_path.exists():
            raise ExportStoreDataError(
                code="stored_artifact_bytes_missing",
                message=f"Stored object payload for artifact_id '{artifact_id}' is missing.",
            )
        return object_path.read_bytes()

    def list_artifacts_for_target(self, target_ref: str) -> tuple[StoredArtifactMetadata, ...]:
        index_path = self._store_root / Path(target_ref_to_index_relpath(target_ref))
        if not index_path.exists():
            return ()

        payload = _load_json(index_path, code="stored_artifact_index_invalid")
        if not isinstance(payload, dict):
            raise ExportStoreDataError(
                code="stored_artifact_index_invalid",
                message=f"Target index for '{target_ref}' must be a JSON object.",
            )
        index_target_ref = _require_string(payload.get("target_ref"), "target index.target_ref")
        if index_target_ref != target_ref:
            raise ExportStoreDataError(
                code="stored_artifact_index_invalid",
                message=f"Target index for '{target_ref}' contains mismatched target_ref '{index_target_ref}'.",
            )
        raw_artifact_ids = payload.get("artifact_ids")
        if not isinstance(raw_artifact_ids, list):
            raise ExportStoreDataError(
                code="stored_artifact_index_invalid",
                message=f"Target index for '{target_ref}' must contain an artifact_ids list.",
            )

        artifacts: list[StoredArtifactMetadata] = []
        for index, item in enumerate(raw_artifact_ids):
            artifact_id = _require_string(item, f"target index.artifact_ids[{index}]")
            metadata = self.get_artifact_metadata(artifact_id)
            if metadata is None:
                raise ExportStoreDataError(
                    code="stored_artifact_metadata_missing",
                    message=f"Target index for '{target_ref}' references missing artifact_id '{artifact_id}'.",
                )
            artifacts.append(metadata)
        artifacts.sort(key=lambda artifact: (artifact.artifact_kind, artifact.artifact_id))
        return tuple(artifacts)

    def _write_metadata(self, metadata: StoredArtifactMetadata) -> None:
        metadata_path = self._store_root / Path(artifact_id_to_metadata_relpath(metadata.artifact_id))
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_bytes(_json_bytes(metadata.to_dict()))

    def _write_target_index(self, target_ref: str, artifact_id: str) -> None:
        index_path = self._store_root / Path(target_ref_to_index_relpath(target_ref))
        index_path.parent.mkdir(parents=True, exist_ok=True)

        artifact_ids: list[str] = []
        if index_path.exists():
            payload = _load_json(index_path, code="stored_artifact_index_invalid")
            if not isinstance(payload, dict):
                raise ExportStoreDataError(
                    code="stored_artifact_index_invalid",
                    message=f"Target index for '{target_ref}' must be a JSON object.",
                )
            raw_artifact_ids = payload.get("artifact_ids")
            if not isinstance(raw_artifact_ids, list):
                raise ExportStoreDataError(
                    code="stored_artifact_index_invalid",
                    message=f"Target index for '{target_ref}' must contain an artifact_ids list.",
                )
            artifact_ids = [_require_string(item, "target index.artifact_ids[]") for item in raw_artifact_ids]

        if artifact_id not in artifact_ids:
            artifact_ids.append(artifact_id)
        artifact_ids.sort()
        index_path.write_bytes(
            _json_bytes(
                {
                    "target_ref": target_ref,
                    "artifact_ids": artifact_ids,
                }
            )
        )


class ResolutionExportStoreEngineService:
    def __init__(
        self,
        *,
        manifest_service: ResolutionManifestService,
        bundle_service: ResolutionBundleService,
        store: LocalExportStore,
    ) -> None:
        self._manifest_service = manifest_service
        self._bundle_service = bundle_service
        self._store = store

    def has_manifest_store_available(self, target_ref: str) -> bool:
        return self._manifest_service.has_manifest_available(target_ref)

    def has_bundle_store_available(self, target_ref: str) -> bool:
        return self._bundle_service.has_bundle_available(target_ref)

    def store_manifest(self, target_ref: str) -> StoredArtifactWriteResult:
        manifest = self._manifest_service.export_manifest(target_ref)
        if manifest is None:
            return StoredArtifactWriteResult(
                status="blocked",
                notices=(
                    Notice(
                        code="store_resolution_manifest_not_available",
                        severity="warning",
                        message=f"No resolved synthetic record matched target_ref '{target_ref}'.",
                    ),
                ),
            )
        try:
            artifact = self._store.store_artifact(
                artifact_kind="resolution_manifest",
                target_ref=target_ref,
                resolved_resource_id=_manifest_resolved_resource_id(manifest),
                content_type="application/json; charset=utf-8",
                payload=_json_bytes(manifest),
                source_action="store_resolution_manifest",
                filename=_manifest_filename(target_ref),
                primary_object=_manifest_primary_object(manifest),
            )
        except ExportStoreDataError as error:
            return StoredArtifactWriteResult(status="blocked", notices=(_store_error_notice(error),))
        return StoredArtifactWriteResult(status="stored", artifact=artifact)

    def store_bundle(self, target_ref: str) -> StoredArtifactWriteResult:
        bundle = self._bundle_service.export_bundle(target_ref)
        if bundle is None:
            return StoredArtifactWriteResult(
                status="blocked",
                notices=(
                    Notice(
                        code="store_resolution_bundle_not_available",
                        severity="warning",
                        message=f"No resolved synthetic record matched target_ref '{target_ref}'.",
                    ),
                ),
            )
        manifest = self._manifest_service.export_manifest(target_ref)
        try:
            artifact = self._store.store_artifact(
                artifact_kind="resolution_bundle",
                target_ref=target_ref,
                resolved_resource_id=_manifest_resolved_resource_id(manifest),
                content_type=bundle.content_type,
                payload=bundle.payload,
                source_action="store_resolution_bundle",
                filename=bundle.filename,
                primary_object=_manifest_primary_object(manifest) if manifest is not None else None,
            )
        except ExportStoreDataError as error:
            return StoredArtifactWriteResult(status="blocked", notices=(_store_error_notice(error),))
        return StoredArtifactWriteResult(status="stored", artifact=artifact)

    def list_artifacts(self, target_ref: str) -> StoredArtifactListResult:
        try:
            artifacts = self._store.list_artifacts_for_target(target_ref)
        except ExportStoreDataError as error:
            return StoredArtifactListResult(
                status="blocked",
                target_ref=target_ref,
                notices=(_store_error_notice(error),),
            )

        if artifacts:
            return StoredArtifactListResult(
                status="available",
                target_ref=target_ref,
                artifacts=artifacts,
            )
        if self.has_manifest_store_available(target_ref) or self.has_bundle_store_available(target_ref):
            return StoredArtifactListResult(status="available", target_ref=target_ref, artifacts=())
        return StoredArtifactListResult(
            status="blocked",
            target_ref=target_ref,
            notices=(
                Notice(
                    code="stored_exports_target_not_available",
                    severity="warning",
                    message=f"No resolved synthetic record matched target_ref '{target_ref}'.",
                ),
            ),
        )

    def get_artifact_metadata(self, artifact_id: str) -> StoredArtifactLookupResult:
        try:
            artifact = self._store.get_artifact_metadata(artifact_id)
        except ValueError:
            return StoredArtifactLookupResult(
                status="blocked",
                notices=(
                    Notice(
                        code="stored_artifact_id_invalid",
                        severity="error",
                        message="artifact_id must match 'sha256:<64 lowercase hex characters>'.",
                    ),
                ),
            )
        except ExportStoreDataError as error:
            return StoredArtifactLookupResult(status="blocked", notices=(_store_error_notice(error),))
        if artifact is None:
            return StoredArtifactLookupResult(
                status="blocked",
                notices=(
                    Notice(
                        code="stored_artifact_not_found",
                        severity="error",
                        message=f"Unknown stored artifact_id '{artifact_id}'.",
                    ),
                ),
            )
        return StoredArtifactLookupResult(status="available", artifact=artifact)

    def get_artifact_content(self, artifact_id: str) -> StoredArtifactContentResult:
        try:
            artifact = self._store.get_artifact_metadata(artifact_id)
            if artifact is None:
                return StoredArtifactContentResult(
                    status="blocked",
                    notices=(
                        Notice(
                            code="stored_artifact_not_found",
                            severity="error",
                            message=f"Unknown stored artifact_id '{artifact_id}'.",
                        ),
                    ),
                )
            payload = self._store.get_artifact_bytes(artifact_id)
        except ValueError:
            return StoredArtifactContentResult(
                status="blocked",
                notices=(
                    Notice(
                        code="stored_artifact_id_invalid",
                        severity="error",
                        message="artifact_id must match 'sha256:<64 lowercase hex characters>'.",
                    ),
                ),
            )
        except ExportStoreDataError as error:
            return StoredArtifactContentResult(status="blocked", notices=(_store_error_notice(error),))
        if payload is None:
            return StoredArtifactContentResult(
                status="blocked",
                notices=(
                    Notice(
                        code="stored_artifact_not_found",
                        severity="error",
                        message=f"Unknown stored artifact_id '{artifact_id}'.",
                    ),
                ),
            )
        return StoredArtifactContentResult(status="available", artifact=artifact, payload=payload)


def _write_bytes_if_missing(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_bytes()
        if existing != payload:
            raise ExportStoreDataError(
                code="stored_artifact_payload_mismatch",
                message=f"Existing store object at '{path}' does not match the expected payload.",
            )
        return
    path.write_bytes(payload)


def _stored_artifact_metadata_from_dict(payload: Any) -> StoredArtifactMetadata:
    if not isinstance(payload, dict):
        raise ExportStoreDataError(
            code="stored_artifact_metadata_invalid",
            message="Stored artifact metadata must be a JSON object.",
        )
    primary_object_payload = payload.get("primary_object")
    primary_object = None
    if primary_object_payload is not None:
        if not isinstance(primary_object_payload, dict):
            raise ExportStoreDataError(
                code="stored_artifact_metadata_invalid",
                message="stored_artifact.primary_object must be a JSON object when provided.",
            )
        primary_object = ObjectSummary(
            id=_require_string(primary_object_payload.get("id"), "stored_artifact.primary_object.id"),
            kind=_optional_string(primary_object_payload.get("kind"), "stored_artifact.primary_object.kind"),
            label=_optional_string(primary_object_payload.get("label"), "stored_artifact.primary_object.label"),
        )

    return StoredArtifactMetadata(
        artifact_id=_require_string(payload.get("artifact_id"), "stored_artifact.artifact_id"),
        artifact_kind=_require_string(payload.get("artifact_kind"), "stored_artifact.artifact_kind"),
        target_ref=_require_string(payload.get("target_ref"), "stored_artifact.target_ref"),
        resolved_resource_id=_optional_string(
            payload.get("resolved_resource_id"),
            "stored_artifact.resolved_resource_id",
        ),
        content_type=_require_string(payload.get("content_type"), "stored_artifact.content_type"),
        byte_length=_require_int(payload.get("byte_length"), "stored_artifact.byte_length"),
        store_path=_require_string(payload.get("store_path"), "stored_artifact.store_path"),
        created_by_slice=_require_string(payload.get("created_by_slice"), "stored_artifact.created_by_slice"),
        source_action=_require_string(payload.get("source_action"), "stored_artifact.source_action"),
        filename=_optional_string(payload.get("filename"), "stored_artifact.filename"),
        primary_object=primary_object,
    )


def _load_json(path: Path, *, code: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ExportStoreDataError(code=code, message=str(error)) from error
    except json.JSONDecodeError as error:
        raise ExportStoreDataError(code=code, message=f"Invalid JSON at '{path}': {error.msg}.") from error


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return f"{json.dumps(payload, indent=2, sort_keys=True)}\n".encode("utf-8")


def _manifest_primary_object(manifest: dict[str, Any]) -> ObjectSummary | None:
    primary_object = manifest.get("primary_object")
    if not isinstance(primary_object, dict):
        return None
    object_id = primary_object.get("id")
    if not isinstance(object_id, str) or not object_id:
        return None
    object_kind = primary_object.get("kind")
    object_label = primary_object.get("label")
    return ObjectSummary(
        id=object_id,
        kind=object_kind if isinstance(object_kind, str) and object_kind else None,
        label=object_label if isinstance(object_label, str) and object_label else None,
    )


def _manifest_resolved_resource_id(manifest: dict[str, Any]) -> str | None:
    resolved_resource_id = manifest.get("resolved_resource_id")
    if not isinstance(resolved_resource_id, str) or not resolved_resource_id:
        return None
    return resolved_resource_id


def _manifest_filename(target_ref: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9.]+", "-", target_ref).strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    return f"eureka-resolution-manifest-{normalized}.json"


def _store_error_notice(error: ExportStoreDataError) -> Notice:
    return Notice(code=error.code, severity="error", message=error.message)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ExportStoreDataError(
            code="stored_artifact_metadata_invalid",
            message=f"{field_name} must be a non-empty string.",
        )
    return value


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name)


def _require_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise ExportStoreDataError(
            code="stored_artifact_metadata_invalid",
            message=f"{field_name} must be a non-negative integer.",
        )
    return value
