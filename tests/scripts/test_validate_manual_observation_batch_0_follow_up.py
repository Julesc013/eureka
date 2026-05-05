import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "control" / "audits" / "manual-observation-batch-0-follow-up-plan-v0"
REPORT = AUDIT / "manual_observation_batch_0_follow_up_report.json"
INVENTORY = ROOT / "control" / "inventory" / "external_baselines" / "manual_observation_batch_0_follow_up.json"
DOC = ROOT / "docs" / "operations" / "MANUAL_OBSERVATION_BATCH_0_FOLLOW_UP.md"


class ManualObservationBatch0FollowUpValidatorTests(unittest.TestCase):
    def test_validator_passes(self):
        completed = subprocess.run(
            [sys.executable, "scripts/validate_manual_observation_batch_0_follow_up.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_validator_json_parses(self):
        completed = subprocess.run(
            [sys.executable, "scripts/validate_manual_observation_batch_0_follow_up.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")

    def test_negative_hard_booleans_fail(self):
        cases = (
            "external_calls_performed",
            "fabricated_observations",
            "manual_observations_performed_by_codex",
            "public_index_mutated",
            "master_index_mutated",
        )
        for field in cases:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                report_path = Path(tmp) / "report.json"
                payload = json.loads(REPORT.read_text(encoding="utf-8"))
                payload[field] = True
                report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
                completed = subprocess.run(
                    [
                        sys.executable,
                        "scripts/validate_manual_observation_batch_0_follow_up.py",
                        "--audit-dir",
                        str(AUDIT),
                        "--report",
                        str(report_path),
                        "--inventory",
                        str(INVENTORY),
                        "--doc",
                        str(DOC),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn(field, completed.stdout)


if __name__ == "__main__":
    unittest.main()

