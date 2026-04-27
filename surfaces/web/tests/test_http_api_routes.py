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
    build_demo_acquisition_public_api,
    build_demo_action_plan_public_api,
    build_demo_absence_public_api,
    build_demo_comparison_public_api,
    build_demo_compatibility_public_api,
    build_demo_decomposition_public_api,
    build_demo_member_access_public_api,
    build_demo_representation_selection_public_api,
    build_demo_resolution_actions_public_api,
    build_demo_resolution_bundle_inspection_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_representations_public_api,
    build_demo_search_public_api,
    build_demo_source_registry_public_api,
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
            acquisition_public_api=build_demo_acquisition_public_api(),
            action_plan_public_api=build_demo_action_plan_public_api(),
            absence_public_api=build_demo_absence_public_api(),
            comparison_public_api=build_demo_comparison_public_api(),
            compatibility_public_api=build_demo_compatibility_public_api(),
            decomposition_public_api=build_demo_decomposition_public_api(),
            member_access_public_api=build_demo_member_access_public_api(),
            handoff_public_api=build_demo_representation_selection_public_api(),
            subject_states_public_api=build_demo_subject_states_public_api(),
            representations_public_api=build_demo_representations_public_api(),
            actions_public_api=build_demo_resolution_actions_public_api(),
            bundle_inspection_public_api=build_demo_resolution_bundle_inspection_public_api(),
            search_public_api=build_demo_search_public_api(),
            source_registry_public_api=build_demo_source_registry_public_api(),
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
        self.assertTrue(payload["workbench_session"]["representations"][0]["is_fetchable"])
        self.assertFalse(payload["workbench_session"]["representations"][1]["is_fetchable"])
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

    def test_fetch_endpoint_returns_bytes_for_fetchable_representation_and_json_for_blocked_cases(self) -> None:
        status, headers, body = self._request(
            "/api/fetch",
            {
                "target_ref": DEFAULT_TARGET_REF,
                "representation_id": "rep.synthetic-demo-app.source",
            },
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/vnd.eureka.synthetic.bundle")
        self.assertIn("synthetic-demo-app.bundle", headers["Content-Disposition"])
        self.assertIn(b"EUREKA-SYNTHETIC-BUNDLE", body)

        unavailable_status, unavailable_headers, unavailable_body = self._request(
            "/api/fetch",
            {
                "target_ref": "github-release:cli/cli@v2.65.0",
                "representation_id": "rep.github-release.cli.cli.release-metadata",
            },
        )
        self.assertEqual(unavailable_status, "422 Unprocessable Entity")
        self.assertEqual(unavailable_headers["Content-Type"], "application/json; charset=utf-8")
        unavailable_payload = json.loads(unavailable_body)
        self.assertEqual(unavailable_payload["acquisition_status"], "unavailable")
        self.assertEqual(unavailable_payload["reason_codes"][0], "representation_not_fetchable")

        blocked_status, _, blocked_body = self._request(
            "/api/fetch",
            {
                "target_ref": DEFAULT_TARGET_REF,
                "representation_id": "rep.synthetic-demo-app.missing",
            },
        )
        self.assertEqual(blocked_status, "404 Not Found")
        blocked_payload = json.loads(blocked_body)
        self.assertEqual(blocked_payload["acquisition_status"], "blocked")
        self.assertEqual(blocked_payload["reason_codes"][0], "representation_not_found")

    def test_fetch_page_route_returns_bytes_for_fetchable_representation(self) -> None:
        status, headers, body = self._request(
            "/fetch",
            {
                "target_ref": DEFAULT_TARGET_REF,
                "representation_id": "rep.synthetic-demo-app.source",
            },
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/vnd.eureka.synthetic.bundle")
        self.assertIn("synthetic-demo-app.bundle", headers["Content-Disposition"])
        self.assertIn(b"EUREKA-SYNTHETIC-BUNDLE", body)

    def test_decompose_endpoint_returns_member_listing_for_supported_representation_and_unsupported_shape_for_binary(self) -> None:
        status, headers, body = self._request(
            "/api/decompose",
            {
                "target_ref": DEFAULT_TARGET_REF,
                "representation_id": "rep.synthetic-demo-app.package",
            },
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["decomposition_status"], "decomposed")
        self.assertEqual(payload["representation_kind"], "fixture_archive")
        self.assertEqual(
            [member["member_path"] for member in payload["members"]],
            [
                "config/settings.json",
                "docs/evidence.txt",
                "README.txt",
            ],
        )
        self.assertEqual(payload["members"][0]["content_type"], "application/json")

        unsupported_status, unsupported_headers, unsupported_body = self._request(
            "/api/decompose",
            {
                "target_ref": "github-release:cli/cli@v2.65.0",
                "representation_id": "rep.github-release.cli.cli.v2.65.0.asset.0",
            },
        )
        self.assertEqual(unsupported_status, "422 Unprocessable Entity")
        self.assertEqual(unsupported_headers["Content-Type"], "application/json; charset=utf-8")
        unsupported_payload = json.loads(unsupported_body)
        self.assertEqual(unsupported_payload["decomposition_status"], "unsupported")
        self.assertEqual(
            unsupported_payload["reason_codes"][0],
            "representation_format_unsupported",
        )

        blocked_status, _, blocked_body = self._request(
            "/api/decompose",
            {
                "target_ref": DEFAULT_TARGET_REF,
                "representation_id": "rep.synthetic-demo-app.unknown",
            },
        )
        self.assertEqual(blocked_status, "404 Not Found")
        blocked_payload = json.loads(blocked_body)
        self.assertEqual(blocked_payload["decomposition_status"], "blocked")
        self.assertEqual(blocked_payload["reason_codes"][0], "representation_not_found")

    def test_decompose_page_route_renders_html_for_supported_representation(self) -> None:
        status, headers, body = self._request(
            "/decompose",
            {
                "target_ref": DEFAULT_TARGET_REF,
                "representation_id": "rep.synthetic-demo-app.package",
            },
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
        html = body.decode("utf-8")
        self.assertIn("Eureka Bounded Decomposition", html)
        self.assertIn("config/settings.json", html)
        self.assertIn("README.txt", html)

    def test_member_endpoint_returns_preview_json_and_raw_bytes_for_known_member(self) -> None:
        status, headers, body = self._request(
            "/api/member",
            {
                "target_ref": DEFAULT_TARGET_REF,
                "representation_id": "rep.synthetic-demo-app.package",
                "member_path": "README.txt",
            },
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["member_access_status"], "previewed")
        self.assertEqual(payload["member_path"], "README.txt")
        self.assertIn("Synthetic Demo App package", payload["text_preview"])

        raw_status, raw_headers, raw_body = self._request(
            "/api/member",
            {
                "target_ref": DEFAULT_TARGET_REF,
                "representation_id": "rep.synthetic-demo-app.package",
                "member_path": "README.txt",
                "raw": "1",
            },
        )
        self.assertEqual(raw_status, "200 OK")
        self.assertEqual(raw_headers["Content-Type"], "text/plain")
        self.assertIn("README.txt", raw_headers["Content-Disposition"])
        self.assertIn(b"Synthetic Demo App package", raw_body)

    def test_member_endpoint_returns_honest_blocked_and_unsupported_shapes(self) -> None:
        blocked_status, blocked_headers, blocked_body = self._request(
            "/api/member",
            {
                "target_ref": DEFAULT_TARGET_REF,
                "representation_id": "rep.synthetic-demo-app.package",
                "member_path": "missing/member.txt",
            },
        )
        self.assertEqual(blocked_status, "404 Not Found")
        self.assertEqual(blocked_headers["Content-Type"], "application/json; charset=utf-8")
        blocked_payload = json.loads(blocked_body)
        self.assertEqual(blocked_payload["member_access_status"], "blocked")
        self.assertEqual(blocked_payload["reason_codes"][0], "member_not_found")

        unsupported_status, _, unsupported_body = self._request(
            "/api/member",
            {
                "target_ref": "github-release:cli/cli@v2.65.0",
                "representation_id": "rep.github-release.cli.cli.v2.65.0.asset.0",
                "member_path": "README.txt",
            },
        )
        self.assertEqual(unsupported_status, "422 Unprocessable Entity")
        unsupported_payload = json.loads(unsupported_body)
        self.assertEqual(unsupported_payload["member_access_status"], "unsupported")
        self.assertEqual(
            unsupported_payload["reason_codes"][0],
            "representation_format_unsupported",
        )

    def test_member_page_route_renders_html_for_previewable_member(self) -> None:
        status, headers, body = self._request(
            "/member",
            {
                "target_ref": DEFAULT_TARGET_REF,
                "representation_id": "rep.synthetic-demo-app.package",
                "member_path": "config/settings.json",
            },
        )

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
        html = body.decode("utf-8")
        self.assertIn("Eureka Member Access", html)
        self.assertIn("config/settings.json", html)
        self.assertIn("Text preview", html)
        self.assertIn("&quot;mode&quot;: &quot;demo&quot;", html)

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
            self.assertIn("primary_lane", payload["results"][0])
            self.assertIn("user_cost_score", payload["results"][0])

        with self.subTest(query="driver.inf"):
            status, _, body = self._request("/api/search", {"q": "driver.inf"})
            self.assertEqual(status, "200 OK")
            payload = json.loads(body)
            member = next(
                result
                for result in payload["results"]
                if result["object"].get("member_kind") == "driver"
            )
            self.assertEqual(member["primary_lane"], "inside_bundles")
            self.assertEqual(member["user_cost_score"], 1)

        with self.subTest(query="missing"):
            status, _, body = self._request("/api/search", {"q": "missing"})
            self.assertEqual(status, "200 OK")
            payload = json.loads(body)
            self.assertEqual(payload["result_count"], 0)
            self.assertEqual(payload["absence"]["code"], "search_no_matches")

    def test_sources_endpoints_return_registry_listing_and_single_source(self) -> None:
        status, headers, body = self._request("/api/sources", {"status": "active_fixture"})

        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        payload = json.loads(body)
        self.assertEqual(payload["status"], "listed")
        self.assertEqual(payload["source_count"], 2)
        self.assertEqual(payload["applied_filters"]["status"], "active_fixture")
        self.assertEqual(
            {entry["source_id"] for entry in payload["sources"]},
            {"local-bundle-fixtures", "synthetic-fixtures"},
        )
        self.assertIn("coverage_depth", payload["sources"][0])
        self.assertIn("capabilities", payload["sources"][0])

        capability_status, _, capability_body = self._request(
            "/api/sources",
            {"capability": "recorded_fixture_backed"},
        )
        self.assertEqual(capability_status, "200 OK")
        capability_payload = json.loads(capability_body)
        self.assertEqual(
            [entry["source_id"] for entry in capability_payload["sources"]],
            [
                "article-scan-recorded-fixtures",
                "github-releases-recorded-fixtures",
                "internet-archive-recorded-fixtures",
            ],
        )

        detail_status, _, detail_body = self._request(
            "/api/source",
            {"id": "github-releases-recorded-fixtures"},
        )
        self.assertEqual(detail_status, "200 OK")
        detail_payload = json.loads(detail_body)
        self.assertEqual(detail_payload["status"], "available")
        self.assertEqual(detail_payload["selected_source_id"], "github-releases-recorded-fixtures")
        self.assertEqual(detail_payload["sources"][0]["connector"]["status"], "fixture_backed")

    def test_source_endpoint_returns_structured_not_found_and_placeholder_honesty(self) -> None:
        not_found_status, _, not_found_body = self._request("/api/source", {"id": "missing-source"})
        self.assertEqual(not_found_status, "404 Not Found")
        not_found_payload = json.loads(not_found_body)
        self.assertEqual(not_found_payload["status"], "blocked")
        self.assertEqual(not_found_payload["notices"][0]["code"], "source_id_not_found")

        placeholder_status, _, placeholder_body = self._request(
            "/api/source",
            {"id": "internet-archive-placeholder"},
        )
        self.assertEqual(placeholder_status, "200 OK")
        placeholder_payload = json.loads(placeholder_body)
        self.assertEqual(placeholder_payload["sources"][0]["status"], "placeholder")
        self.assertEqual(placeholder_payload["sources"][0]["connector"]["status"], "unimplemented")
        self.assertEqual(placeholder_payload["sources"][0]["coverage_depth"], "source_known")
        self.assertFalse(placeholder_payload["sources"][0]["capabilities"]["live_supported"])

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
        self.assertFalse(payload["representations"][0]["is_fetchable"])
        self.assertEqual(payload["representations"][1]["access_kind"], "download")
        self.assertTrue(payload["representations"][1]["is_fetchable"])
        self.assertEqual(payload["representations"][1]["filename"], "gh_2.65.0_windows_amd64.msi")
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
