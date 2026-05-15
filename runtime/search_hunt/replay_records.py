"""Deterministic local Search Hunt replay records."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_replay_id() -> str:
    return "shrpl_" + uuid.uuid4().hex


class HuntReplayMode(str, Enum):
    PLAN_ONLY = "plan_only"
    REPLAY_LOCAL = "replay_local"
    VERIFY_EXISTING = "verify_existing"


class HuntReplayStepKind(str, Enum):
    CREATE_HUNT = "create_hunt"
    APPLY_HUNT_COMMAND = "apply_hunt_command"
    ADD_STEERING_PREFERENCE = "add_steering_preference"
    GENERATE_EXHAUSTION_REPORT = "generate_exhaustion_report"
    CREATE_SEARCH_NEED = "create_search_need"
    CREATE_WORKUNIT_PLAN = "create_workunit_plan"
    CREATE_WORKUNITS = "create_workunits"
    RUN_SAFE_DETERMINISTIC_WORKER = "run_safe_deterministic_worker"
    DRAFT_AGENT_RESEARCH_TASK_DISABLED = "draft_agent_research_task_disabled"
    SUMMARIZE_FINAL_STATE = "summarize_final_state"
    RUN_SOURCE_PROBE = "run_source_probe"
    RUN_EXTRACTION = "run_extraction"
    RUN_AI_MODEL = "run_ai_model"
    RUN_AGENT_RESEARCH = "run_agent_research"
    DOWNLOAD_ARTIFACT = "download_artifact"
    INSTALL_OR_EXECUTE_ARTIFACT = "install_or_execute_artifact"
    MUTATE_MASTER_INDEX = "mutate_master_index"
    DEPLOY_SERVICE = "deploy_service"


class HuntReplayStepStatus(str, Enum):
    PLANNED = "planned"
    EXECUTED = "executed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    MATCHED = "matched"
    DIFF = "diff"
    FAILED = "failed"


@dataclass(frozen=True)
class HuntReplayStep:
    kind: HuntReplayStepKind
    status: HuntReplayStepStatus
    label: str
    expected: Mapping[str, Any]
    actual: Mapping[str, Any]
    policy_decision: Mapping[str, Any]
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @classmethod
    def new(
        cls,
        kind: HuntReplayStepKind | str,
        status: HuntReplayStepStatus | str = HuntReplayStepStatus.PLANNED,
        *,
        label: str | None = None,
        expected: Mapping[str, Any] | None = None,
        actual: Mapping[str, Any] | None = None,
        policy_decision: Mapping[str, Any] | None = None,
        warnings: Sequence[str] = (),
        limitations: Sequence[str] = (),
    ) -> "HuntReplayStep":
        step_kind = coerce_step_kind(kind)
        return cls(
            kind=step_kind,
            status=coerce_step_status(status),
            label=str(label or step_kind.value),
            expected=dict(expected or {}),
            actual=dict(actual or {}),
            policy_decision=dict(policy_decision or default_policy_decision(step_kind)),
            warnings=tuple(str(item) for item in warnings),
            limitations=tuple(str(item) for item in limitations),
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "HuntReplayStep":
        return cls.new(
            payload.get("kind", ""),
            payload.get("status", HuntReplayStepStatus.PLANNED.value),
            label=str(payload.get("label") or ""),
            expected=mapping(payload.get("expected")),
            actual=mapping(payload.get("actual")),
            policy_decision=mapping(payload.get("policy_decision")),
            warnings=tuple_text(payload.get("warnings")),
            limitations=tuple_text(payload.get("limitations")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "hunt_replay_step.v0",
            "kind": self.kind.value,
            "status": self.status.value,
            "label": self.label,
            "expected": dict(self.expected),
            "actual": dict(self.actual),
            "policy_decision": dict(self.policy_decision),
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
        }


@dataclass(frozen=True)
class HuntReplayDiff:
    status: str
    matched: bool
    differences: tuple[Mapping[str, Any], ...]
    expected_summary: Mapping[str, Any]
    actual_summary: Mapping[str, Any]
    warnings: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "HuntReplayDiff":
        return cls(
            status=str(payload.get("status") or "matched"),
            matched=bool(payload.get("matched", True)),
            differences=tuple(mapping(item) for item in sequence(payload.get("differences"))),
            expected_summary=mapping(payload.get("expected_summary")),
            actual_summary=mapping(payload.get("actual_summary")),
            warnings=tuple_text(payload.get("warnings")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "hunt_replay_diff.v0",
            "status": self.status,
            "matched": self.matched,
            "differences": [dict(item) for item in self.differences],
            "expected_summary": dict(self.expected_summary),
            "actual_summary": dict(self.actual_summary),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class HuntReplayFixture:
    replay_source: str
    hunt_id: str
    query: str
    instance_schema_version: str
    index_snapshot_id: str
    expected_steps: tuple[HuntReplayStep, ...]
    blocked_steps: tuple[HuntReplayStep, ...]
    expected_outputs: Mapping[str, Any]
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    created_at: str = ""

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "HuntReplayFixture":
        return cls(
            replay_source=str(payload.get("replay_source") or "local_hunt_record"),
            hunt_id=str(payload.get("hunt_id") or ""),
            query=str(payload.get("query") or ""),
            instance_schema_version=str(payload.get("instance_schema_version") or ""),
            index_snapshot_id=str(payload.get("index_snapshot_id") or ""),
            expected_steps=tuple(HuntReplayStep.from_dict(item) for item in sequence(payload.get("expected_steps"))),
            blocked_steps=tuple(HuntReplayStep.from_dict(item) for item in sequence(payload.get("blocked_steps"))),
            expected_outputs=mapping(payload.get("expected_outputs")),
            warnings=tuple_text(payload.get("warnings")),
            limitations=tuple_text(payload.get("limitations")),
            created_at=str(payload.get("created_at") or utc_now()),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "hunt_replay_fixture.v0",
            "replay_source": self.replay_source,
            "hunt_id": self.hunt_id,
            "query": self.query,
            "instance_schema_version": self.instance_schema_version,
            "index_snapshot_id": self.index_snapshot_id,
            "expected_steps": [item.to_dict() for item in self.expected_steps],
            "blocked_steps": [item.to_dict() for item in self.blocked_steps],
            "expected_outputs": dict(self.expected_outputs),
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class HuntReplayRecord:
    replay_id: str
    replay_source: str
    hunt_id: str
    query: str
    instance_schema_version: str
    index_snapshot_id: str
    expected_steps: tuple[HuntReplayStep, ...]
    executed_steps: tuple[HuntReplayStep, ...]
    blocked_steps: tuple[HuntReplayStep, ...]
    skipped_steps: tuple[HuntReplayStep, ...]
    expected_outputs: Mapping[str, Any]
    actual_outputs: Mapping[str, Any]
    diff_summary: HuntReplayDiff
    status: str
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]
    started_at: str
    finished_at: str

    @classmethod
    def new(
        cls,
        fixture: HuntReplayFixture,
        *,
        actual_outputs: Mapping[str, Any],
        diff_summary: HuntReplayDiff,
        executed_steps: Sequence[HuntReplayStep] = (),
        skipped_steps: Sequence[HuntReplayStep] = (),
        status: str | None = None,
        started_at: str | None = None,
        finished_at: str | None = None,
        warnings: Sequence[str] = (),
        limitations: Sequence[str] = (),
    ) -> "HuntReplayRecord":
        return cls(
            replay_id=new_replay_id(),
            replay_source=fixture.replay_source,
            hunt_id=fixture.hunt_id,
            query=fixture.query,
            instance_schema_version=fixture.instance_schema_version,
            index_snapshot_id=fixture.index_snapshot_id,
            expected_steps=fixture.expected_steps,
            executed_steps=tuple(executed_steps),
            blocked_steps=fixture.blocked_steps,
            skipped_steps=tuple(skipped_steps),
            expected_outputs=dict(fixture.expected_outputs),
            actual_outputs=dict(actual_outputs),
            diff_summary=diff_summary,
            status=str(status or ("pass" if diff_summary.matched else "diff")),
            warnings=tuple(str(item) for item in warnings),
            limitations=tuple(str(item) for item in limitations) or fixture.limitations,
            started_at=started_at or utc_now(),
            finished_at=finished_at or utc_now(),
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "HuntReplayRecord":
        return cls(
            replay_id=str(payload.get("replay_id") or ""),
            replay_source=str(payload.get("replay_source") or ""),
            hunt_id=str(payload.get("hunt_id") or ""),
            query=str(payload.get("query") or ""),
            instance_schema_version=str(payload.get("instance_schema_version") or ""),
            index_snapshot_id=str(payload.get("index_snapshot_id") or ""),
            expected_steps=tuple(HuntReplayStep.from_dict(item) for item in sequence(payload.get("expected_steps"))),
            executed_steps=tuple(HuntReplayStep.from_dict(item) for item in sequence(payload.get("executed_steps"))),
            blocked_steps=tuple(HuntReplayStep.from_dict(item) for item in sequence(payload.get("blocked_steps"))),
            skipped_steps=tuple(HuntReplayStep.from_dict(item) for item in sequence(payload.get("skipped_steps"))),
            expected_outputs=mapping(payload.get("expected_outputs")),
            actual_outputs=mapping(payload.get("actual_outputs")),
            diff_summary=HuntReplayDiff.from_dict(mapping(payload.get("diff_summary"))),
            status=str(payload.get("status") or "pass"),
            warnings=tuple_text(payload.get("warnings")),
            limitations=tuple_text(payload.get("limitations")),
            started_at=str(payload.get("started_at") or utc_now()),
            finished_at=str(payload.get("finished_at") or utc_now()),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "hunt_replay_record.v0",
            "replay_id": self.replay_id,
            "replay_source": self.replay_source,
            "hunt_id": self.hunt_id,
            "query": self.query,
            "instance_schema_version": self.instance_schema_version,
            "index_snapshot_id": self.index_snapshot_id,
            "expected_steps": [item.to_dict() for item in self.expected_steps],
            "executed_steps": [item.to_dict() for item in self.executed_steps],
            "blocked_steps": [item.to_dict() for item in self.blocked_steps],
            "skipped_steps": [item.to_dict() for item in self.skipped_steps],
            "expected_outputs": dict(self.expected_outputs),
            "actual_outputs": dict(self.actual_outputs),
            "diff_summary": self.diff_summary.to_dict(),
            "status": self.status,
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "source_probe_executed": False,
            "extraction_executed": False,
            "external_network_used": False,
            "model_provider_used": False,
            "download_install_execute_performed": False,
            "master_index_mutated": False,
            "site_dist_mutated": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        }


@dataclass(frozen=True)
class HuntReplayResult:
    mode: HuntReplayMode
    fixture: HuntReplayFixture
    record: HuntReplayRecord

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "hunt_replay_result_payload.v0",
            "mode": self.mode.value,
            "fixture": self.fixture.to_dict(),
            "record": self.record.to_dict(),
            "replay_id": self.record.replay_id,
            "hunt_id": self.record.hunt_id,
            "status": self.record.status,
            "diff_summary": self.record.diff_summary.to_dict(),
            "blocked_steps": [item.to_dict() for item in self.record.blocked_steps],
            "source_probe_executed": False,
            "extraction_executed": False,
            "external_network_used": False,
            "model_provider_used": False,
            "download_install_execute_performed": False,
            "master_index_mutated": False,
            "site_dist_mutated": False,
            "deployment_performed": False,
        }


def coerce_replay_mode(value: HuntReplayMode | str) -> HuntReplayMode:
    return value if isinstance(value, HuntReplayMode) else HuntReplayMode(str(value))


def coerce_step_kind(value: HuntReplayStepKind | str) -> HuntReplayStepKind:
    return value if isinstance(value, HuntReplayStepKind) else HuntReplayStepKind(str(value))


def coerce_step_status(value: HuntReplayStepStatus | str) -> HuntReplayStepStatus:
    return value if isinstance(value, HuntReplayStepStatus) else HuntReplayStepStatus(str(value))


def default_policy_decision(kind: HuntReplayStepKind) -> dict[str, Any]:
    blocked = kind in BLOCKED_REPLAY_STEP_KINDS
    return {
        "schema_version": "hunt_replay_step_policy_decision.v0",
        "allowed": not blocked,
        "status": "blocked" if blocked else "allowed",
        "reason": "future action remains blocked by replay policy" if blocked else "deterministic local replay step",
        "source_probe_allowed": False,
        "extraction_allowed": False,
        "model_provider_allowed": False,
        "external_network_allowed": False,
        "download_allowed": False,
        "install_execution_allowed": False,
        "deployment_allowed": False,
        "master_index_mutation_allowed": False,
    }


ENABLED_REPLAY_STEP_KINDS = (
    HuntReplayStepKind.CREATE_HUNT,
    HuntReplayStepKind.APPLY_HUNT_COMMAND,
    HuntReplayStepKind.ADD_STEERING_PREFERENCE,
    HuntReplayStepKind.GENERATE_EXHAUSTION_REPORT,
    HuntReplayStepKind.CREATE_SEARCH_NEED,
    HuntReplayStepKind.CREATE_WORKUNIT_PLAN,
    HuntReplayStepKind.CREATE_WORKUNITS,
    HuntReplayStepKind.RUN_SAFE_DETERMINISTIC_WORKER,
    HuntReplayStepKind.DRAFT_AGENT_RESEARCH_TASK_DISABLED,
    HuntReplayStepKind.SUMMARIZE_FINAL_STATE,
)

BLOCKED_REPLAY_STEP_KINDS = (
    HuntReplayStepKind.RUN_SOURCE_PROBE,
    HuntReplayStepKind.RUN_EXTRACTION,
    HuntReplayStepKind.RUN_AI_MODEL,
    HuntReplayStepKind.RUN_AGENT_RESEARCH,
    HuntReplayStepKind.DOWNLOAD_ARTIFACT,
    HuntReplayStepKind.INSTALL_OR_EXECUTE_ARTIFACT,
    HuntReplayStepKind.MUTATE_MASTER_INDEX,
    HuntReplayStepKind.DEPLOY_SERVICE,
)


def mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def sequence(value: Any) -> Sequence[Any]:
    return value if isinstance(value, (list, tuple)) else ()


def tuple_text(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value)
