import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_ROOT = ROOT / "control/audits/evidence-ledger-local-dry-run-runtime-v0"
REPORT = AUDIT_ROOT / "evidence_ledger_local_dry_run_runtime_report.json"
INVENTORY = ROOT / "control/inventory/evidence_ledger/evidence_ledger_local_dry_run_runtime.json"
OPS_DOC = ROOT / "docs/operations/EVIDENCE_LEDGER_LOCAL_DRY_RUN_RUNTIME.md"
RUNTIME_DOC = ROOT / "runtime/evidence_ledger/README.md"
COMMAND_MATRIX = ROOT / "control/inventory/tests/command_matrix.json"


class EvidenceLedgerLocalDryRunOperationsTests(unittest.TestCase):
    def test_audit_inventory_docs_and_runtime_docs_exist(self) -> None:
        for path in (
            AUDIT_ROOT / "README.md",
            AUDIT_ROOT / "RUNTIME_SCOPE.md",
            AUDIT_ROOT / "DRY_RUN_INPUT_MODEL.md",
            AUDIT_ROOT / "DRY_RUN_OUTPUT_MODEL.md",
            REPORT,
            INVENTORY,
            OPS_DOC,
            RUNTIME_DOC,
        ):
            self.assertTrue(path.is_file(), path)

    def test_report_and_inventory_hard_flags(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        self.assertTrue(report["local_dry_run_runtime_implemented"])
        self.assertTrue(inventory["local_dry_run_runtime_implemented"])
        for key in (
            "authoritative_evidence_ledger_runtime_implemented",
            "live_source_called",
            "external_calls_performed",
            "connector_runtime_executed",
            "source_sync_worker_executed",
            "authoritative_evidence_ledger_written",
            "evidence_ledger_mutated",
            "source_cache_mutated",
            "candidate_index_mutated",
            "public_index_mutated",
            "local_index_mutated",
            "master_index_mutated",
            "public_search_runtime_mutated",
            "claim_accepted_as_truth",
            "promotion_decision_created",
            "hosted_runtime_enabled",
            "telemetry_exported",
            "credentials_used",
            "downloads_enabled",
            "installs_enabled",
            "execution_enabled",
        ):
            self.assertFalse(report[key], key)
        self.assertFalse(inventory["authoritative_evidence_ledger_runtime_implemented"])
        self.assertFalse(inventory["public_search_integration_enabled"])
        self.assertFalse(inventory["truth_acceptance_enabled"])
        self.assertFalse(inventory["promotion_decision_enabled"])

    def test_command_matrix_includes_new_commands(self) -> None:
        matrix = COMMAND_MATRIX.read_text(encoding="utf-8")
        self.assertIn("python scripts/run_evidence_ledger_dry_run.py --all-examples --json", matrix)
        self.assertIn("python scripts/validate_evidence_ledger_dry_run_report.py", matrix)
        self.assertIn("python scripts/validate_evidence_ledger_dry_run_report.py --json", matrix)

    def test_docs_state_dry_run_boundaries(self) -> None:
        text = (OPS_DOC.read_text(encoding="utf-8") + "\n" + RUNTIME_DOC.read_text(encoding="utf-8")).casefold()
        for phrase in (
            "local dry-run",
            "not an authoritative evidence-ledger runtime",
            "no live source calls",
            "no public search integration",
            "does not call live sources",
            "does not alter public search",
            "does not accept claims as truth",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
