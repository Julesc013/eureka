from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from runtime.engine.core import NormalizedCatalog
from runtime.engine.index.index_record import IndexRecord
from runtime.engine.interfaces.normalize import NormalizedResolutionRecord
from runtime.engine.provenance import EvidenceSummary
from runtime.engine.compatibility import compatibility_evidence_payloads, compatibility_summary
from runtime.engine.ranking import assign_result_usefulness
from runtime.engine.representations import RepresentationSummary
from runtime.engine.resolve.source_summary import normalized_record_to_source_summary
from runtime.source_registry import SourceRecord, SourceRegistry


def build_index_records(
    catalog: NormalizedCatalog,
    source_registry: SourceRegistry,
) -> tuple[IndexRecord, ...]:
    records: list[IndexRecord] = []
    records.extend(_build_source_records(source_registry))
    for record in sorted(catalog.records, key=lambda item: item.target_ref):
        records.extend(_build_catalog_records(record))
    return tuple(records)


def _build_source_records(source_registry: SourceRegistry) -> list[IndexRecord]:
    records: list[IndexRecord] = []
    for source_record in sorted(source_registry.records, key=lambda item: item.source_id):
        records.append(
            IndexRecord(
                index_record_id=f"source_record:{source_record.source_id}",
                record_kind="source_record",
                label=source_record.name,
                summary=f"{source_record.status} {source_record.trust_lane} source registry record",
                source_id=source_record.source_id,
                source_family=source_record.source_family,
                source_label=source_record.name,
                content_text=_join_text(
                    source_record.name,
                    source_record.source_family,
                    " ".join(source_record.roles),
                    " ".join(source_record.surfaces),
                    source_record.notes,
                    source_record.legal_posture,
                    source_record.rights_notes,
                ),
                evidence=(
                    f"connector:{source_record.connector.label}",
                    f"status:{source_record.status}",
                    f"trust_lane:{source_record.trust_lane}",
                ),
                route_hints={
                    "surface_route": "/source",
                    "source_id": source_record.source_id,
                    "status": source_record.status,
                },
            )
        )
    return [_annotated_index_record(record) for record in records]


def _build_catalog_records(record: NormalizedResolutionRecord) -> list[IndexRecord]:
    records: list[IndexRecord] = []
    source_summary = normalized_record_to_source_summary(record)
    source_id = source_summary.source_id
    source_label = source_summary.label or record.source_name or record.source_family_label
    version_or_state = _infer_version_or_state(record)
    subject_key = record.object_id
    evidence_text = tuple(_evidence_text(item) for item in record.evidence)
    compatibility_evidence = compatibility_evidence_payloads(record.compatibility_evidence)
    compatibility_text = compatibility_summary(record.compatibility_evidence)
    representation_labels = tuple(summary.label for summary in record.representations if summary.label)

    records.append(
        IndexRecord(
            index_record_id=f"{record.record_kind}:{record.target_ref}",
            record_kind=record.record_kind,
            label=record.object_label,
            summary=_catalog_record_summary(record),
            target_ref=record.target_ref,
            resolved_resource_id=record.object_id,
            source_id=source_id,
            source_family=record.source_family,
            source_label=source_label,
            subject_key=subject_key,
            version_or_state=version_or_state,
            representation_id=record.representation_id,
            member_path=record.member_path,
            parent_target_ref=record.parent_target_ref,
            parent_resolved_resource_id=record.parent_resolved_resource_id,
            parent_representation_id=record.parent_representation_id,
            parent_object_label=record.parent_object_label,
            member_kind=record.member_kind,
            media_type=record.media_type,
            size_bytes=record.size_bytes,
            content_hash=record.content_hash,
            content_text=_join_text(
                record.object_label,
                record.object_kind,
                record.target_ref,
                version_or_state,
                source_label,
                record.member_path,
                record.member_label,
                record.member_kind,
                record.parent_object_label,
                " ".join(record.action_hints),
                " ".join(representation_labels),
                " ".join(evidence_text),
                compatibility_text,
            ),
            evidence=evidence_text,
            action_hints=record.action_hints,
            compatibility_evidence=compatibility_evidence,
            compatibility_summary=compatibility_text,
            route_hints=_compact_mapping({
                "surface_route": "/",
                "target_ref": record.target_ref,
                "record_kind": record.record_kind,
                "parent_target_ref": record.parent_target_ref,
                "parent_representation_id": record.parent_representation_id,
                "member_path": record.member_path,
            }),
        )
    )

    if record.record_kind != "synthetic_member" and record.state_id:
        records.append(
            IndexRecord(
                index_record_id=f"state_or_release:{record.state_id}",
                record_kind="state_or_release",
                label=_state_label(record),
                summary=f"{record.state_kind} for {record.object_label}",
                target_ref=record.target_ref,
                resolved_resource_id=record.object_id,
                source_id=source_id,
                source_family=record.source_family,
                source_label=source_label,
                subject_key=subject_key,
                version_or_state=version_or_state,
                content_text=_join_text(
                    record.object_label,
                    record.state_id,
                    record.state_kind,
                    version_or_state,
                    " ".join(evidence_text),
                ),
                evidence=evidence_text,
                route_hints={
                    "surface_route": "/",
                    "target_ref": record.target_ref,
                    "record_kind": "state_or_release",
                },
            )
        )

    if record.record_kind != "synthetic_member":
        for representation in sorted(record.representations, key=lambda item: item.representation_id):
            records.append(_representation_record(record, representation, source_id, source_label, version_or_state))
            records.extend(
                _member_records(
                    record,
                    representation,
                    source_id=source_id,
                    source_label=source_label,
                )
            )

    for index, evidence in enumerate(record.evidence):
        records.append(
            IndexRecord(
                index_record_id=f"evidence:{record.target_ref}:{index}",
                record_kind="evidence",
                label=f"{record.object_label} evidence {index + 1}",
                summary=f"{evidence.claim_kind} from {evidence.asserted_by_family}",
                target_ref=record.target_ref,
                resolved_resource_id=record.object_id,
                source_id=source_id,
                source_family=record.source_family,
                source_label=source_label,
                subject_key=subject_key,
                version_or_state=version_or_state,
                content_text=_join_text(
                    record.object_label,
                    evidence.claim_kind,
                    evidence.claim_value,
                    evidence.asserted_by_family,
                    evidence.evidence_kind,
                    evidence.evidence_locator,
                    evidence.asserted_by_label,
                ),
                evidence=(_evidence_text(evidence),),
                compatibility_evidence=compatibility_evidence,
                compatibility_summary=compatibility_text,
                route_hints={
                    "surface_route": "/",
                    "target_ref": record.target_ref,
                    "record_kind": "evidence",
                },
            )
        )

    return [_annotated_index_record(item) for item in records]


def _annotated_index_record(record: IndexRecord) -> IndexRecord:
    usefulness = assign_result_usefulness(record)
    return replace(
        record,
        result_lanes=usefulness.result_lanes,
        primary_lane=usefulness.primary_lane,
        user_cost_score=usefulness.user_cost_score,
        user_cost_reasons=usefulness.user_cost_reasons,
        usefulness_summary=usefulness.usefulness_summary,
    )


def _catalog_record_summary(record: NormalizedResolutionRecord) -> str:
    if record.record_kind == "synthetic_member":
        parent_label = record.parent_object_label or record.parent_target_ref or "parent bundle"
        member_kind = record.member_kind or "member"
        return f"{member_kind} member of {parent_label}"
    return f"{record.object_kind} from {record.source_family_label}"


def _representation_record(
    record: NormalizedResolutionRecord,
    representation: RepresentationSummary,
    source_id: str | None,
    source_label: str,
    version_or_state: str | None,
) -> IndexRecord:
    label = representation.label or representation.representation_id
    filename = representation.filename or _basename(representation.fetch_locator or representation.source_locator)
    return IndexRecord(
        index_record_id=f"representation:{record.target_ref}:{representation.representation_id}",
        record_kind="representation",
        label=label,
        summary=f"{representation.representation_kind} representation for {record.object_label}",
        target_ref=record.target_ref,
        resolved_resource_id=record.object_id,
        source_id=source_id,
        source_family=record.source_family,
        source_label=source_label,
        subject_key=record.object_id,
        version_or_state=version_or_state,
        representation_id=representation.representation_id,
        content_text=_join_text(
            label,
            representation.representation_kind,
            filename,
            representation.source_label,
            representation.source_locator,
            representation.fetch_locator,
            record.object_label,
        ),
        evidence=tuple(filter(None, (representation.representation_kind, filename))),
        route_hints={
            "surface_route": "/representations",
            "target_ref": record.target_ref,
            "representation_id": representation.representation_id,
        },
    )


def _member_records(
    record: NormalizedResolutionRecord,
    representation: RepresentationSummary,
    *,
    source_id: str | None,
    source_label: str,
) -> list[IndexRecord]:
    members: list[IndexRecord] = []
    for member_path in _list_zip_member_paths(representation):
        members.append(
            IndexRecord(
                index_record_id=f"member:{record.target_ref}:{representation.representation_id}:{member_path}",
                record_kind="member",
                label=_basename(member_path),
                summary=f"member of {representation.label or representation.representation_id}",
                target_ref=record.target_ref,
                resolved_resource_id=record.object_id,
                source_id=source_id,
                source_family=record.source_family,
                source_label=source_label,
                subject_key=record.object_id,
                version_or_state=_infer_version_or_state(record),
                representation_id=representation.representation_id,
                member_path=member_path,
                content_text=_join_text(
                    member_path,
                    _basename(member_path),
                    representation.label,
                    record.object_label,
                ),
                evidence=(f"member_path:{member_path}",),
                route_hints={
                    "surface_route": "/member",
                    "target_ref": record.target_ref,
                    "representation_id": representation.representation_id,
                    "member_path": member_path,
                },
            )
        )
    return members


def _list_zip_member_paths(representation: RepresentationSummary) -> tuple[str, ...]:
    fetch_locator = representation.fetch_locator
    if not isinstance(fetch_locator, str) or not fetch_locator.lower().endswith(".zip"):
        return ()
    path = Path(fetch_locator)
    if not path.is_file():
        return ()
    try:
        with ZipFile(path, "r") as archive:
            return tuple(
                member.filename
                for member in archive.infolist()
                if not member.is_dir()
            )
    except (BadZipFile, OSError):
        return ()


def _state_label(record: NormalizedResolutionRecord) -> str:
    version_or_state = _infer_version_or_state(record)
    if version_or_state is not None:
        return f"{record.object_label} {version_or_state}"
    return f"{record.object_label} {record.state_kind}"


def _infer_version_or_state(record: NormalizedResolutionRecord) -> str | None:
    if "@" in record.target_ref:
        return record.target_ref.rsplit("@", 1)[1]
    for evidence in record.evidence:
        if evidence.claim_kind.casefold() == "version":
            return evidence.claim_value
    if record.state_id:
        return record.state_id
    return None


def _evidence_text(evidence: EvidenceSummary) -> str:
    parts = [
        evidence.claim_kind,
        evidence.claim_value,
        evidence.asserted_by_family,
        evidence.evidence_kind,
        evidence.asserted_by_label,
    ]
    return " ".join(part for part in parts if part)


def _basename(locator: str | None) -> str | None:
    if not isinstance(locator, str) or not locator:
        return None
    normalized = locator.replace("\\", "/").rstrip("/")
    if not normalized:
        return None
    return normalized.rsplit("/", 1)[-1]


def _join_text(*parts: str | None) -> str | None:
    values = [part.strip() for part in parts if isinstance(part, str) and part.strip()]
    if not values:
        return None
    return " ".join(values)


def _compact_mapping(value: dict[str, object | None]) -> dict[str, object]:
    return {key: item for key, item in value.items() if item is not None}
