from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "generate_compatibility_surfaces.py"
PUBLIC_SITE = REPO_ROOT / "public_site"
REQUIRED_FILES = {
    "lite/index.html",
    "lite/sources.html",
    "lite/evals.html",
    "lite/demo-queries.html",
    "lite/limitations.html",
    "lite/README.txt",
    "text/index.txt",
    "text/sources.txt",
    "text/evals.txt",
    "text/demo-queries.txt",
    "text/limitations.txt",
    "text/README.txt",
    "files/index.html",
    "files/index.txt",
    "files/README.txt",
    "files/manifest.json",
    "files/SHA256SUMS",
    "files/data/README.txt",
}


class GenerateCompatibilitySurfacesScriptTest(unittest.TestCase):
    def test_generator_json_outputs_parseable_summary(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertFalse(payload["contains_live_backend"])
        self.assertFalse(payload["contains_live_probes"])
        self.assertFalse(payload["contains_external_observations"])
        self.assertFalse(payload["contains_executable_downloads"])
        self.assertEqual(set(payload["files"]), REQUIRED_FILES)

    def test_generator_check_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("check_mode: true", completed.stdout)

    def test_build_to_temp_output_produces_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "public_site"
            data = output / "data"
            data.mkdir(parents=True)
            for path in (PUBLIC_SITE / "data").glob("*.json"):
                (data / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-root",
                    str(output),
                    "--data-root",
                    str(data),
                    "--update",
                    "--json",
                ],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "valid")
            for relative in REQUIRED_FILES:
                with self.subTest(relative=relative):
                    self.assertTrue((output / relative).exists())

    def test_sha256sums_match_expected_files(self) -> None:
        for line in (PUBLIC_SITE / "files" / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
            digest, relative = line.split()
            with self.subTest(relative=relative):
                self.assertEqual(hashlib.sha256((PUBLIC_SITE / relative).read_bytes()).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
