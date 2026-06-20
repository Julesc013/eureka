"""Server-rendered private exploration workspace pages."""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence
from urllib.parse import quote

from surfaces.web.workbench.local_html.html import (
    escape_html,
    render_document,
    render_limitations,
    render_link,
    render_navigation,
    render_notice,
    render_table,
    render_warnings,
)

EXAMPLE_SEARCHES = (
    "old blue FTP client for XP",
    "manual for Sound Blaster CT1740",
    "latest Firefox before XP support ended",
    "driver for Win98",
    "article about ray tracing in a 1994 magazine",
)
FIRST_USE_BANNER = "Local only. This page searches Eureka's local demo set and does not contact live services."
FIRST_USE_NAV = render_navigation((("/explore", "Explore"), ("/status", "Status")))


def render_explore_workspace_html(payload: Mapping[str, Any]) -> str:
    query = str(payload.get("query", ""))
    preview = dict(payload.get("preview_index") or {})
    controls = dict(payload.get("run_controls") or {})
    body = "\n".join(
        [
            "<h1>Eureka</h1>",
            "<p>Search for old software, manuals, drivers, and historical-computing clues. Eureka shows local matches and says plainly when it cannot answer yet.</p>",
            _query_form(query),
            _example_searches(payload.get("example_searches") or EXAMPLE_SEARCHES),
            _loading_state(),
            _first_use_search_state(query, preview, payload.get("lanes") or ()),
            _hunt_panel(query, controls.get("start_synthetic_hunt") or {}),
            _blocked_state(),
        ]
    )
    return render_document("Eureka", body, status_banner=FIRST_USE_BANNER, navigation=FIRST_USE_NAV)


def render_explore_runs_html(payload: Mapping[str, Any]) -> str:
    rows = [
        {
            "run_id": _run_link(str(item.get("run_id", ""))),
            "query": item.get("query", ""),
            "state": item.get("state", ""),
            "mode": item.get("mode", ""),
            "workunits": item.get("workunit_count", 0),
            "events": item.get("event_count", 0),
            "replay": "yes" if item.get("replay_eligible") else "no",
        }
        for item in payload.get("runs", []) or []
    ]
    body = "\n".join(
        [
            "<h1>Explore Runs</h1>",
            render_notice("scope", "Durable bundles are read from the shared E2E Reference Runner output root."),
            f"<p>{render_link('/explore', 'Explore workspace')}</p>",
            _raw_table(rows, headers=("run_id", "query", "state", "mode", "workunits", "events", "replay")),
            _boundary_flags(payload),
            render_warnings(_safe_sequence(payload.get("warnings") or ())),
            render_limitations(_safe_sequence(payload.get("limitations") or ())),
        ]
    )
    return render_document("Explore Runs - Eureka Local Appliance", body)


def render_explore_run_html(payload: Mapping[str, Any]) -> str:
    run = dict(payload.get("run") or {})
    result = dict(payload.get("result") or {})
    query = str(run.get("query", ""))
    state = str(run.get("state", ""))
    result_count = int(result.get("result_count", 0) or 0)
    body = "\n".join(
        [
            "<h1>Hunt Result</h1>",
            "<p>A Hunt is a local investigation for one search. It records what Eureka checked and what is still blocked.</p>",
            _hunt_result_state(query, state, result_count),
            _blocked_state(),
            _return_to_search(query),
        ]
    )
    return render_document("Hunt Result - Eureka", body, status_banner=FIRST_USE_BANNER, navigation=FIRST_USE_NAV)


def render_explore_error_html(title: str, message: str, *, query: str = "") -> str:
    body = "\n".join(
        [
            f"<h1>{escape_html(title or 'Eureka needs attention')}</h1>",
            f"<p>{escape_html(message or 'The local search page could not finish that request.')}</p>",
            _query_form(query),
            _example_searches(EXAMPLE_SEARCHES),
            _blocked_state(),
        ]
    )
    return render_document("Eureka Needs Attention", body, status_banner=FIRST_USE_BANNER, navigation=FIRST_USE_NAV)


def render_explore_compare_html(payload: Mapping[str, Any]) -> str:
    body = "\n".join(
        [
            "<h1>Compare Explore Runs</h1>",
            render_notice("scope", "Run comparison is read-only and does not replay or mutate bundles."),
            _compare_form(str(payload.get("left_run_id", "")), str(payload.get("right_run_id", ""))),
            _key_values(
                (
                    ("left_run_id", payload.get("left_run_id", "")),
                    ("right_run_id", payload.get("right_run_id", "")),
                    ("same_query", (payload.get("diff") or {}).get("same_query", "")),
                    ("event_count_delta", (payload.get("diff") or {}).get("event_count_delta", "")),
                    ("workunit_count_delta", (payload.get("diff") or {}).get("workunit_count_delta", "")),
                    ("result_count_delta", (payload.get("diff") or {}).get("result_count_delta", "")),
                )
            ),
            render_table(
                (
                    {"side": "left", **dict(payload.get("left") or {})},
                    {"side": "right", **dict(payload.get("right") or {})},
                ),
                headers=("side", "run_id", "query", "state", "event_count", "workunit_count", "result_count", "validation_status"),
            )
            if payload.get("left") and payload.get("right")
            else render_notice("empty", "Choose two run IDs to compare."),
            _boundary_flags(payload),
            render_warnings(_safe_sequence(payload.get("warnings") or ())),
            render_limitations(_safe_sequence(payload.get("limitations") or ())),
        ]
    )
    return render_document("Explore Compare - Eureka Local Appliance", body)


def _query_form(query: str) -> str:
    return (
        '<form action="/explore" method="get">'
        '<label for="explore-q">What are you looking for?</label> '
        f'<input id="explore-q" name="q" type="search" value="{escape_html(query)}" placeholder="old blue FTP client for XP"> '
        '<button type="submit">Search</button>'
        "</form>"
    )


def _start_form(query: str, control: Mapping[str, Any]) -> str:
    disabled = " disabled" if not control.get("enabled") else ""
    reason = str(control.get("disabled_reason") or "")
    return "\n".join(
        [
            '<form action="/explore/run/start" method="post">',
            '<input type="hidden" name="q" value="' + escape_html(query) + '">',
            '<label for="explore-token">Start token</label> ',
            '<input id="explore-token" name="operator_token" type="password" autocomplete="off"> ',
            f'<button type="submit"{disabled}>Start Hunt</button>',
            f"<p>{escape_html(reason)}</p>" if reason else "",
            "</form>",
        ]
    )


def _example_searches(examples: Sequence[Any]) -> str:
    links = []
    for item in examples:
        text = str(item)
        links.append(f"<li>{render_link('/explore?q=' + quote(text), text)}</li>")
    return '<section aria-labelledby="examples-heading"><h2 id="examples-heading">Example Searches</h2><ul>' + "".join(links) + "</ul></section>"


def _loading_state() -> str:
    return (
        '<section aria-labelledby="loading-state-heading">'
        '<h2 id="loading-state-heading">Searching...</h2>'
        "<p>After you press Search, Eureka checks the local set and returns this page with matches, no matches, or a clear blocked message.</p>"
        "</section>"
    )


def _first_use_search_state(query: str, preview: Mapping[str, Any], lanes: Sequence[Mapping[str, Any]]) -> str:
    has_query = bool(str(query or "").strip())
    warnings = _safe_sequence(preview.get("warnings") or ())
    status = str(preview.get("status") or "")
    if status == "degraded" or warnings:
        return _error_state(warnings or ("The local search set is not ready yet.",))
    if not has_query:
        return (
            '<section aria-labelledby="ready-state-heading">'
            '<h2 id="ready-state-heading">Ready</h2>'
            "<p>Type a search or choose an example to see what Eureka already knows locally.</p>"
            "</section>"
        )
    records = _first_use_records(lanes)
    if not records:
        return (
            '<section aria-labelledby="empty-state-heading">'
            '<h2 id="empty-state-heading">No Local Matches Yet</h2>'
            "<p>That does not prove the thing is gone or never existed. Try a broader phrase, or start a Hunt so Eureka can make a local investigation record for this search.</p>"
            "</section>"
        )
    cards = "".join(_plain_result_card(record) for record in records)
    return (
        '<section aria-labelledby="results-state-heading">'
        f'<h2 id="results-state-heading">Results Found</h2><p>{escape_html(len(records))} local clue{"s" if len(records) != 1 else ""} matched this search.</p>'
        + cards
        + "</section>"
    )


def _hunt_panel(query: str, control: Mapping[str, Any]) -> str:
    if not str(query or "").strip():
        return ""
    return "\n".join(
        [
            '<section aria-labelledby="hunt-heading">',
            '<h2 id="hunt-heading">Need Eureka To Look A Little Harder?</h2>',
            "<p>A Hunt is a local investigation for this search. It is useful when the result is thin, missing, or blocked. This build keeps the Hunt local and does not contact live services.</p>",
            _start_form(query, control),
            "</section>",
        ]
    )


def _blocked_state() -> str:
    return (
        '<section aria-labelledby="blocked-state-heading">'
        '<h2 id="blocked-state-heading">Blocked Here</h2>'
        "<ul>"
        "<li>No public sharing starts from this page.</li>"
        "<li>No live service call starts from this page.</li>"
        "<li>No file transfer or program run starts from this page.</li>"
        "<li>No reviewed answer is created from this page.</li>"
        "</ul>"
        "</section>"
    )


def _error_state(messages: Sequence[Any]) -> str:
    return (
        '<section aria-labelledby="error-state-heading">'
        '<h2 id="error-state-heading">Eureka Could Not Search The Local Set</h2>'
        "<p>Ask the operator to refresh the local instance, then try again.</p>"
        + _list("What happened", messages)
        + "</section>"
    )


def _first_use_records(lanes: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    records: list[Mapping[str, Any]] = []
    for lane in lanes:
        records.extend(record for record in lane.get("records") or [] if isinstance(record, Mapping))
    return records[:8]


def _plain_result_card(record: Mapping[str, Any]) -> str:
    raw_title = str(record.get("title") or "Local clue")
    title = "Local Hunt clue" if _looks_internal_title(raw_title) else _friendly_text(raw_title)
    summary = _friendly_text(record.get("summary") or "Eureka found a local clue for this search.")
    matched = tuple(_friendly_text(item) for item in record.get("why_matched") or ())[:3]
    missing = tuple(_friendly_text(item) for item in record.get("missing") or ())[:3]
    return "\n".join(
        [
            '<article class="explore-result">',
            f"<h3>{escape_html(title)}</h3>",
            f"<p>{escape_html(summary)}</p>",
            _list("Why this matched", matched),
            _list("Still missing", missing),
            "<p>This is a clue, not a final answer.</p>",
            "</article>",
        ]
    )


def _hunt_result_state(query: str, state: str, result_count: int) -> str:
    heading = "Hunt Complete" if state == "completed" else "Hunt State"
    detail = (
        f"Eureka finished a local Hunt for '{query}' and found {result_count} result clue{'s' if result_count != 1 else ''}."
        if state == "completed"
        else f"Eureka recorded the Hunt state as {state or 'unknown'}."
    )
    return (
        '<section aria-labelledby="hunt-result-state-heading">'
        f'<h2 id="hunt-result-state-heading">{escape_html(heading)}</h2>'
        f"<p>{escape_html(detail)}</p>"
        "<p>The Hunt did not make a final reviewed answer.</p>"
        "</section>"
    )


def _return_to_search(query: str) -> str:
    links = [render_link("/explore", "Start another search")]
    if query:
        links.insert(0, render_link("/explore?q=" + quote(query), "Return to this search"))
    return "<p>" + " | ".join(links) + "</p>"


def _friendly_text(value: Any) -> str:
    text = re.sub(r"\b[A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+-\d+\b", "future local work", str(value or ""))
    replacements = {
        "fixture metadata": "local demo data",
        "Preview result": "Local clue",
        "preview record": "local clue",
        "accepted truth": "final answer",
        "synthetic": "demo",
        "authority": "review state",
        "ResolutionRun": "local Hunt",
        "WorkUnits": "local steps",
        "WorkUnit": "local step",
        "workunits": "local steps",
        "workunit": "local step",
        "demo_result": "local clue",
        "download": "file transfer",
        "install": "software setup",
        "execute": "program run",
        "upload": "outbound file transfer",
    }
    for needle, replacement in replacements.items():
        text = text.replace(needle, replacement).replace(needle.title(), replacement.title()).replace(needle.upper(), replacement.upper())
    return text


def _looks_internal_title(value: str) -> bool:
    lowered = str(value or "").lower()
    return any(marker in lowered for marker in ("workunit", "demo_result", "resolutionrun", "run_manifest", "run_state"))


def _compare_form(left: str = "", right: str = "") -> str:
    return (
        '<form action="/explore/compare" method="get">'
        '<label for="left">Left</label> '
        f'<input id="left" name="left" value="{escape_html(left)}"> '
        '<label for="right">Right</label> '
        f'<input id="right" name="right" value="{escape_html(right)}"> '
        '<button type="submit">Compare</button>'
        "</form>"
    )


def _preview_summary(preview: Mapping[str, Any]) -> str:
    stats = dict(preview.get("stats") or {})
    return "\n".join(
        [
            '<section aria-labelledby="preview-summary-heading"><h2 id="preview-summary-heading">Preview Index</h2>',
            _key_values(
                (
                    ("status", preview.get("status", "")),
                    ("preview_index_id", stats.get("preview_index_id", "")),
                    ("records", stats.get("record_count", 0)),
                    ("reviewed", stats.get("reviewed_count", 0)),
                    ("candidates", stats.get("candidate_count", 0)),
                    ("results", preview.get("result_count", 0)),
                )
            ),
            "</section>",
        ]
    )


def _lanes(lanes: Sequence[Mapping[str, Any]]) -> str:
    sections: list[str] = ['<section aria-labelledby="lanes-heading"><h2 id="lanes-heading">Result Lanes</h2>']
    for lane in lanes:
        records = list(lane.get("records") or [])
        sections.append(f'<section aria-labelledby="lane-{escape_html(lane.get("lane_id", ""))}">')
        sections.append(
            f'<h3 id="lane-{escape_html(lane.get("lane_id", ""))}">{escape_html(lane.get("title", ""))} ({escape_html(len(records))})</h3>'
        )
        sections.append(render_notice("scope", str(lane.get("note", ""))))
        if not records:
            sections.append("<p>No records.</p>")
        for record in records:
            sections.append(_result_card(record))
        sections.append("</section>")
    sections.append("</section>")
    return "\n".join(sections)


def _result_card(record: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            '<article class="preview-result">',
            f"<h4>{escape_html(record.get('title') or record.get('result_id') or 'Preview result')}</h4>",
            _key_values(
                (
                    ("status", record.get("status", "")),
                    ("authority", record.get("authority", "")),
                    ("source_family", record.get("source_family", "")),
                    ("review_required", record.get("review_required", "")),
                    ("accepted_truth", record.get("accepted_truth", "")),
                )
            ),
            f"<p>{escape_html(record.get('summary', ''))}</p>",
            _list("Why matched", record.get("why_matched") or ()),
            _list("Why ranked", record.get("why_ranked") or ()),
            _list("Missing", record.get("missing") or ()),
            _list("Permitted actions", record.get("permitted_actions") or ()),
            _list("Unavailable actions", _safe_sequence(record.get("forbidden_actions") or ())),
            "</article>",
        ]
    )


def _recent_runs(runs_payload: Mapping[str, Any]) -> str:
    runs = list(runs_payload.get("runs") or [])
    rows = [
        {
            "run_id": _run_link(str(item.get("run_id", ""))),
            "query": item.get("query", ""),
            "state": item.get("state", ""),
            "workunits": item.get("workunit_count", 0),
            "events": item.get("event_count", 0),
        }
        for item in runs
    ]
    return "\n".join(
        [
            '<section aria-labelledby="recent-runs-heading"><h2 id="recent-runs-heading">Recent Runs</h2>',
            f"<p>{render_link('/explore/runs', 'All explore runs')}</p>",
            _raw_table(rows, headers=("run_id", "query", "state", "workunits", "events")),
            "</section>",
        ]
    )


def _control_forms(run_id: str, controls: Mapping[str, Any]) -> str:
    forms = ['<section aria-labelledby="controls-heading"><h2 id="controls-heading">Run Controls</h2>']
    for action in ("pause", "resume", "cancel", "step", "replay"):
        control = dict(controls.get(action) or {})
        disabled = " disabled" if not control.get("enabled") else ""
        forms.append(
            '<form action="/explore/run/'
            + escape_html(quote(run_id))
            + "/"
            + escape_html(action)
            + '" method="post">'
            + '<label>Operator token <input name="operator_token" type="password" autocomplete="off"></label> '
            + f'<button type="submit"{disabled}>{escape_html(action.title())}</button>'
            + (f" <span>{escape_html(control.get('disabled_reason', ''))}</span>" if control.get("disabled_reason") else "")
            + "</form>"
        )
    forms.append("</section>")
    return "\n".join(forms)


def _event_timeline(events: Sequence[Mapping[str, Any]]) -> str:
    rows = [
        {
            "sequence": item.get("sequence", item.get("event_index", "")),
            "type": item.get("event_type", ""),
            "authority": item.get("authority", ""),
            "workunit": item.get("workunit_id", ""),
        }
        for item in events
    ]
    return '<section aria-labelledby="events-heading"><h2 id="events-heading">Events</h2>' + render_table(rows, headers=("sequence", "type", "authority", "workunit")) + "</section>"


def _workunit_table(workunits: Sequence[Mapping[str, Any]]) -> str:
    rows = [
        {
            "workunit_id": item.get("workunit_id", ""),
            "source_family": item.get("source_family", ""),
            "state": item.get("state", ""),
            "dry_run": item.get("dry_run", ""),
        }
        for item in workunits
    ]
    return '<section aria-labelledby="workunits-heading"><h2 id="workunits-heading">WorkUnits</h2>' + render_table(rows, headers=("workunit_id", "source_family", "state", "dry_run")) + "</section>"


def _run_lanes(lane_snapshot: Mapping[str, Any]) -> str:
    lanes = lane_snapshot.get("lanes") or []
    if isinstance(lanes, Mapping):
        rows = [{"lane": key, "records": len(value or [])} for key, value in lanes.items()]
    else:
        rows = [
            {
                "lane": item.get("lane_id", item.get("id", "")),
                "status": item.get("status", ""),
                "records": item.get("record_count", len(item.get("records") or [])),
            }
            for item in lanes
            if isinstance(item, Mapping)
        ]
    return '<section aria-labelledby="run-lanes-heading"><h2 id="run-lanes-heading">Run Lanes</h2>' + render_table(rows, headers=("lane", "status", "records")) + "</section>"


def _replay_report(report: Mapping[str, Any] | None) -> str:
    if not report:
        return ""
    return '<section aria-labelledby="replay-heading"><h2 id="replay-heading">Replay</h2>' + _key_values((("status", report.get("status", "")), ("strict", report.get("strict", "")))) + "</section>"


def _boundary_flags(payload: Mapping[str, Any]) -> str:
    labels = (
        ("network_provider_calls", "provider calls"),
        ("downloads", "file transfer"),
        ("review_decision_mutation", "review decision write"),
        ("reviewed_record_created", "reviewed record creation"),
        ("reviewed_master_mutation", "reviewed master write"),
        ("public_index_mutation", "public index write"),
        ("public_exposure", "public exposure"),
        ("accepted_truth_created", "accepted truth creation"),
    )
    rows = [{"boundary": label, "value": payload.get(key)} for key, label in labels]
    return '<section aria-labelledby="boundary-heading"><h2 id="boundary-heading">Boundary</h2>' + render_table(rows, headers=("boundary", "value")) + "</section>"


def _key_values(rows: Sequence[tuple[str, Any]]) -> str:
    return render_table(tuple({"key": key, "value": value} for key, value in rows), headers=("key", "value"))


def _list(title: str, items: Sequence[Any]) -> str:
    if not items:
        return ""
    return f"<p>{escape_html(title)}</p><ul>" + "".join(f"<li>{escape_html(item)}</li>" for item in items) + "</ul>"


def _safe_sequence(items: Sequence[Any]) -> tuple[str, ...]:
    return tuple(_safe_ui_text(item) for item in items)


def _safe_ui_text(value: Any) -> str:
    text = str(value)
    replacements = {
        "download": "file transfer",
        "upload": "outbound file transfer",
        "execute": "program run",
        "install": "software setup",
        "call_model_provider": "model provider call",
        "call_provider": "provider call",
        "review mutation": "review decision write",
        "rebuild index": "index refresh",
    }
    lowered = text.lower()
    for needle, replacement in replacements.items():
        lowered = lowered.replace(needle, replacement)
    return lowered


def _run_link(run_id: str) -> str:
    if not run_id:
        return ""
    return render_link("/explore/run/" + quote(run_id), run_id)


def _raw_table(rows: Sequence[Mapping[str, Any]], headers: Sequence[str]) -> str:
    if not rows:
        return "<p>No rows.</p>"
    head = "<thead><tr>" + "".join(f"<th scope=\"col\">{escape_html(item)}</th>" for item in headers) + "</tr></thead>"
    body_rows = []
    for row in rows:
        body_rows.append("<tr>" + "".join(f"<td>{row.get(item, '')}</td>" if item == "run_id" else f"<td>{escape_html(row.get(item, ''))}</td>" for item in headers) + "</tr>")
    return "<table>" + head + "<tbody>" + "".join(body_rows) + "</tbody></table>"
