from __future__ import annotations

import json
import subprocess
import sys
import unittest


class SourceWaveSmokeTests(unittest.TestCase):
    def test_smoke_script_runs_all_families(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_source_wave_smoke.py",
                "--all-families",
                "--transport",
                "fixture",
                "--json",
            ],
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(8, payload["family_count"])
        self.assertFalse(payload["download_performed"])


if __name__ == "__main__":
    unittest.main()
