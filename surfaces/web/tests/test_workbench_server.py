from __future__ import annotations

import ast
import json
from io import BytesIO
from pathlib import Path
import zipfile
from urllib.parse import quote
import unittest

from runtime.gateway.public_api import PublicApiResponse, PublicArtifactResponse
from surfaces.web.server import WorkbenchWsgiApp, render_resolution_workspace_page, render_search_results_page


SURFACE_WEB_ROOT = Path(__file__).resolve().parents[1]


class FakeResolutionJobsPublicApi:
    def __init__(self) -> None:
        self.submit_target_refs: list[str] = []
        self.read_job_ids: list[str] = []
        self._jobs: dict[str, str] = {}

    def submit_resolution_job(self, request) -> PublicApiResponse:
        self.submit_target_refs.append(request.target_ref)
        job_id = f"job-fake-{len(self.submit_target_refs):04d}"
        self._jobs[job_id] = request.target_ref
        return PublicApiResponse(
            status_code=202,
            body={
                "job_id": job_id,
                "status": "accepted",
                "target_ref": request.target_ref,
                "requested_outputs": [],
                "notices": [],
            },
        )

    def read_resolution_job(self, job_id: str) -> PublicApiResponse:
        self.read_job_ids.append(job_id)
        target_ref = self._jobs[job_id]
        if target_ref == "fixture:software/missing-demo-app@0.0.1":
            return PublicApiResponse(
                status_code=200,
                body={
                    "job_id": job_id,
                    "status": "blocked",
                    "target_ref": target_ref,
                    "requested_outputs": [],
                    "notices": [
                        {
                            "code": "fixture_target_not_found",
                            "severity": "warning",
                            "message": f"No governed synthetic record matched target_ref '{target_ref}'.",
                        }
                    ],
                },
            )

        return PublicApiResponse(
            status_code=200,
            body={
                "job_id": job_id,
                "status": "completed",
                "target_ref": target_ref,
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


class FakeResolutionActionsPublicApi:
    def __init__(self) -> None:
        self.list_target_refs: list[str] = []
        self.export_target_refs: list[str] = []

    def list_resolution_actions(self, request) -> PublicApiResponse:
        self.list_target_refs.append(request.target_ref)
        if request.target_ref == "fixture:software/missing-demo-app@0.0.1":
            return PublicApiResponse(
                status_code=200,
                body={
                    "target_ref": request.target_ref,
                    "actions": [
                        {
                            "action_id": "export_resolution_manifest",
                            "label": "Export resolution manifest",
                            "availability": "unavailable",
                        },
                        {
                            "action_id": "export_resolution_bundle",
                            "label": "Export resolution bundle",
                            "availability": "unavailable",
                        }
                    ],
                    "notices": [
                        {
                            "code": "resolution_manifest_not_available",
                            "severity": "warning",
                            "message": f"No resolved synthetic record matched target_ref '{request.target_ref}'.",
                        },
                        {
                            "code": "resolution_bundle_not_available",
                            "severity": "warning",
                            "message": f"No resolved synthetic record matched target_ref '{request.target_ref}'.",
                        }
                    ],
                },
            )
        return PublicApiResponse(
            status_code=200,
            body={
                "target_ref": request.target_ref,
                "actions": [
                    {
                        "action_id": "export_resolution_manifest",
                        "label": "Export resolution manifest",
                        "availability": "available",
                        "href": f"/actions/export-resolution-manifest?target_ref={quote(request.target_ref, safe='')}",
                    },
                    {
                        "action_id": "export_resolution_bundle",
                        "label": "Export resolution bundle",
                        "availability": "available",
                        "href": f"/actions/export-resolution-bundle?target_ref={quote(request.target_ref, safe='')}",
                    }
                ],
                "notices": [],
            },
        )

    def export_resolution_manifest(self, request) -> PublicApiResponse:
        self.export_target_refs.append(request.target_ref)
        if request.target_ref == "fixture:software/missing-demo-app@0.0.1":
            return PublicApiResponse(
                status_code=404,
                body={
                    "action_id": "export_resolution_manifest",
                    "status": "blocked",
                    "target_ref": request.target_ref,
                    "code": "resolution_manifest_not_available",
                    "message": f"No resolved synthetic record matched target_ref '{request.target_ref}'.",
                },
            )
        return PublicApiResponse(
            status_code=200,
            body={
                "manifest_kind": "eureka.resolution_manifest",
                "manifest_version": "0.1.0-draft",
                "target_ref": request.target_ref,
                "primary_object": {
                    "id": "obj.synthetic-demo-app",
                    "kind": "software",
                    "label": "Synthetic Demo App",
                },
                "notices": [],
            },
        )

    def export_resolution_bundle(self, request) -> PublicArtifactResponse:
        self.export_target_refs.append(request.target_ref)
        if request.target_ref == "fixture:software/missing-demo-app@0.0.1":
            return PublicArtifactResponse(
                status_code=404,
                content_type="application/json; charset=utf-8",
                payload=(
                    json.dumps(
                        {
                            "action_id": "export_resolution_bundle",
                            "status": "blocked",
                            "target_ref": request.target_ref,
                            "code": "resolution_bundle_not_available",
                            "message": f"No resolved synthetic record matched target_ref '{request.target_ref}'.",
                        },
                        sort_keys=True,
                    )
                    + "\n"
                ).encode("utf-8"),
            )
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, mode="w") as archive:
            archive.writestr("bundle.json", json.dumps({"target_ref": request.target_ref}, sort_keys=True))
            archive.writestr("manifest.json", json.dumps({"manifest_kind": "eureka.resolution_manifest"}, sort_keys=True))
        return PublicArtifactResponse(
            status_code=200,
            content_type="application/zip",
            filename="eureka-resolution-bundle-fixture-software-synthetic-demo-app-1.0.0.zip",
            payload=buffer.getvalue(),
        )


class FakeSearchPublicApi:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def search_records(self, request) -> PublicApiResponse:
        self.queries.append(request.query)
        if request.query == "synthetic":
            return PublicApiResponse(
                status_code=200,
                body={
                    "query": "synthetic",
                    "result_count": 2,
                    "results": [
                        {
                            "target_ref": "fixture:software/synthetic-demo-app@1.0.0",
                            "object": {
                                "id": "obj.synthetic-demo-app",
                                "kind": "software",
                                "label": "Synthetic Demo App",
                            },
                        },
                        {
                            "target_ref": "fixture:software/synthetic-demo-suite@2.0.0",
                            "object": {
                                "id": "obj.synthetic-demo-suite",
                                "kind": "software",
                                "label": "Synthetic Demo Suite",
                            },
                        },
                    ],
                },
            )
        return PublicApiResponse(
            status_code=200,
            body={
                "query": request.query,
                "result_count": 0,
                "results": [],
                "absence": {
                    "code": "search_no_matches",
                    "message": f"No governed synthetic records matched query '{request.query}'.",
                },
            },
        )


class WorkbenchServerTestCase(unittest.TestCase):
    def test_server_renders_workspace_via_public_submit_read_and_action_boundaries(self) -> None:
        public_api = FakeResolutionJobsPublicApi()
        actions_public_api = FakeResolutionActionsPublicApi()
        html = render_resolution_workspace_page(
            public_api,
            "fixture:software/synthetic-demo-app@1.0.0",
            actions_public_api=actions_public_api,
        )

        self.assertEqual(
            public_api.submit_target_refs,
            ["fixture:software/synthetic-demo-app@1.0.0"],
        )
        self.assertEqual(public_api.read_job_ids, ["job-fake-0001"])
        self.assertEqual(actions_public_api.list_target_refs, ["fixture:software/synthetic-demo-app@1.0.0"])
        self.assertIn("Synthetic Demo App", html)
        self.assertIn("Export resolution manifest", html)
        self.assertIn("/actions/export-resolution-manifest?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0", html)
        self.assertIn("Export resolution bundle", html)
        self.assertIn("/actions/export-resolution-bundle?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0", html)

    def test_server_renders_search_results_via_public_search_boundary(self) -> None:
        public_api = FakeSearchPublicApi()

        html = render_search_results_page(public_api, "synthetic")

        self.assertEqual(public_api.queries, ["synthetic"])
        self.assertIn("Synthetic Demo Suite", html)
        self.assertIn("/?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0", html)

    def test_wsgi_app_handles_query_driven_get_request(self) -> None:
        resolution_public_api = FakeResolutionJobsPublicApi()
        actions_public_api = FakeResolutionActionsPublicApi()
        search_public_api = FakeSearchPublicApi()
        app = WorkbenchWsgiApp(
            resolution_public_api,
            actions_public_api=actions_public_api,
            search_public_api=search_public_api,
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
            resolution_public_api.submit_target_refs,
            ["fixture:software/missing-demo-app@0.0.1"],
        )
        self.assertIn("fixture:software/missing-demo-app@0.0.1", body)
        self.assertIn("No available actions are exposed for this target.", body)
        self.assertNotIn(
            "<a href=\"/actions/export-resolution-manifest?target_ref=fixture%3Asoftware%2Fmissing-demo-app%400.0.1\">",
            body,
        )
        self.assertNotIn(
            "<a href=\"/actions/export-resolution-bundle?target_ref=fixture%3Asoftware%2Fmissing-demo-app%400.0.1\">",
            body,
        )

    def test_wsgi_app_handles_search_requests(self) -> None:
        resolution_public_api = FakeResolutionJobsPublicApi()
        actions_public_api = FakeResolutionActionsPublicApi()
        search_public_api = FakeSearchPublicApi()
        app = WorkbenchWsgiApp(
            resolution_public_api,
            actions_public_api=actions_public_api,
            search_public_api=search_public_api,
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
                    "PATH_INFO": "/search",
                    "QUERY_STRING": "q=synthetic",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")

        self.assertEqual(captured["status"], "200 OK")
        self.assertEqual(search_public_api.queries, ["synthetic"])
        self.assertIn("Synthetic Demo Suite", body)

    def test_wsgi_app_serves_manifest_export_json_for_known_target(self) -> None:
        app = WorkbenchWsgiApp(
            FakeResolutionJobsPublicApi(),
            actions_public_api=FakeResolutionActionsPublicApi(),
            search_public_api=FakeSearchPublicApi(),
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
                    "PATH_INFO": "/actions/export-resolution-manifest",
                    "QUERY_STRING": f"target_ref={quote('fixture:software/synthetic-demo-app@1.0.0')}",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")

        self.assertEqual(captured["status"], "200 OK")
        headers = dict(captured["headers"])
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["manifest_kind"], "eureka.resolution_manifest")
        self.assertEqual(payload["target_ref"], "fixture:software/synthetic-demo-app@1.0.0")

    def test_wsgi_app_serves_blocked_manifest_export_json_for_unknown_target(self) -> None:
        app = WorkbenchWsgiApp(
            FakeResolutionJobsPublicApi(),
            actions_public_api=FakeResolutionActionsPublicApi(),
            search_public_api=FakeSearchPublicApi(),
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
                    "PATH_INFO": "/actions/export-resolution-manifest",
                    "QUERY_STRING": f"target_ref={quote('fixture:software/missing-demo-app@0.0.1')}",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")

        self.assertEqual(captured["status"], "404 Not Found")
        headers = dict(captured["headers"])
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["code"], "resolution_manifest_not_available")
        self.assertEqual(payload["status"], "blocked")

    def test_wsgi_app_serves_bundle_export_zip_for_known_target(self) -> None:
        app = WorkbenchWsgiApp(
            FakeResolutionJobsPublicApi(),
            actions_public_api=FakeResolutionActionsPublicApi(),
            search_public_api=FakeSearchPublicApi(),
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
                    "PATH_INFO": "/actions/export-resolution-bundle",
                    "QUERY_STRING": f"target_ref={quote('fixture:software/synthetic-demo-app@1.0.0')}",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        )

        self.assertEqual(captured["status"], "200 OK")
        headers = dict(captured["headers"])
        self.assertEqual(headers["Content-Type"], "application/zip")
        self.assertIn("eureka-resolution-bundle-fixture-software-synthetic-demo-app-1.0.0.zip", headers["Content-Disposition"])
        with zipfile.ZipFile(BytesIO(body)) as bundle:
            self.assertEqual(bundle.namelist(), ["bundle.json", "manifest.json"])

    def test_wsgi_app_serves_blocked_bundle_export_json_for_unknown_target(self) -> None:
        app = WorkbenchWsgiApp(
            FakeResolutionJobsPublicApi(),
            actions_public_api=FakeResolutionActionsPublicApi(),
            search_public_api=FakeSearchPublicApi(),
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
                    "PATH_INFO": "/actions/export-resolution-bundle",
                    "QUERY_STRING": f"target_ref={quote('fixture:software/missing-demo-app@0.0.1')}",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")

        self.assertEqual(captured["status"], "404 Not Found")
        headers = dict(captured["headers"])
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["code"], "resolution_bundle_not_available")
        self.assertEqual(payload["status"], "blocked")

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
