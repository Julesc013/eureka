from __future__ import annotations

import unittest

from runtime.search.query_plan import plan_query_to_source_actions


class CandidateSuppressionTests(unittest.TestCase):
    def test_software_query_suppresses_os_images(self) -> None:
        plan = plan_query_to_source_actions("Windows 7-compatible portable utilities, not Windows 7 ISO")
        suppression_ids = {item["suppression_id"] for item in plan["candidate_suppressions"]}

        self.assertIn("suppress_os_images_for_software_queries", suppression_ids)
        self.assertIn("suppress_install_media_when_portable_requested", suppression_ids)

    def test_driver_query_suppresses_unrelated_models(self) -> None:
        plan = plan_query_to_source_actions("StyleWriter 2500 Mac OS 8 driver")
        suppression_ids = {item["suppression_id"] for item in plan["candidate_suppressions"]}

        self.assertIn("suppress_unrelated_driver_models", suppression_ids)

    def test_plan_safety_keeps_mutation_and_downloads_disabled(self) -> None:
        plan = plan_query_to_source_actions("DirectX SDK June 2010 offline installer")
        safety = plan["safety"]

        self.assertTrue(safety["candidate_only"])
        self.assertTrue(safety["review_required"])
        for field in (
            "accepted_truth_created",
            "candidate_index_mutated",
            "public_index_mutated",
            "download_performed",
            "extraction_executed",
            "model_provider_used",
        ):
            self.assertFalse(safety[field], field)


if __name__ == "__main__":
    unittest.main()
