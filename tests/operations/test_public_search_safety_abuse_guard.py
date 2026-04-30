from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SAFETY = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_safety.json"
ERROR_SCHEMA = REPO_ROOT / "contracts" / "api" / "error_response.v0.json"
ROUTES = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_routes.json"
SAFETY_DOC = REPO_ROOT / "docs" / "operations" / "PUBLIC_SEARCH_SAFETY_AND_ABUSE_GUARD.md"
READINESS = REPO_ROOT / "docs" / "operations" / "PUBLIC_SEARCH_RUNTIME_READINESS_CHECKLIST.md"
PUBLIC_ALPHA_SAFE_MODE = REPO_ROOT / "docs" / "operations" / "PUBLIC_ALPHA_SAFE_MODE.md"


REQUIRED_FORBIDDEN_PARAMETERS = {
    "index_path",
    "store_root",
    "run_store_root",
    "task_store_root",
    "memory_store_root",
    "local_path",
    "path",
    "file_path",
    "directory",
    "root",
    "url",
    "fetch_url",
    "crawl_url",
    "source_url",
    "download",
    "install",
    "execute",
    "upload",
    "user_file",
    "source_credentials",
    "auth_token",
    "api_key",
    "live_probe",
    "live_source",
    "network",
    "arbitrary_source",
}
REQUIRED_ERROR_CODES = {
    "query_required",
    "query_too_long",
    "limit_too_large",
    "unsupported_mode",
    "unsupported_profile",
    "unsupported_include",
    "forbidden_parameter",
    "local_paths_forbidden",
    "downloads_disabled",
    "installs_disabled",
    "uploads_disabled",
    "live_probes_disabled",
    "live_backend_unavailable",
    "rate_limited",
    "timeout",
    "bad_request",
}


class PublicSearchSafetyAbuseGuardTest(unittest.TestCase):
    def test_safety_inventory_exists_and_parses(self) -> None:
        self.assertTrue(SAFETY.is_file())
        payload = json.loads(SAFETY.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "local_runtime_guard_active")
        self.assertFalse(payload["no_runtime_implemented"])
        self.assertTrue(payload["local_public_search_runtime_implemented"])
        self.assertFalse(payload["hosted_public_search_runtime_implemented"])
        self.assertTrue(payload["no_public_search_live"])

    def test_local_index_only_is_only_allowed_mode(self) -> None:
        payload = json.loads(SAFETY.read_text(encoding="utf-8"))
        self.assertEqual(payload["first_allowed_mode"], "local_index_only")
        self.assertEqual(payload["allowed_modes"], ["local_index_only"])
        self.assertIn("live_probe", payload["disabled_modes"])
        self.assertIn("arbitrary_url_fetch", payload["disabled_modes"])
        self.assertIn("local_path_search", payload["disabled_modes"])
        self.assertIn("download_or_install", payload["disabled_modes"])

    def test_limits_are_conservative(self) -> None:
        payload = json.loads(SAFETY.read_text(encoding="utf-8"))
        self.assertEqual(payload["request_limits"]["max_query_length"], 160)
        self.assertEqual(payload["request_limits"]["min_query_length_after_trim"], 1)
        self.assertEqual(payload["request_limits"]["max_include_items"], 8)
        self.assertEqual(payload["request_limits"]["max_request_body_bytes"], 8192)
        self.assertEqual(payload["result_limits"]["default_result_limit"], 10)
        self.assertEqual(payload["result_limits"]["max_result_limit"], 25)
        self.assertEqual(payload["result_limits"]["max_live_sources_v0"], 0)
        self.assertEqual(payload["timeout_policy"]["max_runtime_ms_contract"], 3000)

    def test_forbidden_parameters_and_behaviors_are_complete(self) -> None:
        payload = json.loads(SAFETY.read_text(encoding="utf-8"))
        self.assertTrue(
            REQUIRED_FORBIDDEN_PARAMETERS.issubset(set(payload["forbidden_parameters"]))
        )
        behaviors = set(payload["forbidden_behaviors"])
        for behavior in (
            "arbitrary_url_fetching",
            "live_external_source_fanout",
            "google_scraping",
            "internet_archive_live_calls",
            "local_filesystem_search",
            "downloads",
            "installs",
            "uploads",
            "telemetry_by_default",
        ):
            self.assertIn(behavior, behaviors)

    def test_error_mapping_references_p26_error_codes(self) -> None:
        safety = json.loads(SAFETY.read_text(encoding="utf-8"))
        error_schema = json.loads(ERROR_SCHEMA.read_text(encoding="utf-8"))
        codes = set(error_schema["properties"]["error"]["properties"]["code"]["enum"])
        self.assertTrue(REQUIRED_ERROR_CODES.issubset(codes))
        self.assertTrue(set(safety["required_error_codes"]).issubset(codes))
        self.assertEqual(safety["error_mapping"]["local_path_or_root_parameter"], "local_paths_forbidden")
        self.assertEqual(safety["error_mapping"]["download_parameter_or_action"], "downloads_disabled")
        self.assertEqual(safety["error_mapping"]["install_or_execute_parameter_or_action"], "installs_disabled")
        self.assertEqual(safety["error_mapping"]["upload_or_user_file_parameter"], "uploads_disabled")

    def test_logging_privacy_and_operator_controls_are_closed(self) -> None:
        payload = json.loads(SAFETY.read_text(encoding="utf-8"))
        self.assertFalse(payload["telemetry_policy"]["implemented"])
        self.assertFalse(payload["telemetry_policy"]["default_enabled"])
        self.assertEqual(payload["logging_privacy_policy"]["telemetry_default"], "off")
        self.assertEqual(payload["logging_privacy_policy"]["private_path_logging"], "forbidden")
        flags = payload["operator_controls"]["required_future_flags"]
        self.assertEqual(flags["EUREKA_PUBLIC_SEARCH_ENABLED"], "0")
        self.assertEqual(flags["EUREKA_OPERATOR_KILL_SWITCH"], "1")
        self.assertEqual(flags["EUREKA_ALLOW_LIVE_PROBES"], "0")
        self.assertEqual(flags["EUREKA_ALLOW_DOWNLOADS"], "0")
        self.assertEqual(flags["EUREKA_ALLOW_TELEMETRY"], "0")

    def test_routes_are_local_runtime_only(self) -> None:
        payload = json.loads(ROUTES.read_text(encoding="utf-8"))
        self.assertTrue(payload["implemented_now"])
        self.assertTrue(payload["runtime_routes_implemented"])
        self.assertEqual(payload["implementation_scope"], "local_prototype_backend")
        self.assertFalse(payload["hosted_public_runtime_implemented"])
        self.assertFalse(payload["static_handoff_implemented"])
        for route in payload["routes"]:
            with self.subTest(route=route["path_template"]):
                self.assertTrue(route["implemented_now"])
                self.assertEqual(route["status"], "local_runtime_implemented")
                self.assertEqual(route["implementation_scope"], "local_prototype_backend")
                self.assertFalse(route["hosted_public_deployment"])
                self.assertEqual(route["allowed_modes"], ["local_index_only"])
                self.assertFalse(route["live_probe_allowed"])
                self.assertFalse(route["downloads_allowed"])
                self.assertFalse(route["local_paths_allowed"])
                self.assertFalse(route["uploads_allowed"])
                self.assertTrue(route["rate_limit_required_before_public"])

    def test_docs_and_readiness_checklist_exist_and_are_honest(self) -> None:
        self.assertTrue(SAFETY_DOC.is_file())
        self.assertTrue(READINESS.is_file())
        text = SAFETY_DOC.read_text(encoding="utf-8").casefold()
        for phrase in (
            "local public search runtime v0",
            "does not add rate-limit middleware",
            "telemetry is not implemented and defaults off",
            "github pages remains static-only",
            "local_index_only",
        ):
            self.assertIn(phrase, text)
        self.assertNotIn("public search is live", text)
        checklist = READINESS.read_text(encoding="utf-8")
        self.assertIn("Local Public Search Runtime v0", checklist)
        self.assertIn("hosted_public_runtime_approved: false", checklist)
        self.assertIn("static_search_handoff_approved: false", checklist)
        self.assertIn("production_claim_allowed: false", checklist)

    def test_public_alpha_safe_mode_remains_compatible(self) -> None:
        text = PUBLIC_ALPHA_SAFE_MODE.read_text(encoding="utf-8").casefold()
        self.assertIn("public search safety / abuse guard v0", text)
        self.assertIn("hosted public search is not live", text)
        self.assertIn("telemetry defaults off", text)


if __name__ == "__main__":
    unittest.main()
