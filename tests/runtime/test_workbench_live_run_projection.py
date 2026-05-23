from __future__ import annotations

import unittest

from runtime.local.service.workbench_live_run import create_workbench_resolution_run


class WorkbenchLiveRunProjectionTests(unittest.TestCase):
    def test_public_projection_hides_operator_fields(self) -> None:
        packet = create_workbench_resolution_run("sampleproject", "public_web", include_ia_hunt_dry_run=True)
        self.assertEqual("public_web", packet["projection_profile"])
        self.assertNotIn("compiled_query_id", packet)
        self.assertTrue(packet["warnings"])
        for workunit in packet["workunits"]:
            self.assertNotIn("input_ref", workunit)
            self.assertNotIn("output_ref", workunit)

    def test_native_projection_is_read_only(self) -> None:
        packet = create_workbench_resolution_run("sampleproject", "native_desktop_read_only", include_ia_hunt_dry_run=True)
        self.assertEqual("native_desktop_read_only", packet["projection_profile"])
        self.assertFalse(packet["boundary_report"]["operator_instance_mutated"])
        self.assertFalse(packet["boundary_report"]["master_index_mutated"])


if __name__ == "__main__":
    unittest.main()
