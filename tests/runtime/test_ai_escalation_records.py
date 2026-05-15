import unittest

from runtime.ai_escalation import AIEscalationForbiddenAction, AIEscalationGate, AIEscalationGateState
from runtime.ai_escalation.records import AIEscalationInputPacket, AIEscalationEligibility, default_output_schema
from runtime.ai_escalation.validation import validate_ai_escalation_gate


class AIEscalationRecordsTests(unittest.TestCase):
    def test_gate_validates_required_disabled_fields(self):
        packet = AIEscalationInputPacket(
            search_hunt_id="shs_test",
            search_need_id="sn_test",
            exhaustion_report_id="she_test",
            agent_research_task_id="art_test",
            query="sampleproject",
            normalized_query="sampleproject",
            checked_layers=("reviewed_public_index",),
            deferred_layers=("source_probes",),
            blocked_by_policy=("source_probe_disabled",),
            steering_preferences=(),
            candidate_context=(),
            absence_context={"absence_state": "not_found"},
            forbidden_actions=tuple(AIEscalationForbiddenAction),
            desired_output_schema=default_output_schema(),
        )
        eligibility = AIEscalationEligibility(
            state=AIEscalationGateState.ELIGIBLE_BUT_DISABLED,
            eligible=True,
            input_packet=packet,
            missing_requirements=(),
            warnings=(),
            limitations=("disabled",),
        )
        gate = AIEscalationGate.new(eligibility)

        validate_ai_escalation_gate(gate)
        payload = gate.to_dict()
        self.assertEqual(payload["state"], "eligible_but_disabled")
        self.assertFalse(payload["provider_enabled"])
        self.assertFalse(payload["execution_enabled"])
        self.assertIn("accept_truth", payload["forbidden_actions"])


if __name__ == "__main__":
    unittest.main()
