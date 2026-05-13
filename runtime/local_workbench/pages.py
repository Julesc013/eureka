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
                )
            ),
            "</section>",
            search_form(),
            "<section aria-labelledby=\"links-heading\"><h2 id=\"links-heading\">Links</h2><ul>",
            f"<li>{render_link('/status', 'Status page')}</li>",
            f"<li>{render_link('/absence?q=sampleproject', 'Sample absence page')}</li>",
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
        {"flag": "lan_enabled", "value": view.lan_enabled},
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


def _key_values(rows: Sequence[tuple[str, Any]]) -> str:
    return render_table(tuple({"field": key, "value": value} for key, value in rows), headers=("field", "value"))


def _normalized_rows(fields: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(fields, Mapping) or not fields:
        return ({"field": "none", "value": ""},)
    return tuple({"field": str(key), "value": str(value)} for key, value in sorted(fields.items()))
