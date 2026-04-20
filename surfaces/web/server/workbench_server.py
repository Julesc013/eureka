from __future__ import annotations

from html import escape
from typing import Callable
from urllib.parse import parse_qs

from runtime.gateway.public_api import ResolutionJobsPublicApi, SubmitResolutionJobRequest, resolution_job_envelope_to_workbench_session
from surfaces.web.workbench import render_resolution_workspace_html


def render_resolution_workspace_page(
    public_api: ResolutionJobsPublicApi,
    target_ref: str,
    *,
    session_id: str = "session.web-workbench",
) -> str:
    submit_response = public_api.submit_resolution_job(
        SubmitResolutionJobRequest.from_parts(target_ref),
    )
    job_id = submit_response.body["job_id"]
    read_response = public_api.read_resolution_job(job_id)

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
    return render_resolution_workspace_html(workbench_session)


class WorkbenchWsgiApp:
    def __init__(
        self,
        public_api: ResolutionJobsPublicApi,
        *,
        default_target_ref: str,
        session_id: str = "session.web-workbench",
    ) -> None:
        self._public_api = public_api
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
        if path != "/":
            return self._respond(
                start_response,
                status="404 Not Found",
                body=_render_error_page(
                    title="Eureka Compatibility Workbench",
                    heading="Page Not Found",
                    message="This bootstrap workbench serves a single compatibility-first page at '/'.",
                ),
            )

        target_ref = self._resolve_target_ref(str(environ.get("QUERY_STRING", "")))
        page = render_resolution_workspace_page(
            self._public_api,
            target_ref,
            session_id=self._session_id,
        )
        return self._respond(start_response, status="200 OK", body=page)

    def _resolve_target_ref(self, query_string: str) -> str:
        query = parse_qs(query_string, keep_blank_values=False)
        raw_target_ref = query.get("target_ref", [self._default_target_ref])[0].strip()
        return raw_target_ref or self._default_target_ref

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
