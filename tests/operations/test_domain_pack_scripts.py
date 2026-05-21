from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class DomainPackScriptTests(unittest.TestCase):
    def test_domain_pack_validate_cli_passes(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_domain_pack.py",
                "--manifest",
                "examples/domain/domain_seed_manifest.json",
                "--validate",
                "--json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertTrue(payload["validation_passed"])
        self.assertEqual(payload["domain_count"], 8)

    def test_domain_pack_list_cli_returns_required_domains(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/eureka_domain_pack.py",
                "--manifest",
                "examples/domain/domain_seed_manifest.json",
                "--list",
                "--json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertIn("legacy_software", payload["domain_ids"])
        self.assertIn("frontier_resolution_media", payload["domain_ids"])


if __name__ == "__main__":
    unittest.main()
