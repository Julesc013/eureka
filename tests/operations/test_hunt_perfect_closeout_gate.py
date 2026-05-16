import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "control/inventory/hunt_perfect_closeout_result.json"
DECISION = ROOT / "control/inventory/hunt_perfect_next_task_decision.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def gate_errors(payload):
    errors = []
    if payload.get("hard_blockers_remaining") != 0:
        errors.append("hard blockers remain")
    if payload.get("warnings_remaining") != 0 and payload.get("status") == "pass":
        errors.append("warnings cannot remain in pass")
    for key in (
        "aide_eval_green",
        "aide_report_size_clean",
        "all_hunt_validators_pass",
        "full_unittest_discovery_pass",
    ):
        if payload.get(key) is not True:
            errors.append(f"{key} must be true")
    for key in (
        "source_probe_executed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if payload.get(key) is not False:
            errors.append(f"{key} must be false")
    return errors


class HuntPerfectCloseoutGateTests(unittest.TestCase):
    def test_current_result_passes_gate(self):
        self.assertEqual([], gate_errors(load_json(RESULT)))

    def test_fails_if_hard_blocker_remains(self):
        payload = load_json(RESULT)
        payload["hard_blockers_remaining"] = 1
        self.assertIn("hard blockers remain", gate_errors(payload))

    def test_fails_if_warning_remains_under_pass_status(self):
        payload = load_json(RESULT)
        payload["warnings_remaining"] = 1
        self.assertIn("warnings cannot remain in pass", gate_errors(payload))

    def test_fails_if_aide_eval_or_report_size_is_not_green(self):
        for key in ("aide_eval_green", "aide_report_size_clean"):
            payload = load_json(RESULT)
            payload[key] = False
            self.assertIn(f"{key} must be true", gate_errors(payload))

    def test_fails_if_validation_or_forbidden_boundary_regresses(self):
        for key, expected in (
            ("all_hunt_validators_pass", f"all_hunt_validators_pass must be true"),
            ("full_unittest_discovery_pass", f"full_unittest_discovery_pass must be true"),
            ("source_probe_executed", f"source_probe_executed must be false"),
            ("extraction_executed", f"extraction_executed must be false"),
            ("model_provider_used", f"model_provider_used must be false"),
            ("deployment_performed", f"deployment_performed must be false"),
        ):
            payload = load_json(RESULT)
            payload[key] = not payload[key]
            self.assertIn(expected, gate_errors(payload))

    def test_next_task_points_to_promotion_when_green(self):
        decision = load_json(DECISION)
        self.assertEqual("HUNT-TO-MAIN-PROMOTION-REVIEW", decision["recommended_next_task"])
        self.assertIn("SYN-00", decision["alternative_next_task"])
        self.assertTrue(decision["syn_can_start"])
        self.assertTrue(decision["f0_can_resume"])
        self.assertFalse(decision["f0_recommended_now"])


if __name__ == "__main__":
    unittest.main()
