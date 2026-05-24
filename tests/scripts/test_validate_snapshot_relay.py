from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class ValidateSnapshotRelayTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/validate_snapshot_relay.py", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
