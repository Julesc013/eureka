from __future__ import annotations

import unittest

from runtime.public_alpha.search_ux_models import build_result_cards


class PublicSearchResultCardTests(unittest.TestCase):
    def test_result_cards_keep_state_separation(self) -> None:
        cards = build_result_cards()
        by_status = {card["status"]: card for card in cards}

        self.assertIn("verified", by_status)
        self.assertIn("candidate", by_status)
        self.assertIn("known_need", by_status)
        self.assertIn("absence", by_status)
        self.assertIn("source_lead", by_status)
        self.assertTrue(by_status["verified"]["accepted_truth"])
        for status, card in by_status.items():
            if status != "verified":
                self.assertFalse(card["accepted_truth"], status)
                self.assertTrue(card["review_required"], status)


if __name__ == "__main__":
    unittest.main()
