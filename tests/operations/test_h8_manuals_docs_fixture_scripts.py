from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from scripts import validate_h8_manuals_docs_standards_fixture_runtime as validator

REPO_ROOT = Path(__file__).resolve().parents[2]


class H8ManualsDocsFixtureScriptTests(unittest.TestCase):
    def test_validator_passes_current_repo(self) -> None:
        result = validator.validate_repo(REPO_ROOT)
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_normalizer_writes_no_files_by_default(self) -> None:
        before = {path.as_posix() for path in (REPO_ROOT / "examples/connectors/h8_manuals_docs_standards/normalized").glob("*.json")}
        result = subprocess.run([sys.executable, "scripts/normalize_h8_manuals_docs_fixture.py", "--source-id", "bitsavers_docs", "--input", "examples/connectors/h8_manuals_docs_standards/fixtures/bitsavers_docs/document_identity_record.json"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {path.as_posix() for path in (REPO_ROOT / "examples/connectors/h8_manuals_docs_standards/normalized").glob("*.json")}
        self.assertEqual(before, after)

    def test_normalizer_writes_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "normalized.json"
            document = Path(tmp) / "document.json"
            result = subprocess.run([sys.executable, "scripts/normalize_h8_manuals_docs_fixture.py", "--source-id", "bitsavers_docs", "--input", "examples/connectors/h8_manuals_docs_standards/fixtures/bitsavers_docs/document_identity_record.json", "--output", str(output), "--document-output", str(document)], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["source_id"], "bitsavers_docs")
            self.assertIn("candidate_id", json.loads(document.read_text(encoding="utf-8")))

    def test_replay_writes_no_files_by_default_and_temp_when_explicit(self) -> None:
        result = subprocess.run([sys.executable, "scripts/replay_h8_manuals_docs_fixtures.py", "--check"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, "scripts/replay_h8_manuals_docs_fixtures.py", "--source-id", "bitsavers_docs", "--output-dir", tmp], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(list(Path(tmp).glob("*.json")))

    def test_scripts_refuse_forbidden_roots(self) -> None:
        commands = [
            [sys.executable, "scripts/normalize_h8_manuals_docs_fixture.py", "--source-id", "bitsavers_docs", "--input", "examples/connectors/h8_manuals_docs_standards/fixtures/bitsavers_docs/document_identity_record.json", "--output", "site/dist/h8.json"],
            [sys.executable, "scripts/normalize_h8_manuals_docs_fixture.py", "--source-id", "bitsavers_docs", "--input", "examples/connectors/h8_manuals_docs_standards/fixtures/bitsavers_docs/document_identity_record.json", "--output", "data/public_index/h8.json"],
            [sys.executable, "scripts/normalize_h8_manuals_docs_fixture.py", "--source-id", "bitsavers_docs", "--input", "examples/connectors/h8_manuals_docs_standards/fixtures/bitsavers_docs/document_identity_record.json", "--output", "document_downloads/h8.json"],
            [sys.executable, "scripts/normalize_h8_manuals_docs_fixture.py", "--source-id", "bitsavers_docs", "--input", "examples/connectors/h8_manuals_docs_standards/fixtures/bitsavers_docs/document_identity_record.json", "--output", "ocr_cache/h8.json"],
            [sys.executable, "scripts/normalize_h8_manuals_docs_fixture.py", "--source-id", "bitsavers_docs", "--input", "examples/connectors/h8_manuals_docs_standards/fixtures/bitsavers_docs/document_identity_record.json", "--output", "media_downloads/h8.json"],
        ]
        for command in commands:
            result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0, command)
            self.assertIn("refusing forbidden output root", result.stdout + result.stderr)

    def test_summary_check(self) -> None:
        result = subprocess.run([sys.executable, "scripts/summarize_h8_manuals_docs_fixture_outputs.py", "--input", "examples/connectors/h8_manuals_docs_standards", "--check", "--json"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["source_count"], 18)

    def test_validator_does_not_create_private_roots(self) -> None:
        validator.validate_repo(REPO_ROOT)
        for rel in (".aide.local", ".local/eureka", ".cache/eureka", "document_downloads", "standards_downloads", "pdf_downloads", "manual_downloads", "datasheet_downloads", "schematic_downloads", "service_manual_downloads", "ocr_cache", "iiif_cache", "media_downloads", "repair_manual_dumps"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
