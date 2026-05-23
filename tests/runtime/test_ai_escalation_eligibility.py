import tempfile
import unittest
from pathlib import Path

from runtime.ai_escalation import evaluate_ai_escalation_eligibility
from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.search.hunt import build_hunt_exhaustion_report
from scripts.eureka_init_instance import initialize_instance


class AIEscalationEligibilityTests(unittest.TestCase):
    def test_preflight_from_hunt_requires_need_and_task_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp)
            initialize_instance(instance)
            runtime = open_local_appliance(instance)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                blocked = evaluate_ai_escalation_eligibility(runtime, hunt_id=hunt.id)
                self.assertEqual(blocked.state.value, "blocked_missing_exhaustion_report")
                runtime.search_hunt.attach_exhaustion_report(hunt.id, build_hunt_exhaustion_report(runtime, hunt.id))
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id)
                runtime.agent_research.draft_task_from_need(runtime, need.id)
                eligible = evaluate_ai_escalation_eligibility(runtime, need_id=need.id)
                self.assertEqual(eligible.state.value, "eligible_but_disabled")
                self.assertFalse(eligible.provider_enabled)
                self.assertEqual(eligible.input_packet.search_need_id, need.id)
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
