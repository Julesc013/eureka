"""Presentation-safe view models for the local workbench."""

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


ABSENCE_LIMITATION = "This is local current-index absence only, not global proof."
LOCAL_INDEX_LIMITATION = "Reviewed results are from the local reviewed public index only."
SOURCE_SCOPE_LIMITATION = "Source coverage shown here is local to the reviewed index."
SEARCHABLE_TEXT_LIMIT = 320
CHECKED_ABSENCE_LAYERS = ("reviewed_public_index",)
UNCHECKED_ABSENCE_LAYERS = (
    "source probes",
    "WorkUnits",
    "extraction",
    "Search Hunt Sessions",
    "broader connectors",
    "AI/semantic search",
)


@dataclass(frozen=True)
class NonClaimBannerView:
    messages: tuple[str, ...]


@dataclass(frozen=True)
class CapabilityUnavailableView:
    capability: str
    status: str
    reason: str


@dataclass(frozen=True)
class ProvenanceRefView:
    label: str
    value: str


@dataclass(frozen=True)
class StoreStatusView:
    store_id: str
    relative_path: str
    opened: bool
    integrity_status: str
    schema_version: str


@dataclass(frozen=True)
class IndexStatusView:
    record_count: int
    rebuild_count: int
    source_ref_count: int
    evidence_ref_count: int
    review_ref_count: int
    source_counts: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class SearchResultCardView:
    record_id: str
    title: str
    description: str
    source_id: str
    source_family: str
    trust_lane: str
    provenance_refs: tuple[ProvenanceRefView, ...]
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


@dataclass(frozen=True)
class HomePageView:
    status: str
    instance_id: str
    instance_schema_version: str
    record_count: int
    lan_enabled: bool
    lan_read_only: bool
    non_claim_banner: NonClaimBannerView
    unavailable_capabilities: tuple[CapabilityUnavailableView, ...]
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class SearchPageView:
    query: str
    result_count: int
    results: tuple[SearchResultCardView, ...]
    local_index_limitation: str
    non_claim_banner: NonClaimBannerView
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ObjectPageView:
    record_id: str
    found: bool
    title: str
    description: str
    source_id: str
    provenance_refs: tuple[ProvenanceRefView, ...]
    normalized_fields: tuple[Mapping[str, Any], ...]
    searchable_text_excerpt: str
    non_claim_banner: NonClaimBannerView
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class SourcePageView:
    source_id: str
    result_count: int
    records: tuple[SearchResultCardView, ...]
    local_scope_note: str
    non_claim_banner: NonClaimBannerView
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class AbsencePageView:
    query: str
    result_count: int
    checked_layers: tuple[str, ...]
    unchecked_layers: tuple[str, ...]
    checked_sources: tuple[str, ...]
    unavailable_capabilities: tuple[CapabilityUnavailableView, ...]
    non_claim: str
    non_claim_banner: NonClaimBannerView
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class StatusPageView:
    instance_id: str
    instance_schema_version: str
    instance_root: str
    store_count: int
    stores: tuple[StoreStatusView, ...]
    index_status: IndexStatusView
    migration_needed: bool
    read_only: bool
    server_enabled: bool
    lan_enabled: bool
    bind_lan: bool
    lan_read_only: bool
    lan_mutations_enabled: bool
    deployment_performed: bool
    production_readiness_claimed: bool
    public_launch_readiness_claimed: bool
    non_claim_banner: NonClaimBannerView
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ReviewQueueItemView:
    review_item_id: str
    subject_kind: str
    subject_id: str
    queue_status: str
    evidence_id: str
    source_cache_entry_id: str
    summary: str
    priority: int


@dataclass(frozen=True)
class ReviewQueuePageView:
    result_count: int
    review_items: tuple[ReviewQueueItemView, ...]
    non_claim_banner: NonClaimBannerView
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ReviewItemPageView:
    review_item_id: str
    found: bool
    queue_status: str
    subject_kind: str
    subject_id: str
    summary: str
    evidence_id: str
    source_cache_entry_id: str
    evidence: tuple[Mapping[str, Any], ...]
    source_cache_entry: tuple[Mapping[str, Any], ...]
    decisions: tuple[Mapping[str, Any], ...]
    events: tuple[Mapping[str, Any], ...]
    non_claim_banner: NonClaimBannerView
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class RebuildPageView:
    record_count: int
    rebuild_count: int
    operator_token_required: bool
    non_claim_banner: NonClaimBannerView
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


def build_home_page_view(status: Mapping[str, Any]) -> HomePageView:
    runtime = _mapping(status.get("runtime"))
    public_index = _mapping(status.get("public_index"))
    service = _mapping(status.get("service"))
    return HomePageView(
        status=str(status.get("status", runtime.get("status", ""))),
        instance_id=str(runtime.get("instance_id", "")),
        instance_schema_version=str(runtime.get("instance_schema_version", "")),
        record_count=int(public_index.get("record_count", 0) or 0),
        lan_enabled=bool(service.get("lan_enabled", runtime.get("lan_enabled", False))),
        lan_read_only=bool(service.get("lan_read_only", True)),
        non_claim_banner=build_non_claim_banner_view(),
        unavailable_capabilities=build_unavailable_capabilities(bool(service.get("lan_enabled", runtime.get("lan_enabled", False)))),
        warnings=_tuple(status.get("warnings")),
        limitations=_unique(_tuple(status.get("limitations")) + (LOCAL_INDEX_LIMITATION,)),
    )


def build_search_page_view(query: str, search_result: Mapping[str, Any]) -> SearchPageView:
    return SearchPageView(
        query=query,
        result_count=int(search_result.get("result_count", 0) or 0),
        results=tuple(_search_card(item) for item in _sequence(search_result.get("results"))),
        local_index_limitation=LOCAL_INDEX_LIMITATION,
        non_claim_banner=build_non_claim_banner_view(),
        warnings=_tuple(search_result.get("warnings")),
        limitations=_unique(_tuple(search_result.get("limitations")) + (LOCAL_INDEX_LIMITATION,)),
    )


def build_object_page_view(record_id: str, record: Mapping[str, Any] | None) -> ObjectPageView:
    payload = _mapping(record)
    return ObjectPageView(
        record_id=record_id,
        found=bool(payload),
        title=str(payload.get("title", record_id if record_id else "Object not found")),
        description=str(payload.get("description", "")),
        source_id=str(payload.get("source_id", "")),
        provenance_refs=_provenance_refs(payload),
        normalized_fields=_normalized_rows(payload.get("normalized_fields")),
        searchable_text_excerpt=_excerpt(payload.get("searchable_text")),
        non_claim_banner=build_non_claim_banner_view(),
        warnings=_tuple(payload.get("warnings")),
        limitations=_unique(_tuple(payload.get("limitations")) + (LOCAL_INDEX_LIMITATION,)),
    )


def build_source_page_view(source_id: str, records: Mapping[str, Any]) -> SourcePageView:
    return SourcePageView(
        source_id=source_id,
        result_count=int(records.get("result_count", 0) or 0),
        records=tuple(_search_card(item) for item in _sequence(records.get("records"))),
        local_scope_note=SOURCE_SCOPE_LIMITATION,
        non_claim_banner=build_non_claim_banner_view(),
        warnings=_tuple(records.get("warnings")),
        limitations=_unique(_tuple(records.get("limitations")) + (SOURCE_SCOPE_LIMITATION, LOCAL_INDEX_LIMITATION)),
    )


def build_absence_page_view(query: str, absence_report: Mapping[str, Any]) -> AbsencePageView:
    report = _mapping(absence_report.get("absence", absence_report))
    limitations = _tuple(absence_report.get("limitations")) + _tuple(report.get("limitations")) + (ABSENCE_LIMITATION,)
    return AbsencePageView(
        query=query,
        result_count=int(report.get("result_count", 0) or 0),
        checked_layers=CHECKED_ABSENCE_LAYERS,
        unchecked_layers=UNCHECKED_ABSENCE_LAYERS,
        checked_sources=tuple(str(item) for item in _sequence(report.get("checked_sources"))),
        unavailable_capabilities=build_unavailable_capabilities(),
        non_claim="Absence is not proof the artifact does not exist.",
        non_claim_banner=build_non_claim_banner_view(),
        warnings=_tuple(absence_report.get("warnings")) + _tuple(report.get("warnings")),
        limitations=_unique(limitations),
    )


def build_status_page_view(status: Mapping[str, Any]) -> StatusPageView:
    runtime = _mapping(status.get("runtime"))
    service = _mapping(status.get("service"))
    stores = _mapping(runtime.get("stores"))
    return StatusPageView(
        instance_id=str(runtime.get("instance_id", "")),
        instance_schema_version=str(runtime.get("instance_schema_version", "")),
        instance_root=str(runtime.get("instance_root", "")),
        store_count=int(runtime.get("store_count", len(stores)) or 0),
        stores=tuple(_store_rows(stores)),
        index_status=_index_status(_mapping(status.get("public_index"))),
        migration_needed=bool(runtime.get("migration_needed", False)),
        read_only=bool(runtime.get("read_only", True)),
        server_enabled=bool(runtime.get("server_enabled", False)),
        lan_enabled=bool(service.get("lan_enabled", runtime.get("lan_enabled", False))),
        bind_lan=bool(service.get("bind_lan", False)),
        lan_read_only=bool(service.get("lan_read_only", True)),
        lan_mutations_enabled=bool(service.get("lan_mutations_enabled", False)),
        deployment_performed=bool(runtime.get("deployment_performed", False)),
        production_readiness_claimed=bool(runtime.get("production_readiness_claimed", False)),
        public_launch_readiness_claimed=bool(runtime.get("public_launch_readiness_claimed", False)),
        non_claim_banner=build_non_claim_banner_view(),
        warnings=_tuple(status.get("warnings")) + _tuple(runtime.get("warnings")),
        limitations=_unique(_tuple(status.get("limitations")) + (LOCAL_INDEX_LIMITATION,)),
    )


def build_review_queue_page_view(payload: Mapping[str, Any]) -> ReviewQueuePageView:
    items = []
    for value in _sequence(payload.get("review_items")):
        item = _mapping(value)
        items.append(
            ReviewQueueItemView(
                review_item_id=str(item.get("review_item_id", "")),
                subject_kind=str(item.get("subject_kind", "")),
                subject_id=str(item.get("subject_id", "")),
                queue_status=str(item.get("queue_status", "")),
                evidence_id=str(item.get("evidence_id", "") or ""),
                source_cache_entry_id=str(item.get("source_cache_entry_id", "") or ""),
                summary=str(item.get("summary", "")),
                priority=int(item.get("priority", 0) or 0),
            )
        )
    return ReviewQueuePageView(
        result_count=int(payload.get("result_count", len(items)) or 0),
        review_items=tuple(items),
        non_claim_banner=build_non_claim_banner_view(),
        warnings=_tuple(payload.get("warnings")),
        limitations=_unique(_tuple(payload.get("limitations")) + ("local review state only",)),
    )


def build_review_item_page_view(review_item_id: str, payload: Mapping[str, Any]) -> ReviewItemPageView:
    item = _mapping(payload.get("review_item"))
    return ReviewItemPageView(
        review_item_id=review_item_id,
        found=bool(payload.get("found", False)),
        queue_status=str(item.get("queue_status", "")),
        subject_kind=str(item.get("subject_kind", "")),
        subject_id=str(item.get("subject_id", "")),
        summary=str(item.get("summary", "")),
        evidence_id=str(item.get("evidence_id", "") or ""),
        source_cache_entry_id=str(item.get("source_cache_entry_id", "") or ""),
        evidence=_mapping_rows(payload.get("evidence")),
        source_cache_entry=_mapping_rows(payload.get("source_cache_entry")),
        decisions=tuple(_mapping(value) for value in _sequence(payload.get("decisions"))),
        events=tuple(_mapping(value) for value in _sequence(payload.get("events"))),
        non_claim_banner=build_non_claim_banner_view(),
        warnings=_tuple(payload.get("warnings")),
        limitations=_unique(_tuple(payload.get("limitations")) + ("local review state only",)),
    )


def build_rebuild_page_view(payload: Mapping[str, Any]) -> RebuildPageView:
    index = _mapping(payload.get("public_index"))
    return RebuildPageView(
        record_count=int(index.get("record_count", 0) or 0),
        rebuild_count=int(index.get("rebuild_count", 0) or 0),
        operator_token_required=bool(payload.get("operator_token_required_for_mutations", True)),
        non_claim_banner=build_non_claim_banner_view(),
        warnings=_tuple(payload.get("warnings")),
        limitations=_unique(_tuple(payload.get("limitations")) + ("rebuild writes only to the local reviewed public index store",)),
    )


def build_non_claim_banner_view() -> NonClaimBannerView:
    return NonClaimBannerView(
        messages=(
            "Local appliance prototype.",
            "Localhost only.",
            "Read-only.",
            "Reviewed local projection, not global truth.",
            "No production or public launch readiness claim.",
        )
    )


def build_unavailable_capabilities(lan_enabled: bool = False) -> tuple[CapabilityUnavailableView, ...]:
    lan_status = "read-only enabled" if lan_enabled else "disabled"
    lan_reason = (
        "Explicit LAN binding is active for read-only inspection only."
        if lan_enabled
        else "Only localhost is enabled unless --bind-lan is supplied."
    )
    return (
        CapabilityUnavailableView("WorkUnits", "queue available", "Durable queue records exist; execution remains disabled."),
        CapabilityUnavailableView("review and index maintenance UI", "operator-gated", "Local review decisions and rebuild require an operator token."),
        CapabilityUnavailableView("source probes", "unavailable", "Live or automated source inspection is not implemented."),
        CapabilityUnavailableView("extraction", "deferred", "Extraction stays deferred until the local appliance track closes."),
        CapabilityUnavailableView("Search Hunt Sessions", "unavailable", "Session runtime is not implemented."),
        CapabilityUnavailableView("LAN mode", lan_status, lan_reason),
        CapabilityUnavailableView("LAN smoke prerequisite", "deferred", "Cross-device read-only smoke is the next LAN proof step."),
        CapabilityUnavailableView("deployment", "disabled", "No deployment is performed."),
    )


def _search_card(value: Any) -> SearchResultCardView:
    item = _mapping(value)
    record_id = str(item.get("record_id") or item.get("id") or "")
    return SearchResultCardView(
        record_id=record_id,
        title=str(item.get("title", record_id)),
        description=str(item.get("description", "")),
        source_id=str(item.get("source_id", "")),
        source_family=str(item.get("source_family", "")),
        trust_lane=str(item.get("trust_lane", "")),
        provenance_refs=_provenance_refs(item),
        warnings=_tuple(item.get("warnings")),
        limitations=_tuple(item.get("limitations")),
    )


def _provenance_refs(record: Mapping[str, Any]) -> tuple[ProvenanceRefView, ...]:
    refs = []
    for label, key in (
        ("source_cache_entry_id", "source_cache_entry_id"),
        ("evidence_id", "evidence_id"),
        ("review_item_id", "review_item_id"),
        ("review_decision_id", "review_decision_id"),
    ):
        value = str(record.get(key, ""))
        if value:
            refs.append(ProvenanceRefView(label=label, value=value))
    return tuple(refs)


def _store_rows(stores: Mapping[str, Any]) -> list[StoreStatusView]:
    rows = []
    for store_id, payload in stores.items():
        item = _mapping(payload)
        rows.append(
            StoreStatusView(
                store_id=str(store_id),
                relative_path=str(item.get("relative_path", "")),
                opened=bool(item.get("opened", False)),
                integrity_status=str(item.get("integrity_status", "")),
                schema_version=str(item.get("schema_version", "")),
            )
        )
    return rows


def _index_status(public_index: Mapping[str, Any]) -> IndexStatusView:
    source_counts = _mapping(public_index.get("source_counts"))
    return IndexStatusView(
        record_count=int(public_index.get("record_count", 0) or 0),
        rebuild_count=int(public_index.get("rebuild_count", 0) or 0),
        source_ref_count=int(public_index.get("source_ref_count", 0) or 0),
        evidence_ref_count=int(public_index.get("evidence_ref_count", 0) or 0),
        review_ref_count=int(public_index.get("review_ref_count", 0) or 0),
        source_counts=tuple({"source_id": str(key), "record_count": int(value or 0)} for key, value in sorted(source_counts.items())),
    )


def _normalized_rows(fields: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(fields, Mapping) or not fields:
        return ({"field": "none", "value": ""},)
    return tuple({"field": str(key), "value": _safe_value(value)} for key, value in sorted(fields.items()))


def _mapping_rows(value: Any) -> tuple[Mapping[str, Any], ...]:
    payload = _mapping(value)
    if not payload:
        return ({"field": "none", "value": ""},)
    return tuple({"field": str(key), "value": _safe_value(item)} for key, item in sorted(payload.items()))


def _excerpt(value: Any) -> str:
    text = str(value or "").strip()
    if len(text) <= SEARCHABLE_TEXT_LIMIT:
        return text
    return text[: SEARCHABLE_TEXT_LIMIT - 3].rstrip() + "..."


def _safe_value(value: Any) -> str:
    if isinstance(value, Mapping):
        return ", ".join(f"{key}: {_safe_value(item)}" for key, item in sorted(value.items()))
    if isinstance(value, (list, tuple, set)):
        return ", ".join(_safe_value(item) for item in value)
    return str(value)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    return value if isinstance(value, (list, tuple)) else ()


def _tuple(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in _sequence(value))


def _unique(values: Sequence[str]) -> tuple[str, ...]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return tuple(result)
