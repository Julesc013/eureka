import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "control/inventory/hunt_warning_zero_result.json"
DISPOSITION = ROOT / "control/inventory/hunt_warning_zero_warning_disposition.json"
REPORT = ROOT / "control/audits/hunt-warning-zero-01-v0/hunt_warning_zero_report.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class HuntWarningZeroTests(unittest.TestCase):
    def test_result_records_zero_current_warnings(self):
        payload = load_json(RESULT)
        self.assertEqual("hunt_warning_zero_result.v0", payload["schema_version"])
        self.assertEqual("pass", payload["status"])
        self.assertEqual(0, payload["warnings_remaining"])
        self.assertEqual(0, payload["hard_blockers_remaining"])
        self.assertTrue(payload["aide_eval_green"])
        self.assertTrue(payload["aide_report_size_clean"])

    def test_warning_disposition_covers_all_current_warnings(self):
        payload = load_json(DISPOSITION)
        self.assertEqual("hunt_warning_zero_warning_disposition.v0", payload["schema_version"])
        self.assertEqual(payload["warnings_before"], payload["warnings_resolved"])
        self.assertEqual(0, payload["warnings_remaining"])
        self.assertEqual(0, payload["child_tasks_created"])

    def test_report_matches_result_boundaries(self):
        result = load_json(RESULT)
        report = load_json(REPORT)
        for key in (
            "source_probe_executed",
            "extraction_executed",
            "model_provider_used",
            "deployment_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
        ):
            self.assertFalse(result[key], key)
            self.assertFalse(report[key], key)


if __name__ == "__main__":
    unittest.main()
