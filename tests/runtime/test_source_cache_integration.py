import json
import unittest
from io import StringIO
from pathlib import Path
from unittest import mock

from scripts.demo_source_cache_store import main as demo_main, run_demo
from scripts.validate_source_cache_store import validate_store


class SourceCacheIntegrationTests(unittest.TestCase):
    def test_source_observation_flow_writes_durable_cache_entry(self) -> None:
        result = run_demo(":memory:")
        self.assertEqual("pass", result["status"])
        self.assertEqual(1, result["summary"]["cache_entry_count"])
        self.assertEqual("cached", result["source_cache_entry"]["status"])

    def test_serialized_cache_entry_contains_no_boundary_fields(self) -> None:
        result = run_demo(":memory:")
        text = json.dumps(result["source_cache_entry"], sort_keys=True)
        self.assertNotIn("truth_boundary", text)
        self.assertNotIn("product_boundary", text)

    def test_store_does_not_write_evidence_review_or_indexes(self) -> None:
        result = run_demo(":memory:")
        self.assertFalse(result["evidence_ledger_writes_enabled"])
        self.assertFalse(result["review_queue_writes_enabled"])
        self.assertFalse(result["public_index_writes_enabled"])
        self.assertFalse(result["master_index_writes_enabled"])

    def test_demo_runs_without_network(self) -> None:
        with mock.patch("socket.socket", side_effect=AssertionError("network disabled")):
            code = demo_main(["--json"], stdout=StringIO())
        self.assertEqual(0, code)

    def test_validator_passes(self) -> None:
        result = validate_store(Path(__file__).resolve().parents[2])
        self.assertEqual("pass", result["status"])
        self.assertEqual(0, result["h_series_dependencies"])
        self.assertEqual(0, result["network_dependencies"])

    def test_no_runtime_connectors_dependency(self) -> None:
        root = Path(__file__).resolve().parents[2] / "runtime/source_cache"
        text = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.py"))
        self.assertNotIn("runtime.connectors", text)
        self.assertNotIn("runtime.local_foundry", text)


if __name__ == "__main__":
    unittest.main()
