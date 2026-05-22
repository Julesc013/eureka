from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts import summarize_h9_media_metadata_sources as summary
from scripts import validate_h9_media_metadata_policy_packs as validator


class H9MediaMetadataSummaryTests(unittest.TestCase):
    def test_summary_counts_and_no_default_writes(self) -> None:
        data = summary.build_summary()
        self.assertEqual(data["source_count"], 20)
        self.assertEqual(data["live_access_enabled_count"], 0)
        self.assertEqual(data["media_download_enabled_count"], 0)
        self.assertEqual(data["media_upload_enabled_count"], 0)
        self.assertEqual(data["fingerprinting_enabled_count"], 0)
        self.assertEqual(summary.main(["--check"]), 0)

    def test_summary_writes_explicit_temp_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "summary.json"
            md = Path(tmp) / "summary.md"
            code = summary.main(["--output", str(output), "--summary-output", str(md)])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["source_count"], 20)
            self.assertIn("H9 Media Metadata", md.read_text(encoding="utf-8"))

    def test_summary_refuses_forbidden_roots(self) -> None:
        self.assertEqual(summary.main(["--output", "site/dist/h9.json"]), 1)
        self.assertEqual(summary.main(["--output", "site/dist/data/public_index/h9.json"]), 1)
        self.assertEqual(summary.main(["--output", "runtime/h9.json"]), 1)
        self.assertEqual(summary.main(["--output", "contracts/h9.json"]), 1)

    def test_validator_default_has_no_network_or_private_roots(self) -> None:
        result = validator.validate_repo()
        self.assertEqual(result["status"], "valid", result["errors"])
        for forbidden in (".aide.local", ".local/eureka", ".cache/eureka", "media_downloads", "media_uploads", "fingerprint_cache", "map_downloads", "ocr_cache"):
            self.assertFalse((validator.REPO_ROOT / forbidden).exists())


if __name__ == "__main__":
    unittest.main()
