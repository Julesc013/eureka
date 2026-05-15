import tempfile
import unittest
from pathlib import Path

from runtime.agent_research import AgentResearchStore, AgentResearchTask


class AgentResearchStoreTests(unittest.TestCase):
    def test_store_init_create_list_and_cancel(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "agent_research.sqlite"
            with AgentResearchStore.open(db) as store:
                store.init()
                store.init()
                task = AgentResearchTask.new(
                    search_hunt_id="shs_test",
                    search_need_id="sn_test",
                    exhaustion_report_id="she_test",
                    query="sampleproject",
                    output_schema={"schema_version": "agent_research_report_schema.v0", "candidate_only": True, "review_required": True},
                )
                created = store.create_task(task)
                self.assertEqual(store.get_task(created.task_id).task_id, created.task_id)
                self.assertEqual(len(store.list_tasks(hunt_id="shs_test")), 1)
                cancelled = store.cancel_task(created.task_id, reason="test")
                self.assertEqual(cancelled.state.value, "cancelled")
                self.assertEqual(store.check_integrity()["status"], "pass")


if __name__ == "__main__":
    unittest.main()
