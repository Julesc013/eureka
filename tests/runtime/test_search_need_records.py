from __future__ import annotations

import unittest

from runtime.search_need import SearchNeed, SearchNeedValidationError, validate_search_need


class SearchNeedRecordTests(unittest.TestCase):
    def test_search_need_validates_required_fields(self) -> None:
        need = SearchNeed.new(
            hunt_id="hunt-1",
            exhaustion_report_id="report-1",
            query="sampleproject",
            need_title="Investigate sampleproject",
            need_summary="Local demand state only.",
            need_kind="find_exact_artifact",
            desired_outcome="improve_index",
            local_result_state="local_absent",
        )

        self.assertIs(validate_search_need(need), need)
        self.assertEqual("sampleproject", need.normalized_query)
        self.assertFalse(need.to_dict()["workunit_creation_enabled"])
        self.assertFalse(need.to_dict()["source_probe_execution_enabled"])

    def test_query_validation_rejects_empty_query(self) -> None:
        need = SearchNeed.new(
            hunt_id="hunt-1",
            exhaustion_report_id="report-1",
            query="sampleproject",
            need_title="Investigate sampleproject",
            need_summary="Local demand state only.",
            need_kind="find_exact_artifact",
            desired_outcome="improve_index",
            local_result_state="local_absent",
        )
        invalid = SearchNeed(
            **{
                **need.__dict__,
                "query": "",
                "normalized_query": "",
            }
        )

        with self.assertRaises(SearchNeedValidationError):
            validate_search_need(invalid)


if __name__ == "__main__":
    unittest.main()
