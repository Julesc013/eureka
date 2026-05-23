import tempfile
import unittest
from pathlib import Path

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.local.operator import write_operator_token_record
from runtime.local.service import LocalServiceApp
from runtime.search.hunt import build_hunt_exhaustion_report
from scripts.eureka_init_instance import initialize_instance


class AgentResearchDisabledBoundaryTests(unittest.TestCase):
    def test_missing_invalid_lan_and_execute_attempts_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp)
            initialize_instance(instance)
            write_operator_token_record(instance, "validator-token")
            runtime = open_local_appliance(instance)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                runtime.search_hunt.attach_exhaustion_report(hunt.id, build_hunt_exhaustion_report(runtime, hunt.id))
                app = LocalServiceApp(runtime)
                self.assertEqual(app.handle("POST", f"/hunt/{hunt.id}/agent-task-draft", body="").status_code, 401)
                self.assertEqual(app.handle("POST", f"/hunt/{hunt.id}/agent-task-draft", body="operator_token=bad").status_code, 401)
                self.assertEqual(
                    app.handle("POST", f"/hunt/{hunt.id}/agent-task-draft", client_host="192.168.1.44", body="operator_token=validator-token").status_code,
                    403,
                )
                self.assertNotEqual(app.handle("POST", "/api/v1/agent-research/execute", body="operator_token=validator-token").status_code, 200)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
