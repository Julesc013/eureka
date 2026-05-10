
import copy
import json
import unittest
from pathlib import Path

from scripts.check_mvp_alpha_operator_signoff import validate_signoff
from scripts.validate_mvp_alpha_operator_review import detect_forbidden_operator_review_claims

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = REPO_ROOT / "examples/audits/mvp_alpha_operator/operator_signoff_packet_unsigned_v0.json"


class MvpAlphaOperatorSignoffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_unsigned_signoff_is_not_approval(self) -> None:
        self.assertEqual(validate_signoff(self.packet), [])
        self.assertEqual(self.packet["signoff_status"], "unsigned")
        self.assertIsNone(self.packet["signed_at_future"])

    def test_pass_status_does_not_infer_approval(self) -> None:
        payload = {"status": "pass", "explicit_operator_approval": False, "operator_signoff_inferred": False}
        self.assertEqual(detect_forbidden_operator_review_claims(payload), [])

    def test_approval_cannot_be_inferred_from_previous_status(self) -> None:
        broken = copy.deepcopy(self.packet)
        broken["truth_boundary"]["operator_signoff_inferred"] = True
        self.assertTrue(any("operator_signoff_inferred" in error for error in validate_signoff(broken)))

    def test_signed_future_current_example_fails(self) -> None:
        broken = copy.deepcopy(self.packet)
        broken["signoff_status"] = "signed_future"
        self.assertTrue(validate_signoff(broken))

    def test_deployment_allowed_true_fails(self) -> None:
        broken = {"deployment_allowed_current": True}
        self.assertTrue(any("deployment_allowed_current" in error for error in detect_forbidden_operator_review_claims(broken)))


if __name__ == "__main__":
    unittest.main()
