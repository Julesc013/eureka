from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts import run_h12_retro_community_live_probe as runner
from scripts import summarize_h12_retro_community_live_probe_outputs as summarizer
from scripts import validate_h12_retro_community_live_probe as validator


class H12RetroCommunityLiveProbeScriptTests(unittest.TestCase):
    def test_cli_writes_no_files_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            before = set(Path(tmp).iterdir())
            code = runner.main(["--source-id", "winworld_metadata", "--request-key", "example_catalog_item_metadata", "--check"])
            after = set(Path(tmp).iterdir())
        self.assertEqual(code, 0)
        self.assertEqual(before, after)

    def test_cli_writes_explicit_outputs_to_temp_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "result.json"
            health = Path(tmp) / "health.json"
            code = runner.main(["--source-id", "winworld_metadata", "--request-key", "example_catalog_item_metadata", "--output", str(out), "--health-output", str(health)])
            self.assertEqual(code, 0)
            self.assertTrue(out.exists())
            self.assertTrue(health.exists())
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(payload["result_status"], "blocked_by_missing_approval")
            self.assertFalse(payload["network_used"])

    def test_cli_refuses_forbidden_roots(self) -> None:
        for path in ("site/dist/h12.json", "site/dist/data/public_index/h12.json", "roms/h12.json", "isos/h12.json", "bios/h12.json", "vintage_software_downloads/h12.json", "archive_extractions/h12.json", "execution_actions/h12.json", "gated_source_accounts/h12.json"):
            with self.subTest(path=path):
                code = runner.main(["--source-id", "winworld_metadata", "--request-key", "example_catalog_item_metadata", "--output", path])
                self.assertNotEqual(code, 0)

    def test_summary_script_writes_no_files_by_default_and_accepts_temp_outputs(self) -> None:
        code = summarizer.main(["--input", "examples/connectors/h12_retro_community/live_probe_results", "--check"])
        self.assertEqual(code, 0)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "summary.json"
            md = Path(tmp) / "summary.md"
            code = summarizer.main(["--input", "examples/connectors/h12_retro_community/live_probe_results", "--output", str(out), "--summary-output", str(md)])
            self.assertEqual(code, 0)
            self.assertTrue(out.exists())
            self.assertTrue(md.exists())

    def test_summary_refuses_forbidden_output_root(self) -> None:
        code = summarizer.main(["--input", "examples/connectors/h12_retro_community/live_probe_results", "--output", "site/dist/h12-summary.json"])
        self.assertNotEqual(code, 0)

    def test_validator_passes_current_repo_and_is_offline(self) -> None:
        result = validator.validate_repo()
        self.assertEqual(result["status"], "valid", result["errors"])
        self.assertFalse(result["network_calls_made"])
