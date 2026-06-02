from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class SnapshotRefreshScriptTests(unittest.TestCase):
    def test_snapshot_refresh_scripts_help(self) -> None:
        for script in (
            "scripts/eureka_snapshot_refresh.py",
            "scripts/eureka_snapshot_refresh_report.py",
        ):
            completed = subprocess.run(
                [sys.executable, str(REPO_ROOT / script), "--help"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, completed.returncode, msg=completed.stderr)

    def test_live_metadata_report_script(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts/eureka_snapshot_refresh_report.py"),
                "--from-live-metadata-examples",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, msg=completed.stderr)
        self.assertIn('"task": "SNAPSHOT-REFRESH-01"', completed.stdout)
        self.assertIn('"live_metadata_candidate_count": 8', completed.stdout)

    def test_live_metadata_review_report_script(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts/eureka_snapshot_refresh_report.py"),
                "--from-live-metadata-review-examples",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, msg=completed.stderr)
        self.assertIn('"task": "SNAPSHOT-REFRESH-02"', completed.stdout)
        self.assertIn('"reviewed_metadata_record_preview_count": 1', completed.stdout)

    def test_local_apply_live_metadata_report_script(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts/eureka_snapshot_refresh_report.py"),
                "--from-local-apply-live-metadata-examples",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, msg=completed.stderr)
        self.assertIn('"task": "SNAPSHOT-REFRESH-03"', completed.stdout)
        self.assertIn('"reviewed_metadata_record_count": 1', completed.stdout)
        self.assertIn('"reviewed_source_lead_count": 2', completed.stdout)

    def test_manuals_driver_report_script(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts/eureka_snapshot_refresh_report.py"),
                "--from-manuals-driver-examples",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, msg=completed.stderr)
        self.assertIn('"task": "SNAPSHOT-REFRESH-04"', completed.stdout)
        self.assertIn('"manuals_scans_candidate_count": 16', completed.stdout)
        self.assertIn('"driver_support_candidate_count": 16', completed.stdout)
        self.assertIn('"total_candidate_count": 68', completed.stdout)

    def test_public_search_ux_report_script(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts/eureka_snapshot_refresh_report.py"),
                "--from-public-search-ux-examples",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, msg=completed.stderr)
        self.assertIn('"task": "SNAPSHOT-REFRESH-05"', completed.stdout)
        self.assertIn('"public_ux_routes_count": 8', completed.stdout)
        self.assertIn('"result_card_states_count": 8', completed.stdout)


if __name__ == "__main__":
    unittest.main()
