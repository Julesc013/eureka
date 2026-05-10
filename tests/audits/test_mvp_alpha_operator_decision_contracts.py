
import json
import unittest
from pathlib import Path

from scripts.validate_mvp_alpha_operator_review import (
    DECISION_OPTIONS,
    validate_mvp_alpha_operator_review,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_ROOT = REPO_ROOT / "examples/audits/mvp_alpha_operator"


class MvpAlphaOperatorDecisionContractTests(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((EXAMPLE_ROOT / name).read_text(encoding="utf-8"))

    def test_operator_review_validator_passes_current_repo(self) -> None:
        report = validate_mvp_alpha_operator_review(REPO_ROOT)
        self.assertEqual(report["status"], "pass", report["errors"])

    def test_operator_decision_contract_examples_validate(self) -> None:
        decision = self.load("operator_decision_request_v0.json")
        self.assertEqual(set(decision["decision_options"]), DECISION_OPTIONS)
        self.assertFalse(decision["explicit_operator_approval"])
        self.assertFalse(decision["deployment_allowed_current"])
        self.assertFalse(decision["launch_allowed_current"])

    def test_launch_blocker_register_validates(self) -> None:
        register = self.load("launch_blocker_register_v0.json")
        self.assertIn("missing_explicit_operator_signoff", register["launch_blockers"])
        self.assertIn("deployment_execution_forbidden_current", register["deployment_blockers"])

    def test_next_task_routing_example_validates(self) -> None:
        route = self.load("operator_next_task_planning_v0.json")
        self.assertEqual(route["next_task_id"], "PUBLIC-ALPHA-DEPLOYMENT-PLAN-01")
        self.assertIn("deployment", route["next_task_forbidden_actions"])


if __name__ == "__main__":
    unittest.main()
