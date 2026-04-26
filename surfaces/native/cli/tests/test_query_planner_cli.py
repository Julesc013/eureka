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
        self.assertIn("platform_is_constraint=True", output)
        self.assertIn("os_iso_image", output)

    def test_query_plan_command_supports_json_output(self) -> None:
        exit_code, output = run_cli(
            "query-plan",
            "latest Firefox before XP support ended",
            "--json",
        )

        payload = json.loads(output)
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "planned")
        self.assertEqual(payload["query_plan"]["task_kind"], "find_latest_compatible_release")
        self.assertEqual(payload["query_plan"]["constraints"]["product_hint"], "Firefox")
        self.assertEqual(
            payload["query_plan"]["constraints"]["temporal_goal"],
            "latest_before_support_drop",
        )

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
        self.assertIn("task_kind: find_latest_compatible_release", output)

    def test_query_plan_command_shows_driver_member_hints(self) -> None:
        exit_code, output = run_cli(
            "query-plan",
            "driver for ThinkPad T42 Wi-Fi Windows 2000",
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("task_kind: find_driver", output)
        self.assertIn("hardware_hint=ThinkPad T42 Wi-Fi", output)
        self.assertIn("INF", output)
        self.assertIn("decompose", output)


if __name__ == "__main__":
    unittest.main()
