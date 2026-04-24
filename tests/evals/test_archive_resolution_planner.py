from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.engine.query_planner import plan_query


TASKS_ROOT = Path("evals/archive_resolution/tasks")


class ArchiveResolutionPlannerEvalTestCase(unittest.TestCase):
    def test_eval_fixtures_match_expected_planner_fields(self) -> None:
        for task_path in sorted(TASKS_ROOT.glob("*.yaml")):
            with self.subTest(task=task_path.name):
                fixture = json.loads(task_path.read_text(encoding="utf-8"))
                expected_plan = fixture.get("expected_plan")
                self.assertIsInstance(expected_plan, dict)

                task = plan_query(str(fixture["raw_query"]))

                self.assertEqual(task.task_kind, expected_plan["task_kind"])
                self.assertEqual(task.object_type, expected_plan["object_type"])

                for key, expected_value in expected_plan.get("constraints", {}).items():
                    actual_value = task.constraints.get(key)
                    if isinstance(expected_value, dict):
                        self.assertIsInstance(actual_value, dict)
                        for nested_key, nested_expected_value in expected_value.items():
                            self.assertEqual(actual_value.get(nested_key), nested_expected_value)
                    else:
                        self.assertEqual(actual_value, expected_value)

                for preferred in expected_plan.get("prefer", []):
                    self.assertIn(preferred, task.prefer)

                for excluded in expected_plan.get("exclude", []):
                    self.assertIn(excluded, task.exclude)


if __name__ == "__main__":
    unittest.main()
