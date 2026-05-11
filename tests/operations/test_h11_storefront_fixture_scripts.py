from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts import normalize_h11_storefront_fixture as normalize
from scripts import replay_h11_storefront_fixtures as replay
from scripts import summarize_h11_storefront_fixture_outputs as summary
from scripts import validate_h11_storefront_fixture_runtime as validator


class H11StorefrontFixtureScriptTests(unittest.TestCase):
    def test_scripts_write_no_files_by_default_and_validate(self) -> None:
        self.assertEqual(normalize.main(["--source-id", "fdroid_metadata", "--input", "examples/connectors/h11_storefront/fixtures/fdroid_metadata/app_product_identity_record.json", "--check"]), 0)
        self.assertEqual(replay.main(["--check"]), 0)
        self.assertEqual(summary.main(["--input", "examples/connectors/h11_storefront", "--check"]), 0)
        self.assertEqual(validator.validate_repo()["status"], "valid")

    def test_scripts_write_explicit_temp_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "normalized.json"
            code = normalize.main(["--source-id", "fdroid_metadata", "--input", "examples/connectors/h11_storefront/fixtures/fdroid_metadata/app_product_identity_record.json", "--output", str(out)])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["source_id"], "fdroid_metadata")
            replay_dir = Path(tmp) / "replay"
            self.assertEqual(replay.main(["--source-id", "fdroid_metadata", "--output-dir", str(replay_dir)]), 0)
            self.assertTrue((replay_dir / "fdroid_metadata" / "normalized_record.json").exists())
            summary_out = Path(tmp) / "summary.json"
            self.assertEqual(summary.main(["--input", "examples/connectors/h11_storefront", "--output", str(summary_out)]), 0)
            self.assertIn("normalized_record_count", summary_out.read_text(encoding="utf-8"))

    def test_scripts_refuse_forbidden_roots(self) -> None:
        base = ["--source-id", "fdroid_metadata", "--input", "examples/connectors/h11_storefront/fixtures/fdroid_metadata/minimal_record.json"]
        for root in ("site/dist/h11.json", "data/public_index/h11.json", "storefront_accounts/h11.json", "app_downloads/h11.json"):
            self.assertNotEqual(normalize.main([*base, "--output", root]), 0)
        self.assertNotEqual(summary.main(["--input", "examples/connectors/h11_storefront", "--output", "site/dist/h11.json"]), 0)
