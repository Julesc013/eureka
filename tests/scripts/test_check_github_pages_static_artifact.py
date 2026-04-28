from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_github_pages_static_artifact.py"
PUBLIC_SITE = REPO_ROOT / "public_site"


class CheckGitHubPagesStaticArtifactScriptTest(unittest.TestCase):
    def test_checker_passes_plain_and_json(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", plain.stdout)
        self.assertIn("static_site_validator: valid", plain.stdout)
        self.assertIn("publication_inventory_validator: valid", plain.stdout)

        payload = self._run_json()
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["errors"], [])
        self.assertEqual(payload["deployment_target"]["base_path"], "/eureka/")
        self.assertEqual(payload["deployment_target"]["artifact_root"], "public_site")
        self.assertTrue(payload["deployment_target"]["no_backend"])
        self.assertTrue(payload["deployment_target"]["no_live_probes"])

    def test_checker_rejects_runtime_source_inside_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_site = Path(temp_dir) / "public_site"
            shutil.copytree(PUBLIC_SITE, temp_site)
            runtime_file = temp_site / "server.py"
            runtime_file.write_text("print('not static')\n", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--site-dir", str(temp_site), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("forbidden" in error.casefold() for error in payload["errors"]))

    def test_checker_rejects_root_relative_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_site = Path(temp_dir) / "public_site"
            shutil.copytree(PUBLIC_SITE, temp_site)
            index = temp_site / "index.html"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    'href="status.html"',
                    'href="/status.html"',
                    1,
                ),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--site-dir", str(temp_site), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("root-relative" in error for error in payload["errors"]))

    def _run_json(self) -> dict:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()

