from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUEST_SCHEMA = REPO_ROOT / "contracts" / "api" / "search_request.v0.json"
RESPONSE_SCHEMA = REPO_ROOT / "contracts" / "api" / "search_response.v0.json"
ERROR_SCHEMA = REPO_ROOT / "contracts" / "api" / "error_response.v0.json"
ROUTES = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_routes.json"
REFERENCE_DOC = REPO_ROOT / "docs" / "reference" / "PUBLIC_SEARCH_API_CONTRACT.md"
MODE_DOC = REPO_ROOT / "docs" / "operations" / "PUBLIC_SEARCH_LOCAL_INDEX_ONLY_MODE.md"
LIVE_PROBE_GATEWAY = REPO_ROOT / "control" / "inventory" / "publication" / "live_probe_gateway.json"
SITE_DIST = REPO_ROOT / "site" / "dist"


REQUIRED_FORBIDDEN_PARAMETERS = {
    "index_path",
    "store_root",
    "run_store_root",
    "task_store_root",
    "memory_store_root",
    "local_path",
    "path",
    "url",
    "fetch_url",
    "download",
    "install",
    "upload",
    "user_file",
    "live_probe",
    "source_credentials",
}
REQUIRED_ERROR_CODES = {
    "bad_request",
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
    "not_found",
    "internal_error",
}


class PublicSearchApiContractTest(unittest.TestCase):
    def test_schemas_and_route_inventory_parse(self) -> None:
        for path in (REQUEST_SCHEMA, RESPONSE_SCHEMA, ERROR_SCHEMA, ROUTES):
            with self.subTest(path=path):
                self.assertTrue(path.is_file())
                self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)

    def test_request_schema_is_local_index_only(self) -> None:
        payload = json.loads(REQUEST_SCHEMA.read_text(encoding="utf-8"))
        properties = payload["properties"]
        self.assertEqual(payload["required"], ["q"])
        self.assertEqual(properties["q"]["maxLength"], 160)
        self.assertEqual(properties["limit"]["default"], 10)
        self.assertEqual(properties["limit"]["maximum"], 25)
        self.assertEqual(properties["mode"]["enum"], ["local_index_only"])
        self.assertEqual(properties["source_policy"]["enum"], ["local_index_only"])
        self.assertNotIn("live_probe", properties["mode"]["enum"])

    def test_forbidden_parameters_present(self) -> None:
        payload = json.loads(REQUEST_SCHEMA.read_text(encoding="utf-8"))
        self.assertTrue(
            REQUIRED_FORBIDDEN_PARAMETERS.issubset(set(payload["x-forbidden_parameters"]))
        )

    def test_response_schema_has_result_and_source_envelopes(self) -> None:
        payload = json.loads(RESPONSE_SCHEMA.read_text(encoding="utf-8"))
        required = set(payload["required"])
        for field in ("results", "checked_sources", "gaps", "warnings", "stability"):
            self.assertIn(field, required)
        result_required = set(payload["$defs"]["result"]["required"])
        for field in (
            "result_id",
            "public_target_ref",
            "result_lane",
            "user_cost",
            "compatibility",
            "evidence",
            "actions",
            "limitations",
        ):
            self.assertIn(field, result_required)
        prohibited = set(payload["x-prohibited_result_fields"])
        self.assertIn("download_url", prohibited)
        self.assertIn("private_local_path", prohibited)

    def test_error_codes_present(self) -> None:
        payload = json.loads(ERROR_SCHEMA.read_text(encoding="utf-8"))
        codes = set(payload["properties"]["error"]["properties"]["code"]["enum"])
        self.assertTrue(REQUIRED_ERROR_CODES.issubset(codes))

    def test_routes_are_local_runtime_only_not_hosted(self) -> None:
        payload = json.loads(ROUTES.read_text(encoding="utf-8"))
        self.assertTrue(payload["implemented_now"])
        self.assertTrue(payload["runtime_routes_implemented"])
        self.assertEqual(payload["implementation_scope"], "local_prototype_backend")
        self.assertFalse(payload["hosted_public_runtime_implemented"])
        self.assertTrue(payload["static_handoff_implemented"])
        self.assertEqual(payload["contract_modes"], ["local_index_only"])
        by_path = {
            (route["method"], route["path_template"]): route
            for route in payload["routes"]
        }
        for key in (
            ("GET", "/search"),
            ("GET", "/api/v1/search"),
            ("GET", "/api/v1/query-plan"),
            ("GET", "/api/v1/status"),
            ("GET", "/api/v1/sources"),
            ("GET", "/api/v1/source/{source_id}"),
        ):
            with self.subTest(route=key):
                route = by_path[key]
                self.assertEqual(route["status"], "local_runtime_implemented")
                self.assertTrue(route["implemented_now"])
                self.assertEqual(route["implementation_scope"], "local_prototype_backend")
                self.assertFalse(route["hosted_public_deployment"])
                self.assertTrue(route["requires_backend"])
                self.assertFalse(route["live_probe_allowed"])
                self.assertFalse(route["downloads_allowed"])
                self.assertFalse(route["local_paths_allowed"])
                self.assertFalse(route["uploads_allowed"])
                self.assertEqual(route["allowed_modes"], ["local_index_only"])

    def test_docs_state_contract_only_and_forbid_unsafe_behaviors(self) -> None:
        combined = (
            REFERENCE_DOC.read_text(encoding="utf-8")
            + "\n"
            + MODE_DOC.read_text(encoding="utf-8")
        ).casefold()
        for phrase in (
            "contract-first",
            "local public search runtime v0",
            "local/prototype backend runtime only",
            "does not make public search hosted",
            "does not claim production api stability",
            "live external calls",
            "local path search",
            "downloads",
            "install",
            "uploads",
            "public search safety / abuse guard v0",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, combined)
        for claim in (
            "public search api is live",
            "/api/v1/search is live",
            "production api stability is guaranteed",
        ):
            with self.subTest(claim=claim):
                self.assertNotIn(claim, combined)

    def test_live_probe_gateway_remains_disabled(self) -> None:
        payload = json.loads(LIVE_PROBE_GATEWAY.read_text(encoding="utf-8"))
        self.assertTrue(payload["no_live_probes_implemented"])
        self.assertTrue(payload["no_network_calls_performed"])
        self.assertFalse(payload["enabled_by_default"])
        self.assertFalse(payload["global_limits"]["allow_arbitrary_url_fetch"])
        self.assertFalse(payload["global_limits"]["allow_downloads"])

    def test_static_site_does_not_claim_public_search_is_live(self) -> None:
        self.assertTrue(SITE_DIST.is_dir())
        bad_claims = (
            "public search api is live",
            "/api/v1/search is live",
            "users can search the hosted backend",
        )
        for path in SITE_DIST.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".html", ".txt", ".json"}:
                continue
            text = path.read_text(encoding="utf-8").casefold()
            for claim in bad_claims:
                with self.subTest(path=path, claim=claim):
                    self.assertNotIn(claim, text)


if __name__ == "__main__":
    unittest.main()
