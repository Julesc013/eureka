from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from scripts import validate_h6_web_archive_news_event_fixture_runtime as validator

REPO_ROOT = Path(__file__).resolve().parents[2]


class H6WebArchiveFixtureScriptTests(unittest.TestCase):
    def test_validator_passes_current_repo(self) -> None:
        result = validator.validate_repo(REPO_ROOT)
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_normalizer_writes_no_files_by_default(self) -> None:
        before = {path.as_posix() for path in (REPO_ROOT / "examples/connectors/h6_web_archive_news_event/normalized").glob("*.json")}
        result = subprocess.run([
            sys.executable, "scripts/normalize_h6_web_archive_fixture.py",
            "--source-id", "wayback_cdx_memento",
            "--input", "examples/connectors/h6_web_archive_news_event/fixtures/wayback_cdx_memento/capture_record.json",
        ], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {path.as_posix() for path in (REPO_ROOT / "examples/connectors/h6_web_archive_news_event/normalized").glob("*.json")}
        self.assertEqual(before, after)

    def test_normalizer_writes_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "normalized.json"
            capture = Path(tmp) / "capture.json"
            result = subprocess.run([
                sys.executable, "scripts/normalize_h6_web_archive_fixture.py",
                "--source-id", "wayback_cdx_memento",
                "--input", "examples/connectors/h6_web_archive_news_event/fixtures/wayback_cdx_memento/capture_record.json",
                "--output", str(output),
                "--capture-output", str(capture),
            ], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["source_id"], "wayback_cdx_memento")
            self.assertIn("web_capture_identity_candidate_id", json.loads(capture.read_text(encoding="utf-8")))

    def test_replay_writes_no_files_by_default_and_temp_when_explicit(self) -> None:
        result = subprocess.run([sys.executable, "scripts/replay_h6_web_archive_fixtures.py", "--check"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, "scripts/replay_h6_web_archive_fixtures.py", "--source-id", "wayback_cdx_memento", "--output-dir", tmp], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(list(Path(tmp).glob("*.json")))

    def test_scripts_refuse_forbidden_roots(self) -> None:
        commands = [
            [sys.executable, "scripts/normalize_h6_web_archive_fixture.py", "--source-id", "wayback_cdx_memento", "--input", "examples/connectors/h6_web_archive_news_event/fixtures/wayback_cdx_memento/capture_record.json", "--output", "site/dist/h6.json"],
            [sys.executable, "scripts/normalize_h6_web_archive_fixture.py", "--source-id", "wayback_cdx_memento", "--input", "examples/connectors/h6_web_archive_news_event/fixtures/wayback_cdx_memento/capture_record.json", "--output", "site/dist/data/public_index/h6.json"],
            [sys.executable, "scripts/normalize_h6_web_archive_fixture.py", "--source-id", "wayback_cdx_memento", "--input", "examples/connectors/h6_web_archive_news_event/fixtures/wayback_cdx_memento/capture_record.json", "--output", "crawl/h6.json"],
            [sys.executable, "scripts/normalize_h6_web_archive_fixture.py", "--source-id", "wayback_cdx_memento", "--input", "examples/connectors/h6_web_archive_news_event/fixtures/wayback_cdx_memento/capture_record.json", "--output", "warc_wacz_cache/h6.json"],
            [sys.executable, "scripts/normalize_h6_web_archive_fixture.py", "--source-id", "wayback_cdx_memento", "--input", "examples/connectors/h6_web_archive_news_event/fixtures/wayback_cdx_memento/capture_record.json", "--output", "media_downloads/h6.json"],
        ]
        for command in commands:
            result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0, command)
            self.assertIn("refusing forbidden output root", result.stdout + result.stderr)

    def test_summary_check(self) -> None:
        result = subprocess.run([sys.executable, "scripts/summarize_h6_web_archive_fixture_outputs.py", "--input", "examples/connectors/h6_web_archive_news_event", "--check", "--json"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["source_count"], 13)


if __name__ == "__main__":
    unittest.main()
