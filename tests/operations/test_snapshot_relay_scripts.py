from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def run_json(*args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, *args, "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout)


class SnapshotRelayScriptTests(unittest.TestCase):
    def test_snapshot_build_script(self) -> None:
        payload = run_json("scripts/eureka_snapshot_build.py", "--from-examples")
        self.assertEqual(payload["schema_version"], "snapshot_build_result.v0")
        self.assertEqual(payload["validation_report"]["status"], "pass")

    def test_relay_project_script(self) -> None:
        payload = run_json(
            "scripts/eureka_relay_project.py",
            "--snapshot",
            "examples/snapshots/sample_snapshot_envelope.json",
            "--query",
            "sampleproject",
            "--projection",
            "public_api_read_only",
        )
        self.assertTrue(payload["read_only"])
        self.assertEqual(payload["query_response"]["result_count"], 1)

    def test_capability_profile_script(self) -> None:
        payload = run_json("scripts/eureka_capability_profile.py", "--profile", "public_api_read_only")
        self.assertEqual(payload["validation"]["status"], "pass")
        self.assertFalse(payload["supports_mutation"])


if __name__ == "__main__":
    unittest.main()
