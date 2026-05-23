from __future__ import annotations

import unittest

from runtime.search.need.records import SearchNeed, SearchNeedDesiredOutcome, SearchNeedKind
from runtime.search.need.workunit_plan import map_need_kind_to_workunit_plan


def need(kind: SearchNeedKind) -> SearchNeed:
    return SearchNeed.new(
        hunt_id="hunt-1",
        exhaustion_report_id="report-1",
        query="sampleproject",
        need_title="Need",
        need_summary="Need summary",
        need_kind=kind,
        desired_outcome=SearchNeedDesiredOutcome.IMPROVE_INDEX,
        local_result_state="local_absent",
    )


class NeedToWorkUnitPlanTests(unittest.TestCase):
    def test_plan_builds_for_each_search_need_kind(self) -> None:
        for kind in SearchNeedKind:
            with self.subTest(kind=kind.value):
                plan = map_need_kind_to_workunit_plan(need(kind))
                self.assertEqual("search_need_workunit_plan.v0", plan.to_dict()["schema_version"])
                self.assertGreaterEqual(len(plan.items), 1)
                for item in plan.items:
                    payload = item.payload
                    self.assertEqual(need(kind).hunt_id, payload["search_hunt_id"])
                    self.assertFalse(payload["execution_enabled"])
                    self.assertFalse(payload["source_probe_execution_enabled"])
                    self.assertFalse(payload["extraction_execution_enabled"])
                    self.assertFalse(payload["model_provider_enabled"])

    def test_policy_blocked_future_actions_are_blocked_in_plan(self) -> None:
        plan = map_need_kind_to_workunit_plan(need(SearchNeedKind.IDENTIFY_UNKNOWN_ARTIFACT))
        blocked = [item for item in plan.items if item.policy_state.value == "blocked_by_policy"]
        self.assertTrue(blocked)
        self.assertTrue(all(item.blocked_reason for item in blocked))


if __name__ == "__main__":
    unittest.main()
