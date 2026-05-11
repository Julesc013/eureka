from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts import summarize_h10_games_emulation_sources as summary
from scripts import validate_h10_games_emulation_policy_packs as validator


class H10GamesEmulationSummaryTests(unittest.TestCase):
    def test_summary_counts_and_no_default_writes(self) -> None:
        data = summary.build_summary()
        self.assertEqual(data["source_count"], 14)
        self.assertEqual(data["live_access_enabled_count"], 0)
        self.assertEqual(data["software_list_hashset_fetch_enabled_count"], 0)
        self.assertEqual(data["downloads_enabled_count"], 0)
        self.assertEqual(data["uploads_enabled_count"], 0)
        self.assertEqual(data["execution_enabled_count"], 0)
        self.assertEqual(data["acquisition_action_enabled_count"], 0)
        self.assertEqual(summary.main(["--check"]), 0)

    def test_summary_writes_explicit_temp_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "summary.json"
            md = Path(tmp) / "summary.md"
            code = summary.main(["--output", str(output), "--summary-output", str(md)])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["source_count"], 14)
            self.assertIn("H10 Games Emulation", md.read_text(encoding="utf-8"))

    def test_summary_refuses_forbidden_roots(self) -> None:
        self.assertEqual(summary.main(["--output", "site/dist/h10.json"]), 1)
        self.assertEqual(summary.main(["--output", "data/public_index/h10.json"]), 1)
        self.assertEqual(summary.main(["--output", "runtime/h10.json"]), 1)
        self.assertEqual(summary.main(["--output", "contracts/h10.json"]), 1)

    def test_validator_default_has_no_network_or_private_roots(self) -> None:
        result = validator.validate_repo()
        self.assertEqual(result["status"], "valid", result["errors"])
        for forbidden in (".aide.local", ".local/eureka", ".cache/eureka", "roms", "isos", "disc_images", "emulators", "bios", "game_installs", "hash_submissions", "storefront_accounts"):
            self.assertFalse((validator.REPO_ROOT / forbidden).exists())


if __name__ == "__main__":
    unittest.main()
