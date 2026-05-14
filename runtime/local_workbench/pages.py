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
    SearchHuntLayerView,
    SearchHuntListPageView,
    SearchHuntNotFoundPageView,
    SearchHuntTransitionView,
    SearchHuntUnavailableActionView,
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
                    ("creates_workunits", False),
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


def _search_hunt_unavailable_actions(actions: Sequence[SearchHuntUnavailableActionView]) -> str:
    rows = tuple({"action": item.action, "status": item.status, "reason": item.reason} for item in actions)
    return "\n".join(
        [
            '<section aria-labelledby="hunt-unavailable-actions-heading"><h2 id="hunt-unavailable-actions-heading">Unavailable next actions</h2>',
            render_table(rows, headers=("action", "status", "reason")),
            "</section>",
        ]
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
