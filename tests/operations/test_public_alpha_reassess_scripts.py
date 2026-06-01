from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class PublicAlphaReassessScriptTests(unittest.TestCase):
    def test_reassess_script_runs(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "eureka_public_alpha_reassess.py"),
                "--from-snapshot-refresh-examples",
                "--json",
            ],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn('"launch_recommended": false', completed.stdout)

    def test_live_metadata_reassess_script_runs(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "eureka_public_alpha_reassess.py"),
                "--from-live-metadata-refresh-examples",
                "--json",
            ],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn('"live_metadata_candidate_count": 8', completed.stdout)
        self.assertIn('"needs_live_candidate_review": true', completed.stdout)

    def test_live_metadata_report_script_runs(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "eureka_public_alpha_reassess_report.py"),
                "--from-live-metadata-examples",
                "--json",
            ],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn('"task": "PUBLIC-ALPHA-REASSESS-01"', completed.stdout)
        self.assertIn('"launch_recommended": false', completed.stdout)

    def test_live_metadata_review_reassess_script_runs(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "eureka_public_alpha_reassess.py"),
                "--from-live-metadata-review-refresh-examples",
                "--json",
            ],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn('"reviewed_metadata_record_preview_count": 1', completed.stdout)
        self.assertIn('"needs_local_apply_of_review_previews": true', completed.stdout)

    def test_live_metadata_review_report_script_runs(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "eureka_public_alpha_reassess_report.py"),
                "--from-live-metadata-review-examples",
                "--json",
            ],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn('"task": "PUBLIC-ALPHA-REASSESS-02"', completed.stdout)
        self.assertIn('"launch_recommended": false', completed.stdout)


if __name__ == "__main__":
    unittest.main()
