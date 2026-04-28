from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_static_host_readiness.py"


class ValidateStaticHostReadinessScriptTest(unittest.TestCase):
    def test_validator_passes_plain_and_json(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", plain.stdout)
        self.assertIn("github_pages_project_base_path: /eureka/", plain.stdout)
        self.assertIn("custom_domain_base_path: /", plain.stdout)

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
        self.assertEqual(payload["github_pages_project_base_path"], "/eureka/")
        self.assertEqual(payload["custom_domain_base_path"], "/")
        self.assertTrue(payload["no_domain_configured"])
        self.assertTrue(payload["no_dns_changes_performed"])
        self.assertTrue(payload["no_cname_file_committed"])

    def test_validator_rejects_cname_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir) / "eureka"
            shutil.copytree(REPO_ROOT, temp_root, ignore=shutil.ignore_patterns(".git"))
            cname = temp_root / "public_site" / "CNAME"
            cname.write_text("example.org\n", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(temp_root / "scripts" / "validate_static_host_readiness.py"), "--repo-root", str(temp_root), "--json"],
                cwd=temp_root,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("CNAME" in error for error in payload["errors"]))

    def test_validator_rejects_root_relative_html_link(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir) / "eureka"
            shutil.copytree(REPO_ROOT, temp_root, ignore=shutil.ignore_patterns(".git"))
            index = temp_root / "public_site" / "index.html"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    'href="status.html"',
                    'href="/status.html"',
                    1,
                ),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [sys.executable, str(temp_root / "scripts" / "validate_static_host_readiness.py"), "--repo-root", str(temp_root), "--json"],
                cwd=temp_root,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertTrue(any("root-relative" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
