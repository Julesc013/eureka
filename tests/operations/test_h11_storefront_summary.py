from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts import summarize_h11_storefront_sources as summary
from scripts import validate_h11_storefront_policy_packs as validator


class H11StorefrontSummaryTests(unittest.TestCase):
    def test_summary_counts_and_no_default_writes(self) -> None:
        data = summary.build_summary()
        self.assertEqual(data["source_count"], 16)
        self.assertEqual(data["live_access_enabled_count"], 0)
        self.assertEqual(data["storefront_product_fetch_enabled_count"], 0)
        self.assertEqual(data["downloads_enabled_count"], 0)
        self.assertEqual(data["account_access_enabled_count"], 0)
        self.assertEqual(data["purchase_automation_enabled_count"], 0)
        self.assertEqual(data["entitlement_checks_enabled_count"], 0)
        self.assertEqual(data["install_launch_enabled_count"], 0)
        self.assertEqual(summary.main(["--check"]), 0)

    def test_summary_writes_explicit_temp_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "summary.json"
            md = Path(tmp) / "summary.md"
            code = summary.main(["--output", str(output), "--summary-output", str(md)])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["source_count"], 16)
            self.assertIn("H11 Storefront", md.read_text(encoding="utf-8"))

    def test_summary_refuses_forbidden_roots(self) -> None:
        self.assertEqual(summary.main(["--output", "site/dist/h11.json"]), 1)
        self.assertEqual(summary.main(["--output", "data/public_index/h11.json"]), 1)
        self.assertEqual(summary.main(["--output", "runtime/h11.json"]), 1)
        self.assertEqual(summary.main(["--output", "contracts/h11.json"]), 1)

    def test_validator_default_has_no_network_or_private_roots(self) -> None:
        result = validator.validate_repo()
        self.assertEqual(result["status"], "valid", result["errors"])
        for forbidden in (".aide.local", ".local/eureka", ".cache/eureka", "storefront_accounts", "receipts", "entitlements", "store_libraries", "app_downloads", "game_installs", "package_downloads", "checkout_sessions"):
            self.assertFalse((validator.REPO_ROOT / forbidden).exists())


if __name__ == "__main__":
    unittest.main()
