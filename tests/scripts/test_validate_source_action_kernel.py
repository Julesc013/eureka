from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class ValidateSourceActionKernelTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_source_action_kernel.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)


if __name__ == "__main__":
    unittest.main()
