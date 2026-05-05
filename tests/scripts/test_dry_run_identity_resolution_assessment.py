import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DryRunIdentityResolutionAssessmentTests(unittest.TestCase):
    def test_dry_run_outputs_valid_json_without_runtime_or_mutation(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_identity_resolution_assessment.py",
                "--left-label",
                "Example App 1.0",
                "--right-label",
                "ExampleApp v1.0",
                "--relation-type",
                "possible_same_object",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        assessment = json.loads(completed.stdout)
        self.assertEqual(assessment["status"], "dry_run_validated")
        self.assertEqual(assessment["asserted_relation"]["relation_type"], "possible_same_object")
        self.assertFalse(assessment["runtime_identity_resolution_implemented"])
        self.assertFalse(assessment["records_merged"])
        self.assertFalse(assessment["destructive_merge_performed"])
        self.assertFalse(assessment["live_source_called"])
        self.assertFalse(assessment["external_calls_performed"])
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp) / "IDENTITY_RESOLUTION_ASSESSMENT.json"
            tmp_path.write_text(json.dumps(assessment), encoding="utf-8")
            validated = subprocess.run(
                [sys.executable, "scripts/validate_identity_resolution_assessment.py", "--assessment", str(tmp_path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
        self.assertEqual(json.loads(validated.stdout)["status"], "valid")


if __name__ == "__main__":
    unittest.main()
