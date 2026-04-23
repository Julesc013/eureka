from __future__ import annotations

import ast
import json
from io import BytesIO
from pathlib import Path
import tempfile
from urllib.parse import urlencode
import unittest
import zipfile

from runtime.gateway.public_api import (
    build_demo_action_plan_public_api,
    build_demo_absence_public_api,
    build_demo_comparison_public_api,
    build_demo_compatibility_public_api,
    build_demo_representation_selection_public_api,
    build_demo_resolution_actions_public_api,
    build_demo_resolution_bundle_inspection_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_representations_public_api,
    build_demo_search_public_api,
    build_demo_subject_states_public_api,
)
from surfaces.web.server import WorkbenchWsgiApp


DEFAULT_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"
MISSING_TARGET_REF = "fixture:software/missing-demo-app@0.0.1"
EXPECTED_RESOLVED_RESOURCE_ID = (
    "resolved:sha256:87e9ca7d6145c26282f042c3c65416d3a174e4629683e8c4da8afb169bcb58c2"
)
SURFACE_WEB_SERVER_ROOT = Path(__file__).resolve().parents[1] / "server"


class HttpApiRoutesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = WorkbenchWsgiApp(
            build_demo_resolution_jobs_public_api(),
            action_plan_public_api=build_demo_action_plan_public_api(),
            absence_public_api=build_demo_absence_public_api(),
            comparison_public_api=build_demo_comparison_public_api(),
            compatibility_public_api=build_demo_compatibility_public_api(),
            handoff_public_api=build_demo_representation_selection_public_api(),
            subject_states_public_api=build_demo_subject_states_public_api(),
            representations_public_api=build_demo_representations_public_api(),
            actions_public_api=build_demo_resolution_actions_public_api(),
            bundle_inspection_public_api=build_demo_resolution_bundle_inspection_public_api(),
            search_public_api=build_demo_search_public_api(),
            default_target_ref=DEFAULT_TARGET_REF,
        )

    def test_resolve_endpoint_returns_machine_readable_success_for_known_target(self) -> None:
        status, headers, body = self._request(
            "/api/resolve",
            {"target_ref": DEFAULT_TARGET_REF, "strategy": "preserve"},
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["workbench_session"]["active_job"]["status"], "completed")
        self.assertEqual(
            payload["workbench_session"]["resolved_resource_id"],
            EXPECTED_RESOLVED_RESOURCE_ID,
        )
        self.assertEqual(payload["workbench_session"]["representations"][0]["representation_kind"], "fixture_artifact")
        self.assertEqual(payload["workbench_session"]["representations"][1]["access_kind"], "view")
        self.assertEqual(payload["workbench_session"]["evidence"][0]["claim_kind"], "label")
        self.assertEqual(payload["action_plan"]["status"], "planned")
        self.assertEqual(payload["action_plan"]["strategy_profile"]["strategy_id"], "preserve")
        self.assertEqual(
            payload["resolution_actions"]["resolved_resource_id"],
            EXPECTED_RESOLVED_RESOURCE_ID,
        )

    def test_action_plan_endpoint_returns_machine_readable_bounded_plan(self) -> None:
        status, headers, body = self._request(
            "/api/action-plan",
            {
                "target_ref": "github-release:cli/cli@v2.65.0",
                "host": "windows-x86_64",
                "strategy": "acquire",
            },
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["status"], "planned")
        self.assertEqual(payload["strategy_profile"]["strategy_id"], "acquire")
        self.assertEqual(payload["compatibility_status"], "compatible")
        self.assertEqual(payload["host_profile"]["host_profile_id"], "windows-x86_64")
        direct_action = next(action for action in payload["actions"] if action["action_id"] == "access_representation")
        self.assertEqual(direct_action["status"], "recommended")

        blocked_status, _, blocked_body = self._request(
            "/api/action-plan",
            {"target_ref": MISSING_TARGET_REF},
        )
        self.assertEqual(blocked_status, "404 Not Found")
        blocked_payload = json.loads(blocked_body)
        self.assertEqual(blocked_payload["status"], "blocked")
        self.assertEqual(blocked_payload["notices"][0]["code"], "target_ref_not_found")

    def test_resolve_endpoint_returns_honest_blocked_outcome_for_unknown_target(self) -> None:
        status, headers, body = self._request("/api/resolve", {"target_ref": MISSING_TARGET_REF})

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["workbench_session"]["active_job"]["status"], "blocked")
        self.assertEqual(
            payload["workbench_session"]["notices"][0]["code"],
            "target_ref_not_found",
        )
        self.assertNotIn("resolved_resource_id", payload["workbench_session"])

    def test_search_endpoint_returns_deterministic_results_and_no_results_response(self) -> None:
        with self.subTest(query="synthetic"):
            status, headers, body = self._request("/api/search", {"q": "synthetic"})
            self.assertEqual(status, "200 OK")
            self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
            payload = json.loads(body)
            self.assertEqual(payload["result_count"], 2)
            self.assertEqual(
                [result["target_ref"] for result in payload["results"]],
                [
                    "fixture:software/synthetic-demo-app@1.0.0",
                    "fixture:software/synthetic-demo-suite@2.0.0",
                ],
            )
            self.assertEqual(
                payload["results"][0]["resolved_resource_id"],
                EXPECTED_RESOLVED_RESOURCE_ID,
            )
            self.assertEqual(payload["results"][0]["evidence"][0]["claim_kind"], "label")

        with self.subTest(query="missing"):
            status, _, body = self._request("/api/search", {"q": "missing"})
            self.assertEqual(status, "200 OK")
            payload = json.loads(body)
            self.assertEqual(payload["result_count"], 0)
            self.assertEqual(payload["absence"]["code"], "search_no_matches")

    def test_absence_endpoints_return_machine_readable_reports(self) -> None:
        resolve_status, headers, resolve_body = self._request(
            "/api/absence/resolve",
            {"target_ref": "fixture:software/archivebox@9.9.9"},
        )
        self.assertEqual(resolve_status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        resolve_payload = json.loads(resolve_body)
        self.assertEqual(resolve_payload["request_kind"], "resolve")
        self.assertEqual(resolve_payload["status"], "explained")
        self.assertEqual(resolve_payload["likely_reason_code"], "known_subject_different_state")
        self.assertEqual(resolve_payload["near_matches"][0]["subject_key"], "archivebox")

        search_status, _, search_body = self._request(
            "/api/absence/search",
            {"q": "archive box"},
        )
        self.assertEqual(search_status, "200 OK")
        search_payload = json.loads(search_body)
        self.assertEqual(search_payload["request_kind"], "search")
        self.assertEqual(search_payload["status"], "explained")
        self.assertEqual(search_payload["likely_reason_code"], "related_subjects_exist")
        self.assertGreaterEqual(len(search_payload["near_matches"]), 3)

    def test_compare_endpoint_returns_machine_readable_comparison_and_blocked_shape(self) -> None:
        status, headers, body = self._request(
            "/api/compare",
            {
                "left": "fixture:software/archivebox@0.8.5",
                "right": "github-release:archivebox/archivebox@v0.8.5",
            },
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["status"], "compared")
        self.assertEqual(payload["left"]["target_ref"], "fixture:software/archivebox@0.8.5")
        self.assertEqual(payload["right"]["target_ref"], "github-release:archivebox/archivebox@v0.8.5")
        self.assertEqual(payload["agreements"][0]["category"], "subject_key")
        self.assertEqual(payload["disagreements"][0]["category"], "object_label")
        self.assertEqual(payload["left"]["evidence"][0]["claim_kind"], "label")
        self.assertEqual(payload["right"]["evidence"][1]["claim_kind"], "version")

        blocked_status, _, blocked_body = self._request(
            "/api/compare",
            {
                "left": "fixture:software/archivebox@0.8.5",
                "right": MISSING_TARGET_REF,
            },
        )
        self.assertEqual(blocked_status, "404 Not Found")
        blocked_payload = json.loads(blocked_body)
        self.assertEqual(blocked_payload["status"], "blocked")
        self.assertEqual(blocked_payload["notices"][0]["code"], "comparison_right_unresolved")

    def test_compatibility_endpoint_returns_machine_readable_verdicts(self) -> None:
        status, headers, body = self._request(
            "/api/compatibility",
            {
                "target_ref": "fixture:software/compatibility-lab@3.2.1",
                "host": "windows-x86_64",
            },
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["status"], "evaluated")
        self.assertEqual(payload["compatibility_status"], "compatible")
        self.assertEqual(payload["host_profile"]["host_profile_id"], "windows-x86_64")
        self.assertEqual(payload["reasons"][0]["code"], "os_family_supported")

        incompatible_status, _, incompatible_body = self._request(
            "/api/compatibility",
            {
                "target_ref": "fixture:software/archive-viewer@0.9.0",
                "host": "linux-x86_64",
            },
        )
        self.assertEqual(incompatible_status, "200 OK")
        incompatible_payload = json.loads(incompatible_body)
        self.assertEqual(incompatible_payload["compatibility_status"], "incompatible")
        self.assertEqual(incompatible_payload["reasons"][0]["code"], "os_family_not_supported")

        unknown_status, _, unknown_body = self._request(
            "/api/compatibility",
            {
                "target_ref": DEFAULT_TARGET_REF,
                "host": "windows-x86_64",
            },
        )
        self.assertEqual(unknown_status, "200 OK")
        unknown_payload = json.loads(unknown_body)
        self.assertEqual(unknown_payload["compatibility_status"], "unknown")
        self.assertEqual(unknown_payload["reasons"][0]["code"], "compatibility_requirements_missing")

    def test_states_endpoint_returns_machine_readable_subject_states_and_missing_shape(self) -> None:
        status, headers, body = self._request("/api/states", {"subject": "archivebox"})

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["status"], "listed")
        self.assertEqual(payload["subject"]["subject_key"], "archivebox")
        self.assertEqual(payload["subject"]["state_count"], 3)
        self.assertEqual(
            [entry["target_ref"] for entry in payload["states"]],
            [
                "fixture:software/archivebox@0.8.5",
                "github-release:archivebox/archivebox@v0.8.5",
                "github-release:archivebox/archivebox@v0.8.4",
            ],
        )
        self.assertEqual(payload["states"][2]["normalized_version_or_state"], "0.8.4")
        self.assertEqual(payload["states"][1]["evidence"][1]["claim_kind"], "version")

        blocked_status, _, blocked_body = self._request("/api/states", {"subject": "missing-subject"})
        self.assertEqual(blocked_status, "404 Not Found")
        blocked_payload = json.loads(blocked_body)
        self.assertEqual(blocked_payload["status"], "blocked")
        self.assertEqual(blocked_payload["notices"][0]["code"], "subject_not_found")

    def test_representations_endpoint_returns_machine_readable_representation_listing(self) -> None:
        status, headers, body = self._request(
            "/api/representations",
            {"target_ref": "github-release:cli/cli@v2.65.0"},
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["status"], "available")
        self.assertEqual(payload["target_ref"], "github-release:cli/cli@v2.65.0")
        self.assertEqual(payload["primary_object"]["label"], "GitHub CLI 2.65.0")
        self.assertEqual(len(payload["representations"]), 3)
        self.assertEqual(payload["representations"][0]["representation_kind"], "release_page")
        self.assertEqual(payload["representations"][1]["access_kind"], "download")
        self.assertEqual(
            payload["representations"][1]["access_locator"],
            "https://github.com/cli/cli/releases/download/v2.65.0/gh_2.65.0_windows_amd64.msi",
        )

    def test_handoff_endpoint_returns_machine_readable_selection_listing(self) -> None:
        status, headers, body = self._request(
            "/api/handoff",
            {
                "target_ref": "github-release:cli/cli@v2.65.0",
                "host": "windows-x86_64",
                "strategy": "acquire",
            },
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["status"], "available")
        self.assertEqual(payload["compatibility_status"], "compatible")
        self.assertEqual(payload["preferred_representation_id"], "rep.github-release.cli.cli.v2.65.0.asset.0")
        preferred = next(
            entry for entry in payload["selections"] if entry["selection_status"] == "preferred"
        )
        self.assertEqual(preferred["label"], "gh_2.65.0_windows_amd64.msi")
        self.assertEqual(preferred["strategy_id"], "acquire")

        blocked_status, _, blocked_body = self._request(
            "/api/handoff",
            {"target_ref": MISSING_TARGET_REF},
        )
        self.assertEqual(blocked_status, "404 Not Found")
        blocked_payload = json.loads(blocked_body)
        self.assertEqual(blocked_payload["status"], "blocked")
        self.assertEqual(blocked_payload["notices"][0]["code"], "target_ref_not_found")

    def test_manifest_export_endpoint_returns_json_with_resolved_resource_id(self) -> None:
        status, headers, body = self._request(
            "/api/export/manifest",
            {"target_ref": DEFAULT_TARGET_REF},
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["manifest_kind"], "eureka.resolution_manifest")
        self.assertEqual(payload["resolved_resource_id"], EXPECTED_RESOLVED_RESOURCE_ID)
        self.assertEqual(payload["evidence"][0]["claim_kind"], "label")
        self.assertEqual(payload["representations"][0]["representation_kind"], "fixture_artifact")
        self.assertEqual(payload["representations"][1]["access_kind"], "view")

    def test_bundle_export_endpoint_returns_zip_bytes(self) -> None:
        status, headers, body = self._request(
            "/api/export/bundle",
            {"target_ref": DEFAULT_TARGET_REF},
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/zip")
        with zipfile.ZipFile(BytesIO(body)) as bundle:
            self.assertEqual(
                bundle.namelist(),
                [
                    "README.txt",
                    "bundle.json",
                    "manifest.json",
                    "records/normalized_record.json",
                ],
            )

    def test_bundle_inspection_endpoint_returns_inspected_result_for_valid_bundle_path(self) -> None:
        _, _, bundle_bytes = self._request(
            "/api/export/bundle",
            {"target_ref": DEFAULT_TARGET_REF},
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle_path = Path(temp_dir) / "synthetic-demo-bundle.zip"
            bundle_path.write_bytes(bundle_bytes)

            status, headers, body = self._request(
                "/api/inspect/bundle",
                {"bundle_path": str(bundle_path)},
            )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["status"], "inspected")
        self.assertEqual(payload["bundle"]["target_ref"], DEFAULT_TARGET_REF)
        self.assertIn("manifest.json", payload["bundle"]["member_list"])
        self.assertEqual(payload["evidence"][0]["claim_kind"], "label")
        self.assertEqual(payload["normalized_record"]["representations"][0]["representation_kind"], "fixture_artifact")
        self.assertEqual(payload["normalized_record"]["representations"][1]["access_kind"], "view")

    def test_store_list_and_read_endpoints_work_for_local_store(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            status, _, body = self._request(
                "/api/store/manifest",
                {"target_ref": DEFAULT_TARGET_REF, "store_root": temp_dir},
            )
            self.assertEqual(status, "200 OK")
            manifest_store_payload = json.loads(body)
            manifest_artifact_id = manifest_store_payload["artifact"]["artifact_id"]
            self.assertEqual(
                manifest_store_payload["artifact"]["resolved_resource_id"],
                EXPECTED_RESOLVED_RESOURCE_ID,
            )
            self.assertEqual(manifest_store_payload["artifact"]["evidence"][0]["claim_kind"], "label")

            status, _, body = self._request(
                "/api/store/bundle",
                {"target_ref": DEFAULT_TARGET_REF, "store_root": temp_dir},
            )
            self.assertEqual(status, "200 OK")
            bundle_store_payload = json.loads(body)
            bundle_artifact_id = bundle_store_payload["artifact"]["artifact_id"]
            self.assertEqual(
                bundle_store_payload["artifact"]["resolved_resource_id"],
                EXPECTED_RESOLVED_RESOURCE_ID,
            )
            self.assertEqual(bundle_store_payload["artifact"]["evidence"][0]["claim_kind"], "label")

            status, headers, body = self._request(
                "/api/stored",
                {"target_ref": DEFAULT_TARGET_REF, "store_root": temp_dir},
            )
            self.assertEqual(status, "200 OK")
            self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
            stored_payload = json.loads(body)
            self.assertEqual(stored_payload["resolved_resource_id"], EXPECTED_RESOLVED_RESOURCE_ID)
            self.assertEqual(
                {artifact["artifact_id"] for artifact in stored_payload["artifacts"]},
                {manifest_artifact_id, bundle_artifact_id},
            )
            self.assertEqual(stored_payload["artifacts"][0]["evidence"][0]["claim_kind"], "label")

            status, headers, body = self._request(
                "/api/stored/artifact",
                {"artifact_id": manifest_artifact_id, "store_root": temp_dir},
            )
            self.assertEqual(status, "200 OK")
            self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
            manifest_payload = json.loads(body)
            self.assertEqual(manifest_payload["manifest_kind"], "eureka.resolution_manifest")
            self.assertEqual(manifest_payload["resolved_resource_id"], EXPECTED_RESOLVED_RESOURCE_ID)
            self.assertEqual(manifest_payload["evidence"][0]["claim_kind"], "label")

            status, headers, body = self._request(
                "/api/stored/artifact",
                {"artifact_id": bundle_artifact_id, "store_root": temp_dir},
            )
            self.assertEqual(status, "200 OK")
            self.assertEqual(headers["Content-Type"], "application/zip")
            with zipfile.ZipFile(BytesIO(body)) as bundle:
                self.assertIn("manifest.json", bundle.namelist())

    def test_http_api_modules_do_not_import_engine_or_connector_internals(self) -> None:
        for path in (
            SURFACE_WEB_SERVER_ROOT / "api_routes.py",
            SURFACE_WEB_SERVER_ROOT / "api_serialization.py",
        ):
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

    def _request(
        self,
        path: str,
        query: dict[str, str] | None = None,
    ) -> tuple[str, dict[str, str], bytes]:
        captured: dict[str, object] = {}

        def start_response(status: str, headers: list[tuple[str, str]]) -> None:
            captured["status"] = status
            captured["headers"] = headers

        body = b"".join(
            self.app(
                {
                    "REQUEST_METHOD": "GET",
                    "PATH_INFO": path,
                    "QUERY_STRING": urlencode(query or {}),
                    "wsgi.input": BytesIO(b""),
                },
                start_response,
            )
        )
        return str(captured["status"]), dict(captured["headers"]), body


if __name__ == "__main__":
    unittest.main()
