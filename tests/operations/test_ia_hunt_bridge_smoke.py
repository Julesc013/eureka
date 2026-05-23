import unittest

from runtime.search.hunt.ia_bridge import (
    build_ia_hunt_boundary_report,
    build_ia_hunt_result_lanes,
    plan_ia_hunt_pipeline,
    run_ia_hunt_pipeline_dry_run,
)


class IAHuntBridgeSmokeTests(unittest.TestCase):
    def test_query_to_result_lanes_smoke(self) -> None:
        plan = plan_ia_hunt_pipeline("sampleproject")
        outputs = run_ia_hunt_pipeline_dry_run(plan)
        lanes = build_ia_hunt_result_lanes(outputs, "operator_workbench")
        boundary = build_ia_hunt_boundary_report(outputs)

        self.assertEqual("sampleproject", lanes["query"])
        self.assertGreater(outputs["source_cache_report"]["record_count"], 0)
        self.assertGreater(outputs["evidence_report"]["candidate_count"], 0)
        self.assertGreater(outputs["candidate_report"]["candidate_count"], 0)
        self.assertGreater(outputs["review_report"]["review_item_count"], 0)
        self.assertTrue(any(lane["lane_kind"] == "blocked_actions" for lane in lanes["lanes"]))
        self.assertFalse(boundary["source_probe_executed"])
        self.assertFalse(boundary["download_performed"])
        self.assertFalse(boundary["extraction_executed"])
        self.assertFalse(boundary["model_provider_used"])
        self.assertFalse(boundary["deployment_performed"])


if __name__ == "__main__":
    unittest.main()
