import json
import tempfile
from pathlib import Path
import unittest

from scripts import run_h7_library_research_live_probe as runner
from scripts import summarize_h7_library_research_live_probe_outputs as summarizer
from scripts import validate_h7_library_research_live_probe as validator


class H7LibraryResearchLiveProbeScriptTests(unittest.TestCase):
    def test_cli_writes_no_files_by_default(self):
        with tempfile.TemporaryDirectory() as tempdir:
            before = set(Path(tempdir).iterdir())
            code = runner.main(["--source-id", "openalex", "--request-key", "example_work_metadata", "--json"])
            after = set(Path(tempdir).iterdir())
        self.assertEqual(code, 0)
        self.assertEqual(before, after)

    def test_cli_writes_explicit_outputs_to_temp_path(self):
        with tempfile.TemporaryDirectory() as tempdir:
            output = Path(tempdir) / "probe.json"
            health = Path(tempdir) / "health.json"
            summary = Path(tempdir) / "summary.md"
            code = runner.main([
                "--source-id",
                "openalex",
                "--request-key",
                "example_work_metadata",
                "--output",
                str(output),
                "--health-output",
                str(health),
                "--summary-output",
                str(summary),
                "--json",
            ])
            self.assertEqual(code, 0)
            self.assertTrue(output.is_file())
            self.assertTrue(health.is_file())
            self.assertTrue(summary.is_file())
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["result_status"], "blocked_by_missing_approval")
            self.assertFalse(payload["network_used"])

    def test_cli_refuses_forbidden_roots(self):
        self.assertEqual(runner.main(["--source-id", "openalex", "--request-key", "example_work_metadata", "--output", "site/dist/probe.json", "--json"]), 1)
        self.assertEqual(runner.main(["--source-id", "openalex", "--request-key", "example_work_metadata", "--output", "site/dist/data/public_index/probe.json", "--json"]), 1)
        self.assertEqual(runner.main(["--source-id", "openalex", "--request-key", "example_work_metadata", "--output", "harvest/probe.json", "--json"]), 1)
        self.assertEqual(runner.main(["--source-id", "openalex", "--request-key", "example_work_metadata", "--output", "media_downloads/probe.json", "--json"]), 1)

    def test_summary_script_writes_no_files_by_default(self):
        code = summarizer.main(["--input", "examples/connectors/h7_library_research/live_probe_results", "--check", "--json"])
        self.assertEqual(code, 0)

    def test_summary_script_writes_explicit_outputs_to_temp_path(self):
        with tempfile.TemporaryDirectory() as tempdir:
            output = Path(tempdir) / "summary.json"
            markdown = Path(tempdir) / "summary.md"
            code = summarizer.main(["--input", "examples/connectors/h7_library_research/live_probe_results", "--output", str(output), "--summary-output", str(markdown), "--json"])
            self.assertEqual(code, 0)
            self.assertTrue(output.is_file())
            self.assertTrue(markdown.is_file())
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(payload["network_used"])

    def test_summary_refuses_forbidden_roots(self):
        self.assertEqual(summarizer.main(["--input", "examples/connectors/h7_library_research/live_probe_results", "--output", "site/dist/summary.json", "--json"]), 1)
        self.assertEqual(summarizer.main(["--input", "examples/connectors/h7_library_research/live_probe_results", "--output", "site/dist/data/public_index/summary.json", "--json"]), 1)

    def test_validator_passes_current_repo(self):
        result = validator.validate_repo()
        self.assertEqual(result["status"], "valid", result["errors"])
        self.assertFalse(result["network_calls_made"])
        self.assertFalse(result["harvest_query_fetch_download_used"])
        self.assertFalse(result["restricted_source_access_used"])


if __name__ == "__main__":
    unittest.main()
