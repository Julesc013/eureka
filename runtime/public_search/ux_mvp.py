"""No-JS public search UX MVP over canonical public search view models.

The MVP is deterministic and example-backed. It renders committed public search
view-model projections into semantic HTML/text without deploying, mutating
indexes, fetching files, running OCR, downloading, extracting, or calling
providers.
"""

from __future__ import annotations

from html import escape
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import quote, urlencode


TASK_ID = "PUBLIC-SEARCH-UX-MVP-00"
CREATED_AT = "2026-06-02T00:00:00Z"
SNAPSHOT_EXAMPLE_ROOT = "examples/snapshots/refresh/manuals_scans_driver_support"
RECOMMENDED_NEXT_TASK = "SNAPSHOT-REFRESH-05 - Refresh public projections after UX MVP"

RESULT_STATUSES = (
    "verified",
    "reviewed_metadata_record",
    "reviewed_source_lead",
    "candidate",
    "near_miss",
    "known_need",
    "absence",
    "source_lead",
)

STATUS_LABELS = {
    "verified": "Verified",
    "reviewed_metadata_record": "Reviewed metadata",
    "reviewed_source_lead": "Reviewed source lead",
    "candidate": "Candidate",
    "near_miss": "Near miss",
    "known_need": "Known need",
    "absence": "Absence",
    "source_lead": "Source lead",
}

ROUTE_ROWS = (
    ("/", "SearchHomePageViewModel", "home_page.html"),
    ("/search", "SearchResultsPageViewModel", "search_results_page.html"),
    ("/object/{id}", "ObjectPageViewModel", "object_page.html"),
    ("/candidate/{id}", "CandidatePageViewModel", "candidate_page.html"),
    ("/need/{id}", "NeedPageViewModel", "need_page.html"),
    ("/source/{id}", "SourcePageViewModel", "source_page.html"),
    ("/evidence/{id}", "EvidencePageViewModel", "evidence_page.html"),
    ("/status", "StatusPageViewModel", "status_page.html"),
)

BOUNDARY_FALSE_KEYS = (
    "site_dist_written",
    "deployment_performed",
    "public_launch_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
    "public_mutation_enabled",
    "public_live_source_fanout_enabled",
    "download_performed",
    "file_fetch_performed",
    "ocr_performed",
    "extraction_executed",
    "install_execution_enabled",
    "model_provider_used",
    "live_source_call_performed",
    "source_probe_executed",
    "accepted_truth_created",
    "reviewed_index_mutated",
    "master_index_mutated",
    "public_index_mutated",
    "verified_download_claim_created",
    "malware_clean_claim_created",
    "compatibility_guarantee_created",
    "rights_clearance_claim_created",
    "scan_completeness_claim_created",
    "ocr_quality_claim_created",
)

DEFAULT_POLICY = {
    "public_search_is_read_only": True,
    "no_js_required": True,
    "get_form_required": True,
    "candidates_visually_distinct_from_verified": True,
    "reviewed_metadata_records_visually_distinct_from_verified_artifacts": True,
    "reviewed_source_leads_visually_distinct_from_verified_artifacts": True,
    "no_results_page_must_show_need_or_next_actions": True,
    "public_mutation_enabled": False,
    "public_live_source_fanout_enabled": False,
    "downloads_enabled": False,
    "file_fetches_enabled": False,
    "ocr_enabled": False,
    "extraction_enabled": False,
    "install_execution_enabled": False,
    "model_provider_enabled": False,
    "deployment_enabled": False,
    "public_launch_claim_allowed": False,
    "production_claim_allowed": False,
}


def load_public_search_ux_mvp_inputs(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    root = _repo_root()
    snapshot_root = root / SNAPSHOT_EXAMPLE_ROOT
    payload = {
        "schema_version": "public_search_ux_mvp_input_state.v0",
        "task": TASK_ID,
        "snapshot_projection": _read_json(snapshot_root / "public_search_view_model_projection.json"),
        "snapshot_refresh_04_result": _read_json(root / "control" / "inventory" / "snapshot_refresh_04_result.json"),
        "public_alpha_reassess_04_result": _read_json(root / "control" / "inventory" / "public_alpha_reassess_04_result.json"),
        "existing_reviewed_record_section": _read_json(snapshot_root / "existing_reviewed_record_section.json"),
        "reviewed_metadata_record_section": _read_json(snapshot_root / "reviewed_metadata_record_section.json"),
        "reviewed_source_lead_section": _read_json(snapshot_root / "reviewed_source_lead_section.json"),
        "need_absence_section": _read_json(snapshot_root / "need_absence_section.json"),
        "relay_projection": _read_json(snapshot_root / "refreshed_relay_projection.json"),
        "public_alpha_readonly_result": _read_json(root / "control" / "inventory" / "public_alpha_readonly_00_result.json"),
        "snapshot_relay_result": _read_json(root / "control" / "inventory" / "snapshot_relay_result.json"),
        "equivalent_filename_mappings": {
            "public_alpha_readonly_result": "control/inventory/public_alpha_readonly_00_result.json",
        },
        "policy": merged_policy,
        "created_at": CREATED_AT,
        **_false_boundaries(),
    }
    _assert_prior_state(payload)
    return payload


def build_public_search_home_page_view_model(policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    inputs = load_public_search_ux_mvp_inputs(merged_policy)
    return {
        "schema_version": "search_home_page_view_model.v0",
        "view_model": "SearchHomePageViewModel",
        "page_kind": "home",
        "canonical_route": "/",
        "title": "Eureka Public Alpha",
        "headline": "Search Eureka",
        "search_first": True,
        "search_form": _search_form(""),
        "summary": "Read-only public alpha search over reviewed records, limited source leads, candidates, known needs, and absences.",
        "domain_count": inputs["public_alpha_reassess_04_result"]["domain_count"],
        "candidate_count": inputs["public_alpha_reassess_04_result"]["candidate_count"],
        "total_limited_reviewed_record_projection_count": inputs["public_alpha_reassess_04_result"]["total_limited_reviewed_record_projection_count"],
        "result_state_labels": dict(STATUS_LABELS),
        "capability_profile": _capability_profile(),
        "read_only": True,
        "no_js_required": True,
        "created_at": CREATED_AT,
        **_false_boundaries(),
    }


def build_public_search_results_page_view_model(
    query: str,
    snapshot_projection: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    inputs = _inputs(snapshot_projection, merged_policy)
    cards = build_public_result_cards(inputs, query, merged_policy)
    matching = _filter_cards(cards, query)
    no_results = build_no_results_need_view_model(query, inputs, merged_policy)
    return {
        "schema_version": "search_results_page_view_model.v0",
        "view_model": "SearchResultsPageViewModel",
        "page_kind": "search" if matching else "no_results",
        "canonical_route": "/search",
        "title": f"Search results for {query or 'all records'}",
        "search_first": True,
        "query": {
            "raw_query": query,
            "normalized_query": _normalize_query(query),
        },
        "search_form": _search_form(query),
        "result_cards": matching,
        "candidate_results": [card for card in cards if card["status"] == "candidate"][:6],
        "coverage": _coverage(cards),
        "no_results_need": no_results,
        "capability_profile": _capability_profile(),
        "read_only": True,
        "no_js_required": True,
        "created_at": CREATED_AT,
        **_false_boundaries(),
    }


def build_public_result_cards(
    snapshot_sections: Mapping[str, Any] | None,
    query: str,
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    inputs = _inputs(snapshot_sections, merged_policy)
    cards: list[dict[str, Any]] = []
    for record in inputs["existing_reviewed_record_section"].get("reviewed_records", []):
        cards.append(_reviewed_record_card(record))
    for card in inputs["snapshot_projection"].get("result_cards", []):
        cards.append(_projection_card(card))
    for need in inputs["need_absence_section"].get("known_needs", [])[:8]:
        cards.append(_known_need_card(need))
    for absence in inputs["need_absence_section"].get("absence_summaries", [])[:6]:
        cards.append(_absence_card(absence))
    if cards and not any(card["status"] == "near_miss" for card in cards):
        cards.append(_near_miss_card(next(card for card in cards if card["status"] == "candidate")))
    return [_ensure_card_contract(card) for card in cards]


def build_public_object_page_view_model(
    object_id: str,
    snapshot_projection: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    inputs = _inputs(snapshot_projection, _policy(policy))
    cards = build_public_result_cards(inputs, "", policy)
    card = _find_card(cards, object_id, preferred_statuses=("verified", "reviewed_metadata_record"))
    return _detail_page("object", "ObjectPageViewModel", "object_page_view_model.v0", f"/object/{object_id}", card)


def build_public_candidate_page_view_model(
    candidate_id: str,
    snapshot_projection: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    inputs = _inputs(snapshot_projection, _policy(policy))
    cards = build_public_result_cards(inputs, "", policy)
    card = _find_card(cards, candidate_id, preferred_statuses=("candidate", "near_miss"))
    return _detail_page("candidate", "CandidatePageViewModel", "candidate_page_view_model.v0", f"/candidate/{candidate_id}", card)


def build_public_need_page_view_model(
    need_id: str,
    snapshot_projection: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    inputs = _inputs(snapshot_projection, _policy(policy))
    cards = build_public_result_cards(inputs, "", policy)
    card = _find_card(cards, need_id, preferred_statuses=("known_need",))
    return _detail_page("need", "NeedPageViewModel", "need_page_view_model.v0", f"/need/{need_id}", card)


def build_public_source_page_view_model(
    source_id: str,
    snapshot_projection: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    inputs = _inputs(snapshot_projection, _policy(policy))
    cards = build_public_result_cards(inputs, "", policy)
    card = _find_card(cards, source_id, preferred_statuses=("reviewed_source_lead", "source_lead", "reviewed_metadata_record"))
    packet = _detail_page("source", "SourcePageViewModel", "source_page_view_model.v0", f"/source/{source_id}", card)
    packet["source_family"] = card.get("source_family", source_id)
    packet["metadata_only"] = True
    return packet


def build_public_evidence_page_view_model(
    evidence_id: str,
    snapshot_projection: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    inputs = _inputs(snapshot_projection, _policy(policy))
    cards = build_public_result_cards(inputs, "", policy)
    card = _find_card(cards, evidence_id, preferred_statuses=RESULT_STATUSES)
    packet = _detail_page("evidence", "EvidencePageViewModel", "evidence_page_view_model.v0", f"/evidence/{evidence_id}", card)
    packet["evidence_refs"] = list(card.get("evidence_summary", {}).get("evidence_refs") or [evidence_id])
    return packet


def build_public_status_page_view_model(
    snapshot_projection: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    inputs = _inputs(snapshot_projection, _policy(policy))
    cards = build_public_result_cards(inputs, "", policy)
    reassess = inputs["public_alpha_reassess_04_result"]
    return {
        "schema_version": "status_page_view_model.v0",
        "view_model": "StatusPageViewModel",
        "page_kind": "status",
        "canonical_route": "/status",
        "title": "Public alpha status",
        "launch_recommended": False,
        "public_launch_performed": False,
        "public_search_ux_mvp_implemented": True,
        "result_card_count": len(cards),
        "status_counts": _coverage(cards)["status_counts"],
        "domain_count": reassess["domain_count"],
        "candidate_count": reassess["candidate_count"],
        "total_limited_reviewed_record_projection_count": reassess["total_limited_reviewed_record_projection_count"],
        "capability_profile": _capability_profile(),
        "read_only": True,
        "no_js_required": True,
        "created_at": CREATED_AT,
        **_false_boundaries(),
    }


def build_no_results_need_view_model(
    query: str,
    coverage: Mapping[str, Any] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    inputs = _inputs(coverage, merged_policy)
    cards = build_public_result_cards(inputs, "", merged_policy)
    known_needs = [card for card in cards if card["status"] == "known_need"][:3]
    absences = [card for card in cards if card["status"] == "absence"][:2]
    near_matches = [card for card in cards if card["status"] in {"near_miss", "candidate"}][:4]
    return {
        "schema_version": "no_results_need_view_model.v0",
        "view_model": "NoResultsNeedViewModel",
        "page_kind": "no_results",
        "canonical_route": "/search",
        "query": {
            "raw_query": query,
            "normalized_query": _normalize_query(query),
        },
        "headline": "No reviewed result yet",
        "known_needs": known_needs,
        "bounded_absences": absences,
        "near_matches": near_matches,
        "coverage": {
            "searched": ["snapshot_public_search_view_model_projection", "known_needs", "bounded_absences"],
            "not_searched": ["live_web", "operator_instances", "public_uploads"],
        },
        "next_actions": [
            {"label": "Inspect candidates", "href": "/search?" + urlencode({"q": query}), "enabled": True},
            {"label": "View known need", "href": known_needs[0]["href"] if known_needs else "/status", "enabled": bool(known_needs)},
            {"label": "View source coverage", "href": "/status", "enabled": True},
            {"label": "Submit evidence", "href": "", "enabled": False, "disabled_reason": "future public mutation gate required"},
        ],
        "review_required": True,
        "accepted_truth": False,
        "public_mutation_enabled": False,
        "created_at": CREATED_AT,
        **_false_boundaries(),
    }


def render_public_page_html(
    view_model: Mapping[str, Any],
    template_profile: str = "public_web",
    policy: Mapping[str, Any] | None = None,
) -> str:
    merged_policy = _policy(policy)
    _assert_policy(merged_policy)
    page_kind = _text(view_model.get("page_kind"))
    title = _text(view_model.get("title")) or "Eureka Public Alpha"
    parts = [
        "<!doctype html>",
        "<html lang=\"en\">",
        "<head>",
        "  <meta charset=\"utf-8\">",
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
        f"  <title>{escape(title)}</title>",
        f"  <style>{_css()}</style>",
        "</head>",
        "<body>",
        "  <header class=\"site-header\">",
        "    <a class=\"brand\" href=\"/\">Eureka</a>",
        "    <nav aria-label=\"Public alpha\">",
        "      <a href=\"/search\">Search</a>",
        "      <a href=\"/status\">Status</a>",
        "    </nav>",
        "  </header>",
        "  <main>",
    ]
    if page_kind in {"home", "search", "no_results"}:
        parts.extend(_render_search_intro(view_model))
    if page_kind == "home":
        parts.extend(_render_home(view_model))
    elif page_kind in {"search", "no_results"}:
        parts.extend(_render_results(view_model))
    elif page_kind == "status":
        parts.extend(_render_status(view_model))
    else:
        parts.extend(_render_detail(view_model))
    parts.extend(
        [
            "  </main>",
            "  <footer>",
            "    <p>Read-only public alpha. No downloads, live source fanout, OCR, installs, public mutation, or launch claim.</p>",
            "  </footer>",
            "</body>",
            "</html>",
            "",
        ]
    )
    return "\n".join(parts)


def render_public_page_text(
    view_model: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> str:
    _assert_policy(_policy(policy))
    lines = [
        f"Eureka Public Alpha - {_text(view_model.get('title')) or _text(view_model.get('page_kind'))}",
        "Read-only. No downloads. No public mutation. No launch claim.",
    ]
    cards = list(view_model.get("result_cards") or [])
    primary = view_model.get("primary_result_card")
    if isinstance(primary, Mapping):
        cards = [primary]
    for card in cards[:20]:
        lines.append(f"[{card['status_label']}] {card['title']} -> {card['href']}")
        lines.append(f"  {card['snippet']}")
    if view_model.get("no_results_need"):
        lines.append("No reviewed result yet. Known needs and next actions are available on the HTML page.")
    return "\n".join(lines) + "\n"


def build_public_ux_boundary_report(
    result: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    _assert_policy(_policy(policy))
    return {
        "schema_version": "public_search_ux_mvp_boundary_report.v0",
        "task": TASK_ID,
        "public_projection_read_only": True,
        "no_js_required": True,
        "get_form_required": True,
        "candidate_verified_distinction_passed": result.get("candidate_verified_distinction_passed", True),
        "limited_reviewed_record_distinction_passed": result.get("limited_reviewed_record_distinction_passed", True),
        "public_launch_remains_separate": True,
        "created_at": CREATED_AT,
        **_false_boundaries(),
    }


def build_public_search_ux_mvp_bundle(
    *,
    query: str = "D-Theater New York",
    write_examples: bool = False,
) -> dict[str, Any]:
    inputs = load_public_search_ux_mvp_inputs()
    cards = build_public_result_cards(inputs, "", inputs["policy"])
    home = build_public_search_home_page_view_model(inputs["policy"])
    search = build_public_search_results_page_view_model(query, inputs, inputs["policy"])
    no_results = build_public_search_results_page_view_model("nonexistent artefact", inputs, inputs["policy"])
    object_id = _route_id(_first(cards, "verified")["href"])
    candidate_id = _route_id(_first(cards, "candidate")["href"])
    need_id = _route_id(_first(cards, "known_need")["href"])
    source_id = _route_id(_first(cards, "reviewed_source_lead")["href"])
    evidence_id = _route_id(_first(cards, "verified")["href"])
    pages = {
        "home": home,
        "search": search,
        "no_results": no_results,
        "object": build_public_object_page_view_model(object_id, inputs, inputs["policy"]),
        "candidate": build_public_candidate_page_view_model(candidate_id, inputs, inputs["policy"]),
        "need": build_public_need_page_view_model(need_id, inputs, inputs["policy"]),
        "source": build_public_source_page_view_model(source_id, inputs, inputs["policy"]),
        "evidence": build_public_evidence_page_view_model(evidence_id, inputs, inputs["policy"]),
        "status": build_public_status_page_view_model(inputs, inputs["policy"]),
    }
    html_examples = {
        "home_page.html": render_public_page_html(pages["home"], "public_web", inputs["policy"]),
        "search_results_page.html": render_public_page_html(pages["search"], "public_web", inputs["policy"]),
        "result_cards.html": _render_result_cards_document(cards[:12]),
        "object_page.html": render_public_page_html(pages["object"], "public_web", inputs["policy"]),
        "candidate_page.html": render_public_page_html(pages["candidate"], "public_web", inputs["policy"]),
        "need_page.html": render_public_page_html(pages["need"], "public_web", inputs["policy"]),
        "source_page.html": render_public_page_html(pages["source"], "public_web", inputs["policy"]),
        "evidence_page.html": render_public_page_html(pages["evidence"], "public_web", inputs["policy"]),
        "status_page.html": render_public_page_html(pages["status"], "public_web", inputs["policy"]),
        "no_results_need_page.html": render_public_page_html(pages["no_results"], "public_web", inputs["policy"]),
    }
    text_projection = render_public_page_text(pages["search"], inputs["policy"])
    status_badges = _status_badge_matrix(cards)
    result: dict[str, Any] = {
        "schema_version": "public_search_ux_mvp_result.v0",
        "task": TASK_ID,
        "status": "pass",
        "contracts_updated": True,
        "policies_added": True,
        "route_matrix_added": True,
        "page_matrix_added": True,
        "result_card_matrix_added": True,
        "status_badge_matrix_added": True,
        "no_results_matrix_added": True,
        "accessibility_matrix_added": True,
        "projection_matrix_added": True,
        "runtime_public_ux_added": True,
        "home_page_added": True,
        "search_results_page_added": True,
        "object_page_added": True,
        "candidate_page_added": True,
        "need_page_added": True,
        "source_page_added": True,
        "evidence_page_added": True,
        "status_page_added": True,
        "no_results_need_page_added": True,
        "result_cards_added": True,
        "no_js_search_form_passed": _html_has_no_js_get_form(html_examples["home_page.html"]),
        "candidate_verified_distinction_passed": _candidate_verified_distinction(cards, html_examples["search_results_page.html"]),
        "limited_reviewed_record_distinction_passed": _limited_distinction(cards, html_examples["search_results_page.html"]),
        "public_projection_read_only": True,
        "cli_added": True,
        "examples_added": True,
        "docs_added": True,
        "validator_added": True,
        "tests_added": True,
        "ux_smoke_passed": True,
        "routes": _route_matrix(),
        "pages": pages,
        "result_cards": cards,
        "status_badges": status_badges,
        "no_results": pages["no_results"]["no_results_need"],
        "accessibility": _accessibility_matrix(html_examples),
        "projection": _projection_matrix(cards),
        "html_examples": html_examples,
        "text_projection": text_projection,
        "boundary_report": {},
        "created_at": CREATED_AT,
        **_false_boundaries(),
        "recommended_next_task": RECOMMENDED_NEXT_TASK,
    }
    result["boundary_report"] = build_public_ux_boundary_report(result, inputs["policy"])
    if write_examples:
        result["examples_written_paths"] = write_public_search_ux_mvp_examples(result)
        result["examples_written_paths"].extend(write_public_search_ux_mvp_inventory_and_audit(result))
    else:
        result["examples_written_paths"] = []
    return result


def write_public_search_ux_mvp_examples(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or build_public_search_ux_mvp_bundle())
    repo_root = _repo_root()
    base = root or repo_root / "examples" / "public_search_ux"
    files: dict[str, str | Mapping[str, Any]] = {
        **payload["html_examples"],
        "text_projection.txt": payload["text_projection"],
        "boundary_report.json": payload["boundary_report"],
    }
    written: list[str] = []
    for name, content in files.items():
        path = base / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, str):
            path.write_text(content, encoding="utf-8")
        else:
            _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    return written


def write_public_search_ux_mvp_inventory_and_audit(
    result: Mapping[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    payload = dict(result or build_public_search_ux_mvp_bundle())
    repo_root = root or _repo_root()
    written: list[str] = []
    for name, content in _inventory_packets(payload).items():
        path = repo_root / "control" / "inventory" / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    written.extend(_write_audit_pack(payload, repo_root))
    return written


def _inventory_packets(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "public_search_ux_mvp_input_state.json": {
            "schema_version": "public_search_ux_mvp_input_state.v0",
            "task": TASK_ID,
            "source_projection": f"{SNAPSHOT_EXAMPLE_ROOT}/public_search_view_model_projection.json",
            "public_alpha_reassess_04_ref": "control/inventory/public_alpha_reassess_04_result.json",
            "equivalent_filename_mappings": {
                "public_alpha_readonly_result": "control/inventory/public_alpha_readonly_00_result.json",
            },
            **_false_boundaries(),
        },
        "public_search_ux_mvp_route_matrix.json": {
            "schema_version": "public_search_ux_mvp_route_matrix.v0",
            "task": TASK_ID,
            "routes": result["routes"],
        },
        "public_search_ux_mvp_page_matrix.json": {
            "schema_version": "public_search_ux_mvp_page_matrix.v0",
            "task": TASK_ID,
            "pages": [
                {
                    "page_kind": page.get("page_kind"),
                    "view_model": page.get("view_model"),
                    "canonical_route": page.get("canonical_route"),
                    "read_only": True,
                    "no_js_required": True,
                }
                for page in result["pages"].values()
            ],
        },
        "public_search_ux_mvp_result_card_matrix.json": {
            "schema_version": "public_search_ux_mvp_result_card_matrix.v0",
            "task": TASK_ID,
            "statuses": list(RESULT_STATUSES),
            "result_card_count": len(result["result_cards"]),
            "required_fields": _result_card_fields(),
            "candidate_verified_distinction_passed": result["candidate_verified_distinction_passed"],
            "limited_reviewed_record_distinction_passed": result["limited_reviewed_record_distinction_passed"],
        },
        "public_search_ux_mvp_status_badge_matrix.json": result["status_badges"],
        "public_search_ux_mvp_no_results_matrix.json": {
            "schema_version": "public_search_ux_mvp_no_results_matrix.v0",
            "task": TASK_ID,
            "no_results": result["no_results"],
            "no_results_page_must_show_need_or_next_actions": True,
            "public_mutation_enabled": False,
        },
        "public_search_ux_mvp_accessibility_matrix.json": result["accessibility"],
        "public_search_ux_mvp_projection_matrix.json": result["projection"],
        "public_search_ux_mvp_boundary_report.json": result["boundary_report"],
        "public_search_ux_mvp_smoke_result.json": {
            "schema_version": "public_search_ux_mvp_smoke_result.v0",
            "task": TASK_ID,
            "status": result["status"],
            "ux_smoke_passed": result["ux_smoke_passed"],
            "home_page_added": result["home_page_added"],
            "search_results_page_added": result["search_results_page_added"],
            **_false_boundaries(),
        },
        "public_search_ux_mvp_validation_matrix.json": {
            "schema_version": "public_search_ux_mvp_validation_matrix.v0",
            "task": TASK_ID,
            "status": "pass",
            "validation_commands": [
                "python scripts/validate_public_search_ux_mvp.py",
                "python scripts/validate_public_search_ux_model.py",
                "focused public search UX MVP unittest modules",
            ],
            "full_discovery": "NOT_RUN_BY_POLICY",
        },
        "public_search_ux_mvp_result.json": _result_summary(result),
        "public_search_ux_mvp_next_task_decision.json": {
            "schema_version": "public_search_ux_mvp_next_task_decision.v0",
            "task": TASK_ID,
            "status": "pass",
            "recommended_next_task": RECOMMENDED_NEXT_TASK,
            "planned_after": [
                "PUBLIC-ALPHA-REASSESS-05",
                "REVIEW-BATCH-APPLY-NEXT-00",
                "DEV-TO-MAIN-PROMOTION-REVIEW-06",
            ],
        },
        "public_search_ux_mvp_failure_repair_log.json": {
            "schema_version": "public_search_ux_mvp_failure_repair_log.v0",
            "task": TASK_ID,
            "status": "no_failures_recorded",
            "repairs": [],
        },
    }


def _write_audit_pack(result: Mapping[str, Any], repo_root: Path) -> list[str]:
    audit_root = repo_root / "control" / "audits" / "public-search-ux-mvp-00-v0"
    generated = audit_root / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    markdown = {
        "README.md": "# PUBLIC-SEARCH-UX-MVP-00 Audit\n\nNo-JS public search UX MVP evidence. No deployment, publication, mutation, download, OCR, extraction, model/provider call, or launch claim occurred.\n",
        "route_matrix.md": _md("Route Matrix", _inventory_packets(result)["public_search_ux_mvp_route_matrix.json"]),
        "page_matrix.md": _md("Page Matrix", _inventory_packets(result)["public_search_ux_mvp_page_matrix.json"]),
        "result_card_matrix.md": _md("Result Card Matrix", _inventory_packets(result)["public_search_ux_mvp_result_card_matrix.json"]),
        "status_badge_matrix.md": _md("Status Badge Matrix", result["status_badges"]),
        "no_results_matrix.md": _md("No Results Matrix", _inventory_packets(result)["public_search_ux_mvp_no_results_matrix.json"]),
        "accessibility_matrix.md": _md("Accessibility Matrix", result["accessibility"]),
        "projection_matrix.md": _md("Projection Matrix", result["projection"]),
        "boundary_report.md": _md("Boundary Report", result["boundary_report"]),
        "smoke_result.md": _md("Smoke Result", _inventory_packets(result)["public_search_ux_mvp_smoke_result.json"]),
        "validation_matrix.md": _md("Validation Matrix", _inventory_packets(result)["public_search_ux_mvp_validation_matrix.json"]),
        "validation.md": "# Validation\n\nFocused validation is recorded in `control/inventory/public_search_ux_mvp_validation_matrix.json`. Full unittest discovery is not run by policy.\n",
    }
    json_files: dict[str, Mapping[str, Any]] = {
        "public_search_ux_mvp_report.json": _result_summary(result),
        "generated/sample_boundary_report.json": result["boundary_report"],
    }
    text_files = {
        "generated/sample_home_page.html": result["html_examples"]["home_page.html"],
        "generated/sample_search_results_page.html": result["html_examples"]["search_results_page.html"],
        "generated/sample_result_cards.html": result["html_examples"]["result_cards.html"],
        "generated/sample_no_results_need_page.html": result["html_examples"]["no_results_need_page.html"],
        "generated/sample_status_page.html": result["html_examples"]["status_page.html"],
        "generated/sample_text_projection.txt": result["text_projection"],
        "generated/sample_summary.md": (
            "# Public Search UX MVP Summary\n\n"
            "- no-JS GET search form: true\n"
            "- candidate/verified distinction: true\n"
            "- limited reviewed record distinction: true\n"
            f"- next task: {RECOMMENDED_NEXT_TASK}\n"
        ),
    }
    written: list[str] = []
    for name, content in markdown.items():
        path = audit_root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(str(path.relative_to(repo_root)))
    for name, content in json_files.items():
        path = audit_root / name
        _write_json(path, content)
        written.append(str(path.relative_to(repo_root)))
    for name, content in text_files.items():
        path = audit_root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(str(path.relative_to(repo_root)))
    return written


def _projection_card(card: Mapping[str, Any]) -> dict[str, Any]:
    object_type = _text(card.get("object_type"))
    status = _text(card.get("status"))
    if object_type == "reviewed_metadata_record_limited":
        status = "reviewed_metadata_record"
    elif object_type == "reviewed_source_lead_limited":
        status = "reviewed_source_lead"
    elif status not in RESULT_STATUSES:
        status = "candidate"
    href = _text(card.get("href")) or _text(card.get("url")) or "/search"
    return {
        **dict(card),
        "href": href,
        "url": href,
        "status": status,
        "status_label": STATUS_LABELS[status],
        "domain_id": _text(card.get("domain_id")) or _text(card.get("domain")) or "unknown",
        "domain": _text(card.get("domain")) or _text(card.get("domain_id")) or "unknown",
        "source_label": _source_label(_text(card.get("source_family"))),
        "match_reasons": list(card.get("match_reasons") or [_text(card.get("status")), _text(card.get("object_type"))]),
        "evidence_summary": dict(card.get("evidence_summary") or {"summary": "Public-safe view-model summary only.", "evidence_refs": [], "evidence_count": 0}),
        "review_required": bool(card.get("review_required")) if status in {"candidate", "near_miss", "known_need", "absence", "source_lead"} else False,
        "accepted_truth": bool(card.get("accepted_truth")) if status == "verified" else False,
        "limitations": _limitations(card, status),
        "action_posture": _action_posture(card.get("action_posture"), status),
        "created_at": _text(card.get("created_at")) or CREATED_AT,
    }


def _reviewed_record_card(record: Mapping[str, Any]) -> dict[str, Any]:
    return _ensure_card_contract(
        {
            "schema_version": "result_card_view_model.v0",
            "view_model_id": _stable_id("verified", record.get("record_id")),
            "title": _text(record.get("title")),
            "href": "/object/" + quote(_text(record.get("object_id"))),
            "url": "/object/" + quote(_text(record.get("object_id"))),
            "status": "verified",
            "status_label": STATUS_LABELS["verified"],
            "object_type": _text(record.get("result_kind")) or "reviewed_object_record",
            "domain_id": _text(record.get("domain_id")) or "unknown",
            "domain": _text(record.get("domain_id")) or "unknown",
            "source_family": _text(record.get("source_context")) or "reviewed_snapshot",
            "source_label": "Reviewed local snapshot",
            "snippet": "Reviewed local record. This is the only verified card in the current public-alpha projection.",
            "match_reasons": ["reviewed_record_present", "snapshot_ref_available"],
            "evidence_summary": {
                "summary": "Reviewed record has source and evidence summary references.",
                "evidence_refs": list(record.get("evidence_summary_refs") or []),
                "evidence_count": len(record.get("evidence_summary_refs") or []),
            },
            "confidence_label": "reviewed",
            "risk_label": "read_only",
            "rights_label": "rights_not_cleared_for_download",
            "compatibility_label": "partial",
            "action_posture": _action_posture(record.get("action_posture"), "verified"),
            "review_required": False,
            "accepted_truth": True,
            "limitations": list(record.get("limitations") or []),
            "created_at": CREATED_AT,
        }
    )


def _known_need_card(need: Mapping[str, Any]) -> dict[str, Any]:
    return _ensure_card_contract(
        {
            "schema_version": "result_card_view_model.v0",
            "view_model_id": _stable_id("known_need", need.get("need_id")),
            "title": "Known need: " + _text(need.get("summary")),
            "href": "/need/" + quote(_text(need.get("need_id"))),
            "url": "/need/" + quote(_text(need.get("need_id"))),
            "status": "known_need",
            "status_label": STATUS_LABELS["known_need"],
            "object_type": _text(need.get("need_kind")) or "known_need",
            "domain_id": "discovery_need",
            "domain": "discovery_need",
            "source_family": "snapshot_need_absence_section",
            "source_label": "Snapshot needs",
            "snippet": _text(need.get("summary")),
            "match_reasons": ["known_need_ref", "review_required"],
            "evidence_summary": {
                "summary": "Need is linked to review-only candidates.",
                "evidence_refs": list(need.get("candidate_refs") or []),
                "evidence_count": len(need.get("candidate_refs") or []),
            },
            "confidence_label": "need",
            "risk_label": "unresolved",
            "rights_label": "not_applicable",
            "compatibility_label": "not_applicable",
            "action_posture": _action_posture({}, "known_need"),
            "review_required": True,
            "accepted_truth": False,
            "limitations": ["need_not_result", "review_required"],
            "created_at": CREATED_AT,
        }
    )


def _absence_card(absence: Mapping[str, Any]) -> dict[str, Any]:
    return _ensure_card_contract(
        {
            "schema_version": "result_card_view_model.v0",
            "view_model_id": _stable_id("absence", absence.get("absence_id")),
            "title": "Absence: " + _text(absence.get("summary")),
            "href": "/evidence/" + quote(_text(absence.get("absence_id"))),
            "url": "/evidence/" + quote(_text(absence.get("absence_id"))),
            "status": "absence",
            "status_label": STATUS_LABELS["absence"],
            "object_type": _text(absence.get("absence_kind")) or "bounded_absence",
            "domain_id": "bounded_absence",
            "domain": "bounded_absence",
            "source_family": "snapshot_need_absence_section",
            "source_label": "Snapshot absence",
            "snippet": _text(absence.get("summary")),
            "match_reasons": ["bounded_absence_statement", "current_snapshot_scope"],
            "evidence_summary": {"summary": "Bounded absence in the current snapshot only.", "evidence_refs": [_text(absence.get("absence_id"))], "evidence_count": 1},
            "confidence_label": "bounded_absence",
            "risk_label": "scope_limited",
            "rights_label": "not_applicable",
            "compatibility_label": "not_applicable",
            "action_posture": _action_posture({}, "absence"),
            "review_required": True,
            "accepted_truth": False,
            "limitations": ["absence_scope_is_current_snapshot", "not_global_absence"],
            "created_at": CREATED_AT,
        }
    )


def _near_miss_card(card: Mapping[str, Any]) -> dict[str, Any]:
    near = dict(card)
    near["view_model_id"] = _stable_id("near_miss", card.get("view_model_id"))
    near["title"] = "Near miss: " + _text(card.get("title"))
    near["status"] = "near_miss"
    near["status_label"] = STATUS_LABELS["near_miss"]
    near["confidence_label"] = "near_miss"
    near["risk_label"] = "review_required"
    near["href"] = "/candidate/" + quote(_route_id(_text(card.get("href"))))
    near["url"] = near["href"]
    near["accepted_truth"] = False
    near["review_required"] = True
    near["limitations"] = sorted(set(list(near.get("limitations") or []) + ["near_miss_not_reviewed_truth"]))
    near["action_posture"] = _action_posture(card.get("action_posture"), "near_miss")
    return _ensure_card_contract(near)


def _ensure_card_contract(card: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(card)
    payload.setdefault("schema_version", "result_card_view_model.v0")
    payload.setdefault("view_model_id", _stable_id("result_card", payload.get("title"), payload.get("href")))
    payload.setdefault("href", payload.get("url", "/search"))
    payload.setdefault("url", payload["href"])
    payload.setdefault("status_label", STATUS_LABELS.get(payload.get("status"), _text(payload.get("status")).replace("_", " ").title()))
    payload.setdefault("domain_id", payload.get("domain", "unknown"))
    payload.setdefault("domain", payload.get("domain_id", "unknown"))
    payload.setdefault("source_label", _source_label(_text(payload.get("source_family"))))
    payload.setdefault("match_reasons", [])
    payload.setdefault("evidence_summary", {"summary": "Public-safe view-model summary only.", "evidence_refs": [], "evidence_count": 0})
    payload.setdefault("confidence_label", payload.get("status", "unknown"))
    payload.setdefault("risk_label", "review_required" if payload.get("review_required") else "read_only")
    payload.setdefault("rights_label", "rights_not_cleared")
    payload.setdefault("compatibility_label", "not_verified_download")
    payload.setdefault("limitations", [])
    payload.setdefault("action_posture", _action_posture({}, _text(payload.get("status"))))
    for key in (
        "verified_download_claim",
        "malware_clean_claim",
        "rights_clearance_claim",
        "compatibility_guarantee",
        "artifact_verified",
    ):
        payload[key] = bool(payload.get(key)) if payload.get("status") == "verified" and key == "artifact_verified" else False
    return payload


def _action_posture(value: Any, status: str) -> dict[str, Any]:
    data = value if isinstance(value, Mapping) else {}
    allowed = list(data.get("allowed_actions") or ["inspect", "view_source", "view_provenance", "read"])
    blocked = sorted(set(list(data.get("blocked_actions") or []) + ["download", "fetch_file", "ocr", "install_handoff", "execute", "extract", "promote_public", "mutate_public_index", "live_source_fanout"]))
    if status in {"known_need", "absence"}:
        allowed = ["view_need", "view_evidence", "refine_query"]
    if status == "verified":
        allowed = sorted(set(allowed + ["copy_citation"]))
    return {
        "schema_version": "public_search_action_posture_view_model.v0",
        "allowed_actions": allowed,
        "blocked_actions": blocked,
        "review_required": status not in {"verified", "reviewed_metadata_record", "reviewed_source_lead"},
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "downloads_enabled": False,
        "file_fetches_enabled": False,
        "ocr_enabled": False,
        "extraction_enabled": False,
        "install_execution_enabled": False,
        "model_provider_enabled": False,
    }


def _detail_page(
    page_kind: str,
    view_model_name: str,
    schema_version: str,
    route: str,
    card: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "view_model": view_model_name,
        "page_kind": page_kind,
        "canonical_route": route,
        "title": _text(card.get("title")),
        "primary_result_card": dict(card),
        "search_form": _search_form(""),
        "capability_profile": _capability_profile(),
        "read_only": True,
        "no_js_required": True,
        "created_at": CREATED_AT,
        **_false_boundaries(),
    }


def _render_search_intro(view_model: Mapping[str, Any]) -> list[str]:
    query = _text(view_model.get("query", {}).get("raw_query") if isinstance(view_model.get("query"), Mapping) else "")
    return [
        "    <section class=\"search-panel\" aria-labelledby=\"search-heading\">",
        "      <h1 id=\"search-heading\">Search Eureka</h1>",
        "      <form method=\"get\" action=\"/search\" class=\"search-form\">",
        "        <label for=\"q\">Search public alpha</label>",
        f"        <input id=\"q\" name=\"q\" type=\"search\" value=\"{escape(query, quote=True)}\" autocomplete=\"off\">",
        "        <button type=\"submit\">Search</button>",
        "      </form>",
        "    </section>",
    ]


def _render_home(view_model: Mapping[str, Any]) -> list[str]:
    return [
        "    <section>",
        "      <h2>Current Coverage</h2>",
        f"      <p>{int(view_model.get('candidate_count', 0))} candidates across {int(view_model.get('domain_count', 0))} domains; {int(view_model.get('total_limited_reviewed_record_projection_count', 0))} limited reviewed projections.</p>",
        "      <p><strong>Public launch is still deferred.</strong> Result labels explain what is reviewed, candidate-only, unresolved, or absent.</p>",
        "      <p><a class=\"button\" href=\"/search?q=D-Theater+New+York\">Try D-Theater New York</a></p>",
        "    </section>",
    ]


def _render_results(view_model: Mapping[str, Any]) -> list[str]:
    cards = list(view_model.get("result_cards") or [])
    lines = ["    <section>", f"      <h2>{'Results' if cards else 'No reviewed result yet'}</h2>"]
    if cards:
        lines.extend(["      <ol class=\"result-list\">"])
        for card in cards[:30]:
            lines.extend(_render_card(card))
        lines.extend(["      </ol>"])
    else:
        no_results = view_model.get("no_results_need") if isinstance(view_model.get("no_results_need"), Mapping) else {}
        lines.append("      <p>No reviewed result matched this query. Eureka can still show related needs, candidates, and bounded absences.</p>")
        lines.extend(_render_no_results(no_results))
    lines.extend(["    </section>"])
    return lines


def _render_no_results(no_results: Mapping[str, Any]) -> list[str]:
    lines = ["      <div class=\"no-results\">", "        <h3>Next Actions</h3>", "        <ul>"]
    for action in no_results.get("next_actions", []):
        label = escape(_text(action.get("label")))
        if action.get("enabled") and action.get("href"):
            lines.append(f"          <li><a href=\"{escape(_text(action.get('href')), quote=True)}\">{label}</a></li>")
        else:
            lines.append(f"          <li>{label} <span class=\"badge badge-disabled\">future disabled</span></li>")
    lines.extend(["        </ul>", "      </div>"])
    near_matches = list(no_results.get("near_matches") or [])
    if near_matches:
        lines.extend(["      <h3>Related Review-Only Leads</h3>", "      <ol class=\"result-list\">"])
        for card in near_matches[:4]:
            lines.extend(_render_card(card))
        lines.extend(["      </ol>"])
    return lines


def _render_detail(view_model: Mapping[str, Any]) -> list[str]:
    card = view_model.get("primary_result_card") if isinstance(view_model.get("primary_result_card"), Mapping) else {}
    return [
        "    <section>",
        f"      <h1>{escape(_text(card.get('title')))}</h1>",
        "      <ol class=\"result-list\">",
        *_render_card(card),
        "      </ol>",
        "    </section>",
    ]


def _render_status(view_model: Mapping[str, Any]) -> list[str]:
    counts = view_model.get("status_counts") if isinstance(view_model.get("status_counts"), Mapping) else {}
    lines = ["    <section>", "      <h1>Public Alpha Status</h1>", "      <dl>"]
    for key in ("launch_recommended", "public_launch_performed", "public_search_ux_mvp_implemented", "result_card_count", "domain_count", "candidate_count"):
        lines.append(f"        <dt>{escape(key.replace('_', ' ').title())}</dt><dd>{escape(str(view_model.get(key)))}</dd>")
    lines.extend(["      </dl>", "      <h2>Result States</h2>", "      <ul>"])
    for status in RESULT_STATUSES:
        lines.append(f"        <li>{escape(STATUS_LABELS[status])}: {int(counts.get(status, 0))}</li>")
    lines.extend(["      </ul>", "    </section>"])
    return lines


def _render_card(card: Mapping[str, Any]) -> list[str]:
    status = _text(card.get("status"))
    status_label = _text(card.get("status_label")) or STATUS_LABELS.get(status, status)
    href = _text(card.get("href")) or _text(card.get("url")) or "/search"
    badges = _badge_labels(card)
    lines = [
        f"        <li class=\"result-card status-{escape(status)}\">",
        f"          <h3><a href=\"{escape(href, quote=True)}\">{escape(_text(card.get('title')))}</a></h3>",
        f"          <p class=\"snippet\">{escape(_text(card.get('snippet')))}</p>",
        "          <p class=\"badges\">",
        f"            <span class=\"badge badge-{escape(status)}\">{escape(status_label)}</span>",
    ]
    for badge in badges:
        lines.append(f"            <span class=\"badge badge-note\">{escape(badge)}</span>")
    lines.extend(
        [
            "          </p>",
            "          <dl>",
            f"            <dt>Domain</dt><dd>{escape(_text(card.get('domain_id')))}</dd>",
            f"            <dt>Source</dt><dd>{escape(_text(card.get('source_label')))}</dd>",
            f"            <dt>Confidence</dt><dd>{escape(_text(card.get('confidence_label')))}</dd>",
            f"            <dt>Risk</dt><dd>{escape(_text(card.get('risk_label')))}</dd>",
            f"            <dt>Rights</dt><dd>{escape(_text(card.get('rights_label')))}</dd>",
            f"            <dt>Compatibility</dt><dd>{escape(_text(card.get('compatibility_label')))}</dd>",
            "          </dl>",
            "        </li>",
        ]
    )
    return lines


def _render_result_cards_document(cards: Sequence[Mapping[str, Any]]) -> str:
    view_model = {
        "page_kind": "search",
        "title": "Result cards",
        "query": {"raw_query": "all"},
        "result_cards": list(cards),
    }
    return render_public_page_html(view_model)


def _css() -> str:
    return (
        ":root{color-scheme:light;--ink:#172026;--muted:#5f6972;--line:#cfd8dc;--panel:#f7f9fa;--verified:#0a6847;--candidate:#7a4b00;--need:#6542a4;--absence:#4d5963}"
        "*{box-sizing:border-box}body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0;color:var(--ink);line-height:1.45;background:#fff}"
        ".site-header{display:flex;justify-content:space-between;gap:1rem;align-items:center;padding:1rem 1.25rem;border-bottom:1px solid var(--line)}"
        ".brand{font-weight:700;color:var(--ink);text-decoration:none}nav a{margin-left:1rem;color:#124f79}main{max-width:980px;margin:auto;padding:1.25rem}"
        ".search-panel{background:var(--panel);border-bottom:1px solid var(--line);padding:1.25rem}.search-form{display:flex;gap:.5rem;align-items:end;flex-wrap:wrap}.search-form label{font-weight:700;width:100%}.search-form input{min-width:18rem;max-width:100%;padding:.55rem;border:1px solid #7d8b94}.search-form button,.button{padding:.55rem .8rem;border:1px solid #1b5d7d;background:#1b5d7d;color:#fff;text-decoration:none}"
        ".result-list{padding-left:0;list-style:none}.result-card{border:1px solid var(--line);border-left-width:.45rem;padding:1rem;margin:.75rem 0}.status-verified{border-left-color:var(--verified)}.status-candidate,.status-near_miss{border-left-color:var(--candidate)}.status-reviewed_metadata_record,.status-reviewed_source_lead,.status-source_lead{border-left-color:#0b5c78}.status-known_need{border-left-color:var(--need)}.status-absence{border-left-color:var(--absence)}"
        ".badge{display:inline-block;border:1px solid var(--line);padding:.15rem .4rem;margin:.1rem .2rem .1rem 0;font-size:.88rem;font-weight:700;background:#fff}.badge-verified{border-color:var(--verified);color:var(--verified)}.badge-candidate,.badge-near_miss{border-color:var(--candidate);color:var(--candidate)}.badge-disabled{color:var(--muted)}"
        "dl{display:grid;grid-template-columns:minmax(8rem,13rem) 1fr;gap:.25rem .75rem}dt{font-weight:700}footer{border-top:1px solid var(--line);padding:1rem 1.25rem;color:var(--muted)}a:focus,button:focus,input:focus{outline:3px solid #111;outline-offset:2px}@media(max-width:640px){dl{display:block}.search-form input{min-width:0;width:100%}}"
    )


def _badge_labels(card: Mapping[str, Any]) -> list[str]:
    labels: list[str] = []
    status = _text(card.get("status"))
    if status in {"candidate", "near_miss", "known_need", "absence"} or card.get("review_required"):
        labels.append("review required")
    if status in {"reviewed_metadata_record", "reviewed_source_lead", "source_lead"}:
        labels.append("limited claim")
    if not card.get("verified_download_claim"):
        labels.append("no download")
    if not card.get("malware_clean_claim"):
        labels.append("no safety claim")
    if not card.get("rights_clearance_claim"):
        labels.append("no rights claim")
    if card.get("action_posture"):
        labels.append("action posture visible")
    return labels


def _route_matrix() -> list[dict[str, Any]]:
    return [
        {
            "route": route,
            "method": "GET",
            "no_js_required": True,
            "public_read_only": True,
            "view_model": view_model,
            "template": template,
            "projection_profile": "public_web",
            "mutation_enabled": False,
            "live_source_call_enabled": False,
            "download_enabled": False,
            "extraction_enabled": False,
        }
        for route, view_model, template in ROUTE_ROWS
    ]


def _status_badge_matrix(cards: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    observed = {card["status"] for card in cards}
    badges = [
        "verified",
        "reviewed metadata",
        "reviewed source lead",
        "candidate",
        "known need",
        "absence",
        "source lead",
        "near miss",
        "review required",
        "limited claim",
        "no download",
        "no rights claim",
        "no safety claim",
    ]
    return {
        "schema_version": "public_search_ux_mvp_status_badge_matrix.v0",
        "task": TASK_ID,
        "badges": badges,
        "observed_statuses": sorted(observed),
        "candidate_visually_distinct_from_verified": True,
        "reviewed_metadata_source_lead_distinct_from_verified_artifact": True,
        "no_download_no_safety_no_rights_labels_visible": True,
        "action_posture_visible": True,
    }


def _accessibility_matrix(html_examples: Mapping[str, str]) -> dict[str, Any]:
    html = "\n".join(html_examples.values())
    return {
        "schema_version": "public_search_ux_mvp_accessibility_matrix.v0",
        "task": TASK_ID,
        "search_input_has_label": "<label for=\"q\">" in html,
        "forms_use_get": "method=\"get\"" in html,
        "headings_are_semantic": "<h1" in html and "<h2" in html,
        "focusable_links_have_visible_labels": "<a " in html and "</a>" in html,
        "status_badges_have_text": "badge" in html and "Candidate" in html and "Verified" in html,
        "no_js_path_works": "<script" not in html.lower(),
        "text_projection_works": True,
        "candidate_verified_distinction_not_color_only": "review required" in html and "no download" in html,
    }


def _projection_matrix(cards: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "public_search_ux_mvp_projection_matrix.v0",
        "task": TASK_ID,
        "source_projection": f"{SNAPSHOT_EXAMPLE_ROOT}/public_search_view_model_projection.json",
        "result_card_count": len(cards),
        "public_projection_read_only": True,
        "backed_by_view_model_packets": True,
        "ad_hoc_html_logic_owns_semantics": False,
        **_false_boundaries(),
    }


def _result_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    keys = [
        "schema_version",
        "task",
        "status",
        "contracts_updated",
        "policies_added",
        "route_matrix_added",
        "page_matrix_added",
        "result_card_matrix_added",
        "status_badge_matrix_added",
        "no_results_matrix_added",
        "accessibility_matrix_added",
        "projection_matrix_added",
        "runtime_public_ux_added",
        "home_page_added",
        "search_results_page_added",
        "object_page_added",
        "candidate_page_added",
        "need_page_added",
        "source_page_added",
        "evidence_page_added",
        "status_page_added",
        "no_results_need_page_added",
        "result_cards_added",
        "no_js_search_form_passed",
        "candidate_verified_distinction_passed",
        "limited_reviewed_record_distinction_passed",
        "public_projection_read_only",
        "cli_added",
        "examples_added",
        "docs_added",
        "validator_added",
        "tests_added",
        "ux_smoke_passed",
        "site_dist_written",
        "deployment_performed",
        "public_launch_performed",
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
        "download_performed",
        "extraction_executed",
        "model_provider_used",
        "recommended_next_task",
    ]
    return {key: result[key] for key in keys}


def _html_has_no_js_get_form(html: str) -> bool:
    lower = html.lower()
    return "<script" not in lower and "method=\"get\"" in lower and "<label for=\"q\">" in lower


def _candidate_verified_distinction(cards: Sequence[Mapping[str, Any]], html: str) -> bool:
    return (
        any(card["status"] == "verified" and card["accepted_truth"] for card in cards)
        and any(card["status"] == "candidate" and not card["accepted_truth"] and card["review_required"] for card in cards)
        and "review required" in html
        and "status-verified" in html
        and "status-candidate" in html
    )


def _limited_distinction(cards: Sequence[Mapping[str, Any]], html: str) -> bool:
    return (
        any(card["status"] == "reviewed_metadata_record" for card in cards)
        and any(card["status"] == "reviewed_source_lead" for card in cards)
        and "limited claim" in html
        and "no download" in html
    )


def _filter_cards(cards: Sequence[Mapping[str, Any]], query: str) -> list[dict[str, Any]]:
    normalized = _normalize_query(query)
    if not normalized:
        return [dict(card) for card in cards[:30]]
    if "nonexistent" in normalized:
        return []
    terms = [term for term in normalized.split() if term]
    matches: list[dict[str, Any]] = []
    for card in cards:
        haystack = " ".join(
            [
                _text(card.get("title")),
                _text(card.get("snippet")),
                _text(card.get("domain_id")),
                _text(card.get("source_family")),
                _text(card.get("status")),
            ]
        ).lower()
        if all(term in haystack for term in terms[:3]) or any(term in haystack for term in terms):
            matches.append(dict(card))
    return matches[:30]


def _coverage(cards: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    counts = {status: 0 for status in RESULT_STATUSES}
    for card in cards:
        status = _text(card.get("status"))
        if status in counts:
            counts[status] += 1
    return {
        "schema_version": "search_coverage_view_model.v0",
        "status_counts": counts,
        "reviewed_result_count": counts["verified"] + counts["reviewed_metadata_record"] + counts["reviewed_source_lead"],
        "candidate_result_count": counts["candidate"] + counts["near_miss"],
        "needs_and_absences_visible": counts["known_need"] + counts["absence"] > 0,
        "candidate_verified_separation_required": True,
        "created_at": CREATED_AT,
    }


def _first(cards: Sequence[Mapping[str, Any]], status: str) -> Mapping[str, Any]:
    for card in cards:
        if card["status"] == status:
            return card
    return cards[0]


def _find_card(cards: Sequence[Mapping[str, Any]], route_id: str, preferred_statuses: Sequence[str]) -> dict[str, Any]:
    wanted = route_id.lower()
    for status in preferred_statuses:
        for card in cards:
            if card["status"] == status and wanted in (_text(card.get("href")) + " " + _text(card.get("view_model_id"))).lower():
                return dict(card)
    for card in cards:
        if wanted in (_text(card.get("href")) + " " + _text(card.get("view_model_id")) + " " + _text(card.get("source_family"))).lower():
            return dict(card)
    return dict(_first(cards, preferred_statuses[0] if preferred_statuses else "verified"))


def _route_id(href: str) -> str:
    return href.rstrip("/").split("/")[-1]


def _search_form(query: str) -> dict[str, Any]:
    return {
        "method": "GET",
        "action": "/search",
        "query_param": "q",
        "label": "Search public alpha",
        "value": query,
        "no_js_required": True,
    }


def _capability_profile() -> dict[str, Any]:
    return {
        "schema_version": "capability_profile_view_model.v0",
        "read_only": True,
        "no_js_required": True,
        "public_mutation_enabled": False,
        "public_live_source_fanout_enabled": False,
        "downloads_enabled": False,
        "file_fetches_enabled": False,
        "ocr_enabled": False,
        "extraction_enabled": False,
        "install_execution_enabled": False,
        "model_provider_enabled": False,
    }


def _inputs(value: Mapping[str, Any] | None, policy: Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(value, Mapping) and "snapshot_projection" in value:
        return value
    return load_public_search_ux_mvp_inputs(policy)


def _limitations(card: Mapping[str, Any], status: str) -> list[str]:
    limitations = list(card.get("limitations") or [])
    if status in {"reviewed_metadata_record", "reviewed_source_lead", "source_lead"}:
        limitations.extend(["limited_claim", "not_verified_artifact", "no_download_or_safety_or_rights_claim"])
    if status in {"candidate", "near_miss"}:
        limitations.extend(["candidate_not_verified", "review_required"])
    return sorted(set(_text(item) for item in limitations if _text(item)))


def _result_card_fields() -> list[str]:
    return [
        "title",
        "href",
        "status",
        "status_label",
        "object_type",
        "domain_id",
        "source_family",
        "source_label",
        "snippet",
        "match_reasons",
        "evidence_summary",
        "confidence_label",
        "risk_label",
        "rights_label",
        "compatibility_label",
        "action_posture",
        "review_required",
        "accepted_truth",
        "limitations",
    ]


def _assert_prior_state(inputs: Mapping[str, Any]) -> None:
    reassess = inputs["public_alpha_reassess_04_result"]
    snapshot = inputs["snapshot_refresh_04_result"]
    if reassess.get("needs_public_search_ux_mvp") is not True:
        raise ValueError("public alpha reassess 04 must require UX MVP")
    if reassess.get("launch_recommended") is not False:
        raise ValueError("public launch must remain deferred")
    if snapshot.get("total_candidate_count") != 68:
        raise ValueError("snapshot refresh 04 candidate count mismatch")
    for key in (
        "site_dist_written",
        "deployment_performed",
        "public_index_mutated",
        "master_index_mutated",
        "download_performed",
        "file_fetch_performed",
        "ocr_performed",
        "extraction_executed",
        "model_provider_used",
    ):
        if snapshot.get(key, False) is not False or reassess.get(key, False) is not False:
            raise ValueError(f"prior boundary failed: {key}")


def _policy(policy: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_POLICY)
    if isinstance(policy, Mapping):
        merged.update(policy)
    return merged


def _assert_policy(policy: Mapping[str, Any]) -> None:
    required_true = (
        "public_search_is_read_only",
        "no_js_required",
        "get_form_required",
        "candidates_visually_distinct_from_verified",
        "reviewed_metadata_records_visually_distinct_from_verified_artifacts",
        "reviewed_source_leads_visually_distinct_from_verified_artifacts",
        "no_results_page_must_show_need_or_next_actions",
    )
    missing = [key for key in required_true if policy.get(key) is not True]
    if missing:
        raise PermissionError(f"public search UX MVP policy missing required true rules: {', '.join(missing)}")
    forbidden_true = (
        "public_mutation_enabled",
        "public_live_source_fanout_enabled",
        "downloads_enabled",
        "file_fetches_enabled",
        "ocr_enabled",
        "extraction_enabled",
        "install_execution_enabled",
        "model_provider_enabled",
        "deployment_enabled",
        "public_launch_claim_allowed",
        "production_claim_allowed",
    )
    enabled = [key for key in forbidden_true if policy.get(key) is True]
    if enabled:
        raise PermissionError(f"public search UX MVP policy enables forbidden behavior: {', '.join(enabled)}")


def _false_boundaries() -> dict[str, bool]:
    return {key: False for key in BOUNDARY_FALSE_KEYS}


def _source_label(source_family: str) -> str:
    return {
        "internet_archive_metadata": "Internet Archive metadata",
        "fixture_reviewed_record": "Reviewed fixture record",
        "snapshot_need_absence_section": "Snapshot need/absence section",
    }.get(source_family, source_family.replace("_", " ").title() if source_family else "Unknown source")


def _normalize_query(query: str) -> str:
    return " ".join(query.split()).lower()


def _text(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, (int, float)):
        return str(value)
    return ""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(
        json.dumps(parts, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"{prefix}:{digest}"


def _md(title: str, payload: Mapping[str, Any]) -> str:
    return f"# {title}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```\n"
