import unittest

from runtime.search_hunt.ia_bridge import (
    IA_WORKUNIT_STATES,
    IA_WORKUNIT_TYPES,
    create_ia_workunits_for_hunt,
    plan_ia_hunt_pipeline,
)


class IAHuntWorkUnitTests(unittest.TestCase):
    def test_workunits_cover_required_types_and_fields(self) -> None:
        plan = plan_ia_hunt_pipeline("sampleproject")
        workunits = plan["workunits"]
        self.assertEqual(set(IA_WORKUNIT_TYPES), {item["workunit_type"] for item in workunits})

        required = {
            "workunit_id",
            "hunt_id",
            "source_family",
            "workunit_type",
            "state",
            "input_ref",
            "output_ref",
            "policy_ref",
            "dry_run",
            "writes_instance_state",
            "write_scope",
            "blocked_actions",
            "created_at",
            "completed_at",
            "limitations",
        }
        for workunit in workunits:
            self.assertLessEqual(required, set(workunit))
            self.assertEqual("internet_archive_metadata", workunit["source_family"])
            self.assertIn(workunit["state"], IA_WORKUNIT_STATES)
            self.assertIn("download", workunit["blocked_actions"])
            self.assertIn("extract", workunit["blocked_actions"])
            self.assertIn("call_model_provider", workunit["blocked_actions"])

    def test_write_workunits_are_temp_or_explicit_only(self) -> None:
        workunits = create_ia_workunits_for_hunt({"hunt_id": "shs_test", "query": "sampleproject"})
        write_units = [item for item in workunits if item["writes_instance_state"]]
        self.assertTrue(write_units)
        for workunit in write_units:
            self.assertEqual("temp_or_explicit_instance_only", workunit["write_scope"])
            self.assertTrue(workunit["dry_run"])


if __name__ == "__main__":
    unittest.main()
