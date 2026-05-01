import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "probe_queue" / "minimal_source_cache_probe_v0" / "PROBE_QUEUE_ITEM.json"


class ProbeQueueItemValidatorTests(unittest.TestCase):
    def test_all_examples_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_probe_queue_item.py", "--all-examples"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_all_examples_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_probe_queue_item.py", "--all-examples", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 3)

    def test_private_path_item_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["probe_identity"]["canonical_probe_label"] = "C:\\Users\\Alice\\private.txt"
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("windows_absolute_path" in error for error in report["errors"]))

    def test_secret_marker_item_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["probe_identity"]["canonical_probe_label"] = "api_key should not be here"
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("api_key_marker" in error for error in report["errors"]))

    def test_probe_execution_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["no_execution_guarantees"]["probe_executed"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("probe_executed" in error for error in report["errors"]))

    def test_live_source_call_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["no_execution_guarantees"]["live_source_called"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("live_source_called" in error for error in report["errors"]))

    def test_master_index_mutation_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["no_mutation_guarantees"]["master_index_mutated"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("master_index_mutated" in error for error in report["errors"]))

    def test_source_cache_mutation_fails(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["no_mutation_guarantees"]["source_cache_mutated"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("source_cache_mutated" in error for error in report["errors"]))

    def test_live_network_requires_approval(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["probe_kind"]["approval_required"] = False
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("approval_required" in error for error in report["errors"]))

    def test_safety_requirements_cannot_disable_download_guard(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["safety_requirements"]["no_downloads"] = False
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("no_downloads" in error for error in report["errors"]))

    def test_non_reversible_fingerprint_required(self) -> None:
        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        payload["probe_identity"]["probe_fingerprint"]["reversible"] = True
        report = self._validate_temp(payload)
        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("reversible" in error for error in report["errors"]))

    def _validate_temp(self, payload: dict) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "PROBE_QUEUE_ITEM.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "scripts/validate_probe_queue_item.py", "--item", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
