import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DryRunQueryObservationTests(unittest.TestCase):
    def _run(self, query: str) -> dict:
        completed = subprocess.run(
            [sys.executable, "scripts/dry_run_query_observation.py", "--query", query, "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(completed.stdout)

    def test_public_safe_dry_run(self) -> None:
        observation = self._run("windows 7 apps")
        self.assertEqual(observation["status"], "dry_run_validated")
        self.assertFalse(observation["raw_query_policy"]["raw_query_retained"])
        self.assertFalse(observation["no_mutation_guarantees"]["master_index_mutated"])
        self.assertEqual(observation["normalized_query"]["text"], "windows 7 apps")

    def test_dry_run_output_validates(self) -> None:
        observation = self._run("windows 7 apps")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "QUERY_OBSERVATION.json"
            path.write_text(json.dumps(observation, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_query_observation.py", "--observation", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")

    def test_private_path_rejected_by_privacy_filter(self) -> None:
        observation = self._run("C:\\Users\\Alice\\private.txt")
        self.assertEqual(observation["status"], "rejected_by_privacy_filter")
        self.assertTrue(observation["privacy"]["private_path_detected"])
        self.assertFalse(observation["privacy"]["public_aggregate_allowed"])
        self.assertEqual(observation["normalized_query"]["text"], "<redacted>")


if __name__ == "__main__":
    unittest.main()
