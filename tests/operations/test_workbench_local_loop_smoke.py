from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class WorkbenchLocalLoopSmokeTests(unittest.TestCase):
    def test_public_and_native_cli_apply_are_blocked(self) -> None:
        for projection in ("public_web", "native_desktop_read_only"):
            with self.subTest(projection=projection):
                completed = subprocess.run(
                    [
                        sys.executable,
                        "scripts/eureka_local_loop_closeout.py",
                        "--query",
                        "sampleproject",
                        "--projection",
                        projection,
                        "--use-temp-instance",
                        "--apply-to-temp",
                        "--operator-token",
                        "local-dev-token",
                        "--confirm",
                        "APPLY_TO_LOCAL_INSTANCE",
                        "--json",
                    ],
                    cwd=REPO_ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertNotEqual(completed.returncode, 0)
                payload = json.loads(completed.stdout)
                self.assertEqual(payload["status"], "blocked")
                self.assertFalse(payload["operator_instance_mutated"])


if __name__ == "__main__":
    unittest.main()
