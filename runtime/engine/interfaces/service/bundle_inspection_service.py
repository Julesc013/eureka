from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from runtime.engine.interfaces.public import Notice, ObjectSummary


@dataclass(frozen=True)
class ResolutionBundleInspectionRequest:
    bundle_path: str | None = None
    bundle_bytes: bytes | None = None
    source_name: str | None = None

    @classmethod
    def from_bundle_path(cls, bundle_path: str) -> "ResolutionBundleInspectionRequest":
        normalized_path = bundle_path.strip()
        if not normalized_path:
            raise ValueError("bundle_path must be a non-empty string.")
        return cls(bundle_path=normalized_path)

    @classmethod
    def from_bundle_bytes(
        cls,
        bundle_bytes: bytes,
        *,
        source_name: str = "resolution_bundle.zip",
    ) -> "ResolutionBundleInspectionRequest":
        if not bundle_bytes:
            raise ValueError("bundle_bytes must be non-empty.")
        normalized_source_name = source_name.strip()
        if not normalized_source_name:
            raise ValueError("source_name must be a non-empty string.")
        return cls(bundle_bytes=bundle_bytes, source_name=normalized_source_name)


@dataclass(frozen=True)
class ResolutionBundleInspectionResult:
    status: str
    source_kind: str
    source_locator: str
    inspected_offline: bool
    bundle_kind: str | None = None
    bundle_version: str | None = None
    target_ref: str | None = None
    primary_object: ObjectSummary | None = None
    member_list: tuple[str, ...] = ()
    normalized_record_summary: dict[str, Any] | None = None
    notices: tuple[Notice, ...] = ()


class ResolutionBundleInspectionService(Protocol):
    def inspect_bundle(
        self,
        request: ResolutionBundleInspectionRequest,
    ) -> ResolutionBundleInspectionResult:
        """Inspect a deterministic resolution bundle from local bytes or a local path."""
