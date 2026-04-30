from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD = REPO_ROOT / "site" / "build.py"
VALIDATE = REPO_ROOT / "site" / "validate.py"
PUBLIC_VALIDATOR = REPO_ROOT / "scripts" / "validate_public_static_site.py"


class StaticSiteGeneratorScriptTest(unittest.TestCase):
    def test_build_check_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(BUILD), "--check"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("deploy_artifact_current: site/dist", completed.stdout)

    def test_build_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(BUILD), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["output_dir"], "site/dist")
        self.assertFalse(payload["generated_output_deployed"])

    def test_build_to_temp_output_produces_valid_static_site(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "generated"
            completed = subprocess.run(
                [sys.executable, str(BUILD), "--output", str(output), "--json"],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "valid")
            for relative in (
                "index.html",
                "search.html",
                "status.html",
                "sources.html",
                "evals.html",
                "demo-queries.html",
                "limitations.html",
                "roadmap.html",
                "local-quickstart.html",
                "site_manifest.json",
                "data/search_handoff.json",
                "assets/site.css",
                "lite/index.html",
                "lite/search.html",
                "text/index.txt",
                "text/search.txt",
                "files/manifest.json",
                "files/search.README.txt",
                "files/SHA256SUMS",
                "demo/index.html",
                "demo/data/demo_snapshots.json",
            ):
                with self.subTest(relative=relative):
                    self.assertTrue((output / relative).exists())

            validation = subprocess.run(
                [sys.executable, str(PUBLIC_VALIDATOR), "--site-root", str(output)],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("status: valid", validation.stdout)

    def test_build_refuses_legacy_static_output(self) -> None:
        legacy_output = REPO_ROOT / ("public" + "_site")
        completed = subprocess.run(
            [sys.executable, str(BUILD), "--output", str(legacy_output)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("refusing to write the retired legacy static artifact", completed.stdout)

    def test_site_validate_plain_and_json_pass(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATE)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", plain.stdout)

        completed = subprocess.run(
            [sys.executable, str(VALIDATE), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["page_count"], 9)
        self.assertEqual(payload["dist_validation_status"], "valid")
        self.assertIn("demo/index.html", payload["dist_demo_files"])


if __name__ == "__main__":
    unittest.main()
