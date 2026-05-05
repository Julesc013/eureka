import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DryRunObjectPageTests(unittest.TestCase):
    def test_dry_run_json_stdout_only_and_validates(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_object_page.py",
                "--label",
                "Windows 7 compatible application",
                "--object-kind",
                "software_version",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        page = json.loads(completed.stdout)
        self.assertEqual(page["status"], "dry_run_validated")
        self.assertFalse(page["runtime_object_page_implemented"])
        self.assertFalse(page["live_source_called"])
        self.assertFalse(page["external_calls_performed"])
        self.assertFalse(page["downloads_enabled"])
        with tempfile.TemporaryDirectory() as tmp:
            page_path = Path(tmp) / "OBJECT_PAGE.json"
            page_path.write_text(json.dumps(page), encoding="utf-8")
            validation = subprocess.run(
                [sys.executable, "scripts/validate_object_page.py", "--page", str(page_path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
        report = json.loads(validation.stdout)
        self.assertEqual(report["status"], "valid")

    def test_invalid_object_kind_rejected(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/dry_run_object_page.py", "--object-kind", "not-real", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(completed.returncode, 0)


if __name__ == "__main__":
    unittest.main()
