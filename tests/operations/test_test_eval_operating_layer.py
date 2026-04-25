import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEST_INVENTORY = ROOT / "control" / "inventory" / "tests"


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class TestTestEvalOperatingLayer(unittest.TestCase):
    def test_test_registry_parses_and_has_required_records(self):
        registry = load_json(TEST_INVENTORY / "test_registry.json")
        self.assertEqual(registry["inventory_kind"], "eureka.test_registry")
        records = {record["test_id"]: record for record in registry["records"]}

        required_ids = {
            "runtime_tests",
            "surfaces_tests",
            "repo_tests",
            "architecture_boundaries",
            "public_alpha_smoke",
            "hosting_pack_generator_check",
            "python_oracle_golden_check",
            "archive_resolution_eval_runner",
            "search_usefulness_audit_runner",
            "route_inventory_validation",
            "source_registry_validation",
            "operating_layer_validation",
            "comprehensive_audit_pack_validation",
            "cargo_check_optional",
            "cargo_test_optional",
        }
        self.assertTrue(required_ids.issubset(records))

        required_fields = {
            "test_id",
            "label",
            "command",
            "category",
            "owner_area",
            "required_for",
            "requires",
            "network",
            "writes",
            "expected_runtime",
            "failure_means",
            "advisory_or_required",
            "notes",
        }
        for record in registry["records"]:
            self.assertTrue(required_fields.issubset(record), record["test_id"])

    def test_command_matrix_parses_and_defines_expected_lanes(self):
        matrix = load_json(TEST_INVENTORY / "command_matrix.json")
        lanes = {lane["lane_id"]: lane for lane in matrix["lanes"]}
        self.assertTrue(
            {
                "fast",
                "standard",
                "full",
                "docs_only",
                "public_alpha",
                "parity",
                "audit",
                "rust_optional",
            }.issubset(lanes)
        )
        self.assertEqual(lanes["rust_optional"]["required_status"], "optional")
        self.assertIn("cargo_check_optional", lanes["rust_optional"]["commands"])

    def test_finding_schema_and_categories_exist(self):
        schema = load_json(ROOT / "control" / "audits" / "schemas" / "finding.schema.json")
        categories = load_json(
            ROOT / "control" / "audits" / "schemas" / "finding_categories.json"
        )
        self.assertIn("finding_id", schema["required"])
        self.assertIn("source_coverage_gap", categories["categories"])
        self.assertIn("eval_truth_gap", categories["categories"])

    def test_aide_queue_and_report_docs_exist_and_parse(self):
        queue = load_json(ROOT / ".aide" / "tasks" / "queue.yaml")
        backlog = load_json(ROOT / ".aide" / "tasks" / "audit_backlog.yaml")
        self.assertGreaterEqual(len(queue["items"]), 5)
        self.assertGreaterEqual(len(backlog["items"]), 3)
        self.assertTrue((ROOT / ".aide" / "tasks" / "README.md").exists())
        self.assertTrue((ROOT / ".aide" / "reports" / "README.md").exists())

    def test_test_eval_lanes_doc_exists(self):
        doc = ROOT / "docs" / "operations" / "TEST_AND_EVAL_LANES.md"
        self.assertTrue(doc.exists())
        text = doc.read_text(encoding="utf-8")
        self.assertIn("rust_optional", text)
        self.assertIn("pending_manual_observation", text)
        self.assertIn("Sync origin", text)

    def test_external_baseline_work_is_not_required_ci(self):
        registry = load_json(TEST_INVENTORY / "test_registry.json")
        required_records = [
            record
            for record in registry["records"]
            if record["advisory_or_required"] == "required"
        ]
        for record in required_records:
            self.assertNotIn("Google scraping", record["notes"])
            self.assertNotIn("Internet Archive scraping", record["notes"])
            self.assertNotEqual(record["network"], "optional_manual")


if __name__ == "__main__":
    unittest.main()

