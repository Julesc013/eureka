import tempfile
import unittest
from pathlib import Path

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_operator import write_operator_token_record
from runtime.local_service import LocalServiceApp
from runtime.search_hunt import build_hunt_exhaustion_report
from scripts.eureka_init_instance import initialize_instance


class AgentResearchUiTests(unittest.TestCase):
    def test_hunt_and_need_pages_show_disabled_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp)
            initialize_instance(instance)
            write_operator_token_record(instance, "validator-token")
            runtime = open_local_appliance(instance)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                runtime.search_hunt.attach_exhaustion_report(hunt.id, build_hunt_exhaustion_report(runtime, hunt.id))
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id)
                runtime.agent_research.draft_task_from_need(runtime, need.id)
                app = LocalServiceApp(runtime)
                hunt_html = app.handle("GET", f"/hunt/{hunt.id}").body
                need_html = app.handle("GET", f"/need/{need.id}").body
                self.assertIn("Agent research disabled boundary", hunt_html)
                self.assertIn("Agent research disabled boundary", need_html)
                self.assertIn("provider_enabled", hunt_html)
                self.assertNotIn("call model provider", hunt_html.lower())
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
