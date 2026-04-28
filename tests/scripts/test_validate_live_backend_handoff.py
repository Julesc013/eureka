from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_live_backend_handoff.py"


class ValidateLiveBackendHandoffScriptTest(unittest.TestCase):
    def test_validator_passes_plain_and_json(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", plain.stdout)
        self.assertIn("reserved_endpoints: 11", plain.stdout)

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
        self.assertIn("/api/v1/status", payload["registered_endpoints"])
        self.assertIn("live_backend", payload["disabled_live_capabilities"])

    def test_validator_rejects_enabled_live_probe_route(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir) / "eureka"
            shutil.copytree(REPO_ROOT, temp_root, ignore=shutil.ignore_patterns(".git"))
            routes_path = temp_root / "control" / "inventory" / "publication" / "live_backend_routes.json"
            payload = json.loads(routes_path.read_text(encoding="utf-8"))
            for route in payload["routes"]:
                if route["path_template"] == "/api/v1/live-probe":
                    route["status"] = "implemented"
                    route["public_alpha_allowed"] = True
            routes_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(temp_root / "scripts" / "validate_live_backend_handoff.py"),
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
        self.assertTrue(any("live-probe" in error for error in payload["errors"]))

    def test_validator_rejects_static_api_v1_link(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir) / "eureka"
            shutil.copytree(REPO_ROOT, temp_root, ignore=shutil.ignore_patterns(".git"))
            status = temp_root / "public_site" / "status.html"
            status.write_text(
                status.read_text(encoding="utf-8").replace(
                    "</main>",
                    '<p><a href="/api/v1/status">Live status</a></p></main>',
                ),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(temp_root / "scripts" / "validate_live_backend_handoff.py"),
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
        self.assertTrue(any("/api/v1" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
