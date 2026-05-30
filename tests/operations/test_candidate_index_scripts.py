from __future__ import annotations

import json
import subprocess
import sys
import unittest


class CandidateIndexScriptsTest(unittest.TestCase):
    def test_candidate_search_script_outputs_read_only_lane(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_candidate_search.py",
                "--query",
                "D-Theater New York 1993",
                "--from-examples",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["accepted_truth"])
        self.assertFalse(payload["public_mutation_enabled"])
        self.assertGreaterEqual(payload["search_result"]["result_count"], 1)


if __name__ == "__main__":
    unittest.main()
