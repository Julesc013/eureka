from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class LocalApplyLiveMetadataScriptTests(unittest.TestCase):
    def test_preview_validate_cli_passes(self) -> None:
        result = self.run_json(
            ["scripts/eureka_local_apply_preview_validate.py", "--from-live-metadata-review-examples", "--json"]
        )

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["eligible_preview_count"], 3)

    def test_temp_apply_cli_passes(self) -> None:
        result = self.run_json(
            [
                "scripts/eureka_local_apply_live_metadata_previews.py",
                "--from-live-metadata-review-examples",
                "--use-temp-instance",
                "--json",
            ]
        )

        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["temp_instance_apply_passed"])

    def run_json(self, args: list[str]) -> dict[str, object]:
        completed = subprocess.run(
            [sys.executable, *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            self.fail(completed.stderr or completed.stdout)
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
