from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.service import (
    ResolutionBundleInspectionRequest,
    ResolutionBundleInspectionService,
)
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


@dataclass(frozen=True)
class InspectResolutionBundleRequest:
    bundle_path: str | None = None
    bundle_bytes: bytes | None = None
    source_name: str | None = None

    @classmethod
    def from_bundle_path(cls, bundle_path: str) -> "InspectResolutionBundleRequest":
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
    ) -> "InspectResolutionBundleRequest":
        if not bundle_bytes:
            raise ValueError("bundle_bytes must be non-empty.")
        normalized_source_name = source_name.strip()
        if not normalized_source_name:
            raise ValueError("source_name must be a non-empty string.")
        return cls(bundle_bytes=bundle_bytes, source_name=normalized_source_name)

    def to_engine_request(self) -> ResolutionBundleInspectionRequest:
        if self.bundle_path is not None:
            return ResolutionBundleInspectionRequest.from_bundle_path(self.bundle_path)
        if self.bundle_bytes is None or self.source_name is None:
            raise ValueError("inspection request must provide either bundle_path or bundle_bytes plus source_name.")
        return ResolutionBundleInspectionRequest.from_bundle_bytes(
            self.bundle_bytes,
            source_name=self.source_name,
        )


class ResolutionBundleInspectionPublicApi:
    def __init__(self, inspection_service: ResolutionBundleInspectionService) -> None:
        self._inspection_service = inspection_service

    def inspect_bundle(self, request: InspectResolutionBundleRequest) -> PublicApiResponse:
        result = self._inspection_service.inspect_bundle(request.to_engine_request())
        return PublicApiResponse(
            status_code=_status_code_for_result(result),
            body=bundle_inspection_result_to_public_envelope(result),
        )


def bundle_inspection_result_to_public_envelope(result) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "status": result.status,
        "inspection_mode": "local_offline" if result.inspected_offline else "unspecified",
        "source": {
            "kind": result.source_kind,
            "locator": result.source_locator,
        },
        "notices": [notice.to_dict() for notice in result.notices],
    }
    if result.resolved_resource_id is not None:
        envelope["resolved_resource_id"] = result.resolved_resource_id
    if result.member_list or result.bundle_kind is not None or result.target_ref is not None:
        bundle_summary: dict[str, Any] = {
            "member_list": list(result.member_list),
        }
        if result.bundle_kind is not None:
            bundle_summary["bundle_kind"] = result.bundle_kind
        if result.bundle_version is not None:
            bundle_summary["bundle_version"] = result.bundle_version
        if result.target_ref is not None:
            bundle_summary["target_ref"] = result.target_ref
        envelope["bundle"] = bundle_summary
    if result.primary_object is not None:
        envelope["primary_object"] = result.primary_object.to_dict()
    if result.evidence:
        envelope["evidence"] = [summary.to_dict() for summary in result.evidence]
    if result.normalized_record_summary is not None:
        envelope["normalized_record"] = dict(result.normalized_record_summary)
    return envelope


def _status_code_for_result(result) -> int:
    if result.status == "inspected":
        return 200
    if not result.notices:
        return 422
    primary_code = result.notices[0].code
    if primary_code == "bundle_path_not_found":
        return 404
    return 422
