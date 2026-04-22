from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
import zipfile

from runtime.engine.provenance import EvidenceSummary
from runtime.engine.interfaces.public import Notice, ObjectSummary
from runtime.engine.interfaces.service import (
    ResolutionBundleInspectionRequest,
    ResolutionBundleInspectionResult,
)
from runtime.engine.snapshots.resolution_bundle import RESOLUTION_BUNDLE_MEMBER_ORDER


_REQUIRED_BUNDLE_MEMBERS = (
    "bundle.json",
    "manifest.json",
    "records/normalized_record.json",
)


class ResolutionBundleInspectionEngineService:
    def inspect_bundle(
        self,
        request: ResolutionBundleInspectionRequest,
    ) -> ResolutionBundleInspectionResult:
        if request.bundle_path is not None:
            return self._inspect_bundle_path(request.bundle_path)
        if request.bundle_bytes is None or request.source_name is None:
            raise ValueError("inspection request must provide either bundle_path or bundle_bytes plus source_name.")
        return self._inspect_bundle_bytes(
            bundle_bytes=request.bundle_bytes,
            source_kind="inline_bytes",
            source_locator=request.source_name,
        )

    def _inspect_bundle_path(self, bundle_path: str) -> ResolutionBundleInspectionResult:
        path = Path(bundle_path)
        if not path.is_file():
            return _blocked_result(
                source_kind="local_path",
                source_locator=str(path),
                code="bundle_path_not_found",
                message=f"Bundle path '{path}' was not found.",
            )

        try:
            payload = path.read_bytes()
        except OSError as exc:
            return _blocked_result(
                source_kind="local_path",
                source_locator=str(path),
                code="bundle_path_unreadable",
                message=f"Bundle path '{path}' could not be read: {exc}.",
            )

        return self._inspect_bundle_bytes(
            bundle_bytes=payload,
            source_kind="local_path",
            source_locator=str(path),
        )

    def _inspect_bundle_bytes(
        self,
        *,
        bundle_bytes: bytes,
        source_kind: str,
        source_locator: str,
    ) -> ResolutionBundleInspectionResult:
        try:
            with zipfile.ZipFile(BytesIO(bundle_bytes)) as bundle:
                member_list = tuple(bundle.namelist())
                missing_members = [name for name in _REQUIRED_BUNDLE_MEMBERS if name not in member_list]
                if missing_members:
                    return _blocked_result(
                        source_kind=source_kind,
                        source_locator=source_locator,
                        code="bundle_member_missing",
                        message=(
                            "Bundle is missing expected members: "
                            + ", ".join(missing_members)
                            + "."
                        ),
                        member_list=member_list,
                    )

                try:
                    bundle_metadata = _read_json_member(bundle, "bundle.json")
                    manifest = _read_json_member(bundle, "manifest.json")
                    normalized_record = _read_json_member(bundle, "records/normalized_record.json")
                except _BundleMemberJsonError as exc:
                    return _blocked_result(
                        source_kind=source_kind,
                        source_locator=source_locator,
                        code="bundle_member_invalid_json",
                        message=f"Bundle member '{exc.member_name}' contains invalid JSON: {exc.reason}.",
                        member_list=member_list,
                    )
        except zipfile.BadZipFile:
            return _blocked_result(
                source_kind=source_kind,
                source_locator=source_locator,
                code="bundle_archive_invalid",
                message="Bundle payload is not a valid ZIP archive.",
            )

        try:
            bundle_kind = _require_string(bundle_metadata.get("bundle_kind"), "bundle.json.bundle_kind")
            bundle_version = _require_string(bundle_metadata.get("bundle_version"), "bundle.json.bundle_version")
            target_ref = _require_string(bundle_metadata.get("target_ref"), "bundle.json.target_ref")
            resolved_resource_id = _require_string(
                bundle_metadata.get("resolved_resource_id"),
                "bundle.json.resolved_resource_id",
            )
            manifest_kind = _require_string(manifest.get("manifest_kind"), "manifest.json.manifest_kind")
            manifest_resolved_resource_id = _require_string(
                manifest.get("resolved_resource_id"),
                "manifest.json.resolved_resource_id",
            )
            primary_object = _coerce_primary_object(manifest.get("primary_object"))
            manifest_evidence = _coerce_evidence_list(manifest.get("evidence"), "manifest.json.evidence")
            normalized_record_summary = _coerce_normalized_record_summary(normalized_record)
            record_evidence = _coerce_evidence_list(
                normalized_record_summary.get("evidence"),
                "records/normalized_record.json.evidence",
            )
        except ValueError as exc:
            return _blocked_result(
                source_kind=source_kind,
                source_locator=source_locator,
                code="bundle_structure_invalid",
                message=str(exc),
                member_list=member_list,
            )

        if bundle_kind != "eureka.resolution_bundle":
            return _blocked_result(
                source_kind=source_kind,
                source_locator=source_locator,
                code="bundle_structure_invalid",
                message="bundle.json.bundle_kind must equal 'eureka.resolution_bundle'.",
                member_list=member_list,
            )
        if manifest_kind != "eureka.resolution_manifest":
            return _blocked_result(
                source_kind=source_kind,
                source_locator=source_locator,
                code="bundle_structure_invalid",
                message="manifest.json.manifest_kind must equal 'eureka.resolution_manifest'.",
                member_list=member_list,
            )
        if manifest_resolved_resource_id != resolved_resource_id:
            return _blocked_result(
                source_kind=source_kind,
                source_locator=source_locator,
                code="bundle_structure_invalid",
                message="bundle.json.resolved_resource_id and manifest.json.resolved_resource_id must match.",
                member_list=member_list,
            )
        if manifest_evidence and record_evidence and manifest_evidence != record_evidence:
            return _blocked_result(
                source_kind=source_kind,
                source_locator=source_locator,
                code="bundle_structure_invalid",
                message="manifest.json.evidence and records/normalized_record.json.evidence must match.",
                member_list=member_list,
            )

        return ResolutionBundleInspectionResult(
            status="inspected",
            source_kind=source_kind,
            source_locator=source_locator,
            inspected_offline=True,
            resolved_resource_id=resolved_resource_id,
            bundle_kind=bundle_kind,
            bundle_version=bundle_version,
            target_ref=target_ref,
            primary_object=primary_object,
            evidence=manifest_evidence or record_evidence,
            member_list=member_list,
            normalized_record_summary=normalized_record_summary,
            notices=(
                Notice(
                    code="bundle_inspected_locally_offline",
                    severity="info",
                    message="Inspected bundle locally and offline without live fixture access.",
                ),
            ),
        )


class _BundleMemberJsonError(Exception):
    def __init__(self, member_name: str, reason: str) -> None:
        super().__init__(f"{member_name}: {reason}")
        self.member_name = member_name
        self.reason = reason


def _read_json_member(bundle: zipfile.ZipFile, member_name: str) -> dict[str, object]:
    try:
        return json.loads(bundle.read(member_name).decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise _BundleMemberJsonError(member_name, exc.msg) from exc


def _coerce_primary_object(value: object) -> ObjectSummary:
    if not isinstance(value, dict):
        raise ValueError("manifest.json.primary_object must be an object.")
    object_id = _require_string(value.get("id"), "manifest.json.primary_object.id")
    object_kind = _optional_string(value.get("kind"), "manifest.json.primary_object.kind")
    object_label = _optional_string(value.get("label"), "manifest.json.primary_object.label")
    return ObjectSummary(id=object_id, kind=object_kind, label=object_label)


def _coerce_normalized_record_summary(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("records/normalized_record.json must be an object.")
    record_kind = _require_string(value.get("record_kind"), "records/normalized_record.json.record_kind")
    target_ref = _require_string(value.get("target_ref"), "records/normalized_record.json.target_ref")
    source = _optional_mapping(value.get("source"), "records/normalized_record.json.source")
    object_summary = _optional_mapping(value.get("object"), "records/normalized_record.json.object")
    state = _optional_mapping(value.get("state"), "records/normalized_record.json.state")
    representation = _optional_mapping(
        value.get("representation"),
        "records/normalized_record.json.representation",
    )
    return {
        "record_kind": record_kind,
        "target_ref": target_ref,
        "resolved_resource_id": _optional_string(
            value.get("resolved_resource_id"),
            "records/normalized_record.json.resolved_resource_id",
        ),
        "source": source,
        "evidence": [summary.to_dict() for summary in _coerce_evidence_list(value.get("evidence"), "records/normalized_record.json.evidence")],
        "object": object_summary,
        "state": state,
        "representation": representation,
        "expected_member_order": list(RESOLUTION_BUNDLE_MEMBER_ORDER),
    }


def _blocked_result(
    *,
    source_kind: str,
    source_locator: str,
    code: str,
    message: str,
    member_list: tuple[str, ...] = (),
) -> ResolutionBundleInspectionResult:
    return ResolutionBundleInspectionResult(
        status="blocked",
        source_kind=source_kind,
        source_locator=source_locator,
        inspected_offline=True,
        member_list=member_list,
        notices=(Notice(code=code, severity="error", message=message),),
    )


def _require_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _optional_string(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string when provided.")
    return value


def _optional_mapping(value: object, field_name: str) -> dict[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object when provided.")
    return dict(value)


def _coerce_evidence_list(value: object, field_name: str) -> tuple[EvidenceSummary, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list when provided.")
    return tuple(_coerce_evidence_summary(item, f"{field_name}[]") for item in value)


def _coerce_evidence_summary(value: object, field_name: str) -> EvidenceSummary:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object.")
    return EvidenceSummary(
        claim_kind=_require_string(value.get("claim_kind"), f"{field_name}.claim_kind"),
        claim_value=_require_string(value.get("claim_value"), f"{field_name}.claim_value"),
        asserted_by_family=_require_string(
            value.get("asserted_by_family"),
            f"{field_name}.asserted_by_family",
        ),
        asserted_by_label=_optional_string(
            value.get("asserted_by_label"),
            f"{field_name}.asserted_by_label",
        ),
        evidence_kind=_require_string(value.get("evidence_kind"), f"{field_name}.evidence_kind"),
        evidence_locator=_require_string(
            value.get("evidence_locator"),
            f"{field_name}.evidence_locator",
        ),
        asserted_at=_optional_string(value.get("asserted_at"), f"{field_name}.asserted_at"),
    )
