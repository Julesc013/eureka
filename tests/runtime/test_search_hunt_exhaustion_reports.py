from __future__ import annotations

import unittest

from runtime.search.hunt.records import (
    SearchHuntBlockedPolicyReport,
    SearchHuntCheckedLayerReport,
    SearchHuntDeferredLayerReport,
    SearchHuntExhaustionReport,
    SearchHuntRecommendedAction,
)
from runtime.search.hunt.validation import validate_search_hunt_exhaustion_report


class SearchHuntExhaustionReportRecordTests(unittest.TestCase):
    def test_report_sections_and_non_claims_are_serialized(self) -> None:
        report = SearchHuntExhaustionReport.new(
            "hunt-1",
            state="informative",
            query_summary={"original_query": "sampleproject", "normalized_query": "sampleproject"},
            checked_layers=[SearchHuntCheckedLayerReport("reviewed_public_index", "checked", "local only")],
            result_state={"reviewed_result_count": 0, "confidence_class": "local_absent"},
            unchecked_or_deferred_layers=[SearchHuntDeferredLayerReport("source_probes", "deferred", "disabled", "later gate")],
            blocked_by_policy=[SearchHuntBlockedPolicyReport("source_probe_disabled", "blocked", "source probe disabled")],
            recommended_next_actions=[SearchHuntRecommendedAction("create_search_need_later", "deferred", "later")],
            limitations=["local current-index absence only"],
        )
        payload = validate_search_hunt_exhaustion_report(report).to_dict()

        for section in (
            "query_summary",
            "checked_layers",
            "result_state",
            "unchecked_or_deferred_layers",
            "blocked_by_policy",
            "recommended_next_actions",
            "limitations",
            "non_claims",
        ):
            self.assertIn(section, payload)
        self.assertIn("local current-index", " ".join(payload["limitations"]))
        self.assertNotIn("production ready", str(payload).lower())
        self.assertNotIn("public launch ready", str(payload).lower())


if __name__ == "__main__":
    unittest.main()
