from __future__ import annotations

import ast
from io import BytesIO
from pathlib import Path
from urllib.parse import quote
import unittest

from runtime.gateway.public_api import PublicApiResponse
from surfaces.web.server import WorkbenchWsgiApp, render_resolution_workspace_page


SURFACE_WEB_ROOT = Path(__file__).resolve().parents[1]


class FakeResolutionJobsPublicApi:
    def __init__(self) -> None:
        self.submit_target_refs: list[str] = []
        self.read_job_ids: list[str] = []

    def submit_resolution_job(self, request) -> PublicApiResponse:
        self.submit_target_refs.append(request.target_ref)
        return PublicApiResponse(
            status_code=202,
            body={
                "job_id": "job-fake-0001",
                "status": "accepted",
                "target_ref": request.target_ref,
                "requested_outputs": [],
                "notices": [],
            },
        )

    def read_resolution_job(self, job_id: str) -> PublicApiResponse:
        self.read_job_ids.append(job_id)
        return PublicApiResponse(
            status_code=200,
            body={
                "job_id": job_id,
                "status": "completed",
                "target_ref": "fixture:software/synthetic-demo-app@1.0.0",
                "requested_outputs": [],
                "notices": [],
                "result": {
                    "notices": [],
                    "primary_object": {
                        "id": "obj.synthetic-demo-app",
                        "kind": "software",
                        "label": "Synthetic Demo App",
                    },
                },
            },
        )


class WorkbenchServerTestCase(unittest.TestCase):
    def test_server_renders_workspace_via_public_submit_and_read_boundary(self) -> None:
        public_api = FakeResolutionJobsPublicApi()
        html = render_resolution_workspace_page(
            public_api,
            "fixture:software/synthetic-demo-app@1.0.0",
        )

        self.assertEqual(
            public_api.submit_target_refs,
            ["fixture:software/synthetic-demo-app@1.0.0"],
        )
        self.assertEqual(public_api.read_job_ids, ["job-fake-0001"])
        self.assertIn("Synthetic Demo App", html)

    def test_wsgi_app_handles_query_driven_get_request(self) -> None:
        public_api = FakeResolutionJobsPublicApi()
        app = WorkbenchWsgiApp(
            public_api,
            default_target_ref="fixture:software/synthetic-demo-app@1.0.0",
        )

        captured: dict[str, object] = {}

        def start_response(status: str, headers: list[tuple[str, str]]) -> None:
            captured["status"] = status
            captured["headers"] = headers

        body = b"".join(
            app(
                {
                    "REQUEST_METHOD": "GET",
                    "PATH_INFO": "/",
                    "QUERY_STRING": f"target_ref={quote('fixture:software/missing-demo-app@0.0.1')}",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")

        self.assertEqual(captured["status"], "200 OK")
        self.assertEqual(
            public_api.submit_target_refs,
            ["fixture:software/missing-demo-app@0.0.1"],
        )
        self.assertIn("fixture:software/synthetic-demo-app@1.0.0", body)

    def test_web_surface_modules_do_not_import_engine_or_connector_internals(self) -> None:
        for path in SURFACE_WEB_ROOT.rglob("*.py"):
            if path.name.startswith("test_"):
                continue

            module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(module):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertFalse(
                            alias.name.startswith("runtime.engine"),
                            f"{path} imports engine internals: {alias.name}",
                        )
                        self.assertFalse(
                            alias.name.startswith("runtime.connectors"),
                            f"{path} imports connector internals: {alias.name}",
                        )
                if isinstance(node, ast.ImportFrom) and node.module is not None:
                    self.assertFalse(
                        node.module.startswith("runtime.engine"),
                        f"{path} imports engine internals: {node.module}",
                    )
                    self.assertFalse(
                        node.module.startswith("runtime.connectors"),
                        f"{path} imports connector internals: {node.module}",
                    )
