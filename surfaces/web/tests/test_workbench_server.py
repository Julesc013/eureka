from __future__ import annotations

import ast
import json
from io import BytesIO
from pathlib import Path
import zipfile
from urllib.parse import quote
import unittest

from runtime.gateway.public_api import (
    build_demo_public_search_public_api,
    build_demo_source_registry_public_api,
)
from runtime.gateway.public_api import PublicApiResponse, PublicArtifactResponse
from surfaces.web.server import (
    WorkbenchWsgiApp,
    render_bundle_inspection_page,
    render_resolution_workspace_page,
    render_search_results_page,
    render_source_registry_page,
)


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


class FakeResolutionBundleInspectionPublicApi:
    def __init__(self) -> None:
        self.bundle_paths: list[str] = []

    def inspect_bundle(self, request) -> PublicApiResponse:
        assert request.bundle_path is not None
        self.bundle_paths.append(request.bundle_path)
        if request.bundle_path == "C:/tmp/missing-bundle.zip":
            return PublicApiResponse(
                status_code=404,
                body={
                    "status": "blocked",
                    "inspection_mode": "local_offline",
                    "source": {
                        "kind": "local_path",
                        "locator": request.bundle_path,
                    },
                    "notices": [
                        {
                            "code": "bundle_path_not_found",
                            "severity": "error",
                            "message": f"Bundle path '{request.bundle_path}' was not found.",
                        }
                    ],
                },
            )
        if request.bundle_path == "C:/tmp/bad-bundle.zip":
            return PublicApiResponse(
                status_code=422,
                body={
                    "status": "blocked",
                    "inspection_mode": "local_offline",
                    "source": {
                        "kind": "local_path",
                        "locator": request.bundle_path,
                    },
                    "notices": [
                        {
                            "code": "bundle_archive_invalid",
                            "severity": "error",
                            "message": "Bundle payload is not a valid ZIP archive.",
                        }
                    ],
                },
            )
        return PublicApiResponse(
            status_code=200,
            body={
                "status": "inspected",
                "inspection_mode": "local_offline",
                "source": {
                    "kind": "local_path",
                    "locator": request.bundle_path,
                },
                "bundle": {
                    "bundle_kind": "eureka.resolution_bundle",
                    "bundle_version": "0.1.0-draft",
                    "target_ref": "fixture:software/synthetic-demo-app@1.0.0",
                    "member_list": [
                        "README.txt",
                        "bundle.json",
                        "manifest.json",
                        "records/normalized_record.json",
                    ],
                },
                "primary_object": {
                    "id": "obj.synthetic-demo-app",
                    "kind": "software",
                    "label": "Synthetic Demo App",
                },
                "normalized_record": {
                    "record_kind": "normalized_resolution_record",
                    "target_ref": "fixture:software/synthetic-demo-app@1.0.0",
                },
                "notices": [
                    {
                        "code": "bundle_inspected_locally_offline",
                        "severity": "info",
                        "message": "Inspected bundle locally and offline without live fixture access.",
                    }
                ],
            },
        )


class FakeStoredExportsPublicApi:
    def __init__(self) -> None:
        self.list_target_refs: list[str] = []
        self.store_manifest_target_refs: list[str] = []
        self.store_bundle_target_refs: list[str] = []
        self.artifact_ids: list[str] = []

    def list_stored_exports(self, request) -> PublicApiResponse:
        self.list_target_refs.append(request.target_ref)
        if request.target_ref == "fixture:software/missing-demo-app@0.0.1":
            return PublicApiResponse(
                status_code=404,
                body={
                    "target_ref": request.target_ref,
                    "store_actions": [
                        {
                            "action_id": "store_resolution_manifest",
                            "label": "Store resolution manifest locally",
                            "availability": "unavailable",
                        },
                        {
                            "action_id": "store_resolution_bundle",
                            "label": "Store resolution bundle locally",
                            "availability": "unavailable",
                        },
                    ],
                    "artifacts": [],
                    "notices": [
                        {
                            "code": "stored_exports_target_not_available",
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
                "store_actions": [
                    {
                        "action_id": "store_resolution_manifest",
                        "label": "Store resolution manifest locally",
                        "availability": "available",
                        "href": f"/store/manifest?target_ref={quote(request.target_ref, safe='')}",
                    },
                    {
                        "action_id": "store_resolution_bundle",
                        "label": "Store resolution bundle locally",
                        "availability": "available",
                        "href": f"/store/bundle?target_ref={quote(request.target_ref, safe='')}",
                    },
                ],
                "artifacts": [
                    {
                        "artifact_id": "sha256:manifest-demo",
                        "artifact_kind": "resolution_manifest",
                        "content_type": "application/json; charset=utf-8",
                        "byte_length": 128,
                        "availability": "available",
                        "href": "/stored/artifact?artifact_id=sha256%3Amanifest-demo",
                        "filename": "eureka-resolution-manifest-demo.json",
                    },
                    {
                        "artifact_id": "sha256:bundle-demo",
                        "artifact_kind": "resolution_bundle",
                        "content_type": "application/zip",
                        "byte_length": 256,
                        "availability": "available",
                        "href": "/stored/artifact?artifact_id=sha256%3Abundle-demo",
                        "filename": "eureka-resolution-bundle-demo.zip",
                    },
                ],
                "notices": [],
            },
        )

    def store_resolution_manifest(self, request) -> PublicApiResponse:
        self.store_manifest_target_refs.append(request.target_ref)
        if request.target_ref == "fixture:software/missing-demo-app@0.0.1":
            return PublicApiResponse(
                status_code=404,
                body={
                    "action_id": "store_resolution_manifest",
                    "status": "blocked",
                    "target_ref": request.target_ref,
                    "code": "store_resolution_manifest_not_available",
                    "message": f"No resolved synthetic record matched target_ref '{request.target_ref}'.",
                },
            )
        return PublicApiResponse(
            status_code=200,
            body={
                "status": "stored",
                "artifact": {
                    "artifact_id": "sha256:manifest-demo",
                    "artifact_kind": "resolution_manifest",
                    "content_type": "application/json; charset=utf-8",
                    "byte_length": 128,
                    "store_path": "objects/sha256/ma/nifest-demo",
                    "created_by_slice": "local_export_store",
                    "source_action": "store_resolution_manifest",
                    "target_ref": request.target_ref,
                },
                "notices": [],
            },
        )

    def store_resolution_bundle(self, request) -> PublicApiResponse:
        self.store_bundle_target_refs.append(request.target_ref)
        if request.target_ref == "fixture:software/missing-demo-app@0.0.1":
            return PublicApiResponse(
                status_code=404,
                body={
                    "action_id": "store_resolution_bundle",
                    "status": "blocked",
                    "target_ref": request.target_ref,
                    "code": "store_resolution_bundle_not_available",
                    "message": f"No resolved synthetic record matched target_ref '{request.target_ref}'.",
                },
            )
        return PublicApiResponse(
            status_code=200,
            body={
                "status": "stored",
                "artifact": {
                    "artifact_id": "sha256:bundle-demo",
                    "artifact_kind": "resolution_bundle",
                    "content_type": "application/zip",
                    "byte_length": 256,
                    "store_path": "objects/sha256/bu/ndle-demo",
                    "created_by_slice": "local_export_store",
                    "source_action": "store_resolution_bundle",
                    "target_ref": request.target_ref,
                },
                "notices": [],
            },
        )

    def get_stored_artifact_content(self, request) -> PublicArtifactResponse:
        self.artifact_ids.append(request.artifact_id)
        if request.artifact_id == "sha256:missing-demo":
            return PublicArtifactResponse(
                status_code=404,
                content_type="application/json; charset=utf-8",
                payload=(
                    json.dumps(
                        {
                            "artifact_id": request.artifact_id,
                            "status": "blocked",
                            "code": "stored_artifact_not_found",
                            "message": f"Unknown stored artifact_id '{request.artifact_id}'.",
                        },
                        sort_keys=True,
                    )
                    + "\n"
                ).encode("utf-8"),
            )
        if request.artifact_id == "sha256:bundle-demo":
            buffer = BytesIO()
            with zipfile.ZipFile(buffer, mode="w") as archive:
                archive.writestr("bundle.json", json.dumps({"artifact_id": request.artifact_id}, sort_keys=True))
            return PublicArtifactResponse(
                status_code=200,
                content_type="application/zip",
                filename="eureka-resolution-bundle-demo.zip",
                payload=buffer.getvalue(),
            )
        return PublicArtifactResponse(
            status_code=200,
            content_type="application/json; charset=utf-8",
            filename="eureka-resolution-manifest-demo.json",
            payload=(
                json.dumps(
                    {
                        "manifest_kind": "eureka.resolution_manifest",
                        "artifact_id": request.artifact_id,
                    },
                    sort_keys=True,
                )
                + "\n"
            ).encode("utf-8"),
        )


class WorkbenchServerTestCase(unittest.TestCase):
    def test_server_renders_workspace_via_public_submit_read_and_action_boundaries(self) -> None:
        public_api = FakeResolutionJobsPublicApi()
        actions_public_api = FakeResolutionActionsPublicApi()
        stored_exports_public_api = FakeStoredExportsPublicApi()
        html = render_resolution_workspace_page(
            public_api,
            "fixture:software/synthetic-demo-app@1.0.0",
            actions_public_api=actions_public_api,
            stored_exports_public_api=stored_exports_public_api,
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
        self.assertEqual(stored_exports_public_api.list_target_refs, ["fixture:software/synthetic-demo-app@1.0.0"])
        self.assertIn("Store resolution manifest locally", html)
        self.assertIn("Store resolution bundle locally", html)
        self.assertIn("sha256:manifest-demo", html)
        self.assertIn("/stored/artifact?artifact_id=sha256%3Amanifest-demo", html)

    def test_server_renders_search_results_via_public_search_boundary(self) -> None:
        public_api = FakeSearchPublicApi()

        html = render_search_results_page(public_api, "synthetic")

        self.assertEqual(public_api.queries, ["synthetic"])
        self.assertIn("Synthetic Demo Suite", html)
        self.assertIn("/?target_ref=fixture%3Asoftware%2Fsynthetic-demo-app%401.0.0", html)

    def test_server_renders_bundle_inspection_page_via_public_inspection_boundary(self) -> None:
        public_api = FakeResolutionBundleInspectionPublicApi()

        html = render_bundle_inspection_page(public_api, "C:/tmp/demo-bundle.zip")

        self.assertEqual(public_api.bundle_paths, ["C:/tmp/demo-bundle.zip"])
        self.assertIn("fixture:software/synthetic-demo-app@1.0.0", html)
        self.assertIn("obj.synthetic-demo-app", html)
        self.assertIn("bundle.json", html)

    def test_wsgi_app_handles_query_driven_get_request(self) -> None:
        resolution_public_api = FakeResolutionJobsPublicApi()
        actions_public_api = FakeResolutionActionsPublicApi()
        bundle_inspection_public_api = FakeResolutionBundleInspectionPublicApi()
        stored_exports_public_api = FakeStoredExportsPublicApi()
        search_public_api = FakeSearchPublicApi()
        app = WorkbenchWsgiApp(
            resolution_public_api,
            actions_public_api=actions_public_api,
            bundle_inspection_public_api=bundle_inspection_public_api,
            stored_exports_public_api=stored_exports_public_api,
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
        self.assertIn("No local store actions are exposed for this target.", body)
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
        bundle_inspection_public_api = FakeResolutionBundleInspectionPublicApi()
        search_public_api = FakeSearchPublicApi()
        app = WorkbenchWsgiApp(
            resolution_public_api,
            actions_public_api=actions_public_api,
            bundle_inspection_public_api=bundle_inspection_public_api,
            search_public_api=search_public_api,
            public_search_public_api=build_demo_public_search_public_api(),
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
        self.assertEqual(search_public_api.queries, [])
        self.assertIn("Eureka Public Search", body)
        self.assertIn("local-index-only", body)
        self.assertIn("Results", body)

    def test_server_renders_source_registry_page_via_public_boundary(self) -> None:
        html = render_source_registry_page(
            build_demo_source_registry_public_api(),
            status="active_fixture",
        )

        self.assertIn("Eureka Source Registry", html)
        self.assertIn("synthetic-fixtures", html)
        self.assertNotIn("github-releases-recorded-fixtures", html)
        self.assertIn("Active fixture-backed source record.", html)
        self.assertIn("coverage: action_indexed", html)

    def test_wsgi_app_handles_source_registry_requests(self) -> None:
        app = WorkbenchWsgiApp(
            FakeResolutionJobsPublicApi(),
            bundle_inspection_public_api=FakeResolutionBundleInspectionPublicApi(),
            search_public_api=FakeSearchPublicApi(),
            source_registry_public_api=build_demo_source_registry_public_api(),
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
                    "PATH_INFO": "/sources",
                    "QUERY_STRING": "status=active_fixture",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")

        self.assertEqual(captured["status"], "200 OK")
        self.assertIn("synthetic-fixtures", body)
        self.assertNotIn("github-releases-recorded-fixtures", body)
        self.assertIn("coverage: action_indexed", body)

    def test_wsgi_app_serves_manifest_export_json_for_known_target(self) -> None:
        app = WorkbenchWsgiApp(
            FakeResolutionJobsPublicApi(),
            actions_public_api=FakeResolutionActionsPublicApi(),
            bundle_inspection_public_api=FakeResolutionBundleInspectionPublicApi(),
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
            bundle_inspection_public_api=FakeResolutionBundleInspectionPublicApi(),
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
            bundle_inspection_public_api=FakeResolutionBundleInspectionPublicApi(),
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
            bundle_inspection_public_api=FakeResolutionBundleInspectionPublicApi(),
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

    def test_wsgi_app_serves_valid_bundle_inspection_page(self) -> None:
        app = WorkbenchWsgiApp(
            FakeResolutionJobsPublicApi(),
            actions_public_api=FakeResolutionActionsPublicApi(),
            bundle_inspection_public_api=FakeResolutionBundleInspectionPublicApi(),
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
                    "PATH_INFO": "/inspect/bundle",
                    "QUERY_STRING": f"bundle_path={quote('C:/tmp/demo-bundle.zip')}",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")

        self.assertEqual(captured["status"], "200 OK")
        self.assertIn("fixture:software/synthetic-demo-app@1.0.0", body)
        self.assertIn("obj.synthetic-demo-app", body)
        self.assertIn("records/normalized_record.json", body)

    def test_wsgi_app_serves_invalid_bundle_inspection_page(self) -> None:
        app = WorkbenchWsgiApp(
            FakeResolutionJobsPublicApi(),
            actions_public_api=FakeResolutionActionsPublicApi(),
            bundle_inspection_public_api=FakeResolutionBundleInspectionPublicApi(),
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
                    "PATH_INFO": "/inspect/bundle",
                    "QUERY_STRING": f"bundle_path={quote('C:/tmp/bad-bundle.zip')}",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")

        self.assertEqual(captured["status"], "200 OK")
        self.assertIn("blocked", body)
        self.assertIn("bundle_archive_invalid", body)
        self.assertIn("Bundle payload is not a valid ZIP archive.", body)

    def test_wsgi_app_serves_store_manifest_json_for_known_target(self) -> None:
        app = WorkbenchWsgiApp(
            FakeResolutionJobsPublicApi(),
            actions_public_api=FakeResolutionActionsPublicApi(),
            bundle_inspection_public_api=FakeResolutionBundleInspectionPublicApi(),
            stored_exports_public_api=FakeStoredExportsPublicApi(),
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
                    "PATH_INFO": "/store/manifest",
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
        self.assertEqual(payload["status"], "stored")
        self.assertEqual(payload["artifact"]["artifact_kind"], "resolution_manifest")

    def test_wsgi_app_serves_stored_manifest_json_for_known_artifact(self) -> None:
        app = WorkbenchWsgiApp(
            FakeResolutionJobsPublicApi(),
            actions_public_api=FakeResolutionActionsPublicApi(),
            bundle_inspection_public_api=FakeResolutionBundleInspectionPublicApi(),
            stored_exports_public_api=FakeStoredExportsPublicApi(),
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
                    "PATH_INFO": "/stored/artifact",
                    "QUERY_STRING": f"artifact_id={quote('sha256:manifest-demo')}",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")

        self.assertEqual(captured["status"], "200 OK")
        headers = dict(captured["headers"])
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["artifact_id"], "sha256:manifest-demo")
        self.assertEqual(payload["manifest_kind"], "eureka.resolution_manifest")

    def test_wsgi_app_serves_stored_bundle_zip_for_known_artifact(self) -> None:
        app = WorkbenchWsgiApp(
            FakeResolutionJobsPublicApi(),
            actions_public_api=FakeResolutionActionsPublicApi(),
            bundle_inspection_public_api=FakeResolutionBundleInspectionPublicApi(),
            stored_exports_public_api=FakeStoredExportsPublicApi(),
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
                    "PATH_INFO": "/stored/artifact",
                    "QUERY_STRING": f"artifact_id={quote('sha256:bundle-demo')}",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        )

        self.assertEqual(captured["status"], "200 OK")
        headers = dict(captured["headers"])
        self.assertEqual(headers["Content-Type"], "application/zip")
        with zipfile.ZipFile(BytesIO(body)) as bundle:
            self.assertEqual(bundle.namelist(), ["bundle.json"])

    def test_wsgi_app_returns_blocked_json_for_unknown_stored_artifact(self) -> None:
        app = WorkbenchWsgiApp(
            FakeResolutionJobsPublicApi(),
            actions_public_api=FakeResolutionActionsPublicApi(),
            bundle_inspection_public_api=FakeResolutionBundleInspectionPublicApi(),
            stored_exports_public_api=FakeStoredExportsPublicApi(),
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
                    "PATH_INFO": "/stored/artifact",
                    "QUERY_STRING": f"artifact_id={quote('sha256:missing-demo')}",
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        ).decode("utf-8")

        self.assertEqual(captured["status"], "404 Not Found")
        headers = dict(captured["headers"])
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["code"], "stored_artifact_not_found")

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
