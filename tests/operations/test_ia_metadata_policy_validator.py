import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class IAMetadataPolicyValidatorTests(unittest.TestCase):
    def test_validator_script_passes(self):
        completed = subprocess.run(
            [sys.executable, "scripts/validate_ia_metadata_policy.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"], payload)
        self.assertFalse(payload["live_calls_enabled"])
        self.assertFalse(payload["source_probe_execution_enabled"])
        self.assertFalse(payload["downloads_enabled"])
        self.assertFalse(payload["source_cache_writes_enabled"])
        self.assertFalse(payload["evidence_ledger_writes_enabled"])
        self.assertFalse(payload["candidate_index_mutation_enabled"])
        self.assertFalse(payload["reviewed_index_mutation_enabled"])
        self.assertFalse(payload["master_index_mutation_enabled"])


if __name__ == "__main__":
    unittest.main()
