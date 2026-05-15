"""Build disabled AI escalation preflight records."""

from typing import Any

from .eligibility import evaluate_ai_escalation_eligibility
from .records import AIEscalationPreflightResult
from .validation import validate_preflight


def build_ai_escalation_preflight(
    runtime: Any,
    hunt_id: str | None = None,
    need_id: str | None = None,
    operator_label: str | None = None,
) -> AIEscalationPreflightResult:
    eligibility = evaluate_ai_escalation_eligibility(runtime, hunt_id=hunt_id, need_id=need_id)
    return validate_preflight(AIEscalationPreflightResult.new(eligibility, operator_label=operator_label))
