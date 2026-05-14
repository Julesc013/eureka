from __future__ import annotations

import unittest

from runtime.local_workbench import (
    build_search_hunt_detail_page_view,
    build_search_hunt_list_page_view,
    build_search_hunt_not_found_page_view,
)
from runtime.search_hunt import SearchHuntSession, SearchHuntTransition


def sample_hunt() -> SearchHuntSession:
    return SearchHuntSession.new("sampleproject", reviewed_result_count=0)


class SearchHuntUiViewModelTests(unittest.TestCase):
    def test_hunt_list_view_model_builds(self) -> None:
        view = build_search_hunt_list_page_view([sample_hunt().to_dict()])
        self.assertEqual(1, view.hunt_count)
        self.assertEqual("sampleproject", view.hunts[0].query)
        self.assertIn("reviewed_public_index", view.hunts[0].checked_layer_summary)
        self.assertTrue(view.unavailable_actions)
        self.assertTrue(view.limitations)

    def test_hunt_detail_view_model_builds(self) -> None:
        hunt = sample_hunt()
        transition = SearchHuntTransition.new(hunt.id, None, hunt.state, "created")
        summaries = [
            {
                "summary_type": "reviewed_index_search",
                "payload": {"query": hunt.query, "normalized_query": hunt.normalized_query, "result_count": 0},
            },
            {
                "summary_type": "local_absence",
                "payload": {"query": hunt.query, "normalized_query": hunt.normalized_query, "local_current_index_absence_only": True},
            },
        ]
        view = build_search_hunt_detail_page_view(hunt, [transition], {"summaries": summaries})
        self.assertTrue(view.found)
        self.assertEqual(hunt.id, view.hunt_id)
        self.assertEqual(1, len(view.transitions))
        self.assertTrue(view.checked_layers)
        self.assertTrue(view.unchecked_layers)
        self.assertTrue(view.reviewed_index_search_summary)
        self.assertTrue(view.local_absence_summary)

    def test_hunt_not_found_page_view_builds(self) -> None:
        view = build_search_hunt_not_found_page_view("missing")
        self.assertEqual("missing", view.hunt_id)
        self.assertIn("not created implicitly", " ".join(view.limitations))


if __name__ == "__main__":
    unittest.main()
