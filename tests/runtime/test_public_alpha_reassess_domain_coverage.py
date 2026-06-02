from __future__ import annotations

import unittest

from runtime.public_alpha import run_public_alpha_reassess_04


class PublicAlphaReassessDomainCoverageTests(unittest.TestCase):
    def test_four_domains_are_represented_but_not_launch_sufficient(self) -> None:
        result = run_public_alpha_reassess_04(from_manuals_driver_snapshot_examples=True)
        domain = result["domain_coverage"]

        self.assertEqual("PUBLIC-ALPHA-REASSESS-04", result["task"])
        self.assertEqual(4, result["domain_count"])
        self.assertEqual(4, domain["domain_count"])
        self.assertTrue(domain["four_domains_represented"])
        self.assertTrue(domain["domain_breadth_improved"])
        self.assertFalse(domain["domain_coverage_launch_sufficient"])
        self.assertIn("manuals_docs_scans", result["domains_represented"])
        self.assertIn("driver_support_media", result["domains_represented"])

    def test_candidate_growth_is_internal_review_value(self) -> None:
        result = run_public_alpha_reassess_04(from_manuals_driver_snapshot_examples=True)

        self.assertEqual(68, result["candidate_count"])
        self.assertEqual(16, result["manuals_scans_candidate_count"])
        self.assertEqual(16, result["driver_support_candidate_count"])
        self.assertFalse(result["launch_recommended"])
        self.assertTrue(result["demo_mode_recommended"])
        self.assertTrue(result["internal_review_recommended"])


if __name__ == "__main__":
    unittest.main()
