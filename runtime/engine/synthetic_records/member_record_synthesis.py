from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath
import re
from typing import Iterable
from zipfile import BadZipFile, ZipFile

from runtime.engine.compatibility import attach_compatibility_evidence
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.normalize import NormalizedResolutionRecord
from runtime.engine.provenance import EvidenceSummary
from runtime.engine.representations import RepresentationSummary
from runtime.engine.resolve.resolved_resource_identity import resolved_resource_id_for_record
from runtime.engine.resolve.source_summary import normalized_record_to_source_summary
from runtime.engine.synthetic_records.member_record import SyntheticMemberRecord


_REPO_ROOT = Path(__file__).resolve().parents[3]
_MAX_TEXT_PREVIEW_CHARS = 320
_TEXT_SUFFIXES = frozenset({".txt", ".inf", ".json", ".md", ".ini", ".cfg"})


def augment_catalog_with_synthetic_member_records(catalog: NormalizedCatalog) -> NormalizedCatalog:
    member_records = synthesize_member_normalized_records(catalog.records)
    if not member_records:
        return catalog
    return NormalizedCatalog(catalog.records + member_records)


def synthesize_member_normalized_records(
    records: Iterable[NormalizedResolutionRecord],
) -> tuple[NormalizedResolutionRecord, ...]:
    return tuple(_to_normalized_record(record) for record in synthesize_member_records(records))


def synthesize_member_records(
    records: Iterable[NormalizedResolutionRecord],
) -> tuple[SyntheticMemberRecord, ...]:
    members: list[SyntheticMemberRecord] = []
    for record in sorted(records, key=lambda item: item.target_ref):
        if record.source_family != "local_bundle_fixtures":
            continue
        for representation in sorted(record.representations, key=lambda item: item.representation_id):
            if representation.fetch_locator is None or not representation.fetch_locator.lower().endswith(".zip"):
                continue
            members.extend(_synthesize_for_representation(record, representation))
    return tuple(sorted(members, key=lambda item: (item.parent_target_ref, item.member_path)))


def synthetic_member_target_ref(parent_target_ref: str, member_path: str) -> str:
    normalized_path = _normalize_member_path(member_path)
    digest = hashlib.sha256(f"{parent_target_ref}\n{normalized_path}".encode("utf-8")).hexdigest()
    return f"member:sha256:{digest}"


def _synthesize_for_representation(
    record: NormalizedResolutionRecord,
    representation: RepresentationSummary,
) -> list[SyntheticMemberRecord]:
    zip_metadata = _zip_member_metadata(representation)
    evidence_by_path = _member_evidence_by_path(record.evidence)
    member_paths = sorted(set(zip_metadata) | set(evidence_by_path), key=str.casefold)
    source = normalized_record_to_source_summary(record)
    parent_resolved_resource_id = resolved_resource_id_for_record(record)
    parent_lineage_base = {
        "source_id": source.source_id,
        "source_family": record.source_family,
        "source_label": source.label,
        "source_locator": record.source_locator,
        "parent_target_ref": record.target_ref,
        "parent_resolved_resource_id": parent_resolved_resource_id,
        "parent_object_id": record.object_id,
        "parent_object_label": record.object_label,
        "parent_representation_id": representation.representation_id,
        "parent_representation_label": representation.label,
        "contained_in": "bounded_fixture_bundle",
    }

    members: list[SyntheticMemberRecord] = []
    for member_path in member_paths:
        normalized_path = _normalize_member_path(member_path)
        metadata = zip_metadata.get(normalized_path, {})
        member_label = _member_label(normalized_path)
        member_kind = _member_kind(normalized_path)
        media_type = _media_type(normalized_path)
        content_hash = metadata.get("content_hash")
        text_preview = metadata.get("text_preview")
        evidence = list(evidence_by_path.get(normalized_path, ()))
        evidence.append(
            EvidenceSummary(
                claim_kind="member_path",
                claim_value=normalized_path,
                asserted_by_family=record.source_family,
                asserted_by_label=record.source_family_label,
                evidence_kind="member_listing",
                evidence_locator=_member_locator(record, representation, normalized_path),
            )
        )
        if content_hash is not None:
            evidence.append(
                EvidenceSummary(
                    claim_kind="member_hash",
                    claim_value=content_hash,
                    asserted_by_family=record.source_family,
                    asserted_by_label=record.source_family_label,
                    evidence_kind="member_listing",
                    evidence_locator=_member_locator(record, representation, normalized_path),
                )
            )
        if text_preview is not None:
            evidence.append(
                EvidenceSummary(
                    claim_kind="member_text",
                    claim_value=text_preview,
                    asserted_by_family=record.source_family,
                    asserted_by_label=record.source_family_label,
                    evidence_kind=_text_evidence_kind(member_kind),
                    evidence_locator=_member_locator(record, representation, normalized_path),
                )
            )
        target_ref = synthetic_member_target_ref(record.target_ref, normalized_path)
        member_record_id = f"synthetic-member:{target_ref.rsplit(':', 1)[-1][:16]}"
        members.append(
            SyntheticMemberRecord(
                member_record_id=member_record_id,
                synthetic_target_ref=target_ref,
                parent_target_ref=record.target_ref,
                parent_resolved_resource_id=parent_resolved_resource_id,
                parent_representation_id=representation.representation_id,
                parent_object_label=record.object_label,
                source_id=source.source_id,
                source_family=record.source_family,
                source_label=source.label,
                member_path=normalized_path,
                member_label=member_label,
                member_kind=member_kind,
                media_type=media_type,
                size_bytes=metadata.get("size_bytes"),
                content_hash=content_hash,
                evidence=tuple(evidence),
                parent_lineage={
                    **parent_lineage_base,
                    "member_path": normalized_path,
                    "member_label": member_label,
                    "member_kind": member_kind,
                },
                action_hints=_action_hints(media_type),
            )
        )
    return members


def _to_normalized_record(member: SyntheticMemberRecord) -> NormalizedResolutionRecord:
    target_hash = member.synthetic_target_ref.rsplit(":", 1)[-1]
    object_id = f"obj.synthetic-member.{target_hash[:24]}"
    representation_id = f"rep.synthetic-member.{target_hash[:24]}"
    access_path_id = f"access.synthetic-member.{target_hash[:24]}"
    representation = RepresentationSummary(
        representation_id=representation_id,
        representation_kind="bundle_member",
        label=f"{member.member_label} member",
        content_type=member.media_type,
        byte_length=member.size_bytes,
        filename=member.member_label,
        source_family=member.source_family,
        source_label=member.source_label,
        source_locator=member.parent_lineage.get("source_locator"),
        access_path_id=access_path_id,
        access_kind="member_path",
        access_locator=f"{member.parent_representation_id}#{member.member_path}",
        is_direct=False,
        is_fetchable=False,
    )
    return attach_compatibility_evidence(NormalizedResolutionRecord(
        target_ref=member.synthetic_target_ref,
        source_name=member.source_family,
        source_locator=str(member.parent_lineage.get("source_locator") or ""),
        object_id=object_id,
        record_kind="synthetic_member",
        source_family=member.source_family,
        source_family_label=member.source_label,
        object_kind="synthetic_member",
        object_label=_object_label(member),
        state_id=f"state.synthetic-member.{target_hash[:24]}.derived",
        state_kind="derived_member",
        representation_id=representation.representation_id,
        representation_kind=representation.representation_kind,
        access_path_id=representation.access_path_id,
        access_path_kind=representation.access_kind,
        access_path_locator=representation.access_locator,
        representations=(representation,),
        evidence=member.evidence,
        parent_target_ref=member.parent_target_ref,
        parent_resolved_resource_id=member.parent_resolved_resource_id,
        parent_representation_id=member.parent_representation_id,
        parent_object_label=member.parent_object_label,
        member_path=member.member_path,
        member_label=member.member_label,
        member_kind=member.member_kind,
        media_type=member.media_type,
        size_bytes=member.size_bytes,
        content_hash=member.content_hash,
        parent_lineage=member.parent_lineage,
        action_hints=member.action_hints,
    ))


def _zip_member_metadata(representation: RepresentationSummary) -> dict[str, dict[str, object]]:
    fetch_locator = representation.fetch_locator
    if fetch_locator is None:
        return {}
    zip_path = _repo_relative_path(fetch_locator)
    if zip_path is None or not zip_path.is_file():
        return {}
    metadata: dict[str, dict[str, object]] = {}
    try:
        with ZipFile(zip_path, "r") as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                member_path = _normalize_member_path(info.filename)
                payload = archive.read(info.filename)
                entry: dict[str, object] = {
                    "size_bytes": len(payload),
                    "content_hash": f"sha256:{hashlib.sha256(payload).hexdigest()}",
                }
                text_preview = _text_preview(member_path, payload)
                if text_preview is not None:
                    entry["text_preview"] = text_preview
                metadata[member_path] = entry
    except (BadZipFile, OSError):
        return {}
    return metadata


def _repo_relative_path(locator: str) -> Path | None:
    candidate = (_REPO_ROOT / locator).resolve()
    try:
        candidate.relative_to(_REPO_ROOT)
    except ValueError:
        return None
    return candidate


def _member_evidence_by_path(
    evidence_items: tuple[EvidenceSummary, ...],
) -> dict[str, tuple[EvidenceSummary, ...]]:
    paths_by_locator: dict[str, str] = {}
    grouped: dict[str, list[EvidenceSummary]] = {}
    for evidence in evidence_items:
        if evidence.claim_kind == "member_listing":
            member_path = _normalize_member_path(evidence.claim_value)
            paths_by_locator[evidence.evidence_locator] = member_path
            grouped.setdefault(member_path, []).append(evidence)
    for evidence in evidence_items:
        member_path = paths_by_locator.get(evidence.evidence_locator)
        if member_path is not None and evidence.claim_kind != "member_listing":
            grouped.setdefault(member_path, []).append(evidence)
    return {member_path: tuple(items) for member_path, items in grouped.items()}


def _normalize_member_path(member_path: str) -> str:
    return member_path.replace("\\", "/").strip("/")


def _member_label(member_path: str) -> str:
    return PurePosixPath(member_path).name or member_path


def _member_kind(member_path: str) -> str:
    value = member_path.casefold()
    if "compatibility" in value:
        return "compatibility_note"
    if "readme" in value:
        return "readme"
    if value.endswith(".inf") or "/drivers/" in value or "driver" in value:
        return "driver"
    if "manifest" in value or value.endswith(".json"):
        return "manifest"
    if "manual" in value or "documentation" in value or "docs/" in value:
        return "documentation"
    if "/utilities/" in value or "utility" in value or "7z" in value:
        return "utility"
    if ".exe" in value or "installer" in value or "setup" in value:
        return "installer_like"
    return "unknown"


def _media_type(member_path: str) -> str | None:
    suffix = PurePosixPath(member_path).suffix.casefold()
    if suffix == ".json":
        return "application/json"
    if suffix in _TEXT_SUFFIXES:
        return "text/plain"
    return "application/octet-stream"


def _text_preview(member_path: str, payload: bytes) -> str | None:
    if _media_type(member_path) not in {"text/plain", "application/json"}:
        return None
    text = payload.decode("utf-8", errors="replace").strip()
    if not text:
        return None
    if len(text) <= _MAX_TEXT_PREVIEW_CHARS:
        return text
    return text[:_MAX_TEXT_PREVIEW_CHARS]


def _member_locator(
    record: NormalizedResolutionRecord,
    representation: RepresentationSummary,
    member_path: str,
) -> str:
    return f"{record.source_locator}#{representation.representation_id}/{member_path}"


def _action_hints(media_type: str | None) -> tuple[str, ...]:
    hints = ["inspect_parent_bundle", "read_member"]
    if media_type in {"text/plain", "application/json"}:
        hints.append("preview_member")
    return tuple(hints)


def _text_evidence_kind(member_kind: str) -> str:
    if member_kind == "compatibility_note":
        return "compatibility_note"
    if member_kind == "readme":
        return "readme"
    if member_kind == "driver":
        return "member_text"
    return "member_text"


def _object_label(member: SyntheticMemberRecord) -> str:
    tokens = _path_tokens(member.member_path)
    parent_label = member.parent_object_label or member.parent_target_ref
    return f"{member.member_path} ({tokens}) in {parent_label}"


def _path_tokens(member_path: str) -> str:
    return " ".join(token for token in re.split(r"[^A-Za-z0-9]+", member_path) if token)
