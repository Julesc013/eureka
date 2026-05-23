import ast
import json
import tempfile
import unittest
from pathlib import Path

from runtime.evidence.ledger import EvidenceLedgerStore
from scripts.demo_evidence_ledger_store import run_demo
from scripts.validate_evidence_ledger_store import validate_store


REPO_ROOT = Path(__file__).resolve().parents[2]


class EvidenceLedgerIntegrationTests(unittest.TestCase):
    def test_demo_runs_without_network(self):
        output = run_demo(":memory:", ":memory:")
        self.assertEqual("pass", output["status"])
        self.assertEqual(1, output["summary"]["source_cache_link_count"])
        self.assertFalse(output["public_index_writes_enabled"])

    def test_validator_passes(self):
        result = validate_store(REPO_ROOT)
        self.assertEqual("pass", result["status"])
        self.assertEqual(0, result["network_dependencies"])
        self.assertEqual(0, result["h_series_dependencies"])

    def test_no_runtime_connectors_dependency(self):
        for path in (REPO_ROOT / "runtime/evidence/ledger").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                module = None
                if isinstance(node, ast.ImportFrom):
                    module = node.module
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertFalse(alias.name.startswith("runtime.connectors"))
                if module:
                    self.assertFalse(module.startswith("runtime.connectors"))
                    self.assertFalse(module.startswith("runtime.local_foundry"))

    def test_file_backed_demo_persists_to_explicit_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_cache_db = Path(tmp) / "source-cache.sqlite"
            evidence_db = Path(tmp) / "evidence-ledger.sqlite"
            output = run_demo(source_cache_db, evidence_db)
            self.assertTrue(source_cache_db.is_file())
            self.assertTrue(evidence_db.is_file())
            with EvidenceLedgerStore.open(evidence_db) as store:
                store.init()
                self.assertEqual(1, store.summarize().evidence_candidate_count)
            self.assertEqual(1, output["summary"]["evidence_candidate_count"])

    def test_serialized_output_has_no_reserved_boundary_fields(self):
        text = json.dumps(run_demo(":memory:", ":memory:"), sort_keys=True)
        self.assertNotIn("truth_boundary", text)
        self.assertNotIn("product_boundary", text)
        self.assertNotIn("accepted_truth", text)
        self.assertNotIn("public_index_mutated", text)
        self.assertNotIn("master_index_mutated", text)


if __name__ == "__main__":
    unittest.main()
