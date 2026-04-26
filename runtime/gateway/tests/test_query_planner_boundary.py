from __future__ import annotations

import unittest

from runtime.gateway import build_demo_query_planner_public_api
from runtime.gateway.public_api import QueryPlanRequest


class QueryPlannerPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_query_planner_public_api()

    def test_plan_query_returns_expected_envelope(self) -> None:
        response = self.public_api.plan_query(
            QueryPlanRequest.from_parts("Windows 7 apps"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["status"], "planned")
        self.assertEqual(response.body["query_plan"]["task_kind"], "browse_software")
        self.assertEqual(
            response.body["query_plan"]["constraints"]["platform"]["marketing_alias"],
            "Windows 7",
        )
        self.assertTrue(response.body["query_plan"]["constraints"]["platform_is_constraint"])
        self.assertIn("os_iso_image", response.body["query_plan"]["exclude"])
        self.assertIn("internet_archive_recorded", response.body["query_plan"]["source_hints"])

    def test_empty_query_returns_structured_error(self) -> None:
        response = self.public_api.plan_query_text("   ")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.body["status"], "blocked")
        self.assertEqual(response.body["notices"][0]["code"], "raw_query_required")


if __name__ == "__main__":
    unittest.main()
