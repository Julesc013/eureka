from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_public_static_site.py"
SITE_DIR = REPO_ROOT / "site/dist"


class ValidatePublicStaticSiteScriptTest(unittest.TestCase):
    def test_validator_passes_plain_and_json(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", plain.stdout)

        payload = self._run_json()
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(len(payload["pages"]), 8)
        self.assertEqual(len(payload["source_ids_checked"]), 9)
        self.assertEqual(payload["missing_source_ids"], [])

    def test_validator_reports_local_links_and_no_scripts(self) -> None:
        payload = self._run_json()
        for page, report in payload["page_reports"].items():
            with self.subTest(page=page):
                self.assertEqual(report["script_count"], 0)
                self.assertEqual(report["broken_local_links"], [])

    def test_validator_fails_for_missing_required_phrase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_site = Path(temp_dir) / "site"
            self._copy_site(temp_site)
            index = temp_site / "index.html"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    "Python reference backend prototype",
                    "backend prototype",
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--site-dir", str(temp_site), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("missing required phrases", completed.stdout)

    def test_validator_fails_for_broken_local_link(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_site = Path(temp_dir) / "site"
            self._copy_site(temp_site)
            page = temp_site / "index.html"
            page.write_text(
                page.read_text(encoding="utf-8").replace(
                    "status.html",
                    "missing-status.html",
                    1,
                ),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--site-dir", str(temp_site), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("local link does not resolve", completed.stdout)

    def _run_json(self) -> dict:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    def _copy_site(self, target: Path) -> None:
        for path in SITE_DIR.rglob("*"):
            if path.is_dir():
                continue
            relative = path.relative_to(SITE_DIR)
            output = target / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
