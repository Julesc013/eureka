import copy
import json
import unittest
from pathlib import Path

from scripts.check_local_mvp_deployment_deferral import check_deferral
from scripts.select_local_mvp_next_task import select_next_task
from scripts.validate_local_mvp_iteration import detect_forbidden_local_mvp_claims

ROOT = Path(__file__).resolve().parents[2]


class LocalMvpNextTaskDecisionTest(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((ROOT / "examples/audits/local_mvp/local_mvp_iteration_plan_v0.json").read_text(encoding="utf-8"))
        self.deferral = json.loads((ROOT / "examples/audits/local_mvp/local_mvp_deployment_deferral_v0.json").read_text(encoding="utf-8"))

    def test_selects_h2(self):
        result = select_next_task(self.plan)
        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertEqual(result["selected_next_task"], "H2-BUNDLE-01")
        self.assertFalse(result["deployment_allowed_current"])
        self.assertFalse(result["launch_allowed_current"])

    def test_deployment_execution_route_fails_without_approval(self):
        plan = copy.deepcopy(self.plan)
        plan["recommended_next_task"] = "PUBLIC-ALPHA-OPERATOR-DEPLOYMENT-APPROVAL-01"
        result = select_next_task(plan)
        self.assertEqual(result["status"], "fail")

    def test_deployment_deferral_passes(self):
        result = check_deferral(self.deferral)
        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertTrue(result["deployment_deferred"])

    def test_planning_only_approval_does_not_allow_deployment(self):
        payload = copy.deepcopy(self.deferral)
        payload["deployment_approval_present"] = True
        result = check_deferral(payload)
        self.assertEqual(result["status"], "fail")

    def test_forbidden_public_alpha_live_claim_fails(self):
        payload = {"truth_boundary": {"public_alpha_live_claimed": True}}
        self.assertTrue(detect_forbidden_local_mvp_claims(payload))

    def test_forbidden_production_claim_fails(self):
        payload = {"truth_boundary": {"production_claimed": True}}
        self.assertTrue(detect_forbidden_local_mvp_claims(payload))

    def test_forbidden_public_index_mutation_fails(self):
        payload = {"product_boundary": {"mutated_public_index": True}}
        self.assertTrue(detect_forbidden_local_mvp_claims(payload))

    def test_provider_token_fixture_fails(self):
        payload = {"token": "ghp_123456789abcdef"}
        self.assertTrue(detect_forbidden_local_mvp_claims(payload))

    def test_rights_malware_installability_claims_fail(self):
        payload = {
            "truth_boundary": {
                "rights_clearance_claimed": True,
                "malware_safety_claimed": True,
                "verified_installability_claimed": True,
            }
        }
        self.assertGreaterEqual(len(detect_forbidden_local_mvp_claims(payload)), 3)


if __name__ == "__main__":
    unittest.main()
