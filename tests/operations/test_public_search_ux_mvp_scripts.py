from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class PublicSearchUxMvpScriptTests(unittest.TestCase):
    def test_render_script_runs(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "eureka_public_search_render.py"),
                "--from-view-model-examples",
                "--json",
            ],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn('"no_js_search_form_passed": true', completed.stdout)

    def test_smoke_scripts_run(self) -> None:
        for script in ("eureka_public_search_ux_smoke.py", "eureka_public_search_route_smoke.py"):
            completed = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / script), "--from-examples", "--json"],
                cwd=REPO_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn('"status": "pass"', completed.stdout)


if __name__ == "__main__":
    unittest.main()
