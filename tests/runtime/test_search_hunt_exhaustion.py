from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.search.hunt import build_hunt_exhaustion_report


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


class SearchHuntExhaustionTests(unittest.TestCase):
    def test_exhaustion_report_builds_for_sample_hunt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                report = build_hunt_exhaustion_report(runtime, hunt.id)
                payload = report.to_dict()

                self.assertEqual(hunt.id, payload["hunt_id"])
                self.assertEqual("sampleproject", payload["query_summary"]["original_query"])
                self.assertTrue(payload["checked_layers"])
                self.assertTrue(payload["unchecked_or_deferred_layers"])
                self.assertTrue(payload["blocked_by_policy"])
                self.assertTrue(payload["recommended_next_actions"])
                self.assertFalse(payload["workunit_creation_performed"])
                self.assertFalse(payload["source_probe_executed"])
            finally:
                close_local_appliance(runtime)

    def test_attach_preserves_report_and_command_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            runtime = open_local_appliance(instance, read_only=False)
            try:
                hunt = runtime.search_hunt.create_session_from_query("missing local thing", runtime=runtime)
                report = build_hunt_exhaustion_report(runtime, hunt.id, operator_label="tester")
                attached = runtime.search_hunt.attach_exhaustion_report(hunt.id, report)
                latest = runtime.search_hunt.get_latest_exhaustion_report(hunt.id)
                commands = runtime.search_hunt.list_commands(hunt.id)

                self.assertEqual(attached.report_id, latest.report_id)
                self.assertEqual("generate_exhaustion_report", commands[-1].command_type)
                self.assertEqual("tester", commands[-1].operator_label)
                self.assertEqual("insufficient_local_index", latest.state.value)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
