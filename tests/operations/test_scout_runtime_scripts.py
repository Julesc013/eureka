from __future__ import annotations

import json
import subprocess
import sys
import unittest


class ScoutRuntimeScriptsTest(unittest.TestCase):
    def test_scout_runtime_script_outputs_review_only_run(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_scout_runtime.py",
                "--from-candidate-examples",
                "--seed",
                "archive_org_dtheater_candidate",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["schema_version"], "scout_run.v0")
        self.assertFalse(payload["accepted_truth"])
        self.assertFalse(payload["live_source_call_performed"])


if __name__ == "__main__":
    unittest.main()
