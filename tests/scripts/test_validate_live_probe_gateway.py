from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_live_probe_gateway.py"


class ValidateLiveProbeGatewayScriptTest(unittest.TestCase):
    def test_validator_passes_plain_and_json(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", plain.stdout)
        self.assertIn("candidate_sources: 9", plain.stdout)
        self.assertIn("wrapper_live_probes_enabled: False", plain.stdout)

        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["errors"], [])
        self.assertIn("internet_archive_metadata", payload["candidate_sources"])
        self.assertIn("google_web_search", payload["manual_only_sources"])
        self.assertFalse(payload["wrapper_live_probes_enabled"])

    def test_validator_rejects_enabled_candidate_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir) / "eureka"
            shutil.copytree(REPO_ROOT, temp_root, ignore=shutil.ignore_patterns(".git"))
            inventory = temp_root / "control" / "inventory" / "publication" / "live_probe_gateway.json"
            payload = json.loads(inventory.read_text(encoding="utf-8"))
            payload["future_candidate_sources"][0]["status"] = "implemented"
            payload["future_candidate_sources"][0]["live_supported_now"] = True
            inventory.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(temp_root / "scripts" / "validate_live_probe_gateway.py"),
                    "--repo-root",
                    str(temp_root),
                    "--json",
                ],
                cwd=temp_root,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("future_disabled" in error for error in payload["errors"]))
        self.assertTrue(any("live_supported_now" in error for error in payload["errors"]))

    def test_validator_rejects_google_live_probe_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir) / "eureka"
            shutil.copytree(REPO_ROOT, temp_root, ignore=shutil.ignore_patterns(".git"))
            inventory = temp_root / "control" / "inventory" / "publication" / "live_probe_gateway.json"
            payload = json.loads(inventory.read_text(encoding="utf-8"))
            payload["future_candidate_sources"].append(
                {
                    "id": "google_web_search",
                    "status": "future_disabled",
                    "live_supported_now": False,
                    "requires_operator_enable": True,
                    "allowed_modes": ["metadata_search"],
                    "forbidden_modes": [
                        "downloads",
                        "scraping",
                        "bulk crawling",
                        "arbitrary URL fetching",
                        "account/private data",
                    ],
                    "default_result_cap": 10,
                    "default_timeout_ms": 5000,
                    "cache_required": True,
                    "evidence_required": True,
                    "notes": "Invalid test candidate.",
                }
            )
            inventory.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(temp_root / "scripts" / "validate_live_probe_gateway.py"),
                    "--repo-root",
                    str(temp_root),
                    "--json",
                ],
                cwd=temp_root,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("Google must not be a live probe candidate" in error for error in payload["errors"]))

    def test_validator_rejects_positive_static_claim(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir) / "eureka"
            shutil.copytree(REPO_ROOT, temp_root, ignore=shutil.ignore_patterns(".git"))
            status = temp_root / "site/dist" / "status.html"
            status.write_text(
                status.read_text(encoding="utf-8").replace(
                    "</main>",
                    "<p>Live probes are available from this backend.</p></main>",
                ),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(temp_root / "scripts" / "validate_live_probe_gateway.py"),
                    "--repo-root",
                    str(temp_root),
                    "--json",
                ],
                cwd=temp_root,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("prohibited positive live-probe claim" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
