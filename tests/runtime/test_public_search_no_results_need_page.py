from __future__ import annotations

import unittest

from runtime.public_search import build_no_results_need_view_model


class PublicSearchNoResultsNeedPageTests(unittest.TestCase):
    def test_no_results_keeps_bounded_need_posture(self) -> None:
        page = build_no_results_need_view_model("missing scanned manual")

        self.assertEqual("no_results", page["page_kind"])
        self.assertFalse(page["accepted_truth"])
        self.assertFalse(page["public_mutation_enabled"])
        self.assertTrue(page["review_required"])
        self.assertGreater(len(page["next_actions"]), 0)
        self.assertTrue(any(action["enabled"] is False for action in page["next_actions"]))


if __name__ == "__main__":
    unittest.main()
