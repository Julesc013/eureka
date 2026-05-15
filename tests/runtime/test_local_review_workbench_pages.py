import unittest

from runtime.local_workbench.pages import render_rebuild_page, render_review_item_page, render_review_queue_page
from runtime.local_workbench.validation import validate_local_workbench_page, validate_no_external_assets
from runtime.local_workbench.view_models import (
    build_rebuild_page_view,
    build_review_item_page_view,
    build_review_queue_page_view,
)


class LocalReviewWorkbenchPageTests(unittest.TestCase):
    def test_review_queue_page_renders_non_claim_banner(self) -> None:
        html = render_review_queue_page(build_review_queue_page_view({"review_items": [], "warnings": [], "limitations": []}))

        self.assertIn("Review queue", html)
        self.assertIn("local review", html.lower())
        self.assertEqual(html, validate_no_external_assets(html))

    def test_review_item_page_renders_operator_gated_decision_form(self) -> None:
        view = build_review_item_page_view(
            "rvi_test",
            {
                "review_item": {"review_item_id": "rvi_test", "summary": "Needs review", "queue_status": "needs_review"},
                "found": True,
                "decisions": [],
                "events": [],
                "evidence": {},
                "source_cache_entry": {},
                "warnings": [],
                "limitations": [],
            },
        )
        html = render_review_item_page(view)

        self.assertIn('method="post"', html)
        self.assertIn('name="operator_token"', html)
        self.assertIn('name="local_only_confirmed"', html)
        self.assertNotIn("local-secret-token", html)
        self.assertNotIn("run probe", html.lower())
        self.assertNotIn("create workunit", html.lower())
        self.assertEqual(html, validate_local_workbench_page(html, allow_operator_mutation_forms=True))

    def test_rebuild_page_renders_operator_gated_form_without_external_assets(self) -> None:
        html = render_rebuild_page(build_rebuild_page_view({"review_queue_count": 0}))

        self.assertIn("Reviewed-index rebuild", html)
        self.assertIn('method="post"', html)
        self.assertIn('name="operator_token"', html)
        self.assertEqual(html, validate_local_workbench_page(html, allow_operator_mutation_forms=True))


if __name__ == "__main__":
    unittest.main()
