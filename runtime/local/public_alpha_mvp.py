"""Local public-alpha read-only surface over the local search MVP."""

from __future__ import annotations

from html import escape
import json
from typing import Any, Mapping, Sequence
from urllib.parse import quote, unquote

from runtime.local.search_index import (
    CANONICAL_STATUSES,
    document_to_result_card,
    index_file_status,
    load_index,
    validate_index,
)
from runtime.local.search_mvp import HARD_QUERY_SMOKE_SET, LocalSearchOptions, LocalSearchService


TASK_ID = "PUBLIC-READONLY-WEB-ALPHA-00"
PUBLIC_ROUTES = (
    "/",
    "/health",
    "/status",
    "/api/status",
    "/about",
    "/method",
    "/search?q=",
    "/api/search?q=",
    "/record/{id}",
)
FORBIDDEN_PUBLIC_TEXT = (
    ".eureka",
    "local_review_ledger",
    "local_reviewed_records",
    "local_search_index",
    "workbench-token",
    "X-Eureka-Workbench-Token",
)


class PublicAlphaService:
    """Read-only public-safe adapter over LocalSearchService and local index docs."""

    def __init__(
        self,
        *,
        search_service: LocalSearchService,
        search_options: LocalSearchOptions,
        deployment_source: str = "local_index",
        bundle_id: str = "",
    ) -> None:
        self._search_service = search_service
        self._search_options = _public_options(search_options)
        self._deployment_source = _safe_text(deployment_source or "local_index")
        self._bundle_id = _safe_text(bundle_id)

    @property
    def search_options(self) -> LocalSearchOptions:
        return self._search_options

    def status(self) -> dict[str, Any]:
        status = index_file_status(self._search_options.index, self._search_options.index_path)
        return {
            "schema_version": "eureka.public_alpha_status.v0",
            "task_id": TASK_ID,
            "status": "pass" if status.get("index_loaded") else "unavailable",
            "public_alpha_mode": True,
            "deployment_source": self._deployment_source,
            "staging_bundle_loaded": self._deployment_source == "staging_bundle",
            "bundle_id": self._bundle_id,
            "deployment_status": "local_only_not_launched",
            "read_only": True,
            "index_loaded": bool(status.get("index_loaded")),
            "index_document_count": int(status.get("index_document_count") or 0),
            "reviewed_record_count": int(status.get("reviewed_record_count") or 0),
            "artifact_verified_count": int(status.get("artifact_verified_count") or 0),
            "metadata_fallback": "none",
            "fallback_mode": "none",
            "live_metadata_enabled": False,
            "network_used": False,
            "public_live_fanout": False,
            "workbench_exposed": False,
            "downloads_enabled": False,
            "file_fetching_enabled": False,
            "wayback_replay_enabled": False,
            "extraction_enabled": False,
            "install_emulation_enabled": False,
            "marketplace_enabled": False,
            "public_mutation_enabled": False,
            "production_auth_enabled": False,
            "public_launch_readiness_claimed": False,
            "production_readiness_claimed": False,
            "canonical_statuses": list(CANONICAL_STATUSES),
            "routes": list(PUBLIC_ROUTES),
            "safe_public_actions": ["view_record"],
            "unsafe_actions_exposed": False,
            "no_mutation": _public_no_mutation(),
        }

    def search(self, query: str) -> dict[str, Any]:
        response = self._search_service.search(query, self._search_options)
        public_results = [_public_card(card) for card in response.get("results") or [] if isinstance(card, Mapping)]
        return {
            "schema_version": "eureka.public_alpha_search_response.v0",
            "task_id": TASK_ID,
            "public_alpha_mode": True,
            "deployment_source": self._deployment_source,
            "staging_bundle_loaded": self._deployment_source == "staging_bundle",
            "bundle_id": self._bundle_id,
            "read_only": True,
            "query": _public_query(response.get("query"), query),
            "normalized_query": str(response.get("normalized_query") or query or ""),
            "status": str(response.get("status") or "unknown"),
            "status_summary": _status_summary(response.get("status_summary"), public_results),
            "result_count": len(public_results),
            "results": public_results,
            "missing": _safe_list(response.get("missing")),
            "safe_next_action": _safe_text(response.get("safe_next_action")),
            "index_loaded": bool(response.get("index_loaded")),
            "index_result_count": int(response.get("index_result_count") or 0),
            "index_document_count": int(response.get("index_document_count") or 0),
            "reviewed_record_count": int(response.get("reviewed_record_count") or 0),
            "artifact_verified_count": int(response.get("artifact_verified_count") or 0),
            "fallback_used": False,
            "fallback_mode": "none",
            "metadata_fallback": "none",
            "live_metadata_enabled": False,
            "public_live_fanout": False,
            "workbench_exposed": False,
            "unsafe_actions_exposed": False,
            "no_mutation": _public_no_mutation(),
        }

    def record(self, record_id: str) -> dict[str, Any]:
        decoded = unquote(str(record_id or ""))
        try:
            index = load_index(self._search_options.index_path)
        except (OSError, json.JSONDecodeError):
            return _record_not_found(decoded, ["index unavailable"])
        errors = validate_index(index)
        if errors:
            return _record_not_found(decoded, errors)
        for document in index.get("documents") or []:
            if isinstance(document, Mapping) and str(document.get("id") or "") == decoded:
                card = _public_card(document_to_result_card(document))
                return {
                    "schema_version": "eureka.public_alpha_record.v0",
                    "task_id": TASK_ID,
                    "status": "pass",
                    "public_alpha_mode": True,
                    "deployment_source": self._deployment_source,
                    "staging_bundle_loaded": self._deployment_source == "staging_bundle",
                    "bundle_id": self._bundle_id,
                    "read_only": True,
                    "record": {
                        **card,
                        "provenance_summary": _public_provenance(document),
                    },
                    "workbench_exposed": False,
                    "live_metadata_enabled": False,
                    "public_mutation_enabled": False,
                    "no_mutation": _public_no_mutation(),
                }
        return _record_not_found(decoded, [])

    def smoke(self, queries: Sequence[str] = HARD_QUERY_SMOKE_SET) -> dict[str, Any]:
        searches = [self.search(query) for query in queries]
        return {
            "schema_version": "eureka.public_alpha_smoke.v0",
            "task_id": TASK_ID,
            "status": "pass",
            "public_alpha_mode": True,
            "deployment_source": self._deployment_source,
            "staging_bundle_loaded": self._deployment_source == "staging_bundle",
            "bundle_id": self._bundle_id,
            "read_only": True,
            "query_count": len(searches),
            "status_summary": _aggregate_status_summary(searches),
            "searches": searches,
            "status_payload": self.status(),
            "workbench_exposed": False,
            "live_metadata_enabled": False,
            "public_mutation_enabled": False,
            "no_mutation": _public_no_mutation(),
        }


def public_alpha_disabled_payload(path: str) -> dict[str, Any]:
    return {
        "schema_version": "eureka.public_alpha_disabled_workbench.v0",
        "task_id": TASK_ID,
        "status": "disabled",
        "path": path,
        "message": "Workbench is not exposed in public-alpha read-only mode.",
        "public_alpha_mode": True,
        "read_only": True,
        "mutation_performed": False,
        "workbench_exposed": False,
        "public_mutation_enabled": False,
    }


def public_alpha_error(path: str, message: str, *, status: str = "fail") -> dict[str, Any]:
    return {
        "schema_version": "eureka.public_alpha_error.v0",
        "task_id": TASK_ID,
        "status": status,
        "path": path,
        "message": message,
        "public_alpha_mode": True,
        "read_only": True,
        "mutation_performed": False,
        "public_mutation_enabled": False,
    }


def render_public_home(status: Mapping[str, Any]) -> str:
    return _page(
        "Eureka Public Alpha",
        [
            "<h1>Eureka Public Alpha</h1>",
            "<p>Local read-only public-alpha surface for evidence-first artifact search. Not deployed. Not launched.</p>",
            '<form action="/search" method="get">',
            '<label for="q">Search</label>',
            '<input id="q" name="q" value="manual for Sound Blaster CT1740">',
            '<button type="submit">Search</button>',
            "</form>",
            _status_block(status),
            "<nav><a href=\"/status\">Status</a> <a href=\"/about\">About</a> <a href=\"/method\">Method</a></nav>",
        ],
    )


def render_public_status(status: Mapping[str, Any]) -> str:
    return _page("Eureka Public Alpha Status", ["<h1>Status</h1>", _status_block(status)])


def render_public_about() -> str:
    return _page(
        "About Eureka",
        [
            "<h1>About Eureka</h1>",
            "<p>Eureka is an evidence-first temporal artifact resolver for hard-to-find software, documents, media, and source traces.</p>",
            "<p>Results can be reviewed, candidate, need, near_miss, policy_blocked, unavailable, or unknown.</p>",
            "<p>A reviewed metadata/source lead is not automatically a verified artifact. Artifact verification remains explicit.</p>",
            "<p>This local alpha does not offer downloads, emulation, public contribution intake, live fanout, or mutation.</p>",
        ],
    )


def render_public_method() -> str:
    return _page(
        "Eureka Method",
        [
            "<h1>Method</h1>",
            "<p>Public-alpha search reads a local reviewed/candidate/need index.</p>",
            "<p>Fallback and live metadata are disabled in public-alpha mode.</p>",
            "<p>Review is the truth boundary. Evidence hints, source hints, missing information, and safe next actions are shown.</p>",
            "<p>Public routes are read-only and expose only record-view links.</p>",
        ],
    )


def render_public_search(payload: Mapping[str, Any]) -> str:
    query = _safe_text(_public_query(payload.get("query"), "").get("raw"))
    rows = [
        "<h1>Search</h1>",
        '<form action="/search" method="get">',
        '<label for="q">Search</label>',
        f'<input id="q" name="q" value="{_e(query)}">',
        '<button type="submit">Search</button>',
        "</form>",
        f"<p><strong>Query:</strong> {_e(query)}</p>",
        f"<p><strong>Status:</strong> {_e(str(payload.get('status') or 'unknown'))}</p>",
        f"<p><strong>Fallback used:</strong> {_e(str(payload.get('fallback_used')).lower())}</p>",
        f"<p><strong>Fallback mode:</strong> {_e(str(payload.get('fallback_mode') or 'none'))}</p>",
    ]
    results = [item for item in payload.get("results") or [] if isinstance(item, Mapping)]
    if not results:
        rows.append("<p>No public results for this query.</p>")
    for result in results:
        rows.append(_result_article(result))
    return _page("Eureka Public Search", rows)


def render_public_record(payload: Mapping[str, Any]) -> str:
    if payload.get("status") == "not_found":
        return _page("Record Not Found", ["<h1>Record Not Found</h1>", "<p>No public record exists for that identifier.</p>"])
    record = payload.get("record") if isinstance(payload.get("record"), Mapping) else {}
    return _page("Eureka Public Record", ["<h1>Record</h1>", _result_article(record), _provenance_block(record)])


def render_public_disabled(payload: Mapping[str, Any]) -> str:
    return _page("Workbench Disabled", ["<h1>Workbench Disabled</h1>", f"<p>{_e(str(payload.get('message') or 'disabled'))}</p>"])


def sanitize_public_payload(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): sanitize_public_payload(item) for key, item in value.items() if _public_key_allowed(str(key))}
    if isinstance(value, list):
        return [sanitize_public_payload(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize_public_payload(item) for item in value]
    if isinstance(value, str):
        return _safe_text(value)
    return value


def render_public_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(sanitize_public_payload(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def _public_options(options: LocalSearchOptions) -> LocalSearchOptions:
    return LocalSearchOptions(
        metadata_fallback="none",
        limit=options.limit,
        show_evidence=options.show_evidence,
        show_debug=False,
        allow_live_metadata=False,
        metadata_timeout_seconds=options.metadata_timeout_seconds,
        metadata_budget=0,
        index="local",
        index_path=options.index_path,
    )


def _public_card(card: Mapping[str, Any]) -> dict[str, Any]:
    result_id = str(card.get("result_id") or card.get("index_document_id") or "")
    record_url = f"/record/{quote(result_id, safe='')}" if result_id else ""
    return {
        "result_id": result_id,
        "record_url": record_url,
        "status": _safe_status(card.get("status")),
        "title": _safe_text(card.get("title")),
        "summary": _safe_text(card.get("summary")),
        "source_hints": _safe_list(card.get("source_hints"), drop_urls=True),
        "evidence_hints": _safe_list(card.get("evidence_hints")),
        "missing": _safe_list(card.get("missing")),
        "safe_next_action": _safe_text(card.get("safe_next_action")),
        "non_verified_reason": _safe_text(card.get("non_verified_reason")),
        "review_state": _safe_text(card.get("review_state") or "unreviewed"),
        "reviewed_record_id": _safe_text(card.get("reviewed_record_id")),
        "artifact_verified": bool(card.get("artifact_verified") is True),
        "verified": bool(card.get("verified") is True),
        "accepted_truth": bool(card.get("accepted_truth") is True),
        "read_actions": [{"label": "View record", "href": record_url, "kind": "read"}] if record_url else [],
    }


def _public_provenance(document: Mapping[str, Any]) -> dict[str, Any]:
    provenance = document.get("provenance") if isinstance(document.get("provenance"), Mapping) else {}
    return {
        "source_family": _safe_text(document.get("source_family")),
        "source_kind": _safe_text(provenance.get("source_kind")),
        "record_state": _safe_text(document.get("record_state")),
        "review_state": _safe_text(document.get("review_state")),
        "artifact_verified": bool(document.get("artifact_verified") is True),
        "local_file_paths_redacted": True,
    }


def _record_not_found(record_id: str, errors: Sequence[str]) -> dict[str, Any]:
    return {
        "schema_version": "eureka.public_alpha_record.v0",
        "task_id": TASK_ID,
        "status": "not_found",
        "public_alpha_mode": True,
        "read_only": True,
        "record_id": _safe_text(record_id),
        "message": "No public record exists for that identifier.",
        "index_available": not errors,
        "workbench_exposed": False,
        "live_metadata_enabled": False,
        "public_mutation_enabled": False,
        "no_mutation": _public_no_mutation(),
    }


def _result_article(result: Mapping[str, Any]) -> str:
    actions = [
        f'<a href="{_e(str(action.get("href") or ""))}">{_e(str(action.get("label") or "View record"))}</a>'
        for action in result.get("read_actions") or []
        if isinstance(action, Mapping) and str(action.get("kind") or "") == "read"
    ]
    return "\n".join(
        [
            f'<article data-status="{_e(str(result.get("status") or "unknown"))}">',
            f"<h2>{_e(str(result.get('title') or 'Untitled'))}</h2>",
            f"<p><strong>Status:</strong> {_e(str(result.get('status') or 'unknown'))}</p>",
            f"<p><strong>Review state:</strong> {_e(str(result.get('review_state') or 'unreviewed'))}</p>",
            f"<p><strong>Artifact verified:</strong> {_e(str(result.get('artifact_verified')).lower())}</p>",
            f"<p>{_e(str(result.get('summary') or ''))}</p>",
            f"<p><strong>Source hints:</strong> {_e(', '.join(result.get('source_hints') or []) or 'none')}</p>",
            f"<p><strong>Evidence hints:</strong> {_e(', '.join(result.get('evidence_hints') or []) or 'none')}</p>",
            f"<p><strong>Missing:</strong> {_e(', '.join(result.get('missing') or []) or 'none')}</p>",
            f"<p><strong>Safe next action:</strong> {_e(str(result.get('safe_next_action') or ''))}</p>",
            f"<p><strong>Non-verified:</strong> {_e(str(result.get('non_verified_reason') or 'not applicable'))}</p>",
            f"<p>{' '.join(actions)}</p>" if actions else "",
            "</article>",
        ]
    )


def _provenance_block(record: Mapping[str, Any]) -> str:
    provenance = record.get("provenance_summary") if isinstance(record.get("provenance_summary"), Mapping) else {}
    return "\n".join(
        [
            "<section>",
            "<h2>Provenance Summary</h2>",
            f"<p><strong>Source family:</strong> {_e(str(provenance.get('source_family') or ''))}</p>",
            f"<p><strong>Source kind:</strong> {_e(str(provenance.get('source_kind') or ''))}</p>",
            f"<p><strong>Local file paths redacted:</strong> {_e(str(provenance.get('local_file_paths_redacted')).lower())}</p>",
            "</section>",
        ]
    )


def _status_block(status: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "<section>",
            f"<p><strong>Public alpha mode:</strong> {_e(str(status.get('public_alpha_mode')).lower())}</p>",
            f"<p><strong>Read only:</strong> {_e(str(status.get('read_only')).lower())}</p>",
            f"<p><strong>Index loaded:</strong> {_e(str(status.get('index_loaded')).lower())}</p>",
            f"<p><strong>Index documents:</strong> {_e(str(status.get('index_document_count') or 0))}</p>",
            f"<p><strong>Reviewed records:</strong> {_e(str(status.get('reviewed_record_count') or 0))}</p>",
            f"<p><strong>Artifact verified count:</strong> {_e(str(status.get('artifact_verified_count') or 0))}</p>",
            f"<p><strong>Metadata fallback:</strong> {_e(str(status.get('metadata_fallback') or 'none'))}</p>",
            f"<p><strong>Live metadata enabled:</strong> {_e(str(status.get('live_metadata_enabled')).lower())}</p>",
            f"<p><strong>Public live fanout:</strong> {_e(str(status.get('public_live_fanout')).lower())}</p>",
            f"<p><strong>Workbench exposed:</strong> {_e(str(status.get('workbench_exposed')).lower())}</p>",
            f"<p><strong>Downloads:</strong> {_e(str(status.get('downloads_enabled')).lower())}</p>",
            f"<p><strong>Public mutation:</strong> {_e(str(status.get('public_mutation_enabled')).lower())}</p>",
            f"<p><strong>Deployment:</strong> {_e(str(status.get('deployment_status') or 'local_only_not_launched'))}</p>",
            "</section>",
        ]
    )


def _page(title: str, rows: list[str]) -> str:
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{_e(title)}</title>",
            "<style>body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;line-height:1.45;margin:0;color:#14212a}main{max-width:920px;margin:auto;padding:1rem}form{display:flex;gap:.5rem;flex-wrap:wrap;margin:1rem 0}input{min-width:18rem;max-width:100%;padding:.5rem}button{padding:.5rem .8rem}article,section{border-top:1px solid #ccd6dc;padding:.8rem 0}a{color:#075985}</style>",
            "</head>",
            "<body>",
            "<main>",
            *rows,
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _public_query(value: Any, fallback: str) -> dict[str, str]:
    if isinstance(value, Mapping):
        return {
            "raw": _safe_text(value.get("raw") or fallback),
            "normalized": _safe_text(value.get("normalized") or fallback),
        }
    return {"raw": _safe_text(fallback), "normalized": _safe_text(fallback)}


def _status_summary(value: Any, results: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    if isinstance(value, Mapping):
        return {status: int(value.get(status) or 0) for status in CANONICAL_STATUSES}
    counts = {status: 0 for status in CANONICAL_STATUSES}
    for result in results:
        status = _safe_status(result.get("status"))
        counts[status] = counts.get(status, 0) + 1
    return counts


def _aggregate_status_summary(searches: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = {status: 0 for status in CANONICAL_STATUSES}
    for search in searches:
        for status, count in (search.get("status_summary") or {}).items():
            counts[str(status)] = counts.get(str(status), 0) + int(count or 0)
    return {key: counts[key] for key in CANONICAL_STATUSES}


def _safe_status(value: Any) -> str:
    status = str(value or "unknown")
    return status if status in CANONICAL_STATUSES else "unknown"


def _safe_list(value: Any, *, drop_urls: bool = False) -> list[str]:
    if not isinstance(value, (list, tuple, set)):
        return []
    result = []
    for item in value:
        text = _safe_text(item)
        if not text:
            continue
        if drop_urls and (text.startswith("http://") or text.startswith("https://")):
            continue
        result.append(text)
    return result


def _safe_text(value: Any) -> str:
    text = str(value or "")
    for marker in FORBIDDEN_PUBLIC_TEXT:
        text = text.replace(marker, "[redacted]")
    text = text.replace("\\", "/")
    parts = [part for part in text.split("/") if part not in {"Users", "Jules", "Projects", "Eureka", "eureka"}]
    return "/".join(parts)[:2000]


def _public_key_allowed(key: str) -> bool:
    blocked = {
        "index_path",
        "ledger_path",
        "records_path",
        "debug",
        "renderer_outputs",
        "run",
        "source_observations",
        "token",
        "workbench_token",
    }
    return key not in blocked


def _public_no_mutation() -> dict[str, bool]:
    return {
        "reviewed_records_mutated": False,
        "review_ledgers_mutated": False,
        "local_index_mutated": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "official_reviewed_records_mutated": False,
        "gate_counts_mutated": False,
        "canon_mutated": False,
        "release_mutated": False,
        "queue_current_mutated": False,
        "source_fixtures_mutated": False,
        "truth_promotion_performed": False,
    }


def _e(value: str) -> str:
    return escape(str(value), quote=True)
