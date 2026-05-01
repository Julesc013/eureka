from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_ai_assisted_drafting_plan.py"
EXAMPLE_ROOT = REPO_ROOT / "examples" / "ai_assisted_drafting" / "minimal_drafting_flow_v0"
TYPED_AI_OUTPUT = EXAMPLE_ROOT / "TYPED_AI_OUTPUT.example.json"


class ValidateAIAssistedDraftingPlanScriptTestCase(unittest.TestCase):
    def test_plain_and_json_validator_pass(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("AI-Assisted Evidence Drafting Plan validation", plain.stdout)
        self.assertIn("status: valid", plain.stdout)
        self.assertIn("model_calls_performed: False", plain.stdout)

        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["typed_output_status"], "passed")
        self.assertFalse(payload["model_calls_performed"])
        self.assertFalse(payload["network_performed"])
        self.assertFalse(payload["mutation_performed"])
        self.assertFalse(payload["public_search_mutated"])
        self.assertFalse(payload["local_index_mutated"])
        self.assertFalse(payload["master_index_mutation_performed"])

    def test_example_typed_output_validates_with_existing_validator(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_ai_output.py", "--output", str(TYPED_AI_OUTPUT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"], payload["errors"])
        self.assertEqual(payload["passed"], 1)
        self.assertFalse(payload["model_calls_performed"])


if __name__ == "__main__":
    unittest.main()
