from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "public-search-production-contract-v0"
REPORT_PATH = AUDIT_ROOT / "public_search_production_contract_report.json"
API_ROOT = REPO_ROOT / "contracts" / "api"


REQUIRED_AUDIT_FILES = {
    "README.md",
    "CONTRACT_SUMMARY.md",
    "ROUTE_CONTRACT.md",
    "REQUEST_CONTRACT.md",
    "RESPONSE_CONTRACT.md",
    "ERROR_CONTRACT.md",
    "RESULT_CARD_ALIGNMENT.md",
    "SOURCE_STATUS_CONTRACT.md",
    "EVIDENCE_SUMMARY_CONTRACT.md",
    "ABSENCE_AND_GAP_CONTRACT.md",
    "SAFETY_AND_LIMITS_CONTRACT.md",
    "VERSIONING_AND_COMPATIBILITY.md",
    "STATIC_TO_DYNAMIC_HANDOFF_REQUIREMENTS.md",
    "HOSTED_WRAPPER_REQUIREMENTS.md",
    "RUNTIME_NON_GOALS.md",
    "RISKS_AND_LIMITATIONS.md",
    "NEXT_STEPS.md",
    "COMMAND_RESULTS.md",
    "public_search_production_contract_report.json",
}

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
    "arbitrary_url_fetch_forbidden",
    "downloads_disabled",
    "installs_disabled",
    "uploads_disabled",
    "live_probes_disabled",
    "live_backend_unavailable",
    "rate_limited",
    "timeout",
    "bad_request",
    "internal_error_public_safe",
}


def _load_json(relative: str) -> dict:
    return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))


class PublicSearchProductionContractTest(unittest.TestCase):
    def test_audit_pack_and_report_exist(self) -> None:
        self.assertTrue(AUDIT_ROOT.is_dir())
        present = {path.name for path in AUDIT_ROOT.iterdir() if path.is_file()}
        self.assertTrue(REQUIRED_AUDIT_FILES.issubset(present))
        self.assertEqual(_load_json(str(REPORT_PATH.relative_to(REPO_ROOT)))["report_id"], "public_search_production_contract_v0")

    def test_request_contract_is_bounded_and_local_index_only(self) -> None:
        payload = _load_json("contracts/api/search_request.v0.json")
        props = payload["properties"]
        self.assertEqual(props["q"]["maxLength"], 160)
        self.assertEqual(props["limit"]["default"], 10)
        self.assertEqual(props["limit"]["maximum"], 25)
        self.assertEqual(props["mode"]["enum"], ["local_index_only"])
        self.assertTrue({"snapshot", "native_client"}.issubset(set(props["profile"]["enum"])))
        include_enum = set(props["include"]["items"]["enum"])
        self.assertTrue({"evidence", "compatibility", "source_summary", "limitations", "gaps", "actions"}.issubset(include_enum))
        self.assertTrue(REQUIRED_FORBIDDEN_PARAMETERS.issubset(set(payload["x-forbidden_parameters"])))

    def test_response_contract_has_production_fields_and_false_flags(self) -> None:
        payload = _load_json("contracts/api/search_response.v0.json")
        props = payload["properties"]
        for field in (
            "result_count",
            "checked",
            "limitations",
            "absence",
            "source_status",
            "timing",
            "request_limits",
            "next_actions",
        ):
            self.assertIn(field, props)
        for flag in (
            "live_probes_enabled",
            "downloads_enabled",
            "uploads_enabled",
            "installs_enabled",
            "local_paths_enabled",
            "arbitrary_url_fetch_enabled",
            "telemetry_enabled",
        ):
            self.assertEqual(props[flag]["const"], False)
        self.assertEqual(payload["x-source_status_schema"], "contracts/api/source_status.v0.json")

    def test_error_codes_and_public_safe_fields_present(self) -> None:
        payload = _load_json("contracts/api/error_response.v0.json")
        props = payload["properties"]
        codes = set(props["error"]["properties"]["code"]["enum"])
        self.assertTrue(REQUIRED_ERROR_CODES.issubset(codes))
        self.assertIn("severity", props["error"]["required"])
        self.assertIn("request_limits", props)
        self.assertIn("no_stack_traces", payload["x-public_safe_error_rules"])

    def test_source_evidence_absence_status_schemas_exist(self) -> None:
        for name in (
            "source_status.v0.json",
            "evidence_summary.v0.json",
            "absence_report.v0.json",
            "public_search_status.v0.json",
        ):
            with self.subTest(name=name):
                self.assertTrue((API_ROOT / name).is_file())
                payload = json.loads((API_ROOT / name).read_text(encoding="utf-8"))
                self.assertEqual(payload["x-status"], "contract_only")

        source = _load_json("contracts/api/source_status.v0.json")
        self.assertIn("live_disabled", source["properties"]["status"]["enum"])
        absence = _load_json("contracts/api/absence_report.v0.json")
        self.assertIn("source_gap", absence["properties"]["absence_status"]["enum"])
        status = _load_json("contracts/api/public_search_status.v0.json")
        self.assertEqual(status["properties"]["hosted_search_implemented"]["const"], False)

    def test_report_does_not_claim_hosting_or_live_behavior(self) -> None:
        report = _load_json("control/audits/public-search-production-contract-v0/public_search_production_contract_report.json")
        for key in (
            "hosted_search_implemented",
            "dynamic_backend_deployed",
            "live_probes_enabled",
            "downloads_enabled",
            "uploads_enabled",
            "installs_enabled",
            "local_paths_enabled",
            "arbitrary_url_fetch_enabled",
            "telemetry_enabled",
        ):
            self.assertFalse(report[key])
        self.assertEqual(report["active_mode"], "local_index_only")
        self.assertEqual(report["next_recommended_branch"], "P54 Hosted Public Search Wrapper v0")

    def test_hosted_wrapper_and_static_handoff_requirements_are_documented(self) -> None:
        wrapper = (AUDIT_ROOT / "HOSTED_WRAPPER_REQUIREMENTS.md").read_text(encoding="utf-8")
        handoff = (AUDIT_ROOT / "STATIC_TO_DYNAMIC_HANDOFF_REQUIREMENTS.md").read_text(encoding="utf-8").casefold()
        for env_var in (
            "EUREKA_PUBLIC_MODE",
            "EUREKA_SEARCH_MODE",
            "EUREKA_ALLOW_LIVE_PROBES",
            "EUREKA_ALLOW_DOWNLOADS",
            "EUREKA_ALLOW_UPLOADS",
            "EUREKA_ALLOW_LOCAL_PATHS",
            "EUREKA_ALLOW_ARBITRARY_URL_FETCH",
            "EUREKA_MAX_QUERY_LEN",
            "EUREKA_MAX_RESULTS",
            "EUREKA_GLOBAL_TIMEOUT_MS",
        ):
            self.assertIn(env_var, wrapper)
        self.assertIn("no fake hosted url", handoff)
        self.assertIn("github pages remains static-only", handoff)


if __name__ == "__main__":
    unittest.main()
