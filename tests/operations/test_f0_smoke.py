from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class F0SmokeTests(unittest.TestCase):
    def run_smoke(self, projection: str) -> dict:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_f0_smoke.py",
                "--fixture-manifest",
                "examples/f0/f0_fixture_manifest.json",
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

    def test_operator_smoke_is_read_only(self) -> None:
        payload = self.run_smoke("operator_workbench")
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["read_only"])
        self.assertTrue(payload["view"]["operator_detail_visible"])

    def test_public_and_native_smoke_are_read_only(self) -> None:
        for projection in ("public_web", "native_desktop_read_only"):
            with self.subTest(projection=projection):
                payload = self.run_smoke(projection)
                self.assertTrue(payload["read_only"])
                self.assertFalse(payload["view"]["operator_detail_visible"])
                self.assertFalse(payload["filesystem_extraction_performed"])


if __name__ == "__main__":
    unittest.main()
