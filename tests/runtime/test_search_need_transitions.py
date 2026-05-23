from __future__ import annotations

import unittest

from runtime.search.need import SearchNeed, SearchNeedTransitionError, apply_transition, validate_transition


def sample_need() -> SearchNeed:
    return SearchNeed.new(
        hunt_id="hunt-1",
        exhaustion_report_id="report-1",
        query="sampleproject",
        need_title="Investigate sampleproject",
        need_summary="Local demand state only.",
        need_kind="find_exact_artifact",
        desired_outcome="improve_index",
        local_result_state="local_absent",
    )


class SearchNeedTransitionTests(unittest.TestCase):
    def test_valid_transitions_pass(self) -> None:
        need = sample_need()
        opened = apply_transition(need, "open", "operator opened")

        self.assertEqual("open", opened.state.value)
        self.assertEqual("open", validate_transition("proposed", "open").value)

    def test_invalid_transitions_fail_closed(self) -> None:
        with self.assertRaises(SearchNeedTransitionError):
            validate_transition("proposed", "satisfied_locally")


if __name__ == "__main__":
    unittest.main()
