from __future__ import annotations

import unittest

from runtime.public_search import build_public_search_ux_mvp_bundle


class PublicSearchAccessibilitySmokeTests(unittest.TestCase):
    def test_accessibility_matrix_passes(self) -> None:
        accessibility = build_public_search_ux_mvp_bundle()["accessibility"]

        self.assertTrue(accessibility["search_input_has_label"])
        self.assertTrue(accessibility["forms_use_get"])
        self.assertTrue(accessibility["headings_are_semantic"])
        self.assertTrue(accessibility["status_badges_have_text"])
        self.assertTrue(accessibility["no_js_path_works"])


if __name__ == "__main__":
    unittest.main()
