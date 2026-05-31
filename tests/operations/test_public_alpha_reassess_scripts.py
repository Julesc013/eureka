from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class PublicAlphaReassessScriptTests(unittest.TestCase):
    def test_reassess_script_runs(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "eureka_public_alpha_reassess.py"),
                "--from-snapshot-refresh-examples",
                "--json",
            ],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn('"launch_recommended": false', completed.stdout)


if __name__ == "__main__":
    unittest.main()
