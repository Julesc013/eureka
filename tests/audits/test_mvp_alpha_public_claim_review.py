
import copy
import json
import unittest
from pathlib import Path

from scripts.check_mvp_alpha_public_claims import check_public_claim_inputs
from scripts.validate_mvp_alpha_operator_review import detect_forbidden_operator_review_claims

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = REPO_ROOT / "examples/audits/mvp_alpha_operator/public_claim_review_v0.json"


class MvpAlphaPublicClaimReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.review = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_public_claim_review_validates(self) -> None:
        report = check_public_claim_inputs(["examples/audits/mvp_alpha_operator"])
        self.assertEqual(report["status"], "pass", report["errors"])
        self.assertIn("production_ready", self.review["forbidden_claims"])

    def test_public_alpha_live_claim_fails(self) -> None:
        broken = {"public_alpha_live": True}
        self.assertTrue(detect_forbidden_operator_review_claims(broken))

    def test_production_claim_fails(self) -> None:
        broken = {"production_claimed": True}
        self.assertTrue(detect_forbidden_operator_review_claims(broken))

    def test_provider_token_fixture_fails(self) -> None:
        broken = {"token": "ghp_1234567890abcdef"}
        self.assertTrue(detect_forbidden_operator_review_claims(broken))

    def test_public_and_master_index_mutation_claims_fail(self) -> None:
        broken = {"public_index_mutated": True, "master_index_mutated": True}
        errors = detect_forbidden_operator_review_claims(broken)
        self.assertTrue(any("public_index_mutated" in error for error in errors))
        self.assertTrue(any("master_index_mutated" in error for error in errors))

    def test_rights_malware_installability_claims_fail(self) -> None:
        broken = {
            "rights_clearance_claimed": True,
            "malware_safety_claimed": True,
            "verified_installability_claimed": True,
        }
        errors = detect_forbidden_operator_review_claims(broken)
        self.assertEqual(len(errors), 3)


if __name__ == "__main__":
    unittest.main()
