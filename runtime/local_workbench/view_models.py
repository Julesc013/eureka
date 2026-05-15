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
SEARCH_HUNT_NON_CLAIM = "Search Hunt Sessions are local investigation state, not reviewed results or accepted evidence."
SEARCH_HUNT_ABSENCE_LIMITATION = "Search Hunt absence is local current-index absence only, not a global finding."
SEARCH_HUNT_UNAVAILABLE_ACTIONS = (
    ("exhaustion report", "available", "Exhaustion reports explain local checked layers and deferred work without executing it."),
    ("SearchNeed pipeline", "available", "Need persistence records local demand without creating work."),
    ("WorkUnit pipeline", "available", "SearchNeeds can create linked WorkUnits without executing them."),
    ("background runner", "available", "Safe deterministic local workers can process linked WorkUnits."),
    ("agent research task drafts", "disabled", "Disabled task records are visible, but providers and execution are not enabled."),
    ("source probes", "disabled", "Source-probe execution remains behind a future source gate."),
    ("extraction", "deferred", "Extraction remains outside this Search Hunt UI state layer."),
    ("AI escalation", "disabled", "Model/provider calls are disabled."),
    ("sync", "disabled", "Sync requires a future reviewed policy gate."),
)
SEARCH_NEED_NON_CLAIM = "SearchNeeds are local demand records, not evidence, source approval, or reviewed results."
AGENT_RESEARCH_NON_CLAIM = "Agent research task drafts are disabled future escalation contracts, not evidence or model output."


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


@dataclass(frozen=True)
class SearchHuntLayerView:
    layer_id: str
    status: str
    note: str


@dataclass(frozen=True)
class SearchHuntTransitionView:
    transition_id: str
    from_state: str
    to_state: str
    reason: str
    created_at: str


@dataclass(frozen=True)
class SearchHuntUnavailableActionView:
    action: str
    status: str
    reason: str


@dataclass(frozen=True)
class SearchHuntCommandView:
    command_id: str
    command_type: str
    previous_state: str
    resulting_state: str
    operator_label: str
    reason: str
    policy_decision: str
    created_at: str


@dataclass(frozen=True)
class SearchHuntSteeringPreferenceView:
    steering_id: str
    command_id: str
    hunt_id: str
    command_type: str
    value: str
    reason: str
    operator_label: str
    active: bool
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class SearchHuntStateCommandView:
    label: str
    action: str
    requires_reason: bool


@dataclass(frozen=True)
class SearchHuntExhaustionRowView:
    name: str
    status: str
    note: str


@dataclass(frozen=True)
class SearchHuntCardView:
    hunt_id: str
    query: str
    normalized_query: str
    state: str
    created_at: str
    updated_at: str
    reviewed_result_count: int
    checked_layer_summary: str
    warning_count: int
    limitation_count: int
    detail_href: str


@dataclass(frozen=True)
class SearchNeedCardView:
    need_id: str
    hunt_id: str
    query: str
    need_title: str
    state: str
    need_kind: str
    desired_outcome: str
    priority: int
    warning_count: int
    limitation_count: int
    detail_href: str
    hunt_href: str


@dataclass(frozen=True)
class SearchNeedTransitionView:
    transition_id: str
    from_state: str
    to_state: str
    reason: str
    created_at: str


@dataclass(frozen=True)
class SearchNeedWorkUnitPlanItemView:
    plan_item_id: str
    kind: str
    title: str
    policy_state: str
    reason: str
    priority: str
    blocked_reason: str


@dataclass(frozen=True)
class SearchNeedWorkUnitView:
    workunit_id: str
    kind: str
    state: str
    title: str
    policy_state: str
    search_need_id: str
    search_hunt_id: str
    exhaustion_report_id: str
    execution_enabled: bool


@dataclass(frozen=True)
class AgentResearchTaskCardView:
    task_id: str
    search_hunt_id: str
    search_need_id: str
    exhaustion_report_id: str
    query: str
    state: str
    provider_enabled: bool
    execution_enabled: bool
    report_candidate_only: bool
    review_required: bool


@dataclass(frozen=True)
class AgentResearchTaskDetailView:
    task_id: str
    state: str
    research_goals: tuple[str, ...]
    forbidden_actions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class AgentResearchDisabledBoundaryView:
    provider_enabled: bool
    execution_enabled: bool
    browser_enabled: bool
    source_probe_enabled: bool
    candidate_only_output: bool
    review_required: bool
    gate_required: str


@dataclass(frozen=True)
class SearchHuntListPageView:
    hunt_count: int
    hunts: tuple[SearchHuntCardView, ...]
    unavailable_actions: tuple[SearchHuntUnavailableActionView, ...]
    non_claim_banner: NonClaimBannerView
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class SearchNeedListPageView:
    need_count: int
    needs: tuple[SearchNeedCardView, ...]
    non_claim_banner: NonClaimBannerView
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class SearchNeedDetailPageView:
    need_id: str
    found: bool
    hunt_id: str
    exhaustion_report_id: str
    query: str
    normalized_query: str
    need_title: str
    need_summary: str
    state: str
    need_kind: str
    desired_outcome: str
    priority: int
    local_result_state: str
    checked_layers: tuple[SearchHuntLayerView, ...]
    deferred_layers: tuple[SearchHuntLayerView, ...]
    recommended_future_work: tuple[SearchHuntExhaustionRowView, ...]
    policy_limitations: tuple[SearchHuntExhaustionRowView, ...]
    transitions: tuple[SearchNeedTransitionView, ...]
    workunit_plan: tuple[SearchNeedWorkUnitPlanItemView, ...]
    workunits: tuple[SearchNeedWorkUnitView, ...]
    agent_research_tasks: tuple[AgentResearchTaskCardView, ...]
    agent_research_boundary: AgentResearchDisabledBoundaryView
    agent_research_task_draft_enabled: bool
    state_transition_enabled: bool
    workunit_creation_enabled: bool
    related_hunt_href: str
    related_exhaustion_href: str
    non_claim_banner: NonClaimBannerView
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]
    operator_token_required: bool = True
    localhost_only_mutations: bool = True
    lan_mutations_enabled: bool = False


@dataclass(frozen=True)
class SearchHuntDetailPageView:
    hunt_id: str
    found: bool
    query: str
    normalized_query: str
    state: str
    intent: str
    destination: str
    created_at: str
    updated_at: str
    reviewed_result_count: int
    candidate_result_count: int
    reviewed_index_search_summary: tuple[Mapping[str, Any], ...]
    local_absence_summary: tuple[Mapping[str, Any], ...]
    checked_layers: tuple[SearchHuntLayerView, ...]
    unchecked_layers: tuple[SearchHuntLayerView, ...]
    transitions: tuple[SearchHuntTransitionView, ...]
    commands: tuple[SearchHuntCommandView, ...]
    steering_preferences: tuple[SearchHuntSteeringPreferenceView, ...]
    latest_exhaustion_report: tuple[Mapping[str, Any], ...]
    exhaustion_checked_layers: tuple[SearchHuntExhaustionRowView, ...]
    exhaustion_deferred_layers: tuple[SearchHuntExhaustionRowView, ...]
    exhaustion_blocked_by_policy: tuple[SearchHuntExhaustionRowView, ...]
    exhaustion_recommended_actions: tuple[SearchHuntExhaustionRowView, ...]
    exhaustion_non_claims: tuple[SearchHuntExhaustionRowView, ...]
    state_commands: tuple[SearchHuntStateCommandView, ...]
    command_controls_enabled: bool
    steering_controls_enabled: bool
    exhaustion_generation_enabled: bool
    search_needs: tuple[SearchNeedCardView, ...]
    workunits: tuple[SearchNeedWorkUnitView, ...]
    agent_research_tasks: tuple[AgentResearchTaskCardView, ...]
    agent_research_boundary: AgentResearchDisabledBoundaryView
    background_runner_plan: tuple[Mapping[str, Any], ...]
    background_runner_blocked_workunits: tuple[Mapping[str, Any], ...]
    background_runner_runs: tuple[Mapping[str, Any], ...]
    runner_controls_enabled: bool
    search_need_creation_enabled: bool
    agent_research_task_draft_enabled: bool
    unavailable_actions: tuple[SearchHuntUnavailableActionView, ...]
    related_search_href: str
    related_absence_href: str
    non_claim_banner: NonClaimBannerView
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]
    operator_token_required: bool = True
    localhost_only_mutations: bool = True
    lan_command_mutations_enabled: bool = False


@dataclass(frozen=True)
class SearchHuntNotFoundPageView:
    hunt_id: str
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


def build_search_hunt_list_page_view(hunts: Sequence[Any], status: Mapping[str, Any] | None = None) -> SearchHuntListPageView:
    payload = _mapping(status)
    cards = tuple(_hunt_card(_hunt_mapping(item)) for item in hunts)
    return SearchHuntListPageView(
        hunt_count=len(cards),
        hunts=cards,
        unavailable_actions=build_search_hunt_unavailable_actions(),
        non_claim_banner=build_non_claim_banner_view(),
        warnings=_tuple(payload.get("warnings")),
        limitations=_unique(_tuple(payload.get("limitations")) + (SEARCH_HUNT_NON_CLAIM, SEARCH_HUNT_ABSENCE_LIMITATION)),
    )


def build_search_hunt_detail_page_view(
    hunt: Any,
    transitions: Sequence[Any],
    status: Mapping[str, Any] | None = None,
) -> SearchHuntDetailPageView:
    payload = _hunt_mapping(hunt)
    status_payload = _mapping(status)
    summary_rows = _summary_rows(status_payload.get("summaries"))
    query = str(payload.get("query", ""))
    hunt_id = str(payload.get("id", ""))
    command_controls_enabled = bool(status_payload.get("command_controls_enabled", False))
    steering_controls_enabled = bool(status_payload.get("steering_controls_enabled", False))
    exhaustion_report = _mapping(status_payload.get("exhaustion_report"))
    exhaustion_generation_enabled = bool(status_payload.get("exhaustion_report_generation_enabled", False))
    linked_needs = tuple(_need_card(_mapping(item)) for item in _sequence(status_payload.get("search_needs")))
    linked_workunits = tuple(_workunit_view(_mapping(item)) for item in _sequence(status_payload.get("workunits")))
    runner_summary = _mapping(status_payload.get("background_runner"))
    runner_plan = _mapping(runner_summary.get("plan"))
    return SearchHuntDetailPageView(
        hunt_id=hunt_id,
        found=bool(payload),
        query=query,
        normalized_query=str(payload.get("normalized_query", "")),
        state=str(payload.get("state", "")),
        intent=str(payload.get("intent", "")),
        destination=str(payload.get("destination", "")),
        created_at=str(payload.get("created_at", "")),
        updated_at=str(payload.get("updated_at", "")),
        reviewed_result_count=int(payload.get("reviewed_result_count", 0) or 0),
        candidate_result_count=int(payload.get("candidate_result_count", 0) or 0),
        reviewed_index_search_summary=summary_rows["reviewed_index_search"],
        local_absence_summary=summary_rows["local_absence"],
        checked_layers=_layer_views(payload.get("checked_layers"), "checked"),
        unchecked_layers=_layer_views(payload.get("unchecked_layers"), "unchecked/deferred"),
        transitions=tuple(_transition_view(item) for item in transitions),
        commands=tuple(_command_view(item) for item in _sequence(status_payload.get("commands"))),
        steering_preferences=tuple(_steering_view(item) for item in _sequence(status_payload.get("steering_preferences"))),
        latest_exhaustion_report=_exhaustion_summary_rows(exhaustion_report),
        exhaustion_checked_layers=_exhaustion_checked_rows(exhaustion_report),
        exhaustion_deferred_layers=_exhaustion_deferred_rows(exhaustion_report),
        exhaustion_blocked_by_policy=_exhaustion_blocked_rows(exhaustion_report),
        exhaustion_recommended_actions=_exhaustion_action_rows(exhaustion_report),
        exhaustion_non_claims=_exhaustion_non_claim_rows(exhaustion_report),
        state_commands=build_search_hunt_state_commands() if command_controls_enabled else (),
        command_controls_enabled=command_controls_enabled,
        steering_controls_enabled=steering_controls_enabled,
        exhaustion_generation_enabled=exhaustion_generation_enabled,
        search_needs=linked_needs,
        workunits=linked_workunits,
        agent_research_tasks=tuple(_agent_task_card(_mapping(item)) for item in _sequence(status_payload.get("agent_research_tasks"))),
        agent_research_boundary=build_agent_research_disabled_boundary_view(),
        background_runner_plan=tuple(_background_runner_plan_row(_mapping(item)) for item in _sequence(runner_plan.get("runnable_workunits"))),
        background_runner_blocked_workunits=tuple(_background_runner_plan_row(_mapping(item)) for item in _sequence(runner_plan.get("blocked_workunits"))),
        background_runner_runs=tuple(_background_runner_run_row(_mapping(item)) for item in _sequence(runner_summary.get("runs"))),
        runner_controls_enabled=bool(status_payload.get("runner_controls_enabled", False)),
        search_need_creation_enabled=bool(status_payload.get("search_need_creation_enabled", False)),
        agent_research_task_draft_enabled=bool(status_payload.get("agent_research_task_draft_enabled", False)),
        unavailable_actions=build_search_hunt_unavailable_actions(),
        related_search_href="/search?q=" + str(query),
        related_absence_href="/absence?q=" + str(query),
        non_claim_banner=build_non_claim_banner_view(),
        warnings=_unique(_tuple(payload.get("warnings")) + _tuple(status_payload.get("warnings"))),
        limitations=_unique(_tuple(payload.get("limitations")) + _tuple(status_payload.get("limitations")) + (SEARCH_HUNT_NON_CLAIM, SEARCH_HUNT_ABSENCE_LIMITATION)),
        operator_token_required=bool(status_payload.get("operator_token_required_for_mutations", True)),
        localhost_only_mutations=bool(status_payload.get("localhost_only_mutations", True)),
        lan_command_mutations_enabled=bool(status_payload.get("lan_command_mutations_enabled", False)),
    )


def build_search_need_list_page_view(needs: Sequence[Any], status: Mapping[str, Any] | None = None) -> SearchNeedListPageView:
    payload = _mapping(status)
    cards = tuple(_need_card(_mapping(item)) for item in needs)
    return SearchNeedListPageView(
        need_count=len(cards),
        needs=cards,
        non_claim_banner=build_non_claim_banner_view(),
        warnings=_tuple(payload.get("warnings")),
        limitations=_unique(_tuple(payload.get("limitations")) + (SEARCH_NEED_NON_CLAIM,)),
    )


def build_search_need_detail_page_view(
    need: Any,
    transitions: Sequence[Any],
    status: Mapping[str, Any] | None = None,
) -> SearchNeedDetailPageView:
    payload = _mapping(need)
    status_payload = _mapping(status)
    need_id = str(payload.get("id", ""))
    hunt_id = str(payload.get("hunt_id", ""))
    exhaustion_report_id = str(payload.get("exhaustion_report_id", ""))
    workunit_plan = _mapping(status_payload.get("workunit_plan"))
    return SearchNeedDetailPageView(
        need_id=need_id,
        found=bool(payload),
        hunt_id=hunt_id,
        exhaustion_report_id=exhaustion_report_id,
        query=str(payload.get("query", "")),
        normalized_query=str(payload.get("normalized_query", "")),
        need_title=str(payload.get("need_title", "")),
        need_summary=str(payload.get("need_summary", "")),
        state=str(payload.get("state", "")),
        need_kind=str(payload.get("need_kind", "")),
        desired_outcome=_display_outcome(str(payload.get("desired_outcome", ""))),
        priority=int(payload.get("priority", 0) or 0),
        local_result_state=str(payload.get("local_result_state", "")),
        checked_layers=_layer_views(payload.get("checked_layers"), "checked"),
        deferred_layers=_layer_views(payload.get("deferred_layers"), "unchecked/deferred"),
        recommended_future_work=_future_work_rows(payload.get("recommended_future_work")),
        policy_limitations=_limitation_rows(payload.get("policy_limitations")),
        transitions=tuple(_need_transition_view(item) for item in transitions),
        workunit_plan=tuple(_workunit_plan_item_view(_mapping(item)) for item in _sequence(workunit_plan.get("items"))),
        workunits=tuple(_workunit_view(_mapping(item)) for item in _sequence(status_payload.get("workunits"))),
        agent_research_tasks=tuple(_agent_task_card(_mapping(item)) for item in _sequence(status_payload.get("agent_research_tasks"))),
        agent_research_boundary=build_agent_research_disabled_boundary_view(),
        agent_research_task_draft_enabled=bool(status_payload.get("agent_research_task_draft_enabled", False)),
        state_transition_enabled=bool(status_payload.get("state_transition_enabled", False)),
        workunit_creation_enabled=bool(status_payload.get("workunit_creation_enabled", False)),
        related_hunt_href="/hunt/" + hunt_id,
        related_exhaustion_href="/hunt/" + hunt_id + "/exhaustion",
        non_claim_banner=build_non_claim_banner_view(),
        warnings=_unique(_tuple(payload.get("warnings")) + _tuple(status_payload.get("warnings"))),
        limitations=_unique(_tuple(payload.get("policy_limitations")) + _tuple(status_payload.get("limitations")) + (SEARCH_NEED_NON_CLAIM,)),
        operator_token_required=bool(status_payload.get("operator_token_required_for_mutations", True)),
        localhost_only_mutations=bool(status_payload.get("localhost_only_mutations", True)),
        lan_mutations_enabled=bool(status_payload.get("lan_mutations_enabled", False)),
    )


def build_search_hunt_not_found_page_view(hunt_id: str) -> SearchHuntNotFoundPageView:
    return SearchHuntNotFoundPageView(
        hunt_id=str(hunt_id),
        non_claim_banner=build_non_claim_banner_view(),
        warnings=(),
        limitations=(SEARCH_HUNT_NON_CLAIM, "Missing hunt IDs are not created implicitly."),
    )


def build_agent_research_disabled_boundary_view() -> AgentResearchDisabledBoundaryView:
    return AgentResearchDisabledBoundaryView(
        provider_enabled=False,
        execution_enabled=False,
        browser_enabled=False,
        source_probe_enabled=False,
        candidate_only_output=True,
        review_required=True,
        gate_required="future provider gate",
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


def build_search_hunt_unavailable_actions() -> tuple[SearchHuntUnavailableActionView, ...]:
    return tuple(SearchHuntUnavailableActionView(action=action, status=status, reason=reason) for action, status, reason in SEARCH_HUNT_UNAVAILABLE_ACTIONS)


def build_search_hunt_state_commands() -> tuple[SearchHuntStateCommandView, ...]:
    return (
        SearchHuntStateCommandView("Pause session", "pause", False),
        SearchHuntStateCommandView("Resume session", "resume", False),
        SearchHuntStateCommandView("Cancel session", "cancel", False),
        SearchHuntStateCommandView("Block session", "block", True),
        SearchHuntStateCommandView("Wait for user", "wait-for-user", False),
        SearchHuntStateCommandView("Wait for policy", "wait-for-policy", False),
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


def _hunt_card(item: Mapping[str, Any]) -> SearchHuntCardView:
    hunt_id = str(item.get("id", ""))
    checked_layers = _tuple(item.get("checked_layers"))
    return SearchHuntCardView(
        hunt_id=hunt_id,
        query=str(item.get("query", "")),
        normalized_query=str(item.get("normalized_query", "")),
        state=str(item.get("state", "")),
        created_at=str(item.get("created_at", "")),
        updated_at=str(item.get("updated_at", "")),
        reviewed_result_count=int(item.get("reviewed_result_count", 0) or 0),
        checked_layer_summary=", ".join(checked_layers) if checked_layers else "none recorded",
        warning_count=len(_tuple(item.get("warnings"))),
        limitation_count=len(_tuple(item.get("limitations"))),
        detail_href="/hunt/" + hunt_id,
    )


def _need_card(item: Mapping[str, Any]) -> SearchNeedCardView:
    need_id = str(item.get("id", ""))
    hunt_id = str(item.get("hunt_id", ""))
    return SearchNeedCardView(
        need_id=need_id,
        hunt_id=hunt_id,
        query=str(item.get("query", "")),
        need_title=str(item.get("need_title", need_id)),
        state=str(item.get("state", "")),
        need_kind=str(item.get("need_kind", "")),
        desired_outcome=_display_outcome(str(item.get("desired_outcome", ""))),
        priority=int(item.get("priority", 0) or 0),
        warning_count=len(_tuple(item.get("warnings"))),
        limitation_count=len(_tuple(item.get("policy_limitations"))),
        detail_href="/need/" + need_id,
        hunt_href="/hunt/" + hunt_id,
    )


def _transition_view(value: Any) -> SearchHuntTransitionView:
    item = _hunt_mapping(value)
    return SearchHuntTransitionView(
        transition_id=str(item.get("id", "")),
        from_state=str(item.get("from_state", "")),
        to_state=str(item.get("to_state", "")),
        reason=str(item.get("reason", "") or ""),
        created_at=str(item.get("created_at", "")),
    )


def _need_transition_view(value: Any) -> SearchNeedTransitionView:
    item = _mapping(value)
    return SearchNeedTransitionView(
        transition_id=str(item.get("id", "")),
        from_state=str(item.get("from_state", "") or ""),
        to_state=str(item.get("to_state", "")),
        reason=str(item.get("reason", "") or ""),
        created_at=str(item.get("created_at", "")),
    )


def _workunit_plan_item_view(value: Mapping[str, Any]) -> SearchNeedWorkUnitPlanItemView:
    return SearchNeedWorkUnitPlanItemView(
        plan_item_id=str(value.get("plan_item_id", "")),
        kind=str(value.get("kind", "")),
        title=str(value.get("title", "")),
        policy_state=str(value.get("policy_state", "")),
        reason=str(value.get("reason", "")),
        priority=str(value.get("priority", "")),
        blocked_reason=str(value.get("blocked_reason", "") or ""),
    )


def _workunit_view(value: Mapping[str, Any]) -> SearchNeedWorkUnitView:
    payload = _mapping(value.get("payload"))
    return SearchNeedWorkUnitView(
        workunit_id=str(value.get("id", "")),
        kind=str(value.get("kind", "")),
        state=str(value.get("state", "")),
        title=str(value.get("title", "")),
        policy_state=str(value.get("policy_state", payload.get("policy_state", ""))),
        search_need_id=str(value.get("search_need_id", payload.get("search_need_id", ""))),
        search_hunt_id=str(value.get("search_hunt_id", payload.get("search_hunt_id", ""))),
        exhaustion_report_id=str(value.get("exhaustion_report_id", payload.get("exhaustion_report_id", ""))),
        execution_enabled=bool(value.get("execution_enabled", payload.get("execution_enabled", False))),
    )


def _agent_task_card(value: Mapping[str, Any]) -> AgentResearchTaskCardView:
    schema = _mapping(value.get("output_schema"))
    return AgentResearchTaskCardView(
        task_id=str(value.get("task_id", "")),
        search_hunt_id=str(value.get("search_hunt_id", "")),
        search_need_id=str(value.get("search_need_id", "")),
        exhaustion_report_id=str(value.get("exhaustion_report_id", "")),
        query=str(value.get("query", "")),
        state=str(value.get("state", "")),
        provider_enabled=bool(value.get("provider_enabled", False)),
        execution_enabled=bool(value.get("execution_enabled", False)),
        report_candidate_only=bool(schema.get("candidate_only", True)),
        review_required=bool(schema.get("review_required", True)),
    )


def _background_runner_plan_row(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return {
        "workunit_id": str(value.get("workunit_id", "")),
        "worker_kind": str(value.get("worker_kind", "")),
        "state": str(value.get("state", "")),
        "policy_state": str(value.get("policy_state", "")),
        "runnable": bool(value.get("runnable", False)),
        "blocked_reason": str(value.get("blocked_reason", "") or ""),
    }


def _background_runner_run_row(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return {
        "run_id": str(value.get("run_id", "")),
        "status": str(value.get("status", "")),
        "worker_kinds": ", ".join(_tuple(value.get("worker_kinds"))),
        "workunit_ids": ", ".join(_tuple(value.get("workunit_ids"))),
        "started_at": str(value.get("started_at", "")),
        "finished_at": str(value.get("finished_at", "") or ""),
    }


def _future_work_rows(value: Any) -> tuple[SearchHuntExhaustionRowView, ...]:
    rows = tuple(SearchHuntExhaustionRowView(str(item), "deferred", "Future work category only; no work was created.") for item in _tuple(value))
    return rows or (SearchHuntExhaustionRowView("none", "not_recorded", "No future work categories recorded."),)


def _limitation_rows(value: Any) -> tuple[SearchHuntExhaustionRowView, ...]:
    rows = tuple(SearchHuntExhaustionRowView("limitation", "active", str(item)) for item in _tuple(value))
    return rows or (SearchHuntExhaustionRowView("none", "not_recorded", "No policy limitations recorded."),)


def _display_outcome(value: str) -> str:
    if value == "acquire_or_download_later_policy_gated":
        return "acquire_later_policy_gated"
    if value == "install_or_emulate_later_policy_gated":
        return "emulate_later_policy_gated"
    if value == "preserve_or_mirror_later_policy_gated":
        return "preserve_later_policy_gated"
    return value


def _command_view(value: Any) -> SearchHuntCommandView:
    item = _hunt_mapping(value)
    return SearchHuntCommandView(
        command_id=str(item.get("command_id", "")),
        command_type=str(item.get("command_type", "")),
        previous_state=str(item.get("previous_state", "")),
        resulting_state=str(item.get("resulting_state", "")),
        operator_label=str(item.get("operator_label", "")),
        reason=str(item.get("reason", "") or ""),
        policy_decision=str(item.get("policy_decision", "")),
        created_at=str(item.get("created_at", "")),
    )


def _steering_view(value: Any) -> SearchHuntSteeringPreferenceView:
    item = _hunt_mapping(value)
    return SearchHuntSteeringPreferenceView(
        steering_id=str(item.get("steering_id", item.get("id", ""))),
        command_id=str(item.get("command_id", "")),
        hunt_id=str(item.get("hunt_id", "")),
        command_type=str(item.get("command_type", "")),
        value=str(item.get("value", "")),
        reason=str(item.get("reason", "") or ""),
        operator_label=str(item.get("operator_label", "")),
        active=bool(item.get("active", False)),
        created_at=str(item.get("created_at", "")),
        updated_at=str(item.get("updated_at", "")),
    )


def _exhaustion_summary_rows(report: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    if not report:
        return ({"field": "latest_exhaustion_report", "value": "not generated"},)
    result_state = _mapping(report.get("result_state"))
    query = _mapping(report.get("query_summary"))
    return (
        {"field": "report_id", "value": report.get("report_id", "")},
        {"field": "state", "value": report.get("state", "")},
        {"field": "created_at", "value": report.get("created_at", "")},
        {"field": "hunt_state", "value": query.get("hunt_state", "")},
        {"field": "confidence_class", "value": result_state.get("confidence_class", "")},
        {"field": "absence_state", "value": result_state.get("absence_state", "")},
    )


def _exhaustion_checked_rows(report: Mapping[str, Any]) -> tuple[SearchHuntExhaustionRowView, ...]:
    rows = []
    for item in _sequence(report.get("checked_layers")):
        value = _mapping(item)
        rows.append(
            SearchHuntExhaustionRowView(
                name=str(value.get("layer", "")),
                status=str(value.get("status", "")),
                note=str(value.get("summary", "")),
            )
        )
    return tuple(rows) or (SearchHuntExhaustionRowView("none", "not_generated", "No exhaustion report has been generated."),)


def _exhaustion_deferred_rows(report: Mapping[str, Any]) -> tuple[SearchHuntExhaustionRowView, ...]:
    rows = []
    for item in _sequence(report.get("unchecked_or_deferred_layers")):
        value = _mapping(item)
        rows.append(
            SearchHuntExhaustionRowView(
                name=str(value.get("layer", "")),
                status=str(value.get("status", "")),
                note=str(value.get("reason", "")),
            )
        )
    return tuple(rows) or (SearchHuntExhaustionRowView("none", "not_generated", "Deferred layer report is not available yet."),)


def _exhaustion_blocked_rows(report: Mapping[str, Any]) -> tuple[SearchHuntExhaustionRowView, ...]:
    rows = []
    for item in _sequence(report.get("blocked_by_policy")):
        value = _mapping(item)
        rows.append(
            SearchHuntExhaustionRowView(
                name=str(value.get("policy_id", "")),
                status=str(value.get("status", "")),
                note=str(value.get("reason", "")),
            )
        )
    return tuple(rows) or (SearchHuntExhaustionRowView("none", "not_generated", "Blocked policy report is not available yet."),)


def _exhaustion_action_rows(report: Mapping[str, Any]) -> tuple[SearchHuntExhaustionRowView, ...]:
    rows = []
    for item in _sequence(report.get("recommended_next_actions")):
        value = _mapping(item)
        rows.append(
            SearchHuntExhaustionRowView(
                name=str(value.get("action", "")),
                status=str(value.get("status", "")),
                note=str(value.get("reason", "")),
            )
        )
    return tuple(rows) or (SearchHuntExhaustionRowView("none", "not_generated", "Recommended future action categories are not available yet."),)


def _exhaustion_non_claim_rows(report: Mapping[str, Any]) -> tuple[SearchHuntExhaustionRowView, ...]:
    rows = []
    for item in _sequence(report.get("non_claims")):
        value = _mapping(item)
        rows.append(
            SearchHuntExhaustionRowView(
                name=str(value.get("claim", "")),
                status="allowed" if bool(value.get("allowed", False)) else "not_claimed",
                note=str(value.get("wording", "")),
            )
        )
    return tuple(rows) or (SearchHuntExhaustionRowView("none", "not_generated", "Non-claim rows are not available yet."),)


def _layer_views(value: Any, status: str) -> tuple[SearchHuntLayerView, ...]:
    layers = _tuple(value)
    if not layers:
        return (SearchHuntLayerView("none", status, "No layers recorded."),)
    note = "Visible in this read-only view."
    if status.startswith("unchecked"):
        note = "Deferred; no background work was started."
    return tuple(SearchHuntLayerView(layer, status, note) for layer in layers)


def _summary_rows(value: Any) -> dict[str, tuple[Mapping[str, Any], ...]]:
    summaries = {"reviewed_index_search": (), "local_absence": ()}
    for raw in _sequence(value):
        item = _hunt_mapping(raw)
        summary_type = str(item.get("summary_type", ""))
        payload = _mapping(item.get("payload"))
        if summary_type == "reviewed_index_search":
            summaries["reviewed_index_search"] = _reviewed_summary_rows(payload)
        elif summary_type == "local_absence":
            summaries["local_absence"] = _absence_summary_rows(payload)
    return summaries


def _reviewed_summary_rows(payload: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    if not payload:
        return ({"field": "reviewed_index_search_summary", "value": "not recorded"},)
    return (
        {"field": "query", "value": payload.get("query", "")},
        {"field": "normalized_query", "value": payload.get("normalized_query", "")},
        {"field": "reviewed_index_only", "value": bool(payload.get("reviewed_index_only", True))},
        {"field": "current_index_only", "value": bool(payload.get("current_index_only", True))},
        {"field": "result_count", "value": int(payload.get("result_count", 0) or 0)},
        {"field": "limit", "value": int(payload.get("limit", 0) or 0)},
    )


def _absence_summary_rows(payload: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    if not payload:
        return ({"field": "local_absence_summary", "value": "not recorded"},)
    absence = _mapping(payload.get("absence"))
    return (
        {"field": "query", "value": payload.get("query", "")},
        {"field": "normalized_query", "value": payload.get("normalized_query", "")},
        {"field": "local_current_index_absence_only", "value": bool(payload.get("local_current_index_absence_only", True))},
        {"field": "result_count", "value": int(absence.get("result_count", 0) or 0)},
        {"field": "unchecked_layer_count", "value": len(_tuple(payload.get("unchecked_layers")))},
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


def _hunt_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return {}


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
