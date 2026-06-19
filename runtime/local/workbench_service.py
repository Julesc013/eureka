"""Local/private Workbench adapter for the local search service."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import quote_plus

from runtime.local.review_materialization import (
    DEFAULT_REVIEW_LEDGER_PATH,
    DEFAULT_REVIEWED_RECORDS_PATH,
    accept_candidate,
    list_candidates,
    review_stats,
)
from runtime.local.search_index import build_local_demo_index, index_file_status, validate_index, write_index
from runtime.local.local_search import LocalSearchOptions, LocalSearchService


TASK_ID = "WORKBENCH-OPERATOR-ROUTES-00"


@dataclass(frozen=True)
class WorkbenchOptions:
    enabled: bool = False
    token: str = ""
    ledger_path: str = DEFAULT_REVIEW_LEDGER_PATH
    records_path: str = DEFAULT_REVIEWED_RECORDS_PATH
    reviewer: str = "local_workbench"
    rebuild_index: bool = True


class WorkbenchService:
    """Thin local Workbench wrapper over search, index, and review primitives."""

    def __init__(
        self,
        *,
        search_service: LocalSearchService,
        search_options: LocalSearchOptions,
        workbench_options: WorkbenchOptions,
    ) -> None:
        self._search_service = search_service
        self._search_options = search_options
        self._workbench_options = workbench_options

    @property
    def options(self) -> WorkbenchOptions:
        return self._workbench_options

    @property
    def search_options(self) -> LocalSearchOptions:
        return self._search_options

    def status(self) -> dict[str, Any]:
        index_status = index_file_status(self._search_options.index, self._search_options.index_path)
        stats = review_stats(self._workbench_options.ledger_path, self._workbench_options.records_path)
        return {
            "schema_version": "eureka.local_workbench_status.v0",
            "task_id": TASK_ID,
            "status": "pass" if self._workbench_options.enabled else "disabled",
            "enabled": self._workbench_options.enabled,
            "service": "local_workbench_p0",
            "local_private": True,
            "token_required": bool(self._workbench_options.token),
            "production_auth": False,
            "public_workbench": False,
            "public_mutation_enabled": False,
            "live_network_enabled": False,
            "downloads_enabled": False,
            "artifact_verified_created": 0,
            "artifact_verified": False,
            "accepted_truth_created": False,
            "reviewer": self._workbench_options.reviewer,
            "ledger_path": self._workbench_options.ledger_path,
            "records_path": self._workbench_options.records_path,
            "rebuild_index_after_accept": self._workbench_options.rebuild_index,
            "routes": [
                "/workbench",
                "/workbench/status",
                "/workbench/candidates?q=",
                "/workbench/review?q=",
                "/workbench/api/status",
                "/workbench/api/candidates?q=",
                "/workbench/api/review/accept",
            ],
            **index_status,
            "review_event_count": int(stats.get("review_event_count") or 0),
            "local_reviewed_record_count": int(stats.get("reviewed_record_count") or 0),
            "review_artifact_verified_count": int(stats.get("artifact_verified_count") or 0),
            "safety": {
                "local_only": True,
                "requires_explicit_enable": True,
                "token_gate": bool(self._workbench_options.token),
                "writes_local_generated_artifacts_only": True,
                "public_index_mutated": False,
                "master_index_mutated": False,
                "official_reviewed_records_mutated": False,
                "gate_counts_mutated": False,
                "canon_mutated": False,
                "release_mutated": False,
                "queue_current_mutated": False,
                "source_fixtures_mutated": False,
            },
        }

    def candidates(self, query: str, *, limit: int = 10) -> dict[str, Any]:
        payload = list_candidates(self._search_options.index_path, query, limit=limit)
        return {
            **payload,
            "task_id": TASK_ID,
            "workbench_enabled": self._workbench_options.enabled,
            "token_required": bool(self._workbench_options.token),
            "local_private": True,
            "artifact_verified": False,
        }

    def accept(
        self,
        *,
        query: str,
        reason: str,
        candidate_id: str = "",
        reviewer: str = "",
    ) -> dict[str, Any]:
        if not str(query or "").strip():
            raise ValueError("query is required")
        if not str(reason or "").strip():
            raise ValueError("reason is required")
        accept_result = accept_candidate(
            index_path=self._search_options.index_path,
            query=query,
            ledger_path=self._workbench_options.ledger_path,
            records_path=self._workbench_options.records_path,
            reviewer=reviewer or self._workbench_options.reviewer,
            reason=reason,
            candidate_id=candidate_id or None,
        )
        rebuild = self._rebuild_index() if self._workbench_options.rebuild_index else {
            "index_rebuilt": False,
            "index_errors": [],
            "index_path": self._search_options.index_path,
        }
        preview = self._search_service.search(query, self._search_options)
        return {
            "schema_version": "eureka.local_workbench_accept_result.v0",
            "task_id": TASK_ID,
            "status": "pass",
            "query": query,
            "candidate_id": accept_result.get("candidate_id"),
            "review_event_id": accept_result.get("review_event_id"),
            "reviewed_record_id": accept_result.get("reviewed_record_id"),
            "event_written": bool(accept_result.get("event_written")),
            "record_written": bool(accept_result.get("record_written")),
            "artifact_verified": False,
            "accepted_truth_created": False,
            "index_rebuilt": bool(rebuild.get("index_rebuilt")),
            "index_path": rebuild.get("index_path"),
            "index_errors": list(rebuild.get("index_errors") or []),
            "search_preview": preview,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "official_reviewed_records_mutated": False,
            "gate_counts_mutated": False,
            "canon_mutated": False,
            "release_mutated": False,
            "queue_current_mutated": False,
            "source_fixtures_mutated": False,
            "limitations": [
                "local/private Workbench P0",
                "writes only local generated review/index artifacts",
                "does not create verified artifact truth",
            ],
        }

    def _rebuild_index(self) -> dict[str, Any]:
        index = build_local_demo_index(reviewed_records_path=self._workbench_options.records_path)
        errors = validate_index(index)
        if errors:
            return {
                "index_rebuilt": False,
                "index_path": self._search_options.index_path,
                "index_errors": list(errors),
            }
        write_index(self._search_options.index_path, index)
        return {
            "index_rebuilt": True,
            "index_path": self._search_options.index_path,
            "index_errors": [],
            "index_document_count": int(index.get("document_count") or 0),
            "reviewed_record_count": int(index.get("reviewed_record_count") or 0),
            "artifact_verified_count": int(index.get("artifact_verified_count") or 0),
        }


def disabled_payload(path: str) -> dict[str, Any]:
    return {
        "schema_version": "eureka.local_workbench_disabled.v0",
        "task_id": TASK_ID,
        "status": "disabled",
        "path": path,
        "message": "Local Workbench routes require --enable-workbench.",
        "enabled": False,
        "public_mutation_enabled": False,
        "local_private": True,
    }


def unauthorized_payload(path: str) -> dict[str, Any]:
    return {
        "schema_version": "eureka.local_workbench_unauthorized.v0",
        "task_id": TASK_ID,
        "status": "unauthorized",
        "path": path,
        "message": "Workbench token is missing or invalid.",
        "mutation_performed": False,
        "public_mutation_enabled": False,
        "artifact_verified": False,
    }


def error_payload(path: str, error: str) -> dict[str, Any]:
    return {
        "schema_version": "eureka.local_workbench_error.v0",
        "task_id": TASK_ID,
        "status": "fail",
        "path": path,
        "error": error,
        "mutation_performed": False,
        "artifact_verified": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def render_workbench_home(status: Mapping[str, Any], *, token: str = "") -> str:
    token_input = _token_input(token)
    return _page(
        "Eureka Local Workbench",
        [
            "<h1>Eureka Local Workbench</h1>",
            "<p>Local/private P0 operator surface. Writes only local generated review/index artifacts.</p>",
            _status_block(status),
            '<form action="/workbench/candidates" method="get">',
            '<label for="q">Query</label>',
            '<input id="q" name="q" value="manual for Sound Blaster CT1740">',
            token_input,
            '<button type="submit">List candidates</button>',
            "</form>",
            "<ul>",
            f'<li><a href="/workbench/status{_token_query(token)}">Workbench status</a></li>',
            f'<li><a href="/workbench/review?q=manual%20for%20Sound%20Blaster%20CT1740{_token_amp(token)}">Review Sound Blaster manual</a></li>',
            "</ul>",
        ],
    )


def render_workbench_status(status: Mapping[str, Any]) -> str:
    return _page("Eureka Workbench Status", ["<h1>Workbench Status</h1>", _status_block(status)])


def render_workbench_candidates(payload: Mapping[str, Any], *, token: str = "") -> str:
    query = str(payload.get("query") or "")
    rows: list[str] = [
        "<h1>Workbench Candidates</h1>",
        f"<p><strong>Query:</strong> {_e(query)}</p>",
        f"<p><strong>Candidate count:</strong> {_e(str(payload.get('candidate_count') or 0))}</p>",
        '<form action="/workbench/candidates" method="get">',
        '<label for="q">Query</label>',
        f'<input id="q" name="q" value="{_e(query)}">',
        _token_input(token),
        '<button type="submit">Refresh candidates</button>',
        "</form>",
    ]
    candidates = [item for item in payload.get("candidates") or [] if isinstance(item, Mapping)]
    if not candidates:
        rows.append("<p>No candidates available for this query.</p>")
    for index, candidate in enumerate(candidates, start=1):
        review_href = (
            f"/workbench/review?q={quote_plus(query)}"
            f"&candidate_id={quote_plus(str(candidate.get('candidate_id') or ''))}"
            f"{_token_amp(token)}"
        )
        rows.extend(
            [
                "<article>",
                f"<h2>{index}. {_e(str(candidate.get('title') or 'Untitled'))}</h2>",
                f"<p><strong>Status:</strong> {_e(str(candidate.get('status') or 'unknown'))}</p>",
                f"<p><strong>Candidate:</strong> {_e(str(candidate.get('candidate_id') or ''))}</p>",
                f"<p><strong>Review state:</strong> {_e(str(candidate.get('review_state') or 'unreviewed'))}</p>",
                f"<p><strong>Artifact verified:</strong> {_e(str(candidate.get('artifact_verified')).lower())}</p>",
                f"<p><strong>Evidence:</strong> {_e(', '.join(candidate.get('evidence_hints') or []) or 'none')}</p>",
                f'<p><a href="{_e(review_href)}">Review candidate</a></p>',
                "</article>",
            ]
        )
    return _page("Eureka Workbench Candidates", rows)


def render_workbench_review(payload: Mapping[str, Any], *, token: str = "", candidate_id: str = "") -> str:
    query = str(payload.get("query") or "")
    rows: list[str] = [
        "<h1>Workbench Review</h1>",
        f"<p><strong>Query:</strong> {_e(query)}</p>",
        f"<p><strong>Candidate count:</strong> {_e(str(payload.get('candidate_count') or 0))}</p>",
        '<form action="/workbench/api/review/accept" method="post">',
        '<input type="hidden" name="query" value="' + _e(query) + '">',
        '<input type="hidden" name="candidate_id" value="' + _e(candidate_id) + '">',
        _token_input(token),
        '<label for="reason">Reason</label>',
        '<input id="reason" name="reason" value="Workbench P0 local accept demo">',
        '<button type="submit">Accept candidate</button>',
        "</form>",
    ]
    for candidate in [item for item in payload.get("candidates") or [] if isinstance(item, Mapping)]:
        rows.extend(
            [
                "<article>",
                f"<h2>{_e(str(candidate.get('title') or 'Untitled'))}</h2>",
                f"<p><strong>Candidate:</strong> {_e(str(candidate.get('candidate_id') or ''))}</p>",
                f"<p><strong>Status:</strong> {_e(str(candidate.get('status') or 'unknown'))}</p>",
                f"<p><strong>Artifact verified:</strong> {_e(str(candidate.get('artifact_verified')).lower())}</p>",
                "</article>",
            ]
        )
    return _page("Eureka Workbench Review", rows)


def render_disabled(payload: Mapping[str, Any]) -> str:
    return _page("Eureka Workbench Disabled", ["<h1>Workbench Disabled</h1>", f"<p>{_e(str(payload.get('message') or 'disabled'))}</p>"])


def render_unauthorized(payload: Mapping[str, Any]) -> str:
    return _page("Eureka Workbench Unauthorized", ["<h1>Workbench Unauthorized</h1>", f"<p>{_e(str(payload.get('message') or 'unauthorized'))}</p>"])


def _status_block(status: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "<section>",
            f"<p><strong>Enabled:</strong> {_e(str(status.get('enabled')).lower())}</p>",
            f"<p><strong>Token required:</strong> {_e(str(status.get('token_required')).lower())}</p>",
            f"<p><strong>Index loaded:</strong> {_e(str(status.get('index_loaded')).lower())}</p>",
            f"<p><strong>Index path:</strong> {_e(str(status.get('index_path') or ''))}</p>",
            f"<p><strong>Indexed documents:</strong> {_e(str(status.get('index_document_count') or 0))}</p>",
            f"<p><strong>Reviewed records:</strong> {_e(str(status.get('reviewed_record_count') or 0))}</p>",
            f"<p><strong>Local reviewed records:</strong> {_e(str(status.get('local_reviewed_record_count') or 0))}</p>",
            f"<p><strong>Artifact verified count:</strong> {_e(str(status.get('artifact_verified_count') or 0))}</p>",
            f"<p><strong>Ledger:</strong> {_e(str(status.get('ledger_path') or ''))}</p>",
            f"<p><strong>Records:</strong> {_e(str(status.get('records_path') or ''))}</p>",
            "<p>Production auth: false. Public Workbench: false. Verified artifact truth created: false.</p>",
            "</section>",
        ]
    )


def _page(title: str, rows: list[str]) -> str:
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            f"<head><meta charset=\"utf-8\"><title>{_e(title)}</title></head>",
            "<body>",
            "<main>",
            *rows,
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _token_input(token: str) -> str:
    if not token:
        return ""
    return f'<input type="hidden" name="token" value="{_e(token)}">'


def _token_query(token: str) -> str:
    return f"?token={quote_plus(token)}" if token else ""


def _token_amp(token: str) -> str:
    return f"&token={quote_plus(token)}" if token else ""


def _e(value: str) -> str:
    return escape(str(value), quote=True)
