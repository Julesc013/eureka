from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "generate_public_data_summaries.py"
SITE_BUILD = REPO_ROOT / "site" / "build.py"
PUBLIC_DATA = REPO_ROOT / "site/dist" / "data"
SOURCE_DIR = REPO_ROOT / "control" / "inventory" / "sources"
PUBLIC_DATA_CONTRACT = (
    REPO_ROOT / "control" / "inventory" / "publication" / "public_data_contract.json"
)
REQUIRED_DATA_FILES = {
    "site_manifest.json",
    "page_registry.json",
    "source_summary.json",
    "eval_summary.json",
    "route_summary.json",
    "build_manifest.json",
}


class GeneratePublicDataSummariesScriptTest(unittest.TestCase):
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
        self.assertEqual(set(payload["data_files"]), REQUIRED_DATA_FILES)

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

    def test_generated_files_exist_and_parse(self) -> None:
        for name in REQUIRED_DATA_FILES:
            with self.subTest(name=name):
                path = PUBLIC_DATA / name
                self.assertTrue(path.exists())
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["schema_version"], "0.1.0")
                self.assertEqual(
                    payload["generated_by"],
                    "scripts/generate_public_data_summaries.py",
                )

    def test_source_summary_includes_all_source_ids_and_no_private_paths(self) -> None:
        payload = json.loads((PUBLIC_DATA / "source_summary.json").read_text(encoding="utf-8"))
        observed_ids = {source["source_id"] for source in payload["sources"]}
        expected_ids = {
            json.loads(path.read_text(encoding="utf-8"))["source_id"]
            for path in SOURCE_DIR.glob("*.source.json")
        }
        self.assertEqual(observed_ids, expected_ids)

        text = json.dumps(payload, sort_keys=True)
        for marker in ("D:\\", "C:\\", "D:\\\\", "C:\\\\", "/Users/", "/home/"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, text)

    def test_site_build_output_includes_public_data_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "dist"
            completed = subprocess.run(
                [sys.executable, str(SITE_BUILD), "--output", str(output), "--json"],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "valid")
            self.assertEqual(set(payload["public_data_files"]), REQUIRED_DATA_FILES)
            for name in REQUIRED_DATA_FILES:
                with self.subTest(name=name):
                    self.assertTrue((output / "data" / name).exists())

    def test_public_data_contract_covers_generated_files(self) -> None:
        contract = json.loads(PUBLIC_DATA_CONTRACT.read_text(encoding="utf-8"))
        entries = {entry["path"]: entry for entry in contract["entries"]}
        for name in REQUIRED_DATA_FILES:
            public_path = f"/data/{name}"
            with self.subTest(public_path=public_path):
                entry = entries[public_path]
                self.assertEqual(entry["status"], "implemented")
                self.assertEqual(entry["stability"], "stable_draft")
                self.assertEqual(
                    entry["generated_by"],
                    "scripts/generate_public_data_summaries.py",
                )
                self.assertFalse(entry["contains_live_data"])
                self.assertFalse(entry["contains_external_observations"])


if __name__ == "__main__":
    unittest.main()
