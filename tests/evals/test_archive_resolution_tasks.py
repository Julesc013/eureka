import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ARCHIVE_RESOLUTION_ROOT = REPO_ROOT / "evals" / "archive_resolution"
TASKS_ROOT = ARCHIVE_RESOLUTION_ROOT / "tasks"
SCHEMA_PATH = ARCHIVE_RESOLUTION_ROOT / "task.schema.yaml"


def _load_yaml_json_subset(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


class ArchiveResolutionTaskCorpusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = _load_yaml_json_subset(SCHEMA_PATH)
        self.required_fields = self.schema["required"]
        self.task_paths = sorted(TASKS_ROOT.glob("*.yaml"))
        self.assertTrue(self.task_paths, "Expected at least one archive-resolution task fixture.")

    def test_schema_declares_expected_required_fields(self) -> None:
        self.assertEqual(
            self.required_fields,
            [
                "id",
                "raw_query",
                "query_family",
                "desired_intent",
                "desired_object_types",
                "target_constraints",
                "bad_result_patterns",
                "acceptable_result_patterns",
                "minimum_granularity",
                "required_evidence",
                "expected_lanes",
                "allowed_absence_outcomes",
            ],
        )

    def test_each_task_is_machine_readable_and_matches_required_shape(self) -> None:
        for task_path in self.task_paths:
            with self.subTest(task=task_path.name):
                task = _load_yaml_json_subset(task_path)
                for field in self.required_fields:
                    self.assertIn(field, task)

                self.assertEqual(task["id"], task_path.stem)
                self.assertIsInstance(task["raw_query"], str)
                self.assertTrue(task["raw_query"].strip())
                self.assertIsInstance(task["query_family"], str)
                self.assertTrue(task["query_family"].strip())
                self.assertIsInstance(task["desired_intent"], str)
                self.assertTrue(task["desired_intent"].strip())

                desired_object_types = task["desired_object_types"]
                self.assertIsInstance(desired_object_types, list)
                self.assertTrue(desired_object_types)
                self.assertTrue(all(isinstance(item, str) and item.strip() for item in desired_object_types))

                target_constraints = task["target_constraints"]
                self.assertIsInstance(target_constraints, dict)
                self.assertTrue(target_constraints)

                for field_name in (
                    "bad_result_patterns",
                    "acceptable_result_patterns",
                    "required_evidence",
                    "expected_lanes",
                    "allowed_absence_outcomes",
                ):
                    value = task[field_name]
                    self.assertIsInstance(value, list, f"{field_name} must be a list.")
                    self.assertTrue(value, f"{field_name} must not be empty.")
                    self.assertTrue(
                        all(isinstance(item, str) and item.strip() for item in value),
                        f"{field_name} entries must be non-empty strings.",
                    )

                self.assertIsInstance(task["minimum_granularity"], str)
                self.assertTrue(task["minimum_granularity"].strip())

    def test_task_ids_are_unique(self) -> None:
        ids = [_load_yaml_json_subset(task_path)["id"] for task_path in self.task_paths]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
