"""Server-rendered local workbench pages."""

from typing import Any, Mapping
from urllib.parse import quote

from .html import escape_html, render_document, render_limitations, render_link, render_notice, render_table, render_warnings
from .templates import record_links, search_form
from .view_models import AbsencePageView, HomePageView, ObjectPageView, SearchPageView, SourcePageView, StatusPageView


def render_home_page(view: HomePageView) -> str:
    body = "\n".join(
        [
            "<h1>Eureka Local Appliance</h1>",
            render_notice("info", "Read-only localhost JSON API with a local workbench over the reviewed public index."),
            "<section aria-labelledby=\"summary-heading\"><h2 id=\"summary-heading\">Status summary</h2>",
            f"<p>Status: {escape_html(view.status)}</p>",
            f"<p>Instance: {escape_html(view.instance_id)}</p>",
            f"<p>Schema version: {escape_html(view.instance_schema_version)}</p>",
            f"<p>Reviewed records: {escape_html(view.record_count)}</p></section>",
            search_form(),
            "<section aria-labelledby=\"links-heading\"><h2 id=\"links-heading\">Links</h2><ul>",
            f"<li>{render_link('/status', 'Status page')}</li>",
            f"<li>{render_link('/absence?q=sampleproject', 'Absence example')}</li>",
            f"<li>{render_link('/api/v1/status', 'API status')}</li>",
            "</ul></section>",
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Eureka Local Appliance", body)


def render_search_page(view: SearchPageView) -> str:
    cards = []
    for result in view.results:
        record_id = str(result.get("record_id", ""))
        source_id = str(result.get("source_id", ""))
        cards.append(
            "<article>"
            f"<h2>{escape_html(result.get('title', record_id))}</h2>"
            f"<p>{escape_html(result.get('description', ''))}</p>"
            f"<p>Source ID: {escape_html(source_id)}</p>"
            f"<p>Review/evidence/index labels: reviewed public index</p>"
            f"{record_links(record_id, source_id)}"
            "</article>"
        )
    empty = ""
    if not cards:
        empty = render_notice(
            "empty",
            "No reviewed results in the local index. This is not a global absence claim.",
        ) + f"<p>{render_link('/absence?q=' + quote(view.query), 'Open absence page')}</p>"
    body = "\n".join(
        [
            "<h1>Search</h1>",
            search_form(view.query),
            f"<p>Submitted query: {escape_html(view.query)}</p>",
            f"<p>Reviewed result count: {escape_html(view.result_count)}</p>",
            empty,
            "".join(cards),
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
                f"<p>Record ID: {escape_html(view.record_id)}</p>",
                render_notice("empty", "The record was not found in the local reviewed index."),
                render_limitations(("Local reviewed index only.",)),
            ]
        )
        return render_document("Object not found - Eureka Local Appliance", body)
    record = view.record
    fields = _normalized_rows(record.get("normalized_fields", {}))
    refs = {
        "source_cache_entry_id": record.get("source_cache_entry_id", ""),
        "evidence_id": record.get("evidence_id", ""),
        "review_item_id": record.get("review_item_id", ""),
        "review_decision_id": record.get("review_decision_id", ""),
    }
    body = "\n".join(
        [
            f"<h1>{escape_html(record.get('title', view.record_id))}</h1>",
            f"<p>Record ID: {escape_html(view.record_id)}</p>",
            f"<p>{escape_html(record.get('description', ''))}</p>",
            f"<p>Source ID: {render_link('/source/' + quote(str(record.get('source_id', ''))), str(record.get('source_id', '')))}</p>",
            "<section aria-labelledby=\"refs-heading\"><h2 id=\"refs-heading\">Evidence and review references</h2>",
            render_table([refs], headers=list(refs.keys())),
            "</section>",
            "<section aria-labelledby=\"fields-heading\"><h2 id=\"fields-heading\">Normalized fields</h2>",
            render_table(fields, headers=("field", "value")),
            "</section>",
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Object - Eureka Local Appliance", body)


def render_source_page(view: SourcePageView) -> str:
    rows = [
        {
            "record_id": record.get("record_id", record.get("id", "")),
            "title": record.get("title", ""),
            "description": record.get("description", ""),
        }
        for record in view.records
    ]
    empty = render_notice("empty", "No local reviewed index records for this source.") if not rows else ""
    body = "\n".join(
        [
            "<h1>Source</h1>",
            f"<p>Source ID: {escape_html(view.source_id)}</p>",
            f"<p>Local reviewed index records: {escape_html(view.result_count)}</p>",
            empty,
            render_table(rows, headers=("record_id", "title", "description")) if rows else "",
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Source - Eureka Local Appliance", body)


def render_absence_page(view: AbsencePageView) -> str:
    checked = [{"checked_layer": "reviewed public index", "value": source} for source in view.checked_sources]
    if not checked:
        checked = [{"checked_layer": "reviewed public index", "value": "no source records in local index"}]
    body = "\n".join(
        [
            "<h1>Absence</h1>",
            search_form(view.query),
            f"<p>Query: {escape_html(view.query)}</p>",
            f"<p>Local result count: {escape_html(view.result_count)}</p>",
            render_notice("info", "Absence is local current-index absence only, not global proof."),
            "<section aria-labelledby=\"checked-heading\"><h2 id=\"checked-heading\">Checked local layers</h2>",
            render_table(checked, headers=("checked_layer", "value")),
            "</section>",
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Absence - Eureka Local Appliance", body)


def render_status_page(view: StatusPageView) -> str:
    flags = [
        {"flag": "server_enabled", "value": view.server_enabled},
        {"flag": "lan_enabled", "value": view.lan_enabled},
        {"flag": "deployment_performed", "value": view.deployment_performed},
        {"flag": "migration_needed", "value": view.migration_needed},
    ]
    body = "\n".join(
        [
            "<h1>Status</h1>",
            f"<p>Instance ID: {escape_html(view.instance_id)}</p>",
            f"<p>Instance schema version: {escape_html(view.instance_schema_version)}</p>",
            f"<p>{render_link('/api/v1/status', 'JSON status')}</p>",
            "<section aria-labelledby=\"stores-heading\"><h2 id=\"stores-heading\">Store status</h2>",
            render_table(view.stores, headers=("store", "opened", "integrity", "schema")),
            "</section>",
            "<section aria-labelledby=\"flags-heading\"><h2 id=\"flags-heading\">Runtime flags</h2>",
            render_table(flags, headers=("flag", "value")),
            "</section>",
            render_warnings(view.warnings),
            render_limitations(view.limitations),
        ]
    )
    return render_document("Status - Eureka Local Appliance", body)


def _normalized_rows(fields: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(fields, Mapping) or not fields:
        return ({"field": "none", "value": ""},)
    return tuple({"field": str(key), "value": str(value)} for key, value in sorted(fields.items()))
