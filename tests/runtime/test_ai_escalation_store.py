import tempfile
import unittest
from pathlib import Path

from runtime.ai_escalation import AIEscalationStore
from runtime.ai_escalation.records import (
    AIEscalationEligibility,
    AIEscalationGate,
    AIEscalationGateState,
    AIEscalationInputPacket,
    AIEscalationForbiddenAction,
    default_output_schema,
)


class AIEscalationStoreTests(unittest.TestCase):
    def test_store_init_create_list_and_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "ai_escalation.sqlite"
            with AIEscalationStore.open(db) as store:
                store.init()
                store.init()
                packet = AIEscalationInputPacket(
                    search_hunt_id="shs_test",
                    search_need_id="sn_test",
                    exhaustion_report_id="she_test",
                    agent_research_task_id="art_test",
                    query="sampleproject",
                    normalized_query="sampleproject",
                    checked_layers=("reviewed_public_index",),
                    deferred_layers=("source_probes",),
                    blocked_by_policy=(),
                    steering_preferences=(),
                    candidate_context=(),
                    absence_context={},
                    forbidden_actions=tuple(AIEscalationForbiddenAction),
                    desired_output_schema=default_output_schema(),
                )
                eligibility = AIEscalationEligibility(AIEscalationGateState.ELIGIBLE_BUT_DISABLED, True, packet, (), (), ("disabled",))
                gate = store.create_gate(AIEscalationGate.new(eligibility))
                self.assertEqual(store.get_gate(gate.gate_id).gate_id, gate.gate_id)
                self.assertEqual(len(store.list_gates(hunt_id="shs_test")), 1)
                self.assertEqual(store.check_integrity()["status"], "pass")


if __name__ == "__main__":
    unittest.main()
