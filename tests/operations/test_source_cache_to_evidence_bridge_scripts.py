import json
import tempfile
import unittest
from pathlib import Path

from scripts import bridge_source_cache_to_evidence, validate_source_cache_to_evidence_bridge


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_METADATA = REPO_ROOT / "examples/sources/cache/records/source_metadata_record_v0.json"


class SourceCacheToEvidenceBridgeScriptTests(unittest.TestCase):
    def test_bridge_script_writes_no_files_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            before = set(Path(tmp).iterdir())
            code = bridge_source_cache_to_evidence.main(["--input", str(SOURCE_METADATA), "--check"])
            after = set(Path(tmp).iterdir())
        self.assertEqual(code, 0)
        self.assertEqual(before, after)

    def test_bridge_script_writes_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "bridge_result.json"
            evidence_output = Path(tmp) / "evidence_candidate.json"
            summary_output = Path(tmp) / "bridge_summary.md"
            code = bridge_source_cache_to_evidence.main(
                [
                    "--input",
                    str(SOURCE_METADATA),
                    "--output",
                    str(output),
                    "--evidence-output",
                    str(evidence_output),
                    "--summary-output",
                    str(summary_output),
                    "--check",
                    "--json",
                ]
            )
            self.assertEqual(code, 0)
            result = json.loads(output.read_text(encoding="utf-8"))
            candidate = json.loads(evidence_output.read_text(encoding="utf-8"))
            summary_text = summary_output.read_text(encoding="utf-8")
        self.assertEqual(result["schema_version"], "source_cache_to_evidence_bridge_result.v0")
        self.assertEqual(candidate["evidence_record_type"], "metadata_claim")
        self.assertTrue(summary_text.startswith("# Source Cache To Evidence Bridge Summary"))

    def test_bridge_script_refuses_site_dist_output(self) -> None:
        self.assertFalse(bridge_source_cache_to_evidence.output_path_allowed(REPO_ROOT / "site/dist/bridge.json"))

    def test_bridge_script_refuses_runtime_output(self) -> None:
        self.assertFalse(bridge_source_cache_to_evidence.output_path_allowed(REPO_ROOT / "runtime/bridge.json"))

    def test_validator_passes_current_repo(self) -> None:
        report = validate_source_cache_to_evidence_bridge.validate_source_cache_to_evidence_bridge(REPO_ROOT)
        self.assertEqual(report["status"], "pass", report["errors"])

    def test_product_boundary_true_claim_fails(self) -> None:
        report = bridge_source_cache_to_evidence.build_report(SOURCE_METADATA)
        result = report["bridge_result"]
        result["product_boundary"]["enabled_telemetry"] = True
        from runtime.local.foundry import source_cache_to_evidence

        self.assertTrue(source_cache_to_evidence.detect_bridge_product_boundary_violations(result))

    def test_runtime_does_not_call_network_model_or_provider(self) -> None:
        runtime_source = (REPO_ROOT / "runtime/local/foundry/source_cache_to_evidence.py").read_text(encoding="utf-8")
        script_source = (REPO_ROOT / "scripts/bridge_source_cache_to_evidence.py").read_text(encoding="utf-8")
        for token in ("requests", "urllib", "socket", "openai", "anthropic", "selenium", "playwright"):
            self.assertNotIn(token, runtime_source)
            self.assertNotIn(token, script_source)

    def test_runtime_does_not_mutate_master_index_or_create_private_roots(self) -> None:
        report = bridge_source_cache_to_evidence.build_report(SOURCE_METADATA)
        self.assertFalse(report["bridge_result"]["product_boundary"]["mutated_master_index"])
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
