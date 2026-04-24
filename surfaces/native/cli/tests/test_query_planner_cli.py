from __future__ import annotations

import json
import tempfile
import unittest
from io import StringIO

from surfaces.native.cli.main import main


def run_cli(*args: str) -> tuple[int, str]:
    output = StringIO()
    exit_code = main(list(args), stdout=output)
    return exit_code, output.getvalue()


class QueryPlannerCliTestCase(unittest.TestCase):
    def test_query_plan_command_renders_expected_fields(self) -> None:
        exit_code, output = run_cli("query-plan", "Windows 7 apps")

        self.assertEqual(exit_code, 0)
        self.assertIn("Query plan", output)
        self.assertIn("task_kind: browse_software", output)
        self.assertIn("object_type: software", output)
        self.assertIn("Windows 7", output)

    def test_query_plan_command_supports_json_output(self) -> None:
        exit_code, output = run_cli(
            "query-plan",
            "latest Firefox before XP support ended",
            "--json",
        )

        payload = json.loads(output)
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "planned")
        self.assertEqual(payload["query_plan"]["task_kind"], "find_software_release")
        self.assertEqual(payload["query_plan"]["constraints"]["product_hint"], "Firefox")

    def test_run_planned_search_persists_resolution_task(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            exit_code, output = run_cli(
                "run-planned-search",
                "latest Firefox before XP support ended",
                "--run-store-root",
                temp_dir,
            )

        self.assertEqual(exit_code, 0)
        self.assertIn("Resolution task", output)
        self.assertIn("task_kind: find_software_release", output)


if __name__ == "__main__":
    unittest.main()
