import json
import tempfile
import unittest
from pathlib import Path

from scripts import record_evidence_ledger, summarize_evidence_ledger, validate_local_evidence_ledger_runtime


REPO_ROOT = Path(__file__).resolve().parents[2]
METADATA_CLAIM = REPO_ROOT / "examples/evidence_ledger_records/metadata_claim_record_v0.json"


class LocalEvidenceLedgerRuntimeScriptTests(unittest.TestCase):
    def test_record_script_writes_no_files_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            before = set(Path(tmp).iterdir())
            code = record_evidence_ledger.main(["--input", str(METADATA_CLAIM), "--check"])
            after = set(Path(tmp).iterdir())
        self.assertEqual(code, 0)
        self.assertEqual(before, after)

    def test_record_script_writes_explicit_report_to_temp_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "evidence_report.json"
            code = record_evidence_ledger.main(["--input", str(METADATA_CLAIM), "--output", str(output), "--check", "--json"])
            self.assertEqual(code, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["record"]["evidence_record_type"], "metadata_claim")

    def test_record_script_refuses_site_dist_output(self) -> None:
        self.assertFalse(record_evidence_ledger.output_path_allowed(REPO_ROOT / "site/dist/evidence.json"))

    def test_record_script_refuses_runtime_output(self) -> None:
        self.assertFalse(record_evidence_ledger.output_path_allowed(REPO_ROOT / "runtime/evidence.json"))

    def test_summarizer_works_on_examples(self) -> None:
        code = summarize_evidence_ledger.main(["--input", str(REPO_ROOT / "examples/evidence_ledger_records"), "--check"])
        self.assertEqual(code, 0)

    def test_summarizer_writes_explicit_report_to_temp_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "evidence_snapshot.json"
            summary = Path(tmp) / "evidence_summary.md"
            code = summarize_evidence_ledger.main(
                [
                    "--input",
                    str(REPO_ROOT / "examples/evidence_ledger_records"),
                    "--output",
                    str(output),
                    "--summary-output",
                    str(summary),
                    "--check",
                ]
            )
            self.assertEqual(code, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(summary.read_text(encoding="utf-8").startswith("# Evidence Ledger Summary"))
        self.assertEqual(payload["summary"]["evidence_record_count"], 10)

    def test_validator_passes_current_repo(self) -> None:
        report = validate_local_evidence_ledger_runtime.validate_local_evidence_ledger_runtime(REPO_ROOT)
        self.assertEqual(report["status"], "pass", report["errors"])

    def test_product_boundary_true_claim_fails(self) -> None:
        report = record_evidence_ledger.build_report(METADATA_CLAIM)
        record = report["record"]
        record["product_boundary"]["enabled_telemetry"] = True
        from runtime.local_foundry import evidence_ledger

        self.assertTrue(evidence_ledger.detect_evidence_product_boundary_violations(record))

    def test_runtime_does_not_call_network_model_or_provider(self) -> None:
        runtime_source = (REPO_ROOT / "runtime/local_foundry/evidence_ledger.py").read_text(encoding="utf-8")
        scripts = (
            (REPO_ROOT / "scripts/record_evidence_ledger.py").read_text(encoding="utf-8")
            + (REPO_ROOT / "scripts/summarize_evidence_ledger.py").read_text(encoding="utf-8")
        )
        for token in ("requests", "urllib", "socket", "openai", "anthropic", "selenium", "playwright"):
            self.assertNotIn(token, runtime_source)
            self.assertNotIn(token, scripts)

    def test_runtime_does_not_mutate_master_index_or_create_private_roots(self) -> None:
        report = record_evidence_ledger.build_report(METADATA_CLAIM)
        self.assertFalse(report["record"]["product_boundary"]["mutated_master_index"])
        for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / rel).exists(), rel)


if __name__ == "__main__":
    unittest.main()
