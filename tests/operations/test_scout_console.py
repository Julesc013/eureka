from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class ScoutConsoleTests(unittest.TestCase):
    def run_console(self, projection: str) -> dict:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_scout_console.py",
                "--manifest",
                "examples/scout/scout_seed_manifest.json",
                "--projection",
                projection,
                "--json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(result.stdout)

    def test_operator_console_view_is_read_only(self) -> None:
        view = self.run_console("operator_workbench")
        self.assertTrue(view["read_only"])
        self.assertTrue(view["operator_detail_visible"])
        self.assertIn("DiscoveryTrailView", view["views"])

    def test_public_and_native_projections_are_read_only(self) -> None:
        for projection in ("public_web", "native_desktop_read_only"):
            with self.subTest(projection=projection):
                view = self.run_console(projection)
                self.assertTrue(view["read_only"])
                self.assertFalse(view["operator_detail_visible"])
                self.assertFalse(view["non_claims"]["evidence_created"])


if __name__ == "__main__":
    unittest.main()
