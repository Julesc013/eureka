import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DryRunSourcePageTests(unittest.TestCase):
    def test_dry_run_json_stdout_only_and_validates(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_source_page.py",
                "--source-id",
                "internet-archive-placeholder",
                "--source-family",
                "internet_archive",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        page = json.loads(completed.stdout)
        self.assertEqual(page["status"], "dry_run_validated")
        self.assertFalse(page["runtime_source_page_implemented"])
        self.assertFalse(page["connector_live_enabled"])
        self.assertFalse(page["live_source_called"])
        self.assertFalse(page["external_calls_performed"])
        with tempfile.TemporaryDirectory() as tmp:
            page_path = Path(tmp) / "SOURCE_PAGE.json"
            page_path.write_text(json.dumps(page), encoding="utf-8")
            validation = subprocess.run(
                [sys.executable, "scripts/validate_source_page.py", "--page", str(page_path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
        report = json.loads(validation.stdout)
        self.assertEqual(report["status"], "valid")

    def test_invalid_source_family_rejected(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/dry_run_source_page.py", "--source-family", "not-real", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(completed.returncode, 0)

    def test_unsafe_source_id_rejected(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/dry_run_source_page.py", "--source-id", "bad/source", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(completed.returncode, 0)


if __name__ == "__main__":
    unittest.main()
