from __future__ import annotations

import subprocess
import sys
import unittest


class ValidateSourceWaveTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_source_wave.py"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
