from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class SnapshotRelaySmokeTests(unittest.TestCase):
    def test_snapshot_relay_smoke_commands(self) -> None:
        commands = (
            [sys.executable, "scripts/eureka_snapshot_build.py", "--from-examples", "--json"],
            [sys.executable, "scripts/eureka_snapshot_validate.py", "--snapshot", "examples/snapshots/sample_snapshot_envelope.json", "--json"],
            [
                sys.executable,
                "scripts/eureka_relay_project.py",
                "--snapshot",
                "examples/snapshots/sample_snapshot_envelope.json",
                "--query",
                "sampleproject",
                "--projection",
                "lite_client_read_only",
                "--json",
            ],
        )
        for command in commands:
            with self.subTest(command=command):
                subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=True)


if __name__ == "__main__":
    unittest.main()
