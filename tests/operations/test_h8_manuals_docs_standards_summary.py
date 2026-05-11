from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts import summarize_h8_manuals_docs_standards_sources as summary
from scripts import validate_h8_manuals_docs_standards_policy_packs as validator


class H8ManualsDocsStandardsSummaryTests(unittest.TestCase):
    def test_summary_counts_and_no_default_writes(self) -> None:
        data = summary.build_summary()
        self.assertEqual(data["source_count"], 18)
        self.assertEqual(data["live_access_enabled_count"], 0)
        self.assertEqual(data["download_enabled_count"], 0)
        self.assertEqual(data["full_text_ocr_enabled_count"], 0)
        with tempfile.TemporaryDirectory() as tmp:
            before = set(Path(tmp).iterdir())
            code = summary.main(["--check"])
            after = set(Path(tmp).iterdir())
            self.assertEqual(code, 0)
            self.assertEqual(before, after)

    def test_summary_writes_explicit_temp_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "summary.json"
            md = Path(tmp) / "summary.md"
            code = summary.main(["--output", str(output), "--summary-output", str(md)])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["source_count"], 18)
            self.assertIn("H8 Manuals Docs Standards", md.read_text(encoding="utf-8"))

    def test_summary_refuses_forbidden_roots(self) -> None:
        self.assertEqual(summary.main(["--output", "site/dist/h8.json"]), 1)
        self.assertEqual(summary.main(["--output", "data/public_index/h8.json"]), 1)

    def test_validator_default_has_no_network_or_private_roots(self) -> None:
        result = validator.validate_repo()
        self.assertEqual(result["status"], "valid", result["errors"])
        for forbidden in (".aide.local", ".local/eureka", ".cache/eureka", "document_downloads", "standards_downloads", "ocr_cache"):
            self.assertFalse((validator.REPO_ROOT / forbidden).exists())


if __name__ == "__main__":
    unittest.main()
