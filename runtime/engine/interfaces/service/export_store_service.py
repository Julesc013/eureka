from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from runtime.engine.interfaces.public.resolution import Notice, ObjectSummary


@dataclass(frozen=True)
class StoredArtifactMetadata:
    artifact_id: str
    artifact_kind: str
    target_ref: str
    content_type: str
    byte_length: int
    store_path: str
    created_by_slice: str
    source_action: str
    resolved_resource_id: str | None = None
    filename: str | None = None
    primary_object: ObjectSummary | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "artifact_id": self.artifact_id,
            "artifact_kind": self.artifact_kind,
            "target_ref": self.target_ref,
            "content_type": self.content_type,
            "byte_length": self.byte_length,
            "store_path": self.store_path,
            "created_by_slice": self.created_by_slice,
            "source_action": self.source_action,
        }
        if self.resolved_resource_id is not None:
            payload["resolved_resource_id"] = self.resolved_resource_id
        if self.filename is not None:
            payload["filename"] = self.filename
        if self.primary_object is not None:
            payload["primary_object"] = self.primary_object.to_dict()
        return payload


@dataclass(frozen=True)
class StoredArtifactWriteResult:
    status: str
    artifact: StoredArtifactMetadata | None = None
    notices: tuple[Notice, ...] = ()


@dataclass(frozen=True)
class StoredArtifactListResult:
    status: str
    target_ref: str
    artifacts: tuple[StoredArtifactMetadata, ...] = ()
    notices: tuple[Notice, ...] = ()


@dataclass(frozen=True)
class StoredArtifactLookupResult:
    status: str
    artifact: StoredArtifactMetadata | None = None
    notices: tuple[Notice, ...] = ()


@dataclass(frozen=True)
class StoredArtifactContentResult:
    status: str
    artifact: StoredArtifactMetadata | None = None
    payload: bytes | None = None
    notices: tuple[Notice, ...] = ()


class ExportStoreService(Protocol):
    def has_manifest_store_available(self, target_ref: str) -> bool:
        """Return whether manifest export can be stored for the target."""

    def has_bundle_store_available(self, target_ref: str) -> bool:
        """Return whether bundle export can be stored for the target."""

    def store_manifest(self, target_ref: str) -> StoredArtifactWriteResult:
        """Store a deterministic manifest export for the target."""

    def store_bundle(self, target_ref: str) -> StoredArtifactWriteResult:
        """Store a deterministic bundle export for the target."""

    def list_artifacts(self, target_ref: str) -> StoredArtifactListResult:
        """List stored artifacts for the target."""

    def get_artifact_metadata(self, artifact_id: str) -> StoredArtifactLookupResult:
        """Return stored metadata for an artifact identity."""

    def get_artifact_content(self, artifact_id: str) -> StoredArtifactContentResult:
        """Return stored bytes plus metadata for an artifact identity."""
