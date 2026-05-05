import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ManualObservationBatch0StatusReporterTests(unittest.TestCase):
    def test_reporter_json_parses(self):
        completed = subprocess.run(
            [sys.executable, "scripts/report_manual_observation_batch_0_status.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["batch_id"], "batch_0")
        self.assertIn("observed_count", payload)
        self.assertIn("pending_count", payload)
        self.assertEqual(payload["hard_booleans"]["external_calls_performed"], False)
        self.assertEqual(payload["hard_booleans"]["web_browsing_performed"], False)
        self.assertEqual(payload["hard_booleans"]["fabricated_observations"], False)


if __name__ == "__main__":
    unittest.main()

