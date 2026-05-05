from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class DryRunSearchResultExplanationTests(unittest.TestCase):
    def test_dry_run_outputs_valid_stdout_only_json(self):
        result = subprocess.run(
            [sys.executable, "scripts/dry_run_search_result_explanation.py", "--title", "Example result", "--match-kind", "lexical_match", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIs(payload["runtime_explanation_implemented"], False)
        self.assertIs(payload["explanation_generated_by_runtime"], False)
        self.assertIs(payload["public_search_response_changed"], False)
        self.assertIs(payload["live_source_called"], False)
        self.assertIs(payload["external_calls_performed"], False)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "SEARCH_RESULT_EXPLANATION.json"
            path.write_text(result.stdout, encoding="utf-8")
            validation = subprocess.run(
                [sys.executable, "scripts/validate_search_result_explanation.py", "--explanation", str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertEqual(validation.returncode, 0, validation.stderr)


if __name__ == "__main__":
    unittest.main()
