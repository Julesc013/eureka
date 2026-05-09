import json
import unittest
from pathlib import Path

from scripts.validate_hosting_readiness import REQUIRED_POLICIES, detect_forbidden_hosting_claims

REPO_ROOT = Path(__file__).resolve().parents[2]


class HostingPolicyTests(unittest.TestCase):
    def load_json(self, relative: str) -> dict:
        return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))

    def test_required_policies_exist(self) -> None:
        for relative in REQUIRED_POLICIES:
            self.assertTrue((REPO_ROOT / relative).is_file(), relative)
            self.assertIn("schema_version", self.load_json(relative))

    def test_no_deploy_policy_blocks_provider_actions(self) -> None:
        policy = self.load_json("control/inventory/hosting/hosting_no_deploy_policy.json")
        self.assertTrue(policy["no_provider_api_calls"])
        self.assertTrue(policy["no_dns_changes"])
        self.assertTrue(policy["no_deployment"])
        self.assertTrue(policy["no_generated_site_distribution_regeneration"])

    def test_truth_policy_blocks_launch_and_safety_claims(self) -> None:
        policy = self.load_json("control/inventory/hosting/hosting_truth_policy.json")
        self.assertTrue(policy["hosting_readiness_is_not_launch"])
        self.assertFalse(policy["public_alpha_live_claimed"])
        self.assertFalse(policy["production_claimed"])
        self.assertFalse(policy["public_index_mutation_allowed"])
        self.assertFalse(policy["master_index_mutation_allowed"])

    def test_positive_claims_are_rejected(self) -> None:
        payload = {
            "public_alpha_live_claimed": True,
            "production_claimed": True,
            "rights_clearance_claimed": True,
            "malware_safety_claimed": True,
            "verified_installability_claimed": True,
        }
        self.assertEqual(len(detect_forbidden_hosting_claims(payload)), 5)


if __name__ == "__main__":
    unittest.main()
