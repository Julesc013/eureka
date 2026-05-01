from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX_ROOT = REPO_ROOT / "data" / "public_index"
REPORT = REPO_ROOT / "control" / "audits" / "public-search-index-builder-v0" / "public_search_index_builder_report.json"
VALIDATOR = REPO_ROOT / "scripts" / "validate_public_search_index_builder.py"


class PublicSearchIndexBuilderOperationTest(unittest.TestCase):
    def test_index_artifacts_exist_and_stats_match_documents(self) -> None:
        for name in (
            "build_manifest.json",
            "source_coverage.json",
            "index_stats.json",
            "search_documents.ndjson",
            "checksums.sha256",
        ):
            self.assertTrue((INDEX_ROOT / name).is_file(), name)
        docs = [
            json.loads(line)
            for line in (INDEX_ROOT / "search_documents.ndjson").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        stats = json.loads((INDEX_ROOT / "index_stats.json").read_text(encoding="utf-8"))
        self.assertEqual(stats["document_count"], len(docs))
        self.assertGreater(len(docs), 0)

    def test_public_search_runtime_uses_generated_index(self) -> None:
        from runtime.gateway.public_api import build_demo_public_search_public_api

        api = build_demo_public_search_public_api()
        status = api.status({}).body
        self.assertEqual(status["index_status"], "generated_public_search_index")
        self.assertEqual(status["index_document_count"], 584)

        result = api.search({"q": ["windows 7 apps"]}).body
        self.assertEqual(result["index_status"], "generated_public_search_index")
        self.assertGreater(len(result["results"]), 0)
        absence = api.search({"q": ["no-such-local-index-hit"]}).body
        self.assertEqual(absence["ok"], True)
        self.assertEqual(absence["absence_summary"]["status"], "bounded_absence")

    def test_report_records_hard_false_safety_booleans(self) -> None:
        payload = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(payload["report_id"], "public_search_index_builder_v0")
        self.assertTrue(payload["local_public_search_integrated"])
        for field_name in (
            "live_sources_used",
            "external_calls_performed",
            "private_paths_detected",
            "executable_payloads_included",
            "downloads_enabled",
            "uploads_enabled",
            "local_paths_enabled",
            "arbitrary_url_fetch_enabled",
            "master_index_mutated",
            "pack_import_performed",
            "ai_runtime_enabled",
        ):
            self.assertFalse(payload[field_name], field_name)

    def test_p55_validator_passes_plain_and_json(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", plain.stdout)

        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["errors"], [])


if __name__ == "__main__":
    unittest.main()
