
import json
import unittest
from pathlib import Path

from scripts.validate_mvp_alpha_audit import detect_forbidden_mvp_claims

REPO_ROOT = Path(__file__).resolve().parents[2]


class MvpAlphaGateDecisionTests(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((REPO_ROOT / "examples/audits/mvp_alpha" / name).read_text(encoding="utf-8"))

    def test_gate_cannot_allow_deployment_or_launch(self) -> None:
        gate = self.load("mvp_alpha_gate_decision_ready_for_operator_review_v0.json")
        self.assertTrue(gate["operator_review_required"])
        self.assertFalse(gate["launch_allowed_current"])
        self.assertFalse(gate["deployment_allowed_current"])
        self.assertFalse(gate["public_alpha_live_claim_allowed"])
        self.assertFalse(gate["production_claim_allowed"])

    def test_operator_signoff_cannot_be_inferred(self) -> None:
        packet = self.load("mvp_alpha_operator_review_packet_v0.json")
        self.assertEqual(packet["review_status"], "operator_review_required")
        self.assertFalse(packet["truth_boundary"]["operator_signoff_inferred"])
        self.assertIn("Operator launch decision", packet["required_signoffs"])

    def test_needs_remediation_gate_remains_non_deploying(self) -> None:
        gate = self.load("mvp_alpha_gate_decision_needs_remediation_v0.json")
        self.assertEqual(gate["decision"], "NEEDS_REMEDIATION")
        self.assertTrue(gate["remediation_required"])
        self.assertFalse(gate["deployment_allowed_current"])

    def test_unsafe_claims_are_rejected(self) -> None:
        for payload in (
            {"truth_boundary": {"master_index_mutated": True}},
            {"truth_boundary": {"malware_safety_claimed": True}},
            {"truth_boundary": {"verified_installability_claimed": True}},
            {"product_boundary": {"enabled_uploads": True}},
            {"product_boundary": {"enabled_accounts": True}},
            {"product_boundary": {"enabled_telemetry": True}},
        ):
            self.assertTrue(detect_forbidden_mvp_claims(payload))


if __name__ == "__main__":
    unittest.main()
