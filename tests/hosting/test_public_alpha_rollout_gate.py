
import copy
import json
import unittest
from pathlib import Path

from scripts.check_public_alpha_dns_readiness import check_dns_readiness
from scripts.validate_public_alpha_deployment_plan import detect_forbidden_deployment_claims

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_ROOT = REPO_ROOT / "examples/hosting/deployment"


class PublicAlphaRolloutGateTests(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((EXAMPLE_ROOT / name).read_text(encoding="utf-8"))

    def test_rollout_gate_validates(self) -> None:
        gate = self.load("public_alpha_rollout_gate_operator_required_v0.json")
        self.assertFalse(gate["launch_allowed_current"])
        self.assertFalse(gate["deployment_allowed_current"])
        self.assertIn("explicit_operator_deployment_approval", gate["missing_evidence"])

    def test_operator_checklist_validates(self) -> None:
        checklist = self.load("public_alpha_operator_checklist_v0.json")
        self.assertTrue(checklist["operator_signoff_required"])
        self.assertGreaterEqual(len(checklist["checklist_items"]), 10)

    def test_dns_readiness_unknown_validates(self) -> None:
        dns = self.load("public_alpha_dns_readiness_unknown_v0.json")
        self.assertEqual(check_dns_readiness(dns), [])

    def test_dns_configured_without_evidence_fails(self) -> None:
        dns = self.load("public_alpha_dns_readiness_unknown_v0.json")
        dns["custom_domain_status"] = "configured_future"
        self.assertTrue(check_dns_readiness(dns))

    def test_noop_report_validates(self) -> None:
        noop = self.load("public_alpha_deployment_noop_report_v0.json")
        self.assertFalse(noop["deployment_performed"])
        self.assertFalse(noop["provider_api_called"])
        self.assertFalse(noop["dns_changed"])

    def test_site_dist_and_operator_signoff_claims_fail(self) -> None:
        errors = detect_forbidden_deployment_claims({"site_dist_mutated": True, "operator_signoff_inferred": True})
        self.assertEqual(len(errors), 2)


if __name__ == "__main__":
    unittest.main()
