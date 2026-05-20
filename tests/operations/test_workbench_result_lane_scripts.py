from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "eureka_workbench_result_lanes.py"


class WorkbenchResultLaneScriptTest(unittest.TestCase):
    def test_cli_operator_public_and_native_json(self) -> None:
        for projection in ("operator_workbench", "public_web", "native_desktop_read_only"):
            with self.subTest(projection=projection):
                result = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--query",
                        "sampleproject",
                        "--projection",
                        projection,
                        "--from-play-demo",
                        "--from-ia-examples",
                        "--json",
                    ],
                    cwd=REPO_ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                payload = json.loads(result.stdout)
                self.assertEqual(projection, payload["projection_profile"])
                self.assertEqual("sampleproject", payload["query"])
                self.assertTrue(payload["lanes"])
                self.assertTrue(payload["boundary_report"]["unsafe_actions_blocked"])


if __name__ == "__main__":
    unittest.main()
