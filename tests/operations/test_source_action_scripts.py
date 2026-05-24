from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class SourceActionScriptsTests(unittest.TestCase):
    def test_fixture_action_cli_json(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_source_action.py",
                "--source-family",
                "fixture_source_action",
                "--action-kind",
                "metadata_search",
                "--query",
                "sampleproject",
                "--transport",
                "fixture",
                "--dry-run",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("completed", payload["status"])
        self.assertFalse(payload["boundary_report"]["download_performed"])

    def test_manifest_cli_json(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_source_action_manifest.py",
                "--manifest",
                "examples/source_actions/fixture_source_action_manifest.json",
                "--validate",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("pass", json.loads(completed.stdout)["status"])


if __name__ == "__main__":
    unittest.main()
