from __future__ import annotations

import unittest

from runtime.search.query_plan import archive_org_metadata_query, plan_query_to_source_actions


class SourceQueryRewriteTests(unittest.TestCase):
    def test_frontier_media_rewrite_expands_technical_terms(self) -> None:
        rewrite = archive_org_metadata_query(
            plan_query_to_source_actions("New York 1993 D-Theater HD demo tape original source")
        )

        for term in ("D-Theater", "D-VHS", "JVC", "Hi-Vision", "MUSE"):
            self.assertIn(term.casefold(), rewrite.casefold())

    def test_windows_utility_rewrite_preserves_portable_and_suppresses_iso(self) -> None:
        rewrite = archive_org_metadata_query(
            plan_query_to_source_actions("Windows 7-compatible portable utilities, not Windows 7 ISO")
        )

        self.assertIn("portable", rewrite.casefold())
        self.assertIn("-iso", rewrite.casefold())
        self.assertNotIn(" windows 7 iso portable", rewrite.casefold())

    def test_driver_rewrite_keeps_model_and_platform(self) -> None:
        rewrite = archive_org_metadata_query(plan_query_to_source_actions("StyleWriter 2500 Mac OS 8 driver"))

        self.assertIn("StyleWriter 2500", rewrite)
        self.assertIn("Mac OS 8", rewrite)
        self.assertIn("driver", rewrite.casefold())


if __name__ == "__main__":
    unittest.main()
