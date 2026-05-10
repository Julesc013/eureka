import json
import unittest
from pathlib import Path

from scripts.validate_local_mvp_iteration import REQUIRED_CONTRACTS, REQUIRED_EXAMPLES, validate_local_mvp_iteration

ROOT = Path(__file__).resolve().parents[2]


class LocalMvpIterationContractsTest(unittest.TestCase):
    def test_validator_passes_current_repo(self):
        report = validate_local_mvp_iteration(ROOT)
        self.assertEqual(report["status"], "pass", report["errors"])

    def test_contracts_are_valid_json(self):
        for relative in REQUIRED_CONTRACTS:
            with self.subTest(relative=relative):
                payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                self.assertIn("schema_version", payload["properties"])
                self.assertTrue(payload["required"])

    def test_examples_are_valid_json(self):
        for relative in REQUIRED_EXAMPLES:
            with self.subTest(relative=relative):
                payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                self.assertIn("schema_version", payload)

    def test_h2_is_recommended_and_deployment_deferred(self):
        plan = json.loads((ROOT / "examples/audits/local_mvp/local_mvp_iteration_plan_v0.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["recommended_next_task"], "H2-BUNDLE-01")
        self.assertTrue(plan["deployment_deferral"]["deployment_deferred"])
        self.assertFalse(plan["deployment_deferral"]["deployment_approval_present"])

    def test_deferred_options_are_not_selected(self):
        for name in ("h3", "j1_deferred", "k_deferred", "l_deferred"):
            matches = list((ROOT / "examples/audits/local_mvp").glob(f"local_mvp_next_wave_option_{name}_v0.json"))
            self.assertEqual(len(matches), 1)
            option = json.loads(matches[0].read_text(encoding="utf-8"))
            self.assertEqual(option["option_status"], "deferred")


if __name__ == "__main__":
    unittest.main()
