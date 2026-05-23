import tempfile
import unittest
from pathlib import Path

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.search.hunt import build_hunt_exhaustion_report
from scripts.eureka_init_instance import initialize_instance


class AgentResearchTaskBuilderTests(unittest.TestCase):
    def test_draft_from_hunt_and_need(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp)
            initialize_instance(instance)
            runtime = open_local_appliance(instance)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                runtime.search_hunt.attach_exhaustion_report(hunt.id, build_hunt_exhaustion_report(runtime, hunt.id))
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id)
                task_from_hunt = runtime.agent_research.draft_task_from_hunt(runtime, hunt.id)
                task_from_need = runtime.agent_research.draft_task_from_need(runtime, need.id)
                self.assertEqual(task_from_hunt.search_hunt_id, hunt.id)
                self.assertEqual(task_from_need.search_need_id, need.id)
                self.assertFalse(task_from_hunt.provider_enabled)
                self.assertFalse(task_from_need.execution_enabled)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
