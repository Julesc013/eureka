from __future__ import annotations

import json
import subprocess
import sys
import unittest


class SourceWaveScriptTests(unittest.TestCase):
    def test_list_families_script(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/eureka_source_wave.py", "--list-families", "--json"],
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertIn("internet_archive_metadata_v2", payload["families"])

    def test_family_fixture_script(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_source_wave.py",
                "--family",
                "github_releases_metadata",
                "--action-kind",
                "release_metadata_read",
                "--query",
                "sampleproject",
                "--transport",
                "fixture",
                "--json",
            ],
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("completed", payload["status"])
        self.assertFalse(payload["live_call_performed"])


if __name__ == "__main__":
    unittest.main()
