"""Disabled local AI escalation gate contracts."""

from .eligibility import evaluate_ai_escalation_eligibility
from .errors import (
    AIEscalationClosedError,
    AIEscalationError,
    AIEscalationNotFoundError,
    AIEscalationValidationError,
)
from .gate import create_ai_escalation_gate
from .preflight import build_ai_escalation_preflight
from .records import (
    AIEscalationEligibility,
    AIEscalationForbiddenAction,
    AIEscalationGate,
    AIEscalationGateState,
    AIEscalationInputPacket,
    AIEscalationOutputClass,
    AIEscalationPreflightResult,
    default_output_schema,
    default_safety_checks,
)
from .store import AIEscalationStore
from .validation import (
    validate_ai_escalation_gate,
    validate_no_forbidden_side_effects,
    validate_no_truth_claims,
    validate_preflight,
    validate_provider_disabled,
)


ALLOWED_AI_ESCALATION_GATE_STATES = tuple(item.value for item in AIEscalationGateState)
ALLOWED_AI_ESCALATION_OUTPUT_CLASSES = tuple(item.value for item in AIEscalationOutputClass)
ALLOWED_AI_ESCALATION_FORBIDDEN_ACTIONS = tuple(item.value for item in AIEscalationForbiddenAction)

__all__ = [
    "ALLOWED_AI_ESCALATION_FORBIDDEN_ACTIONS",
    "ALLOWED_AI_ESCALATION_GATE_STATES",
    "ALLOWED_AI_ESCALATION_OUTPUT_CLASSES",
    "AIEscalationClosedError",
    "AIEscalationEligibility",
    "AIEscalationError",
    "AIEscalationForbiddenAction",
    "AIEscalationGate",
    "AIEscalationGateState",
    "AIEscalationInputPacket",
    "AIEscalationNotFoundError",
    "AIEscalationOutputClass",
    "AIEscalationPreflightResult",
    "AIEscalationStore",
    "AIEscalationValidationError",
    "build_ai_escalation_preflight",
    "create_ai_escalation_gate",
    "default_output_schema",
    "default_safety_checks",
    "evaluate_ai_escalation_eligibility",
    "validate_ai_escalation_gate",
    "validate_no_forbidden_side_effects",
    "validate_no_truth_claims",
    "validate_preflight",
    "validate_provider_disabled",
]
