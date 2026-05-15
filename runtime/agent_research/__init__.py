"""Disabled local agent research task contracts."""

from .errors import (
    AgentResearchClosedError,
    AgentResearchError,
    AgentResearchNotFoundError,
    AgentResearchValidationError,
)
from .records import (
    AgentResearchForbiddenAction,
    AgentResearchGoal,
    AgentResearchReportSchema,
    AgentResearchTask,
    AgentResearchTaskState,
    AgentResearchTaskSummary,
)
from .report_schema import (
    build_agent_research_report_schema,
    validate_agent_research_report_shape,
    validate_candidate_only_report,
)
from .store import AgentResearchStore
from .task_builder import (
    build_agent_research_input_packet,
    build_agent_research_task_from_hunt,
    build_agent_research_task_from_need,
)
from .validation import (
    validate_agent_research_task,
    validate_no_forbidden_side_effects,
    validate_no_truth_claims,
    validate_provider_disabled,
)


ALLOWED_AGENT_RESEARCH_TASK_STATES = tuple(item.value for item in AgentResearchTaskState)
ALLOWED_AGENT_RESEARCH_GOALS = tuple(item.value for item in AgentResearchGoal)
ALLOWED_AGENT_RESEARCH_FORBIDDEN_ACTIONS = tuple(item.value for item in AgentResearchForbiddenAction)

__all__ = [
    "ALLOWED_AGENT_RESEARCH_FORBIDDEN_ACTIONS",
    "ALLOWED_AGENT_RESEARCH_GOALS",
    "ALLOWED_AGENT_RESEARCH_TASK_STATES",
    "AgentResearchClosedError",
    "AgentResearchError",
    "AgentResearchForbiddenAction",
    "AgentResearchGoal",
    "AgentResearchNotFoundError",
    "AgentResearchReportSchema",
    "AgentResearchStore",
    "AgentResearchTask",
    "AgentResearchTaskState",
    "AgentResearchTaskSummary",
    "AgentResearchValidationError",
    "build_agent_research_input_packet",
    "build_agent_research_report_schema",
    "build_agent_research_task_from_hunt",
    "build_agent_research_task_from_need",
    "validate_agent_research_report_shape",
    "validate_agent_research_task",
    "validate_candidate_only_report",
    "validate_no_forbidden_side_effects",
    "validate_no_truth_claims",
    "validate_provider_disabled",
]
