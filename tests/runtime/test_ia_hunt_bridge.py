import tempfile
import unittest
from pathlib import Path

from runtime.search.hunt.ia_bridge import (
    build_ia_hunt_boundary_report,
    collect_ia_hunt_outputs,
    plan_ia_hunt_pipeline,
    run_ia_hunt_pipeline_dry_run,
    run_ia_hunt_pipeline_temp_instance,
)


class IAHuntBridgeRuntimeTests(unittest.TestCase):
    def test_dry_run_creates_plan_without_writes(self) -> None:
        plan = plan_ia_hunt_pipeline("sampleproject")
        outputs = run_ia_hunt_pipeline_dry_run(plan)
        boundary = build_ia_hunt_boundary_report(outputs)

        self.assertEqual("ia_hunt_pipeline_plan.v0", plan["schema_version"])
        self.assertEqual(10, plan["workunit_count"])
        self.assertTrue(outputs["dry_run"])
        self.assertFalse(boundary["source_probe_executed"])
        self.assertFalse(boundary["live_ia_call_performed"])
        self.assertFalse(boundary["source_cache_write_performed"])
        self.assertFalse(boundary["evidence_write_performed"])
        self.assertFalse(boundary["candidate_index_mutated"])
        self.assertFalse(boundary["reviewed_index_mutated"])
        self.assertFalse(boundary["master_index_mutated"])

    def test_temp_instance_bridge_writes_only_to_temp_scope(self) -> None:
        plan = plan_ia_hunt_pipeline("sampleproject")
        with tempfile.TemporaryDirectory() as tmp:
            outputs = run_ia_hunt_pipeline_temp_instance(plan, tmp, "test-token")
            boundary = build_ia_hunt_boundary_report(outputs)
            collected = collect_ia_hunt_outputs(Path(tmp))

        self.assertFalse(outputs["dry_run"])
        self.assertEqual("temp_instance", boundary["source_cache_write_scope"])
        self.assertEqual("temp_instance", boundary["evidence_write_scope"])
        self.assertEqual("temp_instance", boundary["candidate_index_write_scope"])
        self.assertEqual("temp_instance", boundary["reviewed_index_write_scope"])
        self.assertFalse(boundary["operator_instance_mutated"])
        self.assertFalse(boundary["master_index_mutated"])
        self.assertGreater(collected["reviewed_record_count"], 0)


if __name__ == "__main__":
    unittest.main()
