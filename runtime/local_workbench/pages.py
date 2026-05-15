"""Server-rendered local workbench pages."""

from typing import Any, Mapping, Sequence
from urllib.parse import quote

from .html import escape_html, render_document, render_limitations, render_link, render_notice, render_table, render_warnings
from .templates import record_links, search_form
from .view_models import (
    AbsencePageView,
    CapabilityUnavailableView,
    HomePageView,
    ObjectPageView,
    RebuildPageView,
    ReviewItemPageView,
    ReviewQueuePageView,
    SearchHuntDetailPageView,
    SearchHuntExhaustionRowView,
    SearchHuntLayerView,
    SearchHuntListPageView,
    SearchHuntNotFoundPageView,
    SearchHuntCommandView,
    SearchHuntStateCommandView,
    SearchHuntSteeringPreferenceView,
    SearchHuntTransitionView,
    SearchHuntUnavailableActionView,
    SearchNeedCardView,
    SearchNeedDetailPageView,
    SearchNeedListPageView,
    SearchNeedTransitionView,
    SearchNeedWorkUnitPlanItemView,
    SearchNeedWorkUnitView,
    SearchPageView,
    SearchResultCardView,
    SourcePageView,
    StatusPageView,
)


def render_home_page(view: HomePageView) -> str:
    body = "\n".join(
        [
            "<h1>Eureka Local Appliance</h1>",
            render_notice("info", "Read-only localhost JSON API with a local workbench over the reviewed public index."),
            "<section aria-labelledby=\"summary-heading\"><h2 id=\"summary-heading\">Local appliance status card</h2>",
            _key_values(
                (
                    ("status", view.status),
                    ("instance_id", view.instance_id),
                    ("instance_schema_version", view.instance_schema_version),
                    ("reviewed_local_record_count", view.record_count),
                    ("lan_enabled", view.lan_enabled),
                    ("lan_read_only", view.lan_read_only),
                )
            ),
            "</section>",
            render_notice(
                "warning" if view.lan_enabled else "scope",
                "LAN mode is read-only inspection only." if view.lan_enabled else "LAN binding is disabled by default.",
            ),
            search_form(),
            "<section aria-labelledby=\"links-heading\"><h2 id=\"links-heading\">Links</h2><ul>",
            f"<li>{render_link('/status', 'Status page')}</li>",
            f"<li>{render_link('/absence?q=sampleproject', 'Sample absence page')}</li>",
            f"<li>{render_link('/hunts', 'Search Hunts')}</li>",
            f"<li>{render_link('/needs', 'SearchNeeds')}</li>",
            f"<li>{render_link('/review', 'Review queue')}</li>",
            f"<li>{render_link('/rebuild', 'Reviewed-index rebuild')}</li>",
            f"<li>{render_link('/api/v1/status', 'JSON API status')}</li>",
            f"<li>{render_link('/api/v1/health', 'JSON health')}</li>",
            "</ul></section>",
            _unavailable_capabilities(view.unavailable_capabilities),
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Eureka Local Appliance", body)


def render_search_page(view: SearchPageView) -> str:
    cards = "".join(_result_card(result) for result in view.results)
    empty = ""
    if not view.results:
        empty = render_notice(
            "empty",
            "No reviewed results in the local index. This is local current-index absence only, not global proof.",
        ) + f"<p>{render_link('/absence?q=' + quote(view.query), 'Open absence page')}</p>"
    body = "\n".join(
        [
            "<h1>Search</h1>",
            render_notice("scope", view.local_index_limitation),
            search_form(view.query),
            f"<p>Submitted query: {escape_html(view.query)}</p>",
            f"<p>Reviewed result count: {escape_html(view.result_count)}</p>",
            _key_values((("query", view.query), ("reviewed_local_result_count", view.result_count))),
            empty,
            cards,
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Search - Eureka Local Appliance", body)


def render_object_page(view: ObjectPageView) -> str:
    if not view.found:
        body = "\n".join(
            [
                "<h1>Object not found</h1>",
                _key_values((("record_id", view.record_id),)),
                render_notice("empty", "The record was not found in the local reviewed index."),
                "<p>" + render_link("/search", "Back to search") + " | " + render_link("/status", "Status") + "</p>",
                render_limitations(view.limitations),
            ]
        )
        return render_document("Object not found - Eureka Local Appliance", body)
    body = "\n".join(
        [
            f"<h1>{escape_html(view.title)}</h1>",
            _key_values(
                (
                    ("record_id", view.record_id),
                    ("description", view.description),
                    ("source_id", view.source_id),
                    ("searchable_text_excerpt", view.searchable_text_excerpt),
                )
            ),
            "<p>"
            + " | ".join(
                (
                    render_link("/search", "Back to search"),
                    render_link("/source/" + quote(view.source_id), "Source page") if view.source_id else render_link("/status", "Status"),
                    render_link("/status", "Status"),
                )
            )
            + "</p>",
            _provenance_table(view.provenance_refs),
            "<section aria-labelledby=\"fields-heading\"><h2 id=\"fields-heading\">Normalized fields</h2>",
            render_table(view.normalized_fields, headers=("field", "value")),
            "</section>",
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Object - Eureka Local Appliance", body)


def render_source_page(view: SourcePageView) -> str:
    cards = "".join(_result_card(record) for record in view.records)
    empty = render_notice("empty", "No local reviewed index records for this source.") if not view.records else ""
    body = "\n".join(
        [
            "<h1>Source</h1>",
            render_notice("scope", view.local_scope_note),
            _key_values((("source_id", view.source_id), ("source_record_count_in_local_reviewed_index", view.result_count))),
            empty,
            cards,
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Source - Eureka Local Appliance", body)


def render_absence_page(view: AbsencePageView) -> str:
    checked_sources = [{"source_id": source} for source in view.checked_sources] or [{"source_id": "no reviewed source records in local index"}]
    body = "\n".join(
        [
            "<h1>Absence</h1>",
            search_form(view.query),
            _key_values((("query", view.query), ("local_result_count", view.result_count))),
            render_notice("warning", view.non_claim),
            render_notice("scope", "Absence is local current-index absence only, not global proof."),
            "<section aria-labelledby=\"checked-heading\"><h2 id=\"checked-heading\">Checked local layers</h2>",
            render_table(tuple({"checked_layer": layer} for layer in view.checked_layers), headers=("checked_layer",)),
            "</section>",
            "<section aria-labelledby=\"sources-heading\"><h2 id=\"sources-heading\">Checked source references</h2>",
            render_table(checked_sources, headers=("source_id",)),
            "</section>",
            "<section aria-labelledby=\"unchecked-heading\"><h2 id=\"unchecked-heading\">Unchecked and deferred layers</h2>",
            render_table(tuple({"unchecked_layer": layer} for layer in view.unchecked_layers), headers=("unchecked_layer",)),
            "</section>",
            _unavailable_capabilities(view.unavailable_capabilities),
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Absence - Eureka Local Appliance", body)


def render_status_page(view: StatusPageView) -> str:
    flags = [
        {"flag": "read_only", "value": view.read_only},
        {"flag": "migration_needed", "value": view.migration_needed},
        {"flag": "server_enabled", "value": view.server_enabled},
        {"flag": "bind_lan", "value": view.bind_lan},
        {"flag": "lan_enabled", "value": view.lan_enabled},
        {"flag": "lan_read_only", "value": view.lan_read_only},
        {"flag": "lan_mutations_enabled", "value": view.lan_mutations_enabled},
        {"flag": "deployment_performed", "value": view.deployment_performed},
        {"flag": "production_readiness_claimed", "value": view.production_readiness_claimed},
        {"flag": "public_launch_readiness_claimed", "value": view.public_launch_readiness_claimed},
    ]
    store_rows = tuple(
        {
            "store": store.store_id,
            "relative_path": store.relative_path,
            "opened": store.opened,
            "integrity": store.integrity_status,
            "schema": store.schema_version,
        }
        for store in view.stores
    )
    index = view.index_status
    body = "\n".join(
        [
            "<h1>Status</h1>",
            render_notice(
                "warning" if view.lan_enabled else "scope",
                "Explicit LAN binding is read-only and unsafe routes stay localhost-only."
                if view.lan_enabled
                else "LAN binding is disabled by default; explicit bind flag is required.",
            ),
            "<section aria-labelledby=\"instance-heading\"><h2 id=\"instance-heading\">Instance</h2>",
            f"<p>Instance ID: {escape_html(view.instance_id)}</p>",
            _key_values(
                (
                    ("instance_id", view.instance_id),
                    ("instance_schema_version", view.instance_schema_version),
                    ("instance_root", view.instance_root),
                    ("store_manifest_store_count", view.store_count),
                )
            ),
            "</section>",
            "<section aria-labelledby=\"stores-heading\"><h2 id=\"stores-heading\">Store status</h2>",
            render_table(store_rows, headers=("store", "relative_path", "opened", "integrity", "schema")),
            "</section>",
            "<section aria-labelledby=\"index-heading\"><h2 id=\"index-heading\">Reviewed public index status</h2>",
            _key_values(
                (
                    ("record_count", index.record_count),
                    ("rebuild_count", index.rebuild_count),
                    ("source_ref_count", index.source_ref_count),
                    ("evidence_ref_count", index.evidence_ref_count),
                    ("review_ref_count", index.review_ref_count),
                )
            ),
            render_table(index.source_counts, headers=("source_id", "record_count")) if index.source_counts else "<p>No source counts in local index.</p>",
            "</section>",
            "<section aria-labelledby=\"flags-heading\"><h2 id=\"flags-heading\">Runtime and non-claim flags</h2>",
            render_table(flags, headers=("flag", "value")),
            "</section>",
            "<section aria-labelledby=\"status-links-heading\"><h2 id=\"status-links-heading\">Machine-readable status</h2><ul>",
            f"<li>{render_link('/api/v1/status', 'JSON status')}</li>",
            f"<li>{render_link('/api/v1/health', 'JSON health')}</li>",
            "</ul></section>",
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Status - Eureka Local Appliance", body)


def render_review_queue_page(view: ReviewQueuePageView) -> str:
    rows = tuple(
        {
            "review_item_id": render_link("/review/" + quote(item.review_item_id), item.review_item_id),
            "status": item.queue_status,
            "subject": item.subject_id,
            "evidence_id": item.evidence_id,
            "source_cache_entry_id": item.source_cache_entry_id,
            "summary": item.summary,
            "priority": item.priority,
        }
        for item in view.review_items
    )
    body = "\n".join(
        [
            "<h1>Review queue</h1>",
            render_notice("scope", "Local review decisions are local operator state only."),
            f"<p>Review item count: {escape_html(view.result_count)}</p>",
            _render_html_table(
                rows,
                headers=("review_item_id", "status", "subject", "evidence_id", "source_cache_entry_id", "summary", "priority"),
            )
            if rows
            else render_notice("empty", "No local review items are queued."),
            "<p>" + render_link("/rebuild", "Reviewed-index rebuild") + " | " + render_link("/status", "Status") + "</p>",
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Review queue - Eureka Local Appliance", body)


def render_review_item_page(view: ReviewItemPageView) -> str:
    if not view.found:
        body = "\n".join(
            [
                "<h1>Review item not found</h1>",
                _key_values((("review_item_id", view.review_item_id),)),
                render_notice("empty", "The review item was not found in the local review queue."),
                "<p>" + render_link("/review", "Back to review queue") + "</p>",
                render_limitations(view.limitations),
            ]
        )
        return render_document("Review item not found - Eureka Local Appliance", body)
    body = "\n".join(
        [
            "<h1>Review item</h1>",
            render_notice("scope", "Decision recording is local-only and requires an operator token."),
            _key_values(
                (
                    ("review_item_id", view.review_item_id),
                    ("queue_status", view.queue_status),
                    ("subject_kind", view.subject_kind),
                    ("subject_id", view.subject_id),
                    ("summary", view.summary),
                    ("evidence_id", view.evidence_id),
                    ("source_cache_entry_id", view.source_cache_entry_id),
                )
            ),
            _decision_form(view.review_item_id),
            "<section aria-labelledby=\"evidence-heading\"><h2 id=\"evidence-heading\">Evidence reference</h2>",
            render_table(view.evidence, headers=("field", "value")),
            "</section>",
            "<section aria-labelledby=\"cache-heading\"><h2 id=\"cache-heading\">Source cache reference</h2>",
            render_table(view.source_cache_entry, headers=("field", "value")),
            "</section>",
            "<section aria-labelledby=\"decisions-heading\"><h2 id=\"decisions-heading\">Decision history</h2>",
            _render_mapping_sequence(view.decisions, ("decision_id", "decision_kind", "decision_status", "decision_actor", "reason", "created_at")),
            "</section>",
            "<section aria-labelledby=\"events-heading\"><h2 id=\"events-heading\">Review event history</h2>",
            _render_mapping_sequence(view.events, ("event_id", "event_kind", "created_at")),
            "</section>",
            "<p>" + render_link("/review", "Back to review queue") + " | " + render_link("/rebuild", "Reviewed-index rebuild") + "</p>",
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Review item - Eureka Local Appliance", body)


def render_rebuild_page(view: RebuildPageView) -> str:
    body = "\n".join(
        [
            "<h1>Reviewed-index rebuild</h1>",
            render_notice("scope", "Rebuild writes only to the explicit local reviewed public index store."),
            _key_values(
                (
                    ("reviewed_local_record_count", view.record_count),
                    ("rebuild_count", view.rebuild_count),
                    ("operator_token_required", view.operator_token_required),
                    ("master_index_mutated", False),
                    ("site_dist_mutated", False),
                )
            ),
            _rebuild_form(),
            "<p>" + render_link("/review", "Review queue") + " | " + render_link("/api/v1/rebuild/status", "JSON rebuild status") + "</p>",
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Reviewed-index rebuild - Eureka Local Appliance", body)


def render_search_hunt_list_page(view: SearchHuntListPageView) -> str:
    rows = tuple(
        {
            "hunt_id": render_link(item.detail_href, item.hunt_id),
            "query": item.query,
            "state": item.state,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "reviewed_result_count": item.reviewed_result_count,
            "checked_layers": item.checked_layer_summary,
            "warning_count": item.warning_count,
            "limitation_count": item.limitation_count,
        }
        for item in view.hunts
    )
    body = "\n".join(
        [
            "<h1>Search Hunts</h1>",
            render_notice("scope", "Search Hunt Sessions are local investigation state, not reviewed results."),
            _key_values((("hunt_count", view.hunt_count), ("read_only", True), ("adds_hunts", False), ("state_changes_enabled", False))),
            _render_html_table(
                rows,
                headers=(
                    "hunt_id",
                    "query",
                    "state",
                    "created_at",
                    "updated_at",
                    "reviewed_result_count",
                    "checked_layers",
                    "warning_count",
                    "limitation_count",
                ),
            )
            if rows
            else render_notice("empty", "No Search Hunt Sessions are stored in this local instance."),
            _search_hunt_unavailable_actions(view.unavailable_actions),
            "<p>" + render_link("/search", "Search reviewed index") + " | " + render_link("/status", "Status") + "</p>",
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Search Hunts - Eureka Local Appliance", body)


def render_search_hunt_detail_page(view: SearchHuntDetailPageView) -> str:
    if not view.found:
        return render_search_hunt_not_found_page(
            SearchHuntNotFoundPageView(
                hunt_id=view.hunt_id,
                non_claim_banner=view.non_claim_banner,
                warnings=view.warnings,
                limitations=view.limitations,
            )
        )
    body = "\n".join(
        [
            "<h1>Search Hunt Session</h1>",
            render_notice("scope", "This hunt records local investigation state only; it is not accepted evidence."),
            render_notice("scope", "Local absence is current-index absence only."),
            _key_values(
                (
                    ("hunt_id", view.hunt_id),
                    ("query", view.query),
                    ("normalized_query", view.normalized_query),
                    ("state", view.state),
                    ("intent", view.intent),
                    ("destination", view.destination),
                    ("created_at", view.created_at),
                    ("updated_at", view.updated_at),
                    ("reviewed_result_count", view.reviewed_result_count),
                    ("candidate_result_count", view.candidate_result_count),
                    ("workunit_creation_available", True),
                    ("workunit_execution_enabled", False),
                    ("source_probe_ran", False),
                    ("model_provider_used", False),
                )
            ),
            "<p>" + render_link(view.related_search_href, "Related local search") + " | " + render_link(view.related_absence_href, "Related local absence") + " | " + render_link("/hunts", "Back to hunts") + "</p>",
            "<section aria-labelledby=\"hunt-search-summary-heading\"><h2 id=\"hunt-search-summary-heading\">Reviewed-index search summary</h2>",
            render_table(view.reviewed_index_search_summary, headers=("field", "value")),
            "</section>",
            "<section aria-labelledby=\"hunt-absence-summary-heading\"><h2 id=\"hunt-absence-summary-heading\">Local absence summary</h2>",
            render_table(view.local_absence_summary, headers=("field", "value")),
            "</section>",
            _search_hunt_layers("checked-layers-heading", "Checked layers", view.checked_layers),
            _search_hunt_layers("unchecked-layers-heading", "Unchecked and deferred layers", view.unchecked_layers),
            _search_hunt_exhaustion_report(view),
            _search_hunt_linked_needs(view.search_needs),
            _search_hunt_linked_workunits(view.workunits),
            _background_hunt_runner_section(view),
            _search_need_creation_form(view) if view.search_need_creation_enabled else "",
            _search_hunt_command_controls(view) if view.command_controls_enabled else "",
            _search_hunt_steering_controls(view) if view.steering_controls_enabled else "",
            _search_hunt_command_history(view.commands),
            _search_hunt_steering_preferences(view.steering_preferences),
            _search_hunt_transitions(view.transitions),
            _search_hunt_unavailable_actions(view.unavailable_actions),
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Search Hunt Session - Eureka Local Appliance", body)


def render_search_hunt_not_found_page(view: SearchHuntNotFoundPageView) -> str:
    body = "\n".join(
        [
            "<h1>Search Hunt not found</h1>",
            _key_values((("hunt_id", view.hunt_id), ("created_implicitly", False))),
            render_notice("empty", "The Search Hunt Session was not found in this local instance."),
            render_notice("scope", "Missing hunt IDs are never created implicitly by the read-only UI."),
            "<p>" + render_link("/hunts", "Back to Search Hunts") + " | " + render_link("/search", "Search reviewed index") + "</p>",
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Search Hunt not found - Eureka Local Appliance", body)


def render_search_need_list_page(view: SearchNeedListPageView) -> str:
    rows = tuple(
        {
            "need_id": render_link(item.detail_href, item.need_id),
            "query": item.query,
            "state": item.state,
            "kind": item.need_kind,
            "desired_outcome": item.desired_outcome,
            "priority": item.priority,
            "linked_hunt": render_link(item.hunt_href, item.hunt_id) if item.hunt_id else "",
            "warning_count": item.warning_count,
            "limitation_count": item.limitation_count,
        }
        for item in view.needs
    )
    body = "\n".join(
        [
            "<h1>SearchNeeds</h1>",
            render_notice("scope", "SearchNeeds are local demand records, not evidence or reviewed results."),
            _key_values((("need_count", view.need_count), ("workunit_creation_available", True), ("workunit_execution_enabled", False), ("source_probe_ran", False), ("model_provider_used", False))),
            _render_html_table(
                rows,
                headers=("need_id", "query", "state", "kind", "desired_outcome", "priority", "linked_hunt", "warning_count", "limitation_count"),
            )
            if rows
            else render_notice("empty", "No SearchNeeds are stored in this local instance."),
            "<p>" + render_link("/hunts", "Search Hunts") + " | " + render_link("/status", "Status") + "</p>",
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("SearchNeeds - Eureka Local Appliance", body)


def render_search_need_detail_page(view: SearchNeedDetailPageView) -> str:
    if not view.found:
        body = "\n".join(
            [
                "<h1>SearchNeed not found</h1>",
                _key_values((("need_id", view.need_id), ("created_implicitly", False))),
                render_notice("empty", "The SearchNeed was not found in this local instance."),
                "<p>" + render_link("/needs", "Back to SearchNeeds") + "</p>",
                render_warnings(view.warnings),
                render_limitations(view.limitations),
            ]
        )
        return render_document("SearchNeed not found - Eureka Local Appliance", body)
    body = "\n".join(
        [
            "<h1>SearchNeed</h1>",
            render_notice("scope", "This SearchNeed records local demand only; it is not evidence, source approval, or reviewed truth."),
            _key_values(
                (
                    ("need_id", view.need_id),
                    ("hunt_id", view.hunt_id),
                    ("exhaustion_report_id", view.exhaustion_report_id),
                    ("query", view.query),
                    ("normalized_query", view.normalized_query),
                    ("state", view.state),
                    ("need_kind", view.need_kind),
                    ("desired_outcome", view.desired_outcome),
                    ("priority", view.priority),
                    ("local_result_state", view.local_result_state),
                    ("workunit_creation_available", view.workunit_creation_enabled),
                    ("workunit_execution_enabled", False),
                    ("source_probe_ran", False),
                    ("model_provider_used", False),
                )
            ),
            "<p>" + render_link(view.related_hunt_href, "Linked hunt") + " | " + render_link(view.related_exhaustion_href, "Linked exhaustion report") + " | " + render_link("/needs", "Back to SearchNeeds") + "</p>",
            "<section aria-labelledby=\"need-summary-heading\"><h2 id=\"need-summary-heading\">Need summary</h2>",
            _key_values((("need_title", view.need_title), ("need_summary", view.need_summary))),
            "</section>",
            _search_hunt_layers("need-checked-layers-heading", "Checked layers", view.checked_layers),
            _search_hunt_layers("need-deferred-layers-heading", "Deferred layers", view.deferred_layers),
            '<section aria-labelledby="need-future-work-heading"><h2 id="need-future-work-heading">Recommended future work categories</h2>',
            _search_hunt_exhaustion_rows(view.recommended_future_work),
            "</section>",
            '<section aria-labelledby="need-limitations-heading"><h2 id="need-limitations-heading">Policy limitations</h2>',
            _search_hunt_exhaustion_rows(view.policy_limitations),
            "</section>",
            _search_need_workunit_plan(view.workunit_plan),
            _search_need_linked_workunits(view.workunits),
            _search_need_workunit_form(view) if view.workunit_creation_enabled else "",
            _search_need_state_form(view) if view.state_transition_enabled else "",
            _search_need_transitions(view.transitions),
            _search_need_unavailable_actions(),
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("SearchNeed - Eureka Local Appliance", body)


def _result_card(result: SearchResultCardView) -> str:
    return (
        "<article>"
        f"<h2>{escape_html(result.title or result.record_id)}</h2>"
        + _key_values(
            (
                ("record_id", result.record_id),
                ("description", result.description),
                ("source_id", result.source_id),
                ("source_family", result.source_family or "not available"),
                ("trust_lane", result.trust_lane or "not available"),
            )
        )
        + _provenance_table(result.provenance_refs)
        + record_links(result.record_id, result.source_id)
        + render_warnings(result.warnings)
        + render_limitations(result.limitations)
        + "</article>"
    )


def _provenance_table(refs: Sequence[Any]) -> str:
    rows = tuple({"reference": ref.label, "value": ref.value} for ref in refs if ref.value)
    return "\n".join(
        [
            "<section aria-labelledby=\"refs-heading\"><h2 id=\"refs-heading\">Evidence and review references</h2>",
            "<p>Provenance references for the local reviewed projection.</p>",
            render_table(rows, headers=("reference", "value")) if rows else "<p>No provenance references available in this local projection.</p>",
            "</section>",
        ]
    )


def _unavailable_capabilities(capabilities: Sequence[CapabilityUnavailableView]) -> str:
    rows = tuple({"capability": item.capability, "status": item.status, "reason": item.reason} for item in capabilities)
    return "\n".join(
        [
            "<section aria-labelledby=\"unavailable-heading\"><h2 id=\"unavailable-heading\">Unavailable capabilities</h2>",
            render_table(rows, headers=("capability", "status", "reason")),
            "</section>",
        ]
    )


def _search_hunt_layers(section_id: str, title: str, layers: Sequence[SearchHuntLayerView]) -> str:
    rows = tuple({"layer": item.layer_id, "status": item.status, "note": item.note} for item in layers)
    return "\n".join(
        [
            f'<section aria-labelledby="{escape_html(section_id)}"><h2 id="{escape_html(section_id)}">{escape_html(title)}</h2>',
            render_table(rows, headers=("layer", "status", "note")),
            "</section>",
        ]
    )


def _search_hunt_command_controls(view: SearchHuntDetailPageView) -> str:
    forms = []
    for item in view.state_commands:
        forms.append(_hunt_state_command_form(view.hunt_id, item))
    return "\n".join(
        [
            '<section aria-labelledby="hunt-command-controls-heading"><h2 id="hunt-command-controls-heading">Operator state controls</h2>',
            render_notice("scope", "Controls require an operator token and mutate only local Search Hunt state."),
            render_notice("scope", "LAN clients cannot use command routes."),
            _key_values(
                (
                    ("operator_token_required", view.operator_token_required),
                    ("localhost_only_mutations", view.localhost_only_mutations),
                    ("lan_command_mutations_enabled", view.lan_command_mutations_enabled),
                    ("workunit_creation_enabled", False),
                    ("source_probe_execution_enabled", False),
                    ("model_provider_enabled", False),
                )
            ),
            "\n".join(forms),
            "</section>",
        ]
    )


def _hunt_state_command_form(hunt_id: str, command: SearchHuntStateCommandView) -> str:
    action = "/hunt/" + quote(hunt_id) + "/" + quote(command.action)
    reason_required = " required" if command.requires_reason else ""
    reason_note = "Required." if command.requires_reason else "Optional."
    return "\n".join(
        [
            f'<form method="post" action="{escape_html(action)}">',
            f'<p><strong>{escape_html(command.label)}</strong></p>',
            '<p><label>Operator token <input name="operator_token" type="password" autocomplete="off"></label></p>',
            '<p><label>Operator label <input name="operator_label" value="local_operator"></label></p>',
            f'<p><label>Reason <textarea name="reason"{reason_required}></textarea></label> {escape_html(reason_note)}</p>',
            f'<p><button type="submit">{escape_html(command.label)}</button></p>',
            "</form>",
        ]
    )


def _search_hunt_steering_controls(view: SearchHuntDetailPageView) -> str:
    return "\n".join(
        [
            '<section aria-labelledby="hunt-steering-controls-heading"><h2 id="hunt-steering-controls-heading">Steering preferences</h2>',
            render_notice("scope", "Steering records operator preference only; it is not source approval or evidence."),
            f'<form method="post" action="/hunt/{escape_html(quote(view.hunt_id))}/steer">',
            '<p><label>Operator token <input name="operator_token" type="password" autocomplete="off"></label></p>',
            '<p><label>Operator label <input name="operator_label" value="local_operator"></label></p>',
            '<p><label>Type <select name="type">',
            "".join(f'<option value="{escape_html(item)}">{escape_html(item)}</option>' for item in _steering_types()),
            "</select></label></p>",
            '<p><label>Value <input name="value"></label></p>',
            '<p><label>Reason <textarea name="reason"></textarea></label></p>',
            '<p><button type="submit">Record steering preference</button></p>',
            "</form>",
            "</section>",
        ]
    )


def _search_hunt_exhaustion_report(view: SearchHuntDetailPageView) -> str:
    return "\n".join(
        [
            '<section aria-labelledby="hunt-exhaustion-heading"><h2 id="hunt-exhaustion-heading">Exhaustion report</h2>',
            render_notice("scope", "Exhaustion reports explain local current-index state and deferred work only."),
            render_table(view.latest_exhaustion_report, headers=("field", "value")),
            _search_hunt_exhaustion_generation_form(view) if view.exhaustion_generation_enabled else "",
            '<section aria-labelledby="hunt-exhaustion-checked-heading"><h2 id="hunt-exhaustion-checked-heading">Exhaustion checked layers</h2>',
            _search_hunt_exhaustion_rows(view.exhaustion_checked_layers),
            "</section>",
            '<section aria-labelledby="hunt-exhaustion-deferred-heading"><h2 id="hunt-exhaustion-deferred-heading">Exhaustion deferred layers</h2>',
            _search_hunt_exhaustion_rows(view.exhaustion_deferred_layers),
            "</section>",
            '<section aria-labelledby="hunt-exhaustion-policy-heading"><h2 id="hunt-exhaustion-policy-heading">Blocked-by-policy entries</h2>',
            _search_hunt_exhaustion_rows(view.exhaustion_blocked_by_policy),
            "</section>",
            '<section aria-labelledby="hunt-exhaustion-actions-heading"><h2 id="hunt-exhaustion-actions-heading">Recommended future action categories</h2>',
            _search_hunt_exhaustion_rows(view.exhaustion_recommended_actions),
            "</section>",
            '<section aria-labelledby="hunt-exhaustion-non-claims-heading"><h2 id="hunt-exhaustion-non-claims-heading">Exhaustion non-claims</h2>',
            _search_hunt_exhaustion_rows(view.exhaustion_non_claims),
            "</section>",
            "</section>",
        ]
    )


def _search_hunt_exhaustion_generation_form(view: SearchHuntDetailPageView) -> str:
    action = "/hunt/" + quote(view.hunt_id) + "/exhaustion"
    return "\n".join(
        [
            render_notice("scope", "Report generation requires an operator token and is localhost-only."),
            f'<form method="post" action="{escape_html(action)}">',
            '<p><label>Operator token <input name="operator_token" type="password" autocomplete="off"></label></p>',
            '<p><label>Operator label <input name="operator_label" value="local_operator"></label></p>',
            '<p><button type="submit">Generate local exhaustion report</button></p>',
            "</form>",
        ]
    )


def _search_hunt_exhaustion_rows(rows: Sequence[SearchHuntExhaustionRowView]) -> str:
    payload = tuple({"name": item.name, "status": item.status, "note": item.note} for item in rows)
    return render_table(payload, headers=("name", "status", "note"))


def _search_hunt_linked_needs(needs: Sequence[SearchNeedCardView]) -> str:
    rows = tuple(
        {
            "need_id": render_link(item.detail_href, item.need_id),
            "state": item.state,
            "kind": item.need_kind,
            "desired_outcome": item.desired_outcome,
            "priority": item.priority,
        }
        for item in needs
    )
    return "\n".join(
        [
            '<section aria-labelledby="hunt-search-needs-heading"><h2 id="hunt-search-needs-heading">Linked SearchNeeds</h2>',
            render_table(rows, headers=("need_id", "state", "kind", "desired_outcome", "priority")) if rows else "<p>No SearchNeeds are linked to this hunt.</p>",
            "</section>",
        ]
    )


def _search_hunt_linked_workunits(workunits: Sequence[SearchNeedWorkUnitView]) -> str:
    rows = tuple(
        {
            "workunit_id": item.workunit_id,
            "kind": item.kind,
            "state": item.state,
            "policy_state": item.policy_state,
            "linked_need": render_link("/need/" + quote(item.search_need_id), item.search_need_id) if item.search_need_id else "",
            "execution_enabled": item.execution_enabled,
        }
        for item in workunits
    )
    return "\n".join(
        [
            '<section aria-labelledby="hunt-workunits-heading"><h2 id="hunt-workunits-heading">Linked WorkUnits</h2>',
            render_table(rows, headers=("workunit_id", "kind", "state", "policy_state", "linked_need", "execution_enabled")) if rows else "<p>No linked WorkUnits are recorded for this hunt.</p>",
            render_notice("scope", "WorkUnits shown here are local queue records only; this page has no runner controls."),
            "</section>",
        ]
    )


def _background_hunt_runner_section(view: SearchHuntDetailPageView) -> str:
    runnable_rows = tuple(dict(item) for item in view.background_runner_plan)
    blocked_rows = tuple(dict(item) for item in view.background_runner_blocked_workunits)
    run_rows = tuple(dict(item) for item in view.background_runner_runs)
    controls = _background_hunt_runner_controls(view) if view.runner_controls_enabled else ""
    return "\n".join(
        [
            '<section aria-labelledby="background-hunt-runner-heading"><h2 id="background-hunt-runner-heading">Background hunt runner</h2>',
            render_notice("scope", "The runner is limited to safe deterministic local workers."),
            render_notice("scope", "Source probes, extraction, AI/model providers, acquisition or launch actions, and deployment remain disabled."),
            "<h3>Runnable WorkUnits</h3>",
            render_table(runnable_rows, headers=("workunit_id", "worker_kind", "state", "policy_state", "runnable", "blocked_reason")) if runnable_rows else "<p>No safe runnable WorkUnits are currently available.</p>",
            "<h3>Policy-blocked WorkUnits</h3>",
            render_table(blocked_rows, headers=("workunit_id", "worker_kind", "state", "policy_state", "runnable", "blocked_reason")) if blocked_rows else "<p>No policy-blocked linked WorkUnits are recorded.</p>",
            "<h3>Latest runner history</h3>",
            render_table(run_rows, headers=("run_id", "status", "worker_kinds", "workunit_ids", "started_at", "finished_at")) if run_rows else "<p>No background hunt runs are recorded.</p>",
            controls,
            "</section>",
        ]
    )


def _background_hunt_runner_controls(view: SearchHuntDetailPageView) -> str:
    run_next = "/hunt/" + quote(view.hunt_id) + "/runner/run-next"
    run_batch = "/hunt/" + quote(view.hunt_id) + "/runner/run-batch"
    plan = "/hunt/" + quote(view.hunt_id) + "/runner/plan"
    return "\n".join(
        [
            '<section aria-labelledby="background-hunt-controls-heading"><h3 id="background-hunt-controls-heading">Runner controls</h3>',
            render_notice("scope", "Run controls require an operator token and localhost access."),
            f'<form method="post" action="{escape_html(plan)}">',
            '<p><label>Batch limit <input name="limit" value="10"></label></p>',
            '<p><button type="submit">Refresh plan preview</button></p>',
            "</form>",
            f'<form method="post" action="{escape_html(run_next)}">',
            '<p><label>Operator token <input name="operator_token" type="password" autocomplete="off"></label></p>',
            '<p><label>Operator label <input name="operator_label" value="local_operator"></label></p>',
            '<p><button type="submit">Run next safe worker</button></p>',
            "</form>",
            f'<form method="post" action="{escape_html(run_batch)}">',
            '<p><label>Operator token <input name="operator_token" type="password" autocomplete="off"></label></p>',
            '<p><label>Operator label <input name="operator_label" value="local_operator"></label></p>',
            '<p><label>Batch limit <input name="limit" value="1"></label></p>',
            '<p><button type="submit">Run safe batch</button></p>',
            "</form>",
            "</section>",
        ]
    )


def _search_need_creation_form(view: SearchHuntDetailPageView) -> str:
    action = "/hunt/" + quote(view.hunt_id) + "/search-need"
    return "\n".join(
        [
            '<section aria-labelledby="hunt-search-need-create-heading"><h2 id="hunt-search-need-create-heading">Create SearchNeed</h2>',
            render_notice("scope", "SearchNeed creation requires an operator token and records local demand only."),
            render_notice("scope", "WorkUnit generation is handled from SearchNeed detail pages; source inspection, extraction, and model escalation remain disabled."),
            f'<form method="post" action="{escape_html(action)}">',
            '<p><label>Operator token <input name="operator_token" type="password" autocomplete="off"></label></p>',
            '<p><label>Operator label <input name="operator_label" value="local_operator"></label></p>',
            '<p><label>Idempotency key <input name="idempotency_key"></label></p>',
            '<p><button type="submit">Create local SearchNeed</button></p>',
            "</form>",
            "</section>",
        ]
    )


def _search_hunt_command_history(commands: Sequence[SearchHuntCommandView]) -> str:
    rows = tuple(
        {
            "command_id": item.command_id,
            "command_type": item.command_type,
            "previous_state": item.previous_state,
            "resulting_state": item.resulting_state,
            "operator_label": item.operator_label,
            "reason": item.reason,
            "policy_decision": item.policy_decision,
            "created_at": item.created_at,
        }
        for item in commands
    )
    return "\n".join(
        [
            '<section aria-labelledby="hunt-command-history-heading"><h2 id="hunt-command-history-heading">Command history</h2>',
            render_table(rows, headers=("command_id", "command_type", "previous_state", "resulting_state", "operator_label", "reason", "policy_decision", "created_at")) if rows else "<p>No command history recorded.</p>",
            "</section>",
        ]
    )


def _search_hunt_steering_preferences(preferences: Sequence[SearchHuntSteeringPreferenceView]) -> str:
    rows = tuple(
        {
            "steering_id": item.steering_id,
            "command_type": item.command_type,
            "value": item.value,
            "reason": item.reason,
            "operator_label": item.operator_label,
            "active": item.active,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
        }
        for item in preferences
    )
    removal_forms = "\n".join(_steering_remove_form(item) for item in preferences if item.active)
    return "\n".join(
        [
            '<section aria-labelledby="hunt-steering-preferences-heading"><h2 id="hunt-steering-preferences-heading">Active and inactive steering preferences</h2>',
            render_table(rows, headers=("steering_id", "command_type", "value", "reason", "operator_label", "active", "created_at", "updated_at")) if rows else "<p>No steering preferences recorded.</p>",
            removal_forms,
            "</section>",
        ]
    )


def _steering_remove_form(item: SearchHuntSteeringPreferenceView) -> str:
    action = "/hunt/" + quote(item.hunt_id) + "/steer"
    return (
        '<form method="post" action="">'
        f'<input type="hidden" name="steering_id" value="{escape_html(item.steering_id)}">'
        '<p><label>Operator token <input name="operator_token" type="password" autocomplete="off"></label> '
        '<label>Reason <input name="reason"></label> '
        '<button type="submit">Deactivate steering preference</button></p>'
        "</form>"
    ).replace('action=""', f'action="{escape_html(action)}"')


def _search_hunt_transitions(transitions: Sequence[SearchHuntTransitionView]) -> str:
    rows = tuple(
        {
            "transition_id": item.transition_id,
            "from_state": item.from_state,
            "to_state": item.to_state,
            "reason": item.reason,
            "created_at": item.created_at,
        }
        for item in transitions
    )
    return "\n".join(
        [
            '<section aria-labelledby="transition-history-heading"><h2 id="transition-history-heading">Transition history</h2>',
            render_table(rows, headers=("transition_id", "from_state", "to_state", "reason", "created_at")) if rows else "<p>No transition history recorded.</p>",
            "</section>",
        ]
    )


def _search_need_state_form(view: SearchNeedDetailPageView) -> str:
    action = "/need/" + quote(view.need_id) + "/state"
    options = "".join(f'<option value="{escape_html(item)}">{escape_html(item)}</option>' for item in _search_need_states())
    return "\n".join(
        [
            '<section aria-labelledby="need-state-form-heading"><h2 id="need-state-form-heading">Operator state update</h2>',
            render_notice("scope", "State updates require an operator token and mutate only local SearchNeed state."),
            f'<form method="post" action="{escape_html(action)}">',
            '<p><label>Operator token <input name="operator_token" type="password" autocomplete="off"></label></p>',
            f'<p><label>State <select name="state">{options}</select></label></p>',
            '<p><label>Reason <textarea name="reason"></textarea></label></p>',
            '<p><button type="submit">Update local state</button></p>',
            "</form>",
            "</section>",
        ]
    )


def _search_need_workunit_plan(items: Sequence[SearchNeedWorkUnitPlanItemView]) -> str:
    rows = tuple(
        {
            "plan_item_id": item.plan_item_id,
            "kind": item.kind,
            "title": item.title,
            "policy_state": item.policy_state,
            "priority": item.priority,
            "blocked_reason": item.blocked_reason,
            "reason": item.reason,
        }
        for item in items
    )
    return "\n".join(
        [
            '<section aria-labelledby="need-workunit-plan-heading"><h2 id="need-workunit-plan-heading">WorkUnit plan preview</h2>',
            render_notice("scope", "Plan preview is deterministic and does not persist queue records."),
            render_table(rows, headers=("plan_item_id", "kind", "title", "policy_state", "priority", "blocked_reason", "reason")) if rows else "<p>No WorkUnit plan items are available.</p>",
            "</section>",
        ]
    )


def _search_need_linked_workunits(workunits: Sequence[SearchNeedWorkUnitView]) -> str:
    rows = tuple(
        {
            "workunit_id": item.workunit_id,
            "kind": item.kind,
            "state": item.state,
            "title": item.title,
            "policy_state": item.policy_state,
            "linked_hunt": render_link("/hunt/" + quote(item.search_hunt_id), item.search_hunt_id) if item.search_hunt_id else "",
            "execution_enabled": item.execution_enabled,
        }
        for item in workunits
    )
    return "\n".join(
        [
            '<section aria-labelledby="need-workunits-heading"><h2 id="need-workunits-heading">Linked WorkUnits</h2>',
            render_table(rows, headers=("workunit_id", "kind", "state", "title", "policy_state", "linked_hunt", "execution_enabled")) if rows else "<p>No linked WorkUnits are recorded for this SearchNeed.</p>",
            render_notice("scope", "Policy-gated WorkUnits stay blocked; this page has no execution controls."),
            "</section>",
        ]
    )


def _search_need_workunit_form(view: SearchNeedDetailPageView) -> str:
    action = "/need/" + quote(view.need_id) + "/workunits"
    return "\n".join(
        [
            '<section aria-labelledby="need-workunit-form-heading"><h2 id="need-workunit-form-heading">Persist WorkUnit plan</h2>',
            render_notice("scope", "Persisting the plan requires an operator token and writes only local queue records."),
            f'<form method="post" action="{escape_html(action)}">',
            '<p><label>Operator token <input name="operator_token" type="password" autocomplete="off"></label></p>',
            '<p><label>Operator label <input name="operator_label" value="local_operator"></label></p>',
            '<p><label>Idempotency key <input name="idempotency_key"></label></p>',
            '<p><button type="submit">Persist planned WorkUnits</button></p>',
            "</form>",
            "</section>",
        ]
    )


def _search_need_transitions(transitions: Sequence[SearchNeedTransitionView]) -> str:
    rows = tuple(
        {
            "transition_id": item.transition_id,
            "from_state": item.from_state,
            "to_state": item.to_state,
            "reason": item.reason,
            "created_at": item.created_at,
        }
        for item in transitions
    )
    return "\n".join(
        [
            '<section aria-labelledby="need-transition-history-heading"><h2 id="need-transition-history-heading">Transition history</h2>',
            render_table(rows, headers=("transition_id", "from_state", "to_state", "reason", "created_at")) if rows else "<p>No transition history recorded.</p>",
            "</section>",
        ]
    )


def _search_need_unavailable_actions() -> str:
    rows = (
        {"action": "WorkUnit pipeline", "status": "available", "reason": "SearchNeeds can persist linked queue records without running them."},
        {"action": "background runner", "status": "deferred", "reason": "Runner scheduling is handled by the next pipeline."},
        {"action": "source probes", "status": "disabled", "reason": "Source inspection requires a future source policy gate."},
        {"action": "extraction", "status": "deferred", "reason": "Extraction requires a later safety gate."},
        {"action": "AI escalation", "status": "disabled", "reason": "Model/provider calls are disabled."},
        {"action": "public sync", "status": "disabled", "reason": "Sync requires a future policy gate."},
    )
    return "\n".join(
        [
            '<section aria-labelledby="need-unavailable-actions-heading"><h2 id="need-unavailable-actions-heading">Unavailable future actions</h2>',
            render_table(rows, headers=("action", "status", "reason")),
            "</section>",
        ]
    )


def _search_need_states() -> tuple[str, ...]:
    return (
        "proposed",
        "open",
        "waiting_for_user",
        "waiting_for_policy",
        "blocked",
        "satisfied_locally",
        "superseded",
        "cancelled",
    )


def _search_hunt_unavailable_actions(actions: Sequence[SearchHuntUnavailableActionView]) -> str:
    rows = tuple({"action": item.action, "status": item.status, "reason": item.reason} for item in actions)
    return "\n".join(
        [
            '<section aria-labelledby="hunt-unavailable-actions-heading"><h2 id="hunt-unavailable-actions-heading">Unavailable next actions</h2>',
            render_table(rows, headers=("action", "status", "reason")),
            "</section>",
        ]
    )


def _steering_types() -> tuple[str, ...]:
    return (
        "include_source_family",
        "exclude_source_family",
        "prefer_official_sources",
        "allow_community_sources",
        "metadata_only",
        "allow_extraction_future",
        "disallow_extraction",
        "allow_ai_escalation_future",
        "disallow_ai_escalation",
        "add_note",
        "set_priority",
    )


def _key_values(rows: Sequence[tuple[str, Any]]) -> str:
    return render_table(tuple({"field": key, "value": value} for key, value in rows), headers=("field", "value"))


def _decision_form(review_item_id: str) -> str:
    action = "/review/" + quote(review_item_id) + "/decision"
    return "\n".join(
        [
            '<section aria-labelledby="decision-heading"><h2 id="decision-heading">Record local review decision</h2>',
            f'<form method="post" action="{escape_html(action)}">',
            '<p><label for="operator-token">Operator token</label> '
            '<input id="operator-token" name="operator_token" type="password" autocomplete="off"></p>',
            '<p><label for="operator-label">Operator label</label> '
            '<input id="operator-label" name="operator_label" value="local_operator"></p>',
            '<p><label for="decision">Decision</label> <select id="decision" name="decision">',
            '<option value="accept">accept</option>',
            '<option value="reject">reject</option>',
            '<option value="block">block</option>',
            '<option value="request_more_evidence">request_more_evidence</option>',
            '<option value="note_only">note_only</option>',
            "</select></p>",
            '<p><label for="reason">Reason</label> <textarea id="reason" name="reason"></textarea></p>',
            '<p><label><input type="checkbox" name="local_only_confirmed" value="true"> '
            "I confirm this accept decision is local-only review state.</label></p>",
            '<p><button type="submit">Record decision</button></p>',
            "</form></section>",
        ]
    )


def _rebuild_form() -> str:
    return "\n".join(
        [
            '<section aria-labelledby="rebuild-heading"><h2 id="rebuild-heading">Apply local reviewed-index rebuild</h2>',
            '<form method="post" action="/rebuild">',
            '<p><label for="rebuild-token">Operator token</label> '
            '<input id="rebuild-token" name="operator_token" type="password" autocomplete="off"></p>',
            '<p><label for="rebuild-label">Operator label</label> '
            '<input id="rebuild-label" name="operator_label" value="local_operator"></p>',
            '<p><label><input type="checkbox" name="dry_run" value="true"> Dry run only</label></p>',
            '<p><button type="submit">Rebuild local reviewed index</button></p>',
            "</form></section>",
        ]
    )


def _render_mapping_sequence(rows: Sequence[Mapping[str, Any]], headers: Sequence[str]) -> str:
    if not rows:
        return "<p>No rows.</p>"
    return render_table(tuple({header: row.get(header, "") for header in headers} for row in rows), headers=headers)


def _render_html_table(rows: Sequence[Mapping[str, Any]], headers: Sequence[str]) -> str:
    if not rows:
        return "<p>No rows.</p>"
    head = "<thead><tr>" + "".join(f'<th scope="col">{escape_html(item)}</th>' for item in headers) + "</tr></thead>"
    body_rows = []
    for row in rows:
        cells = []
        for item in headers:
            value = row.get(item, "")
            text = str(value)
            cells.append(f"<td>{text if text.startswith('<a ') else escape_html(text)}</td>")
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    return "<table>" + head + "<tbody>" + "".join(body_rows) + "</tbody></table>"


def _normalized_rows(fields: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(fields, Mapping) or not fields:
        return ({"field": "none", "value": ""},)
    return tuple({"field": str(key), "value": str(value)} for key, value in sorted(fields.items()))
