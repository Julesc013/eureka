from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class DomainConsoleTests(unittest.TestCase):
    def test_operator_console_view_is_read_only_with_full_detail(self) -> None:
        payload = _console("legacy_software", "operator_workbench")
        self.assertTrue(payload["read_only"])
        self.assertTrue(payload["operator_detail_visible"])
        self.assertIn("identity_rules", payload["views"]["DomainPackView"])
        self.assertIn("download", payload["blocked_actions"])

    def test_public_and_native_views_are_read_only_summaries(self) -> None:
        for projection in ("public_web", "native_desktop_read_only"):
            with self.subTest(projection=projection):
                payload = _console("frontier_resolution_media", projection)
                self.assertTrue(payload["read_only"])
                self.assertFalse(payload["operator_detail_visible"])
                self.assertNotIn("identity_rules", payload["views"]["DomainPackView"])


def _console(domain_id: str, projection: str) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/eureka_domain_console.py",
            "--domain",
            domain_id,
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


if __name__ == "__main__":
    unittest.main()
