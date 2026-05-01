import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SourceCacheDryRunTests(unittest.TestCase):
    def test_dry_run_json_validates(self) -> None:
        completed = subprocess.run([sys.executable, "scripts/dry_run_source_cache_record.py", "--label", "IA metadata cache example", "--source-family", "internet_archive", "--kind", "source_metadata", "--json"], cwd=ROOT, text=True, capture_output=True, check=True)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "dry_run_validated")
        self.assertFalse(payload["no_runtime_guarantees"]["cache_write_performed"])
        self.assertFalse(payload["no_runtime_guarantees"]["live_source_called"])
        self._validate(payload)

    def test_private_label_redacted(self) -> None:
        completed = subprocess.run([sys.executable, "scripts/dry_run_source_cache_record.py", "--label", "cache C:\\Users\\Alice\\private.txt", "--source-family", "internet_archive", "--kind", "source_metadata", "--json"], cwd=ROOT, text=True, capture_output=True, check=True)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "rejected_by_policy")
        self.assertEqual(payload["cache_identity"]["canonical_cache_label"], "<redacted-source-cache-label>")
        self._validate(payload)

    def _validate(self, payload: dict) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SOURCE_CACHE_RECORD.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            completed = subprocess.run([sys.executable, "scripts/validate_source_cache_record.py", "--record", str(path), "--json"], cwd=ROOT, text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(completed.stdout)["status"], "valid")


if __name__ == "__main__":
    unittest.main()
