"""Durable local Search Hunt session runtime."""

from .absence_summary import build_local_absence_summary
from .commands import SearchHuntCommand, SearchHuntCommandResult, SearchHuntCommandType
from .exhaustion import (
    build_blocked_policy_reports,
    build_checked_layer_reports,
    build_deferred_layer_reports,
    build_hunt_exhaustion_report,
    build_recommended_actions,
)
from .errors import (
    SearchHuntClosedError,
    SearchHuntError,
    SearchHuntIntegrityError,
    SearchHuntNotFoundError,
    SearchHuntTransitionError,
    SearchHuntValidationError,
)
from .records import (
    SearchHuntCheckedLayer,
    SearchHuntDestination,
    SearchHuntExhaustionReport,
    SearchHuntExhaustionState,
    SearchHuntIntent,
    SearchHuntSession,
    SearchHuntState,
    SearchHuntSummary,
    SearchHuntTransition,
    SearchHuntUncheckedLayer,
)
from .run_records import (
    BackgroundHuntPlan,
    BackgroundHuntPlanItem,
    BackgroundHuntRun,
    BackgroundHuntRunResult,
    BackgroundHuntRunStatus,
    BackgroundHuntWorkerPolicyDecision,
)
from .replay import (
    build_replay_fixture_from_hunt,
    build_replay_plan_from_hunt,
    run_hunt_replay,
    verify_existing_hunt_against_replay,
)
from .replay_diff import diff_replay_outputs
from .replay_records import (
    BLOCKED_REPLAY_STEP_KINDS,
    ENABLED_REPLAY_STEP_KINDS,
    HuntReplayDiff,
    HuntReplayFixture,
    HuntReplayMode,
    HuntReplayRecord,
    HuntReplayResult,
    HuntReplayStep,
    HuntReplayStepKind,
    HuntReplayStepStatus,
)
from .replay_validation import validate_replay_fixture, validate_replay_result
from .runner import (
    build_background_hunt_plan,
    list_background_hunt_runs,
    run_background_hunt_batch,
    run_next_hunt_workunit,
    summarize_background_hunt,
)
from .search_summary import build_reviewed_index_search_summary
from .steering import SearchHuntSteeringPreference, SearchHuntSteeringType
from .store import SearchHuntStore
from .transitions import ALLOWED_TRANSITIONS, apply_transition, validate_transition
from .validation import validate_no_forbidden_side_effects, validate_no_truth_claims, validate_query_text, validate_search_hunt_session


ALLOWED_SEARCH_HUNT_STATES = tuple(item.value for item in SearchHuntState)
ALLOWED_SEARCH_HUNT_INTENTS = tuple(item.value for item in SearchHuntIntent)
ALLOWED_SEARCH_HUNT_DESTINATIONS = tuple(item.value for item in SearchHuntDestination)
ALLOWED_SEARCH_HUNT_CHECKED_LAYERS = tuple(item.value for item in SearchHuntCheckedLayer)
ALLOWED_SEARCH_HUNT_UNCHECKED_LAYERS = tuple(item.value for item in SearchHuntUncheckedLayer)
ALLOWED_SEARCH_HUNT_COMMAND_TYPES = tuple(item.value for item in SearchHuntCommandType)
ALLOWED_SEARCH_HUNT_STEERING_TYPES = tuple(item.value for item in SearchHuntSteeringType)
ALLOWED_SEARCH_HUNT_EXHAUSTION_STATES = tuple(item.value for item in SearchHuntExhaustionState)
ALLOWED_HUNT_REPLAY_MODES = tuple(item.value for item in HuntReplayMode)
ALLOWED_HUNT_REPLAY_STEP_KINDS = tuple(item.value for item in HuntReplayStepKind)
ALLOWED_HUNT_REPLAY_STEP_STATUSES = tuple(item.value for item in HuntReplayStepStatus)

__all__ = [
    "ALLOWED_SEARCH_HUNT_CHECKED_LAYERS",
    "ALLOWED_SEARCH_HUNT_COMMAND_TYPES",
    "ALLOWED_SEARCH_HUNT_DESTINATIONS",
    "ALLOWED_SEARCH_HUNT_EXHAUSTION_STATES",
    "ALLOWED_HUNT_REPLAY_MODES",
    "ALLOWED_HUNT_REPLAY_STEP_KINDS",
    "ALLOWED_HUNT_REPLAY_STEP_STATUSES",
    "ALLOWED_SEARCH_HUNT_INTENTS",
    "ALLOWED_SEARCH_HUNT_STATES",
    "ALLOWED_SEARCH_HUNT_STEERING_TYPES",
    "ALLOWED_SEARCH_HUNT_UNCHECKED_LAYERS",
    "ALLOWED_TRANSITIONS",
    "BLOCKED_REPLAY_STEP_KINDS",
    "ENABLED_REPLAY_STEP_KINDS",
    "BackgroundHuntPlan",
    "BackgroundHuntPlanItem",
    "BackgroundHuntRun",
    "BackgroundHuntRunResult",
    "BackgroundHuntRunStatus",
    "BackgroundHuntWorkerPolicyDecision",
    "HuntReplayDiff",
    "HuntReplayFixture",
    "HuntReplayMode",
    "HuntReplayRecord",
    "HuntReplayResult",
    "HuntReplayStep",
    "HuntReplayStepKind",
    "HuntReplayStepStatus",
    "SearchHuntCheckedLayer",
    "SearchHuntClosedError",
    "SearchHuntCommand",
    "SearchHuntCommandResult",
    "SearchHuntCommandType",
    "SearchHuntDestination",
    "SearchHuntError",
    "SearchHuntExhaustionReport",
    "SearchHuntExhaustionState",
    "SearchHuntIntegrityError",
    "SearchHuntIntent",
    "SearchHuntNotFoundError",
    "SearchHuntSession",
    "SearchHuntState",
    "SearchHuntSteeringPreference",
    "SearchHuntSteeringType",
    "SearchHuntStore",
    "SearchHuntSummary",
    "SearchHuntTransition",
    "SearchHuntTransitionError",
    "SearchHuntUncheckedLayer",
    "SearchHuntValidationError",
    "apply_transition",
    "build_background_hunt_plan",
    "build_blocked_policy_reports",
    "build_checked_layer_reports",
    "build_deferred_layer_reports",
    "build_hunt_exhaustion_report",
    "build_local_absence_summary",
    "build_recommended_actions",
    "build_replay_fixture_from_hunt",
    "build_replay_plan_from_hunt",
    "build_reviewed_index_search_summary",
    "diff_replay_outputs",
    "list_background_hunt_runs",
    "run_background_hunt_batch",
    "run_hunt_replay",
    "run_next_hunt_workunit",
    "summarize_background_hunt",
    "validate_no_forbidden_side_effects",
    "validate_no_truth_claims",
    "validate_query_text",
    "validate_replay_fixture",
    "validate_replay_result",
    "validate_search_hunt_session",
    "validate_transition",
    "verify_existing_hunt_against_replay",
]
