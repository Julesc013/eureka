from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Mapping

from runtime.engine.index import IndexRecord
from runtime.source_registry import SourceRecordNotFoundError, SourceRegistry


REPO_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_INDEX_ROOT = REPO_ROOT / "data" / "public_index"
SEARCH_DOCUMENTS_PATH = PUBLIC_INDEX_ROOT / "search_documents.ndjson"
PUBLIC_INDEX_SCHEMA_VERSION = "0.1.0"
PUBLIC_INDEX_ID = "eureka_public_search_index_v0"

BLOCKED_ACTIONS = ("download", "upload", "install_handoff", "execute")
ALLOWED_ACTIONS = ("inspect", "view_source", "view_provenance", "read")
GLOBAL_LIMITATIONS = (
    "local_index_only",
    "fixture_or_recorded_corpus_only",
    "no_live_source_calls",
    "no_downloads",
    "no_uploads",
    "no_installs",
    "no_private_paths",
    "no_rights_clearance_claim",
    "no_malware_safety_claim",
)
GLOBAL_WARNINGS = (
    "Generated from controlled repo fixture and recorded metadata only.",
    "No live source probe or external API call was performed.",
    "No download, upload, install, execute, or account action is enabled.",
)


@dataclass(frozen=True)
class PublicSearchIndexLoadResult:
    status: str
    records: tuple[IndexRecord, ...]
    document_count: int
    index_root: Path
    errors: tuple[str, ...] = ()


def public_search_index_exists(index_root: Path = PUBLIC_INDEX_ROOT) -> bool:
    return (index_root / "search_documents.ndjson").is_file()


def load_public_search_index_records(
    index_root: Path = PUBLIC_INDEX_ROOT,
) -> PublicSearchIndexLoadResult:
    path = index_root / "search_documents.ndjson"
    if not path.is_file():
        return PublicSearchIndexLoadResult(
            status="missing",
            records=(),
            document_count=0,
            index_root=index_root,
            errors=(f"{path.as_posix()}: missing public search index document file.",),
        )
    records: list[IndexRecord] = []
    errors: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            document = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"search_documents.ndjson:{line_number}: invalid JSON: {exc}.")
            continue
        if not isinstance(document, Mapping):
            errors.append(f"search_documents.ndjson:{line_number}: document must be an object.")
            continue
        try:
            records.append(index_record_from_public_document(document))
        except (TypeError, ValueError) as exc:
            errors.append(f"search_documents.ndjson:{line_number}: {exc}.")
    return PublicSearchIndexLoadResult(
        status="valid" if not errors else "invalid",
        records=tuple(records),
        document_count=len(records),
        index_root=index_root,
        errors=tuple(errors),
    )


def public_document_from_index_record(
    record: IndexRecord,
    source_registry: SourceRegistry,
) -> dict[str, Any]:
    source_record = _source_record(record.source_id, source_registry)
    source_status = getattr(source_record, "status", "unknown")
    source_coverage_depth = (
        getattr(getattr(source_record, "coverage", None), "coverage_depth", None) or "unknown"
    )
    platform_terms, architecture_terms = _compatibility_terms(record)
    version_terms = _version_terms(record)
    date_terms = _date_terms(record.search_text())
    keyword_terms = _keyword_terms(record, platform_terms, architecture_terms, version_terms, date_terms)
    public_target_ref = record.target_ref or record.index_record_id
    result_lane = record.primary_lane or (record.result_lanes[0] if record.result_lanes else "other")
    evidence_items = tuple(_safe_summary(item, limit=280) for item in record.evidence if item)
    search_text = _safe_summary(record.search_text(), limit=4000)
    return _drop_none(
        {
            "schema_version": PUBLIC_INDEX_SCHEMA_VERSION,
            "index_id": PUBLIC_INDEX_ID,
            "doc_id": _public_doc_id(record.index_record_id),
            "record_id": record.index_record_id,
            "record_kind": record.record_kind,
            "title": _safe_summary(record.label, limit=240),
            "subtitle": _safe_summary(record.summary, limit=240) if record.summary else None,
            "description": _safe_summary(record.summary or record.label, limit=360),
            "source_id": record.source_id or "unknown-source",
            "source_family": record.source_family or "unknown",
            "source_label": record.source_label or (getattr(source_record, "name", None) or record.source_id or "Unknown source"),
            "source_status": source_status,
            "source_coverage_depth": source_coverage_depth,
            "object_family": record.member_kind or record.record_kind,
            "representation_kind": _representation_kind(record),
            "member_path": _safe_member_path(record.member_path),
            "parent_ref": record.parent_target_ref,
            "parent_label": record.parent_object_label,
            "resolved_resource_id": record.resolved_resource_id,
            "subject_key": record.subject_key,
            "representation_id": record.representation_id,
            "member_kind": record.member_kind,
            "media_type": record.media_type,
            "size_bytes": record.size_bytes,
            "content_hash": record.content_hash,
            "platform_terms": platform_terms,
            "architecture_terms": architecture_terms,
            "version_terms": version_terms,
            "date_terms": date_terms,
            "keyword_terms": keyword_terms,
            "compatibility_summary": _safe_summary(record.compatibility_summary or "", limit=500),
            "compatibility_evidence_items": [_safe_json_mapping(item) for item in record.compatibility_evidence],
            "evidence_summary": _evidence_summary(evidence_items),
            "evidence_items": list(evidence_items),
            "result_lane": result_lane,
            "result_lanes": list(record.result_lanes or (result_lane,)),
            "user_cost_score": record.user_cost_score if record.user_cost_score is not None else 9,
            "user_cost_reasons": list(record.user_cost_reasons),
            "user_cost_summary": record.usefulness_summary or "user cost unknown",
            "allowed_actions": list(ALLOWED_ACTIONS),
            "blocked_actions": list(BLOCKED_ACTIONS),
            "warnings": list(GLOBAL_WARNINGS),
            "limitations": list(GLOBAL_LIMITATIONS),
            "public_target_ref": public_target_ref,
            "route_hints": _safe_json_mapping(record.route_hints or {}),
            "search_text": search_text,
            "live_source_used": False,
            "external_call_performed": False,
            "private_path_included": False,
            "executable_payload_included": False,
        }
    )


def index_record_from_public_document(document: Mapping[str, Any]) -> IndexRecord:
    return IndexRecord(
        index_record_id=_required_text(document, "record_id"),
        record_kind=_required_text(document, "record_kind"),
        label=_required_text(document, "title"),
        summary=_optional_text(document.get("description")),
        target_ref=_optional_text(document.get("public_target_ref")),
        resolved_resource_id=_optional_text(document.get("resolved_resource_id")),
        source_id=_optional_text(document.get("source_id")),
        source_family=_optional_text(document.get("source_family")),
        source_label=_optional_text(document.get("source_label")),
        subject_key=_optional_text(document.get("subject_key")),
        version_or_state=_first_text(document.get("version_terms")),
        representation_id=_optional_text(document.get("representation_id")),
        member_path=_optional_text(document.get("member_path")),
        parent_target_ref=_optional_text(document.get("parent_ref")),
        parent_object_label=_optional_text(document.get("parent_label")),
        member_kind=_optional_text(document.get("member_kind")),
        media_type=_optional_text(document.get("media_type")),
        size_bytes=_optional_int(document.get("size_bytes")),
        content_hash=_optional_text(document.get("content_hash")),
        content_text=_required_text(document, "search_text"),
        evidence=_text_tuple(document.get("evidence_items")),
        action_hints=_text_tuple(document.get("allowed_actions")),
        compatibility_evidence=_mapping_tuple(document.get("compatibility_evidence_items")),
        compatibility_summary=_optional_text(document.get("compatibility_summary")),
        result_lanes=_text_tuple(document.get("result_lanes")) or (_required_text(document, "result_lane"),),
        primary_lane=_required_text(document, "result_lane"),
        user_cost_score=_optional_int(document.get("user_cost_score")),
        user_cost_reasons=_text_tuple(document.get("user_cost_reasons")),
        usefulness_summary=_optional_text(document.get("user_cost_summary")),
        route_hints=_safe_json_mapping(document.get("route_hints") or {}),
        created_by_slice="public_search_index_builder_v0",
    )


def _source_record(source_id: str | None, source_registry: SourceRegistry) -> Any:
    if not source_id:
        return None
    try:
        return source_registry.get_record(source_id)
    except SourceRecordNotFoundError:
        return None


def _public_doc_id(record_id: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9._:-]+", "-", record_id).strip("-")
    return f"public-doc:{safe}"


def _compatibility_terms(record: IndexRecord) -> tuple[list[str], list[str]]:
    platforms: set[str] = set()
    architectures: set[str] = set()
    for item in record.compatibility_evidence:
        if not isinstance(item, Mapping):
            continue
        architecture = item.get("architecture")
        if isinstance(architecture, str) and architecture and architecture != "unknown":
            architectures.add(architecture)
        platform = item.get("platform")
        if isinstance(platform, Mapping):
            for field_name in ("family", "name", "version", "marketing_alias"):
                value = platform.get(field_name)
                if isinstance(value, str) and value:
                    platforms.add(value)
    return sorted(platforms), sorted(architectures)


def _version_terms(record: IndexRecord) -> list[str]:
    terms = set()
    if record.version_or_state:
        terms.add(record.version_or_state)
    for item in (record.label, record.summary, record.target_ref):
        if not isinstance(item, str):
            continue
        for match in re.findall(r"\b(?:v?\d+(?:\.\d+){0,3}|windows\s+(?:xp|7|98|2000|95))\b", item, re.I):
            terms.add(match)
    return sorted(terms, key=str.casefold)


def _date_terms(text: str) -> list[str]:
    return sorted(set(re.findall(r"\b(?:19|20)\d{2}\b", text)))


def _keyword_terms(
    record: IndexRecord,
    platform_terms: list[str],
    architecture_terms: list[str],
    version_terms: list[str],
    date_terms: list[str],
) -> list[str]:
    raw = " ".join(
        item
        for item in (
            record.label,
            record.summary or "",
            record.member_path or "",
            record.source_family or "",
            record.source_label or "",
            " ".join(record.result_lanes),
            " ".join(platform_terms),
            " ".join(architecture_terms),
            " ".join(version_terms),
            " ".join(date_terms),
        )
        if item
    )
    return sorted({token for token in re.split(r"[^a-z0-9.]+", raw.casefold()) if len(token) >= 2})


def _representation_kind(record: IndexRecord) -> str:
    if record.representation_id:
        return "bounded_fixture_representation"
    if record.member_path:
        return "bounded_fixture_member"
    return "metadata_summary"


def _evidence_summary(evidence_items: tuple[str, ...]) -> str:
    if not evidence_items:
        return "No public evidence summary attached."
    return " | ".join(evidence_items[:3])


def _safe_member_path(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.replace("\\", "/")
    if _looks_private_path(normalized):
        return None
    return normalized[:300]


def _safe_summary(value: str, *, limit: int) -> str:
    normalized = " ".join(value.replace("\r", " ").replace("\n", " ").split())
    if _looks_private_path(normalized):
        normalized = _redact_private_path_markers(normalized)
    return normalized[:limit]


def _looks_private_path(value: str) -> bool:
    folded = value.replace("\\", "/").casefold()
    return bool(
        re.search(r"\b[a-z]:/", folded)
        or "/users/" in folded
        or "/home/" in folded
        or "/tmp/" in folded
        or "appdata/" in folded
        or ".eureka-local" in folded
        or ".eureka-cache" in folded
        or ".eureka-staging" in folded
    )


def _redact_private_path_markers(value: str) -> str:
    redacted = re.sub(r"\b[A-Za-z]:/[^\s]+", "[redacted-private-path]", value)
    redacted = re.sub(r"/(?:Users|home|tmp)/[^\s]+", "[redacted-private-path]", redacted, flags=re.I)
    return redacted


def _safe_json_mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {}
    result: dict[str, Any] = {}
    for key, item in sorted(value.items()):
        if item is None:
            continue
        if isinstance(item, str):
            result[str(key)] = _safe_summary(item, limit=500)
        elif isinstance(item, (int, float, bool)):
            result[str(key)] = item
        elif isinstance(item, Mapping):
            result[str(key)] = _safe_json_mapping(item)
        elif isinstance(item, list):
            result[str(key)] = [
                _safe_summary(element, limit=300) if isinstance(element, str) else element
                for element in item
                if isinstance(element, (str, int, float, bool, dict))
            ]
    return result


def _drop_none(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}


def _required_text(document: Mapping[str, Any], field_name: str) -> str:
    value = document.get(field_name)
    if not isinstance(value, str) or not value:
        raise ValueError(f"missing required text field {field_name!r}")
    return value


def _optional_text(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _optional_int(value: Any) -> int | None:
    return value if isinstance(value, int) and value >= 0 else None


def _first_text(value: Any) -> str | None:
    values = _text_tuple(value)
    return values[0] if values else None


def _text_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item) for item in value if isinstance(item, str) and item)


def _mapping_tuple(value: Any) -> tuple[dict[str, Any], ...]:
    if not isinstance(value, list):
        return ()
    return tuple(dict(item) for item in value if isinstance(item, Mapping))
