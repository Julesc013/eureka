import json
import unittest
from pathlib import Path

from runtime.hosting.launch_evidence import validate_public_launch_evidence_packet
from runtime.hosting.readiness import validate_public_launch_readiness_audit

REPO_ROOT = Path(__file__).resolve().parents[2]


class PublicLaunchEvidenceTests(unittest.TestCase):
    def load_json(self, relative: str) -> dict:
        return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))

    def test_operator_signoff_required_and_not_inferred(self) -> None:
        packet = self.load_json("examples/hosting/launch/public_launch_evidence_packet_required_v0.json")
        self.assertTrue(packet["operator_signoff_required"])
        self.assertEqual(validate_public_launch_evidence_packet(packet, {})["status"], "pass")
        signoff = self.load_json("examples/hosting/launch/public_launch_operator_signoff_required_v0.json")
        self.assertFalse(signoff["explicit_approval"])

    def test_public_alpha_and_production_claims_fail(self) -> None:
        audit = self.load_json("examples/hosting/launch/public_launch_readiness_audit_v0.json")
        audit["readiness_status"] = "ready_for_public_alpha_future"
        result = validate_public_launch_readiness_audit(audit, {})
        self.assertEqual(result["status"], "fail")

    def test_readiness_audit_currently_local_only(self) -> None:
        audit = self.load_json("examples/hosting/launch/public_launch_readiness_audit_v0.json")
        result = validate_public_launch_readiness_audit(audit, {})
        self.assertEqual(result["status"], "pass", result)
        self.assertIn("operator signoff", audit["missing_evidence"])


if __name__ == "__main__":
    unittest.main()
