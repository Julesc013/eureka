from __future__ import annotations

import unittest

from runtime.resolution_run import (
    BLOCKED_ACTIONS,
    InMemoryRunEventLog,
    create_resolution_run,
    run_resolution_dry_run,
)
from runtime.resolution_run.command_handler import handle_run_command
from runtime.resolution_run.errors import ResolutionRunPolicyError


class ResolutionRunKernelTests(unittest.TestCase):
    def test_create_resolution_run_is_headless(self) -> None:
        result = create_resolution_run("sampleproject")
        self.assertEqual("resolution_run_kernel_create_result.v0", result["schema_version"])
        self.assertEqual("created", result["run"]["state"])
        self.assertFalse(result["source_probe_executed"])
        self.assertFalse(result["live_ia_call_performed"])
        self.assertFalse(result["store_mutation_performed"])
        self.assertGreaterEqual(len(result["events"]), 2)

    def test_dry_run_plans_ia_workunits_and_lanes(self) -> None:
        result = run_resolution_dry_run("sampleproject")
        self.assertEqual("completed", result["run"]["state"])
        self.assertGreater(result["workunit_schedule"]["workunit_count"], 0)
        self.assertGreater(result["lane_snapshot"]["lane_count"], 0)
        lane_kinds = {lane["lane_kind"] for lane in result["lane_snapshot"]["lane_page"]["lanes"]}
        self.assertIn("running_workunits", lane_kinds)
        self.assertIn("ia_metadata_candidates", lane_kinds)
        self.assertIn("blocked_actions", lane_kinds)

    def test_boundaries_remain_false(self) -> None:
        result = run_resolution_dry_run("sampleproject")
        for key, value in result["boundaries"].items():
            if key == "schema_version":
                continue
            self.assertFalse(value, key)

    def test_unsafe_command_is_blocked(self) -> None:
        result = create_resolution_run("sampleproject")
        log = InMemoryRunEventLog()
        with self.assertRaises(ResolutionRunPolicyError):
            handle_run_command(result["run"], {"command_type": "download"}, log)
        self.assertIn("download", BLOCKED_ACTIONS)
        self.assertEqual("command_blocked", log.list_events()[0]["event_type"])


if __name__ == "__main__":
    unittest.main()
