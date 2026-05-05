import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class NpmMetadataConnectorRuntimePlanValidatorTests(unittest.TestCase):
    def test_validator_passes(self):
        completed = subprocess.run(
            [sys.executable, "scripts/validate_npm_metadata_connector_runtime_plan.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("status: valid", completed.stdout)

    def test_validator_json_parses(self):
        completed = subprocess.run(
            [sys.executable, "scripts/validate_npm_metadata_connector_runtime_plan.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["readiness_decision"], "blocked_connector_approval_pending")

    def test_operations_doc_says_planning_only(self):
        text = (ROOT / "docs" / "operations" / "NPM_METADATA_CONNECTOR_RUNTIME_PLAN.md").read_text(encoding="utf-8").lower()
        for phrase in (
            "planning-only",
            "no runtime",
            "no external calls",
            "no arbitrary package",
            "no tarball download",
            "no install",
            "no dependency resolution",
            "no lifecycle script",
            "no mutation",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
