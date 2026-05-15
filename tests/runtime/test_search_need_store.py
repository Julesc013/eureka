from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.search_need import SearchNeed


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


class SearchNeedStoreTests(unittest.TestCase):
    def test_store_init_create_list_show_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            runtime = open_local_appliance(instance)
            try:
                migrations = runtime.search_need.init()
                self.assertTrue(migrations)
                need = SearchNeed.new(
                    hunt_id="hunt-1",
                    exhaustion_report_id="report-1",
                    query="sampleproject",
                    need_title="Investigate sampleproject",
                    need_summary="Local demand state only.",
                    need_kind="find_exact_artifact",
                    desired_outcome="improve_index",
                    local_result_state="local_absent",
                    idempotency_key="need-key",
                )
                created = runtime.search_need.create_need(need)
                duplicate = runtime.search_need.create_need(need)
                listed = runtime.search_need.list_needs()

                self.assertEqual(created.id, duplicate.id)
                self.assertEqual(created.id, runtime.search_need.get_need(created.id).id)
                self.assertEqual(1, len(listed))
                self.assertEqual("pass", runtime.search_need.check_integrity()["status"])
            finally:
                close_local_appliance(runtime)

    def test_transition_history_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = init_instance(tmp)
            runtime = open_local_appliance(instance)
            try:
                need = runtime.search_need.create_need(
                    SearchNeed.new(
                        hunt_id="hunt-1",
                        exhaustion_report_id="report-1",
                        query="sampleproject",
                        need_title="Investigate sampleproject",
                        need_summary="Local demand state only.",
                        need_kind="find_exact_artifact",
                        desired_outcome="improve_index",
                        local_result_state="local_absent",
                    )
                )
                runtime.search_need.transition_need(need.id, "open", "operator opened")
                transitions = runtime.search_need.list_transitions(need.id)

                self.assertEqual("created", transitions[0].reason)
                self.assertEqual("open", transitions[-1].to_state.value)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
