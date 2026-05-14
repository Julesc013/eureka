from __future__ import annotations

import unittest

from runtime.local_workbench import (
    build_search_hunt_detail_page_view,
    build_search_hunt_list_page_view,
    build_search_hunt_not_found_page_view,
    render_search_hunt_detail_page,
    render_search_hunt_list_page,
    render_search_hunt_not_found_page,
    validate_local_workbench_page,
)
from runtime.search_hunt import SearchHuntSession, SearchHuntTransition


def sample_hunt() -> SearchHuntSession:
    return SearchHuntSession.new("sampleproject", reviewed_result_count=0)


class SearchHuntUiPageTests(unittest.TestCase):
    def assert_read_only_page(self, html: str) -> None:
        validate_local_workbench_page(html)
        lowered = html.lower()
        self.assertIn("local appliance prototype", lowered)
        self.assertNotIn("<script", lowered)
        self.assertNotIn("method=\"post\"", lowered)
        self.assertNotIn("create hunt", lowered)
        self.assertNotIn("transition hunt", lowered)
        self.assertNotIn("create workunit", lowered)
        self.assertNotIn("href=\"http://", lowered)

    def test_hunt_list_page_renders(self) -> None:
        html = render_search_hunt_list_page(build_search_hunt_list_page_view([sample_hunt()]))
        self.assert_read_only_page(html)
        self.assertIn("Search Hunts", html)
        self.assertIn("Unavailable next actions", html)
        self.assertIn("checked_layers", html)

    def test_hunt_detail_page_renders_transition_history_and_layers(self) -> None:
        hunt = sample_hunt()
        transition = SearchHuntTransition.new(hunt.id, None, hunt.state, "created")
        html = render_search_hunt_detail_page(build_search_hunt_detail_page_view(hunt, [transition], {"summaries": []}))
        self.assert_read_only_page(html)
        self.assertIn("Transition history", html)
        self.assertIn("Checked layers", html)
        self.assertIn("Unchecked and deferred layers", html)
        self.assertIn("Reviewed-index search summary", html)
        self.assertIn("Local absence summary", html)

    def test_hunt_not_found_page_renders(self) -> None:
        html = render_search_hunt_not_found_page(build_search_hunt_not_found_page_view("missing"))
        self.assert_read_only_page(html)
        self.assertIn("Search Hunt not found", html)
        self.assertIn("created_implicitly", html)


if __name__ == "__main__":
    unittest.main()
