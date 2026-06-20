from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class E2EPreviewIndexCliTests(unittest.TestCase):
    def test_cli_build_validate_search_list_and_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            runs_root = temp_root / "runs"
            preview_root = temp_root / "preview"

            run_completed = _run(
                "scripts/eureka_resolution_run.py",
                "run",
                "--mode",
                "synthetic",
                "--query",
                "old blue FTP client for XP",
                "--out",
                str(runs_root),
                "--json",
            )
            self.assertEqual(0, run_completed.returncode, run_completed.stderr)

            build_completed = _run(
                "scripts/eureka_index.py",
                "preview-build",
                "--runs-root",
                str(runs_root),
                "--out",
                str(preview_root),
                "--json",
            )
            self.assertEqual(0, build_completed.returncode, build_completed.stderr)
            build_payload = json.loads(build_completed.stdout)

            validate_completed = _run(
                "scripts/eureka_index.py",
                "preview-validate",
                "--index",
                build_payload["current_path"],
                "--strict",
                "--json",
            )
            stats_completed = _run(
                "scripts/eureka_index.py",
                "preview-stats",
                "--index",
                build_payload["current_path"],
                "--json",
            )
            search_completed = _run(
                "scripts/eureka_index.py",
                "preview-search",
                "--index",
                build_payload["current_path"],
                "--query",
                "old blue FTP client for XP",
                "--include-synthetic",
                "--json",
            )
            list_completed = _run(
                "scripts/eureka_index.py",
                "preview-list-generations",
                "--root",
                str(preview_root),
                "--json",
            )
            rollback_completed = _run(
                "scripts/eureka_index.py",
                "preview-rollback",
                "--root",
                str(preview_root),
                "--to",
                build_payload["preview_index_id"],
                "--json",
            )

        self.assertEqual(0, validate_completed.returncode, validate_completed.stderr)
        self.assertEqual("pass", json.loads(validate_completed.stdout)["status"])
        self.assertEqual(0, stats_completed.returncode, stats_completed.stderr)
        self.assertGreater(json.loads(stats_completed.stdout)["record_count"], 0)
        self.assertEqual(0, search_completed.returncode, search_completed.stderr)
        self.assertGreater(json.loads(search_completed.stdout)["result_count"], 0)
        self.assertEqual(0, list_completed.returncode, list_completed.stderr)
        self.assertEqual(1, json.loads(list_completed.stdout)["generation_count"])
        self.assertEqual(0, rollback_completed.returncode, rollback_completed.stderr)
        self.assertEqual(build_payload["preview_index_id"], json.loads(rollback_completed.stdout)["to_generation"])

    def test_cli_build_does_not_treat_synthetic_run_as_reviewed_truth(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            runs_root = temp_root / "runs"
            preview_root = temp_root / "preview"
            self.assertEqual(
                0,
                _run(
                    "scripts/eureka_resolution_run.py",
                    "run",
                    "--mode",
                    "synthetic",
                    "--query",
                    "sampleproject",
                    "--out",
                    str(runs_root),
                    "--json",
                ).returncode,
            )
            build = _run(
                "scripts/eureka_index.py",
                "preview-build",
                "--runs-root",
                str(runs_root),
                "--out",
                str(preview_root),
                "--json",
            )
            payload = json.loads(build.stdout)
            records_path = Path(payload["record_file"])
            records = [json.loads(line) for line in records_path.read_text(encoding="utf-8").splitlines() if line.strip()]

        self.assertEqual(0, build.returncode, build.stderr)
        self.assertTrue(records)
        self.assertTrue(all(record["authority"] == "synthetic_test" for record in records))
        self.assertTrue(all(record["accepted_truth"] is False for record in records))
        self.assertFalse(any(record["status"] == "reviewed" for record in records))


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


if __name__ == "__main__":
    unittest.main()
