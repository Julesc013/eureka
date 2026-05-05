import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PublicHostedDeploymentVerifierTests(unittest.TestCase):
    def test_json_with_no_urls_is_operator_gated(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify_public_hosted_deployment.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertTrue(report["ok"])
        self.assertEqual(report["static_site_status"], "not_configured")
        self.assertEqual(report["hosted_backend_status"], "not_configured")
        self.assertEqual(report["route_verification_status"], "not_configured")
        self.assertEqual(report["safety_verification_status"], "operator_gated")
        self.assertFalse(report["hard_booleans"]["deployment_verified"])
        self.assertFalse(report["hard_booleans"]["hosted_public_search_live"])

    def test_strict_requires_configured_verification(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify_public_hosted_deployment.py", "--json", "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        report = json.loads(completed.stdout)
        self.assertFalse(report["ok"])
        self.assertEqual(report["static_site_status"], "not_configured")

    def test_rejects_unsafe_url_scheme_before_network(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/verify_public_hosted_deployment.py",
                "--static-url",
                "file:///tmp/not-a-public-url",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertIsNone(report["static_url"])
        self.assertEqual(report["static_site_status"], "not_configured")
        self.assertTrue(any("scheme is not http/https" in item for item in report["warnings"]))

    def test_rejects_non_explicit_non_eureka_repo_url(self) -> None:
        from scripts import verify_public_hosted_deployment as verifier

        warnings: list[str] = []
        result = verifier._choose_valid_url(  # noqa: SLF001 - testing verifier boundary helper.
            [verifier.ConfiguredUrl("https://example.invalid/eureka/", "repo:test", False)],
            role="static",
            warnings=warnings,
        )
        self.assertIsNone(result)
        self.assertTrue(any("not a recognized Eureka public URL" in warning for warning in warnings))

    def test_secret_query_params_are_redacted(self) -> None:
        from scripts import verify_public_hosted_deployment as verifier

        redacted = verifier._redact_url(  # noqa: SLF001 - testing public redaction guarantee.
            "https://example.invalid/search?q=windows&api_key=secret-value&auth_token=secret-value"
        )
        self.assertNotIn("secret-value", redacted or "")
        self.assertIn("%3Credacted%3E", redacted or "")


if __name__ == "__main__":
    unittest.main()
