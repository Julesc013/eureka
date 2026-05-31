from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class PublicSearchUxModelScriptTests(unittest.TestCase):
    def test_cli_builds_bundle(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "eureka_public_search_ux_model.py"),
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
        self.assertIn('"contract_authority_root": "contracts/view/models/public_search"', completed.stdout)


if __name__ == "__main__":
    unittest.main()
