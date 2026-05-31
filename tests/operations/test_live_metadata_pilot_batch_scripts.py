import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class LiveMetadataPilotScriptTests(unittest.TestCase):
    def test_cli_smoke_modes(self):
        commands = [
            [sys.executable, "scripts/eureka_live_metadata_pilot_approval.py", "--template", "--json"],
            [sys.executable, "scripts/eureka_live_metadata_pilot_batch.py", "--dry-run", "--json"],
            [sys.executable, "scripts/eureka_live_metadata_pilot_batch.py", "--fixture", "--json"],
            [sys.executable, "scripts/eureka_live_metadata_pilot_report.py", "--from-examples", "--json"],
        ]
        for command in commands:
            with self.subTest(command=command):
                completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertIsInstance(json.loads(completed.stdout), dict)


if __name__ == "__main__":
    unittest.main()
