import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "query_observations" / "minimal_query_observation_v0" / "QUERY_OBSERVATION.json"


class QueryObservationValidatorTests(unittest.TestCase):
    def test_all_examples_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_query_observation.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_all_examples_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_query_observation.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 1)

    def test_private_path_observation_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["normalized_query"]["text"] = "C:\\Users\\Alice\\private.txt"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "QUERY_OBSERVATION.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_query_observation.py", "--observation", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("windows_absolute_path" in error for error in report["errors"]))

    def test_secret_marker_observation_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["normalized_query"]["text"] = "api_key should not be here"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "QUERY_OBSERVATION.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_query_observation.py", "--observation", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        report = json.loads(completed.stdout)
        self.assertTrue(any("api_key_marker" in error for error in report["errors"]))

    def test_master_index_mutation_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["no_mutation_guarantees"]["master_index_mutated"] = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "QUERY_OBSERVATION.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_query_observation.py", "--observation", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        report = json.loads(completed.stdout)
        self.assertTrue(any("master_index_mutated" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
