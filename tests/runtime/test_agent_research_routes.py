import tempfile
import unittest
from pathlib import Path

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_operator import write_operator_token_record
from runtime.local_service import LocalServiceApp
from runtime.search_hunt import build_hunt_exhaustion_report
from scripts.eureka_init_instance import initialize_instance


class AgentResearchRoutesTests(unittest.TestCase):
    def test_routes_create_disabled_draft_and_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp)
            initialize_instance(instance)
            write_operator_token_record(instance, "validator-token")
            runtime = open_local_appliance(instance)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                runtime.search_hunt.attach_exhaustion_report(hunt.id, build_hunt_exhaustion_report(runtime, hunt.id))
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id)
                app = LocalServiceApp(runtime)
                self.assertEqual(app.handle("POST", f"/api/v1/hunt/{hunt.id}/agent-task-draft", body="operator_token=validator-token").status_code, 200)
                self.assertEqual(app.handle("POST", f"/api/v1/need/{need.id}/agent-task-draft", body="operator_token=validator-token").status_code, 200)
                self.assertEqual(app.handle("GET", f"/api/v1/hunt/{hunt.id}/agent-tasks").status_code, 200)
                self.assertEqual(app.handle("GET", f"/api/v1/need/{need.id}/agent-tasks").status_code, 200)
                self.assertEqual(app.handle("GET", "/api/v1/agent-research/report-schema").status_code, 200)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
