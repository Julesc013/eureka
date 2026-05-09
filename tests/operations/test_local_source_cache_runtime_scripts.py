import json
import tempfile
import unittest
from pathlib import Path

from scripts import record_source_cache, summarize_source_cache, validate_local_source_cache_runtime


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_LEAD = REPO_ROOT / "examples/source_cache_records/source_lead_record_v0.json"


class LocalSourceCacheRuntimeScriptTests(unittest.TestCase):
    def test_record_script_writes_no_files_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            before = set(Path(tmp).iterdir())
            code = record_source_cache.main(["--input", str(SOURCE_LEAD), "--check"])
            after = set(Path(tmp).iterdir())
        self.assertEqual(code, 0)
        self.assertEqual(before, after)

    def test_record_script_writes_explicit_report_to_temp_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "source_cache_report.json"
            code = record_source_cache.main(["--input", str(SOURCE_LEAD), "--output", str(output), "--check", "--json"])
            self.assertEqual(code, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["record"]["source_cache_record_type"], "source_lead_record")

    def test_record_script_refuses_site_dist_output(self) -> None:
        self.assertFalse(record_source_cache.output_path_allowed(REPO_ROOT / "site/dist/source_cache.json"))

    def test_record_script_refuses_runtime_output(self) -> None:
        self.assertFalse(record_source_cache.output_path_allowed(REPO_ROOT / "runtime/source_cache.json"))

    def test_summarizer_works_on_examples(self) -> None:
        code = summarize_source_cache.main(["--input", str(REPO_ROOT / "examples/source_cache_records"), "--check"])
        self.assertEqual(code, 0)

    def test_summarizer_writes_explicit_report_to_temp_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "source_cache_snapshot.json"
            summary = Path(tmp) / "source_cache_summary.md"
            code = summarize_source_cache.main(
                [
                    "--input",
                    str(REPO_ROOT / "examples/source_cache_records"),
                    "--output",
                    str(output),
                    "--summary-output",
                    str(summary),
                    "--check",
                ]
            )
            self.assertEqual(code, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(summary.read_text(encoding="utf-8").startswith("# Source Cache Summary"))
        self.assertEqual(payload["summary"]["source_cache_record_count"], 8)

    def test_validator_passes_current_repo(self) -> None:
        report = validate_local_source_cache_runtime.validate_local_source_cache_runtime(REPO_ROOT)
        self.assertEqual(report["status"], "pass", report["errors"])

    def test_product_boundary_true_claim_fails(self) -> None:
        report = record_source_cache.build_report(SOURCE_LEAD)
        record = report["record"]
        record["product_boundary"]["enabled_telemetry"] = True
        from runtime.local_foundry import source_cache

        self.assertTrue(source_cache.detect_product_boundary_violations(record))

    def test_runtime_does_not_call_network_model_or_provider(self) -> None:
        runtime_source = (REPO_ROOT / "runtime/local_foundry/source_cache.py").read_text(encoding="utf-8")
        scripts = (
            (REPO_ROOT / "scripts/record_source_cache.py").read_text(encoding="utf-8")
            + (REPO_ROOT / "scripts/summarize_source_cache.py").read_text(encoding="utf-8")
        )
        for token in ("requests", "urllib", "socket", "openai", "anthropic", "selenium", "playwright"):
            self.assertNotIn(token, runtime_source)
            self.assertNotIn(token, scripts)

    def test_runtime_does_not_mutate_master_index_or_create_private_roots(self) -> None:
        report = record_source_cache.build_report(SOURCE_LEAD)
        self.assertFalse(report["record"]["product_boundary"]["mutated_master_index"])
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
