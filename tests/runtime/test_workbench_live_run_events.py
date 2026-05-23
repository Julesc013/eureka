from __future__ import annotations

import unittest

from runtime.local.service.workbench_live_run import create_workbench_resolution_run, get_workbench_run_events


class WorkbenchLiveRunEventsTests(unittest.TestCase):
    def test_events_append_and_read(self) -> None:
        packet = create_workbench_resolution_run("sampleproject", include_ia_hunt_dry_run=True)
        event_types = {event["event_type"] for event in packet["events"]}
        self.assertIn("run.created", event_types)
        self.assertIn("query.compiled", event_types)
        self.assertIn("lanes.snapshot_created", event_types)
        self.assertIn("workunits.planned", event_types)
        self.assertIn("ia_hunt.dry_run_planned", event_types)
        self.assertIn("action.blocked", event_types)
        response = get_workbench_run_events(packet["run_id"])
        self.assertEqual(packet["run_id"], response["run_id"])
        self.assertEqual(packet["event_count"], len(response["data"]))


if __name__ == "__main__":
    unittest.main()
