import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class PublicQueryObservationRuntimePlanValidatorTests(unittest.TestCase):
    def test_validator_passes(self):
        completed = subprocess.run([sys.executable, "scripts/validate_public_query_observation_runtime_plan.py"], cwd=ROOT, text=True, capture_output=True, check=True)
        self.assertIn("status: valid", completed.stdout)

    def test_validator_json_parses(self):
        completed = subprocess.run([sys.executable, "scripts/validate_public_query_observation_runtime_plan.py", "--json"], cwd=ROOT, text=True, capture_output=True, check=True)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["readiness_decision"], "blocked_hosted_deployment_unverified")

    def test_docs_say_planning_only(self):
        text = (ROOT / "docs" / "operations" / "PUBLIC_QUERY_OBSERVATION_RUNTIME_PLAN.md").read_text(encoding="utf-8").lower()
        for phrase in ("planning", "hosted deployment gate", "no raw query", "no telemetry", "disabled-by-default"):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
