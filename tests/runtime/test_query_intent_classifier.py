from __future__ import annotations

import unittest

from runtime.search.query_plan import classify_intent


class QueryIntentClassifierTests(unittest.TestCase):
    def test_required_intents_are_classified(self) -> None:
        cases = {
            "New York 1993 D-Theater HD demo tape original source": "find_frontier_resolution_media",
            "Windows 7-compatible portable utilities, not Windows 7 ISO": "find_software",
            "StyleWriter 2500 Mac OS 8 driver": "find_driver_or_support_media",
            "DirectX SDK June 2010 offline installer": "find_exact_artifact",
            "best apps": "ambiguous_query",
        }

        for query, expected in cases.items():
            with self.subTest(query=query):
                self.assertEqual(expected, classify_intent(query)["intent"])

    def test_source_release_and_manual_intents_are_distinct(self) -> None:
        self.assertEqual(
            "find_source_release_or_package",
            classify_intent("archivebox source code release github")["intent"],
        )
        self.assertEqual(
            "find_manual_or_document",
            classify_intent("Sound Blaster CT1740 service manual scan")["intent"],
        )


if __name__ == "__main__":
    unittest.main()
