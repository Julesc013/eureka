import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DryRunComparisonPageTests(unittest.TestCase):
    def test_dry_run_json_stdout_only_and_validates(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/dry_run_comparison_page.py",
                "--label",
                "Compare two Windows 7 compatible app candidates",
                "--comparison-type",
                "object_identity_comparison",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        page = json.loads(completed.stdout)
        self.assertEqual(page["status"], "dry_run_validated")
        self.assertFalse(page["runtime_comparison_page_implemented"])
        self.assertFalse(page["comparison_winner_claimed"])
        self.assertFalse(page["live_source_called"])
        self.assertFalse(page["external_calls_performed"])
        with tempfile.TemporaryDirectory() as tmp:
            page_path = Path(tmp) / "COMPARISON_PAGE.json"
            page_path.write_text(json.dumps(page), encoding="utf-8")
            validation = subprocess.run(
                [sys.executable, "scripts/validate_comparison_page.py", "--page", str(page_path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
        report = json.loads(validation.stdout)
        self.assertEqual(report["status"], "valid")

    def test_invalid_comparison_type_rejected(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/dry_run_comparison_page.py", "--comparison-type", "winner_page", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(completed.returncode, 0)

    def test_unsafe_label_rejected(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/dry_run_comparison_page.py", "--label", "bad\\path", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(completed.returncode, 0)


if __name__ == "__main__":
    unittest.main()
