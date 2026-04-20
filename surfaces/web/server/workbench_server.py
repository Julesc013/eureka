from __future__ import annotations

import json
from html import escape
from typing import Callable
from urllib.parse import parse_qs

from runtime.gateway.public_api import (
    ResolutionActionRequest,
    ResolutionActionsPublicApi,
    ResolutionJobsPublicApi,
    SearchCatalogRequest,
    SearchPublicApi,
    SubmitResolutionJobRequest,
    resolution_actions_envelope_to_view_model,
    resolution_job_envelope_to_workbench_session,
    search_response_envelope_to_search_results_view_model,
)
from surfaces.web.workbench import render_resolution_workspace_html, render_search_results_html


def render_resolution_workspace_page(
    resolution_public_api: ResolutionJobsPublicApi,
    target_ref: str,
    *,
    actions_public_api: ResolutionActionsPublicApi | None = None,
    session_id: str = "session.web-workbench",
) -> str:
    submit_response = resolution_public_api.submit_resolution_job(
        SubmitResolutionJobRequest.from_parts(target_ref),
    )
    job_id = submit_response.body["job_id"]
    read_response = resolution_public_api.read_resolution_job(job_id)

    if read_response.status_code != 200:
        return _render_error_page(
            title="Eureka Compatibility Workbench",
            heading="Resolution Job Not Found",
            message=read_response.body.get("message", "No job state was available for the requested work."),
        )

    workbench_session = resolution_job_envelope_to_workbench_session(
        read_response.body,
        session_id=session_id,
    )
    resolution_actions = None
    if actions_public_api is not None:
        resolution_actions = resolution_actions_envelope_to_view_model(
            actions_public_api.list_resolution_actions(ResolutionActionRequest.from_parts(target_ref)).body
        )
    return render_resolution_workspace_html(
        workbench_session,
        resolution_actions=resolution_actions,
    )


class WorkbenchWsgiApp:
    def __init__(
        self,
        resolution_public_api: ResolutionJobsPublicApi,
        *,
        actions_public_api: ResolutionActionsPublicApi | None = None,
        search_public_api: SearchPublicApi,
        default_target_ref: str,
        session_id: str = "session.web-workbench",
    ) -> None:
        self._resolution_public_api = resolution_public_api
        self._actions_public_api = actions_public_api
        self._search_public_api = search_public_api
        self._default_target_ref = default_target_ref
        self._session_id = session_id

    def __call__(
        self,
        environ: dict[str, object],
        start_response: Callable[[str, list[tuple[str, str]]], object],
    ) -> list[bytes]:
        method = str(environ.get("REQUEST_METHOD", "GET")).upper()
        if method != "GET":
            return self._respond(
                start_response,
                status="405 Method Not Allowed",
                body=_render_error_page(
                    title="Eureka Compatibility Workbench",
                    heading="Method Not Allowed",
                    message="This bootstrap workbench accepts GET requests only.",
                ),
                extra_headers=[("Allow", "GET")],
            )

        path = str(environ.get("PATH_INFO") or "/")
        if path not in {"/", "/search", "/actions/export-resolution-manifest"}:
            return self._respond(
                start_response,
                status="404 Not Found",
                body=_render_error_page(
                    title="Eureka Compatibility Workbench",
                    heading="Page Not Found",
                    message="This bootstrap workbench serves compatibility-first pages at '/', '/search', and '/actions/export-resolution-manifest'.",
                ),
            )

        query_string = str(environ.get("QUERY_STRING", ""))
        if path == "/":
            target_ref = self._resolve_target_ref(query_string)
            page = render_resolution_workspace_page(
                self._resolution_public_api,
                target_ref,
                actions_public_api=self._actions_public_api,
                session_id=self._session_id,
            )
            return self._respond(start_response, status="200 OK", body=page)
        if path == "/search":
            query = self._resolve_search_query(query_string)
            page = render_search_results_page(
                self._search_public_api,
                query,
            )
            return self._respond(start_response, status="200 OK", body=page)

        target_ref = self._resolve_target_ref(query_string)
        if self._actions_public_api is None:
            return self._respond(
                start_response,
                status="404 Not Found",
                body=_render_error_page(
                    title="Eureka Compatibility Workbench",
                    heading="Manifest Export Unavailable",
                    message="This bootstrap workbench was not configured with a public action boundary.",
                ),
            )

        export_response = self._actions_public_api.export_resolution_manifest(
            ResolutionActionRequest.from_parts(target_ref),
        )
        return self._respond_json(
            start_response,
            status="200 OK" if export_response.status_code == 200 else "404 Not Found",
            payload=export_response.body,
        )

    def _resolve_target_ref(self, query_string: str) -> str:
        query = parse_qs(query_string, keep_blank_values=False)
        raw_target_ref = query.get("target_ref", [self._default_target_ref])[0].strip()
        return raw_target_ref or self._default_target_ref

    def _resolve_search_query(self, query_string: str) -> str:
        query = parse_qs(query_string, keep_blank_values=False)
        raw_query = query.get("q", [""])[0].strip()
        return raw_query

    def _respond(
        self,
        start_response: Callable[[str, list[tuple[str, str]]], object],
        *,
        status: str,
        body: str,
        extra_headers: list[tuple[str, str]] | None = None,
    ) -> list[bytes]:
        payload = body.encode("utf-8")
        headers = [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(payload))),
        ]
        if extra_headers:
            headers.extend(extra_headers)
        start_response(status, headers)
        return [payload]

    def _respond_json(
        self,
        start_response: Callable[[str, list[tuple[str, str]]], object],
        *,
        status: str,
        payload: dict[str, object],
    ) -> list[bytes]:
        body = json.dumps(payload, indent=2, sort_keys=True)
        encoded = f"{body}\n".encode("utf-8")
        headers = [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(encoded))),
        ]
        start_response(status, headers)
        return [encoded]


def _render_error_page(*, title: str, heading: str, message: str) -> str:
    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "  <head>\n"
        "    <meta charset=\"utf-8\">\n"
        f"    <title>{escape(title)}</title>\n"
        "  </head>\n"
        "  <body>\n"
        f"    <h1>{escape(heading)}</h1>\n"
        f"    <p>{escape(message)}</p>\n"
        "  </body>\n"
        "</html>\n"
    )


def render_search_results_page(
    public_api: SearchPublicApi,
    query: str,
) -> str:
    normalized_query = query.strip()
    if not normalized_query:
        return render_search_results_html(
            {
                "query": "",
                "result_count": 0,
                "results": [],
            }
        )

    response = public_api.search_records(SearchCatalogRequest.from_parts(normalized_query))
    search_results = search_response_envelope_to_search_results_view_model(response.body)
    return render_search_results_html(search_results)
