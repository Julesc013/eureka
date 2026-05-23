from __future__ import annotations

import unittest

from runtime.local.service.workbench_live_run import create_workbench_resolution_run


class WorkbenchLiveRunTests(unittest.TestCase):
    def test_create_run_from_query(self) -> None:
        packet = create_workbench_resolution_run("sampleproject", include_ia_hunt_dry_run=True)
        self.assertEqual("workbench_live_run_packet.v0", packet["schema_version"])
        self.assertTrue(packet["run_id"])
        self.assertEqual("completed", packet["state"])
        self.assertGreater(packet["lane_count"], 0)
        self.assertGreater(packet["workunit_count"], 0)
        self.assertFalse(packet["live_ia_call_performed"])
        self.assertFalse(packet["source_probe_executed"])


if __name__ == "__main__":
    unittest.main()
