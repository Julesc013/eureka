import tempfile
import unittest
from pathlib import Path

from runtime.ai_escalation import build_ai_escalation_preflight, create_ai_escalation_gate
from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.search.hunt import build_hunt_exhaustion_report
from scripts.eureka_init_instance import initialize_instance


class AIEscalationPreflightTests(unittest.TestCase):
    def test_preflight_from_hunt_and_need_and_disabled_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp)
            initialize_instance(instance)
            runtime = open_local_appliance(instance)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                runtime.search_hunt.attach_exhaustion_report(hunt.id, build_hunt_exhaustion_report(runtime, hunt.id))
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id)
                runtime.agent_research.draft_task_from_need(runtime, need.id)
                hunt_preflight = build_ai_escalation_preflight(runtime, hunt_id=hunt.id)
                need_preflight = build_ai_escalation_preflight(runtime, need_id=need.id)
                gate = create_ai_escalation_gate(runtime, need_id=need.id)
                self.assertFalse(hunt_preflight.provider_enabled)
                self.assertFalse(need_preflight.execution_enabled)
                self.assertTrue(gate.candidate_only_output)
                self.assertIn("alias_hypotheses", [item.value for item in gate.output_classes])
                self.assertIn("run_extraction_current_task", [item.value for item in gate.forbidden_actions])
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
