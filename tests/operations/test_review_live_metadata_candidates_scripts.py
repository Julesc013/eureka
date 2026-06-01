from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class ReviewLiveMetadataCandidateScriptTests(unittest.TestCase):
    def test_cli_smoke_modes(self) -> None:
        commands = [
            [sys.executable, "scripts/eureka_review_live_metadata_candidates.py", "--from-live-metadata-examples", "--json"],
            [sys.executable, "scripts/eureka_live_metadata_promotion_preview.py", "--from-live-metadata-examples", "--json"],
            [sys.executable, "scripts/eureka_live_metadata_local_apply_handoff.py", "--from-live-metadata-examples", "--json"],
            [sys.executable, "scripts/eureka_live_metadata_review_report.py", "--from-examples", "--json"],
        ]
        for command in commands:
            with self.subTest(command=command):
                completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
                self.assertEqual(0, completed.returncode, completed.stderr)
                self.assertIsInstance(json.loads(completed.stdout), dict)


if __name__ == "__main__":
    unittest.main()
