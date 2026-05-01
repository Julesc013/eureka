from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "hosted-public-search-wrapper-v0"
REPORT_PATH = AUDIT_ROOT / "hosted_public_search_wrapper_report.json"

REQUIRED_AUDIT_FILES = {
    "README.md",
    "WRAPPER_SUMMARY.md",
    "HOSTED_MODE_REQUIREMENTS.md",
    "ROUTE_IMPLEMENTATION_STATUS.md",
    "ENVIRONMENT_VARIABLES.md",
    "SAFETY_DEFAULTS.md",
    "HEALTH_AND_STATUS_ENDPOINTS.md",
    "DEPLOYMENT_TEMPLATE_REVIEW.md",
    "LOCAL_REHEARSAL_RESULTS.md",
    "PUBLIC_CLAIM_REVIEW.md",
    "OPERATOR_DEPLOYMENT_STEPS.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "COMMAND_RESULTS.md",
    "hosted_public_search_wrapper_report.json",
}

HARD_FALSE_KEYS = {
    "hosted_backend_deployed",
    "hosted_deployment_verified",
    "dynamic_backend_deployed",
    "live_probes_enabled",
    "downloads_enabled",
    "uploads_enabled",
    "local_paths_enabled",
    "arbitrary_url_fetch_enabled",
    "telemetry_enabled",
    "accounts_enabled",
    "external_calls_enabled",
    "ai_runtime_enabled",
}


class HostedPublicSearchWrapperAuditTest(unittest.TestCase):
    def test_audit_pack_and_report_exist(self) -> None:
        self.assertTrue(AUDIT_ROOT.is_dir())
        present = {path.name for path in AUDIT_ROOT.iterdir() if path.is_file()}
        self.assertTrue(REQUIRED_AUDIT_FILES.issubset(present))
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(report["report_id"], "hosted_public_search_wrapper_v0")
        self.assertTrue(report["hosted_wrapper_implemented"])
        self.assertEqual(report["public_search_mode"], "local_index_only")

    def test_report_keeps_hard_booleans_closed(self) -> None:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        for key in HARD_FALSE_KEYS:
            with self.subTest(key=key):
                self.assertIs(report[key], False)
        self.assertEqual(report["local_rehearsal_results"]["status"], "passed")
        self.assertEqual(report["local_rehearsal_results"]["failed_checks"], 0)

    def test_scripts_and_docs_exist(self) -> None:
        for relative in (
            "scripts/run_hosted_public_search.py",
            "scripts/check_hosted_public_search_wrapper.py",
            "scripts/validate_hosted_public_search_wrapper.py",
            "docs/operations/HOSTED_PUBLIC_SEARCH.md",
            "docs/operations/PUBLIC_SEARCH_HOSTING.md",
            "docs/operations/PUBLIC_SEARCH_ENVIRONMENT.md",
            "docs/operations/PUBLIC_SEARCH_ROLLBACK.md",
        ):
            with self.subTest(relative=relative):
                self.assertTrue((REPO_ROOT / relative).is_file())

    def test_docs_record_not_deployed_and_safe_mode(self) -> None:
        combined = "\n".join(
            (REPO_ROOT / relative).read_text(encoding="utf-8").casefold()
            for relative in (
                "docs/operations/HOSTED_PUBLIC_SEARCH.md",
                "docs/operations/PUBLIC_SEARCH_HOSTING.md",
                "docs/operations/PUBLIC_SEARCH_ENVIRONMENT.md",
                "docs/operations/PUBLIC_SEARCH_ROLLBACK.md",
            )
        )
        self.assertIn("local_index_only", combined)
        self.assertIn("not deployed", combined)
        self.assertIn("no live probes", combined)
        self.assertIn("no telemetry", combined)

    def test_deployment_templates_are_safe_placeholders(self) -> None:
        dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("scripts/run_hosted_public_search.py", dockerfile)
        for phrase in (
            "EUREKA_SEARCH_MODE=local_index_only",
            "EUREKA_ALLOW_LIVE_PROBES=0",
            "EUREKA_ALLOW_DOWNLOADS=0",
            "EUREKA_ALLOW_UPLOADS=0",
            "EUREKA_ALLOW_LOCAL_PATHS=0",
            "EUREKA_ALLOW_ARBITRARY_URL_FETCH=0",
        ):
            self.assertIn(phrase, dockerfile)

        render = (REPO_ROOT / "deploy" / "render" / "render.yaml").read_text(encoding="utf-8")
        self.assertIn("healthCheckPath: /healthz", render)
        self.assertIn("local_index_only", render)
        self.assertNotIn("api_key", render.casefold())
        self.assertNotIn("auth_token", render.casefold())


if __name__ == "__main__":
    unittest.main()
