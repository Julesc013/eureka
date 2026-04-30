from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOT = REPO_ROOT / "contracts" / "master_index"
INVENTORY_ROOT = REPO_ROOT / "control" / "inventory" / "master_index"
EXAMPLE_QUEUE = REPO_ROOT / "examples" / "master_index_review_queue" / "minimal_review_queue_v0"
REFERENCE_DOC = REPO_ROOT / "docs" / "reference" / "MASTER_INDEX_REVIEW_QUEUE_CONTRACT.md"
ARCHITECTURE_DOC = REPO_ROOT / "docs" / "architecture" / "MASTER_INDEX_REVIEW_QUEUE.md"
AUDIT_REPORT = (
    REPO_ROOT
    / "control"
    / "audits"
    / "master-index-review-queue-contract-v0"
    / "master_index_review_queue_contract_report.json"
)


class MasterIndexReviewQueueContractTestCase(unittest.TestCase):
    def test_schemas_and_inventory_parse(self) -> None:
        for path in [
            SCHEMA_ROOT / "review_queue_manifest.v0.json",
            SCHEMA_ROOT / "review_queue_entry.v0.json",
            SCHEMA_ROOT / "review_decision.v0.json",
            INVENTORY_ROOT / "review_queue_policy.json",
            INVENTORY_ROOT / "review_state_taxonomy.json",
            INVENTORY_ROOT / "acceptance_requirements.json",
            AUDIT_REPORT,
        ]:
            self.assertTrue(path.exists(), path)
            json.loads(path.read_text(encoding="utf-8"))

    def test_example_queue_shape(self) -> None:
        manifest = json.loads((EXAMPLE_QUEUE / "REVIEW_QUEUE_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], "master_index_review_queue_manifest.v0")
        self.assertTrue(manifest["no_runtime_implemented"])
        self.assertTrue(manifest["no_upload_implemented"])
        self.assertTrue(manifest["no_accounts_implemented"])
        self.assertTrue(manifest["no_auto_acceptance"])
        self.assertEqual(manifest["queue_entries"], ["queue_entries.jsonl"])
        self.assertEqual(manifest["decision_files"], ["review_decisions.jsonl"])

    def test_entries_and_decisions_reference_each_other(self) -> None:
        entries = _read_jsonl(EXAMPLE_QUEUE / "queue_entries.jsonl")
        decisions = _read_jsonl(EXAMPLE_QUEUE / "review_decisions.jsonl")
        self.assertEqual(len(entries), 1)
        self.assertEqual(len(decisions), 1)
        entry_ids = {entry["queue_entry_id"] for entry in entries}
        self.assertIn(decisions[0]["queue_entry_id"], entry_ids)
        self.assertEqual(decisions[0]["decision"], "defer")
        self.assertFalse(decisions[0]["public_claims_allowed"]["allowed"])
        self.assertGreater(len(decisions[0]["limitations"]), 0)

    def test_example_queue_has_no_executables_private_paths_or_live_urls(self) -> None:
        forbidden_suffixes = {".exe", ".msi", ".dmg", ".pkg", ".app", ".deb", ".rpm", ".iso", ".db", ".sqlite", ".sqlite3"}
        for path in EXAMPLE_QUEUE.rglob("*"):
            if not path.is_file():
                continue
            self.assertNotIn(path.suffix.lower(), forbidden_suffixes)
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("http://", text)
            self.assertNotIn("https://", text)
            self.assertNotIn("C:\\", text)
            self.assertNotIn("/Users/", text)
            self.assertNotIn("/home/", text)

    def test_docs_state_contract_only_boundaries(self) -> None:
        combined = (
            REFERENCE_DOC.read_text(encoding="utf-8")
            + "\n"
            + ARCHITECTURE_DOC.read_text(encoding="utf-8")
        ).lower()
        for phrase in [
            "contract-only",
            "no hosted queue",
            "validation is not acceptance",
            "contribution is not truth",
            "automatic acceptance",
            "does not implement uploads",
            "source/evidence/index pack import planning",
        ]:
            self.assertIn(phrase, combined)

    def test_audit_report_records_no_runtime_claims(self) -> None:
        report = json.loads(AUDIT_REPORT.read_text(encoding="utf-8"))
        self.assertFalse(report["runtime_implemented"])
        self.assertFalse(report["upload_implemented"])
        self.assertFalse(report["accounts_implemented"])
        self.assertFalse(report["hosted_master_index_implemented"])
        self.assertFalse(report["automatic_acceptance_implemented"])
        self.assertFalse(report["rights_clearance_claimed"])
        self.assertFalse(report["malware_safety_claimed"])
        self.assertFalse(report["canonical_truth_claimed"])


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    unittest.main()
