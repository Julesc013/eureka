from __future__ import annotations

import unittest

from runtime.gateway import build_demo_query_planner_public_api
from runtime.gateway.public_api import QueryPlanRequest, query_plan_envelope_to_view_model


class QueryPlannerViewModelsTestCase(unittest.TestCase):
    def test_planned_envelope_coerces_to_view_model(self) -> None:
        response = build_demo_query_planner_public_api().plan_query(
            QueryPlanRequest.from_parts("driver for ThinkPad T42 Wi-Fi Windows 2000"),
        )

        view_model = query_plan_envelope_to_view_model(response.body)

        self.assertEqual(view_model["status"], "planned")
        self.assertEqual(view_model["query_plan"]["task_kind"], "find_driver")
        self.assertEqual(
            view_model["query_plan"]["constraints"]["platform"]["marketing_alias"],
            "Windows 2000",
        )
        self.assertEqual(
            view_model["query_plan"]["constraints"]["hardware_hint"],
            "ThinkPad T42 Wi-Fi",
        )
        self.assertIn("INF", view_model["query_plan"]["constraints"]["representation_hints"])


if __name__ == "__main__":
    unittest.main()
