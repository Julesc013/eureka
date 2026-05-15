"""Create disabled AI escalation gate records."""

from typing import Any

from .eligibility import evaluate_ai_escalation_eligibility
from .records import AIEscalationGate
from .validation import validate_ai_escalation_gate


def create_ai_escalation_gate(
    runtime: Any,
    hunt_id: str | None = None,
    need_id: str | None = None,
    operator_label: str | None = None,
) -> AIEscalationGate:
    eligibility = evaluate_ai_escalation_eligibility(runtime, hunt_id=hunt_id, need_id=need_id)
    gate = validate_ai_escalation_gate(AIEscalationGate.new(eligibility, operator_label=operator_label))
    return runtime.ai_escalation.create_gate(gate)
