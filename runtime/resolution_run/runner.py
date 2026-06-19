"""Durable local E2E reference runner built on the ResolutionRun kernel."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import os
import re
import tempfile
from typing import Any, Iterable, Mapping, Sequence

from .command_handler import handle_run_command
from .errors import ResolutionRunPolicyError, ResolutionRunValidationError
from .event_log import InMemoryRunEventLog, canonical_json, sha256_hex, validate_event_hash_chain
from .lane_projector import build_run_lane_snapshot
from .policy_gate import DEFAULT_RUN_POLICY, evaluate_run_policy
from .run_store import FIXED_CREATED_AT, InMemoryRunStore, stable_id
from .workunit_scheduler import schedule_ia_hunt_workunits


RUNNER_SCHEMA_VERSION = "eureka.e2e_reference_runner.v0"
DEFAULT_OUTPUT_ROOT = Path(".eureka/e2e-reference/runs")
DEFAULT_SYNTHETIC_FIXTURE = "success_two_workunits"
SYNTHETIC_NAMESPACE = "synthetic:e2e-reference"
TERMINAL_STATES = {"completed", "failed", "cancelled", "policy_blocked"}
KNOWN_EVENT_TYPES = {
    "run_created",
    "query_compiled",
    "run_planned",
    "run_started",
    "run_paused",
    "run_resumed",
    "run_cancelled",
    "run_completed",
    "run_failed",
    "run_replayed",
    "workunits_scheduled",
    "workunit_queued",
    "workunit_started",
    "workunit_retry_scheduled",
    "workunit_succeeded",
    "workunit_failed",
    "workunit_partial_success",
    "budget_refused",
    "timeout_reached",
    "lane_snapshot_built",
    "coverage_report_built",
    "bundle_written",
    "live_shadow_policy_blocked",
    "command_applied",
    "command_blocked",
}


@dataclass(frozen=True)
class FixedRunnerClock:
    """Deterministic clock for tests, synthetic runs, and replay."""

    timestamp: str = FIXED_CREATED_AT
    monotonic_value: float = 0.0

    def now(self) -> str:
        return self.timestamp

    def monotonic(self) -> float:
        return self.monotonic_value


@dataclass(frozen=True)
class RunnerBudget:
    max_workunits: int = 10
    max_attempts_per_workunit: int = 2
    max_events: int = 200
    max_elapsed_seconds: int = 60
    max_result_records_per_workunit: int = 10
    failure_policy: str = "continue_with_partial_failure"

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_workunits": self.max_workunits,
            "max_attempts_per_workunit": self.max_attempts_per_workunit,
            "max_events": self.max_events,
            "max_elapsed_seconds": self.max_elapsed_seconds,
            "max_result_records_per_workunit": self.max_result_records_per_workunit,
            "failure_policy": self.failure_policy,
        }


@dataclass(frozen=True)
class RunnerConfig:
    mode: str = "synthetic"
    projection_profile: str = "operator_workbench"
    fixture: str = DEFAULT_SYNTHETIC_FIXTURE
    output_root: Path | None = None
    write_bundle: bool = False
    include_ia_hunt: bool = False
    scheduler_kind: str = "synthetic_fixture"
    budget: RunnerBudget = field(default_factory=RunnerBudget)
    strict_replay: bool = True
    allow_live_shadow: bool = False


class SyntheticFixtureScheduler:
    """Deterministic synthetic scheduler backed by committed fixture files."""

    def __init__(self, fixture_name: str = DEFAULT_SYNTHETIC_FIXTURE) -> None:
        self.fixture_name = fixture_name

    def schedule(self, query: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
        fixture = load_synthetic_fixture(self.fixture_name)
        workunits = []
        for index, item in enumerate(fixture.get("workunits", [])):
            workunit = dict(item)
            workunit.setdefault("workunit_id", stable_id("synthetic_workunit", {"fixture": self.fixture_name, "query": query, "index": index}))
            workunit.setdefault("hunt_id", stable_id("synthetic_hunt", {"fixture": self.fixture_name, "query": query}))
            workunit.setdefault("source_family", "synthetic")
            workunit.setdefault("workunit_type", "synthetic_metadata_probe")
            workunit.setdefault("state", "queued")
            workunit.setdefault("dry_run", True)
            workunit.setdefault("writes_instance_state", False)
            workunit.setdefault("write_scope", "none")
            workunit.setdefault("blocked_actions", [])
            workunit.setdefault("limitations", ["synthetic_input_posture", "not_reviewed_record"])
            workunits.append(workunit)
        return {
            "schema_version": "resolution_run_workunit_schedule.v0",
            "source_family": "synthetic",
            "dry_run": True,
            "fixture_id": str(fixture.get("fixture_id", self.fixture_name)),
            "workunits": workunits,
            "workunit_count": len(workunits),
            "blocked_actions": [],
            "plan": {"schema_version": "synthetic_workunit_plan.v0", "query": query, "fixture": self.fixture_name},
        }


class IADryRunScheduler:
    """Compatibility scheduler for the existing IA-Hunt dry-run path."""

    def schedule(self, query: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
        return schedule_ia_hunt_workunits(query, policy or DEFAULT_RUN_POLICY)


class SyntheticWorkUnitExecutor:
    """Execute deterministic fixture WorkUnits without provider access."""

    def execute(self, workunit: Mapping[str, Any], attempt: int) -> dict[str, Any]:
        script = list(workunit.get("attempts") or [])
        if not script:
            script = [{"status": workunit.get("expected_status", "succeeded"), "result_count": 1}]
        index = min(max(attempt - 1, 0), len(script) - 1)
        result = dict(script[index])
        result.setdefault("schema_version", "synthetic_workunit_result.v0")
        result.setdefault("attempt", attempt)
        result.setdefault("workunit_id", str(workunit.get("workunit_id", "")))
        result.setdefault("result_records", _synthetic_result_records(workunit, result))
        result.setdefault("network_provider_calls", False)
        result.setdefault("accepted_truth", False)
        result.setdefault("reviewed_record_created", False)
        return result


class DisabledLiveShadowExecutor:
    """Fail-closed live-shadow executor."""

    def execute(self, workunit: Mapping[str, Any], attempt: int) -> dict[str, Any]:
        return {
            "schema_version": "live_shadow_blocked_result.v0",
            "workunit_id": str(workunit.get("workunit_id", "live-shadow-blocked")),
            "status": "policy_blocked",
            "attempt": attempt,
            "blocked_reason": "live_shadow_requires_separate_provider_approval",
            "network_provider_calls": False,
            "accepted_truth": False,
            "reviewed_record_created": False,
        }


class LocalRunBundleStore:
    """Write and validate local E2E run bundles under one output root."""

    def __init__(self, output_root: str | Path = DEFAULT_OUTPUT_ROOT) -> None:
        self.output_root = Path(output_root)

    def write_bundle(self, result: Mapping[str, Any], events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        run = dict(result.get("run") or {})
        run_id = _safe_run_id(str(run.get("run_id") or result.get("run_id") or ""))
        run_dir = _safe_child(self.output_root, run_id)
        run_dir.mkdir(parents=True, exist_ok=True)
        workunits = list((result.get("workunit_schedule") or {}).get("workunits") or [])
        bundle_files: dict[str, Any] = {
            "run_state.json": run,
            "events.jsonl": [dict(event) for event in events],
            "workunits.jsonl": workunits,
            "result.json": _result_for_bundle(result),
            "boundary_report.json": dict(result.get("boundaries") or {}),
            "lane_snapshot.json": dict(result.get("lane_snapshot") or {}),
        }
        file_hashes: dict[str, str] = {}
        for relative, payload in bundle_files.items():
            path = run_dir / relative
            if relative.endswith(".jsonl"):
                text = "".join(canonical_json(item) + "\n" for item in payload)
            else:
                text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
            _atomic_write_text(path, text)
            file_hashes[relative] = sha256_hex(text)
        manifest = build_run_manifest(result, events, file_hashes=file_hashes, run_dir=run_dir)
        _atomic_write_text(run_dir / "run_manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        return manifest

    def validate_bundle(self, run_dir: str | Path, *, strict: bool = True, write_report: bool = False) -> dict[str, Any]:
        return validate_run_bundle(run_dir, strict=strict, write_report=write_report)

    def replay(self, run_dir: str | Path, *, strict: bool = True) -> dict[str, Any]:
        return replay_run_bundle(run_dir, strict=strict)


class E2EReferenceRunner:
    """One local runner lifecycle for synthetic, replay, and blocked live-shadow modes."""

    def __init__(
        self,
        *,
        store: InMemoryRunStore | None = None,
        event_log: InMemoryRunEventLog | None = None,
        clock: FixedRunnerClock | None = None,
        bundle_store: LocalRunBundleStore | None = None,
    ) -> None:
        self.store = store or InMemoryRunStore()
        self.event_log = event_log or InMemoryRunEventLog()
        self.clock = clock or FixedRunnerClock()
        self.bundle_store = bundle_store

    def run_to_completion(self, query: str, config: RunnerConfig | None = None) -> dict[str, Any]:
        config = config or RunnerConfig()
        if config.mode == "replay":
            raise ResolutionRunValidationError("replay mode requires replay_run_bundle")
        if config.mode == "live-shadow":
            return self._run_live_shadow(query, config)
        if config.mode != "synthetic":
            raise ResolutionRunValidationError(f"unsupported runner mode: {config.mode}")
        run = self._create_run(query, config)
        if config.budget.max_events < 8:
            self._event(run, "budget_refused", {"budget": "max_events", "max_events": config.budget.max_events})
            self._transition(run, "failed", "event budget exhausted before execution")
            return self._finish_result(run, {}, {}, [], config)
        if config.budget.max_elapsed_seconds <= 0:
            self._transition(run, "failed", "timeout budget exhausted before start")
            self._event(run, "timeout_reached", {"max_elapsed_seconds": config.budget.max_elapsed_seconds})
            return self._finish_result(run, {}, {}, [], config)
        self._transition(run, "planned", "runner planned")
        if config.scheduler_kind == "ia_dry_run" and not config.include_ia_hunt:
            schedule = {
                "schema_version": "resolution_run_workunit_schedule.v0",
                "source_family": "internet_archive_metadata",
                "dry_run": True,
                "workunits": [],
                "workunit_count": 0,
                "blocked_actions": [],
                "plan": {},
            }
        else:
            scheduler = IADryRunScheduler() if config.scheduler_kind == "ia_dry_run" else SyntheticFixtureScheduler(config.fixture)
            schedule = scheduler.schedule(query, DEFAULT_RUN_POLICY)
        if schedule.get("workunit_count", 0) > config.budget.max_workunits:
            self._event(
                run,
                "budget_refused",
                {"scheduled": schedule.get("workunit_count", 0), "max_workunits": config.budget.max_workunits},
            )
            schedule["workunits"] = list(schedule.get("workunits", []))[: config.budget.max_workunits]
            schedule["workunit_count"] = len(schedule["workunits"])
        self._event(run, "workunits_scheduled", {"workunit_count": schedule.get("workunit_count", 0), "scheduler_kind": config.scheduler_kind})
        for workunit in schedule.get("workunits", []) or []:
            self._event(run, "workunit_queued", {"state": "queued"}, workunit_id=str(workunit.get("workunit_id", "")))
        self._transition(run, "running", "runner started")
        result_records = self._execute_workunits(run, schedule, config)
        terminal_state = "completed" if run.get("state") not in {"failed", "cancelled"} else str(run.get("state"))
        if terminal_state == "completed":
            self._transition(run, "completed", "runner completed")
        lane_snapshot = build_run_lane_snapshot(
            run,
            schedule,
            projection_profile=config.projection_profile,
            run_ia_dry_run=config.scheduler_kind == "ia_dry_run" and config.include_ia_hunt,
        )
        self._event(run, "lane_snapshot_built", {"snapshot_id": lane_snapshot["snapshot_id"]})
        coverage_report = _coverage_report(run, schedule, lane_snapshot, config)
        self._event(run, "coverage_report_built", {"coverage_report_id": coverage_report["coverage_report_id"]})
        return self._finish_result(run, schedule, lane_snapshot, result_records, config, coverage_report=coverage_report)

    def create(self, query: str, config: RunnerConfig | None = None) -> dict[str, Any]:
        return self._create_run(query, config or RunnerConfig())

    def pause(self, run: Mapping[str, Any]) -> dict[str, Any]:
        if run.get("state") in TERMINAL_STATES:
            raise ResolutionRunValidationError("cannot pause a terminal run")
        if run.get("state") != "running":
            raise ResolutionRunValidationError("can only pause a running run")
        updated = dict(run)
        self._transition(updated, "paused", "runner paused")
        return updated

    def resume(self, run: Mapping[str, Any]) -> dict[str, Any]:
        if run.get("state") != "paused":
            raise ResolutionRunValidationError("can only resume a paused run")
        updated = dict(run)
        self._transition(updated, "running", "runner resumed")
        return updated

    def cancel(self, run: Mapping[str, Any]) -> dict[str, Any]:
        if run.get("state") in TERMINAL_STATES:
            raise ResolutionRunValidationError("cannot cancel a terminal run")
        updated = dict(run)
        self._transition(updated, "cancelled", "runner cancelled")
        return updated

    def _create_run(self, query: str, config: RunnerConfig) -> dict[str, Any]:
        if not str(query).strip():
            raise ResolutionRunValidationError("query is required")
        run = self.store.create(str(query).strip(), config.projection_profile)
        run_identity = {
            "query": str(query).strip(),
            "profile": config.projection_profile,
            "mode": config.mode,
            "fixture": config.fixture,
            "scheduler": config.scheduler_kind,
        }
        run["run_id"] = stable_id("run", run_identity)
        run["coverage_report_id"] = stable_id("coverage", run["run_id"])
        run.update(
            {
                "runner_schema_version": RUNNER_SCHEMA_VERSION,
                "mode": config.mode,
                "synthetic": config.mode == "synthetic",
                "synthetic_namespace": SYNTHETIC_NAMESPACE if config.mode == "synthetic" else "",
                "live_shadow_approval": config.allow_live_shadow,
                "terminal_posture": "non_terminal",
                "budget": config.budget.to_dict(),
            }
        )
        self.store.update(run)
        self._event(run, "run_created", {"query": run["query"], "mode": config.mode})
        self._event(run, "query_compiled", {"compiled_query_id": run["compiled_query_id"]})
        return run

    def _run_live_shadow(self, query: str, config: RunnerConfig) -> dict[str, Any]:
        run = self._create_run(query, config)
        if config.allow_live_shadow:
            raise ResolutionRunPolicyError("live-shadow provider access is not authorized by this task")
        self._transition(run, "policy_blocked", "live-shadow requires separate provider approval")
        self._event(
            run,
            "live_shadow_policy_blocked",
            {"blocked_reason": "live_shadow_requires_separate_provider_approval", "network_provider_calls": False},
        )
        return self._finish_result(run, {}, {}, [], config)

    def _execute_workunits(self, run: dict[str, Any], schedule: Mapping[str, Any], config: RunnerConfig) -> list[dict[str, Any]]:
        if config.scheduler_kind == "ia_dry_run":
            return []
        executor = SyntheticWorkUnitExecutor()
        records: list[dict[str, Any]] = []
        partial_failures = 0
        for workunit in schedule.get("workunits", []) or []:
            workunit_id = str(workunit.get("workunit_id", ""))
            attempt = 1
            while attempt <= config.budget.max_attempts_per_workunit:
                self._event(run, "workunit_started", {"attempt": attempt}, workunit_id=workunit_id)
                outcome = executor.execute(workunit, attempt)
                status = str(outcome.get("status", "succeeded"))
                if status == "retryable_failure" and attempt < config.budget.max_attempts_per_workunit:
                    partial_failures += 1
                    self._event(run, "workunit_retry_scheduled", {"attempt": attempt, "reason": outcome.get("reason", "retryable_failure")}, workunit_id=workunit_id)
                    attempt += 1
                    continue
                if status == "succeeded":
                    self._event(run, "workunit_succeeded", {"attempt": attempt, "result_count": len(outcome.get("result_records", []) or [])}, workunit_id=workunit_id)
                    records.extend(list(outcome.get("result_records", []) or [])[: config.budget.max_result_records_per_workunit])
                elif status == "partial_success":
                    partial_failures += 1
                    self._event(run, "workunit_partial_success", {"attempt": attempt, "result_count": len(outcome.get("result_records", []) or [])}, workunit_id=workunit_id)
                    records.extend(list(outcome.get("result_records", []) or [])[: config.budget.max_result_records_per_workunit])
                else:
                    partial_failures += 1
                    self._event(run, "workunit_failed", {"attempt": attempt, "status": status, "reason": outcome.get("reason", status)}, workunit_id=workunit_id)
                    if config.budget.failure_policy == "fail_fast":
                        self._transition(run, "failed", f"workunit failed: {workunit_id}")
                break
            if run.get("state") == "failed":
                break
        run["partial_failure_count"] = partial_failures
        return records

    def _finish_result(
        self,
        run: dict[str, Any],
        schedule: Mapping[str, Any],
        lane_snapshot: Mapping[str, Any],
        result_records: Sequence[Mapping[str, Any]],
        config: RunnerConfig,
        *,
        coverage_report: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        run["terminal_posture"] = _terminal_posture(run)
        self.store.update(run)
        events = self.event_log.list_events(str(run.get("run_id")))
        boundaries = boundary_report(config.mode, policy_blocked=run.get("state") == "policy_blocked")
        result = {
            "schema_version": "resolution_run_kernel_result.v0",
            "runner_schema_version": RUNNER_SCHEMA_VERSION,
            "mode": config.mode,
            "run_id": str(run.get("run_id", "")),
            "run": run,
            "events": events,
            "event_count": len(events),
            "workunit_schedule": dict(schedule),
            "lane_snapshot": dict(lane_snapshot),
            "coverage_report": dict(coverage_report or _coverage_report(run, schedule, lane_snapshot, config)),
            "result_records": [dict(record) for record in result_records],
            "result_count": len(result_records),
            "partial_failure_count": int(run.get("partial_failure_count", 0) or 0),
            "blocked_actions": _blocked_actions(),
            "boundaries": boundaries,
            "accepted_truth": False,
            "reviewed_record_created": False,
        }
        if config.write_bundle:
            bundle_store = self.bundle_store or LocalRunBundleStore(config.output_root or DEFAULT_OUTPUT_ROOT)
            manifest = bundle_store.write_bundle(result, events)
            self._event(run, "bundle_written", {"run_dir": manifest["run_dir"], "event_chain_head": manifest["event_chain_head"]})
            events = self.event_log.list_events(str(run.get("run_id")))
            manifest = bundle_store.write_bundle({**result, "events": events}, events)
            result["events"] = events
            result["event_count"] = len(events)
            result["bundle_manifest"] = manifest
            result["run_dir"] = str((bundle_store.output_root / str(run.get("run_id", ""))).resolve())
        return result

    def _transition(self, run: dict[str, Any], state: str, reason: str) -> None:
        previous = str(run.get("state", ""))
        run["state"] = state
        run.setdefault("state_history", [])
        run["state_history"] = list(run.get("state_history", [])) + [{"state": state, "at": self.clock.now(), "reason": reason}]
        event_type = {
            "planned": "run_planned",
            "running": "run_started" if previous != "paused" else "run_resumed",
            "paused": "run_paused",
            "cancelled": "run_cancelled",
            "completed": "run_completed",
            "failed": "run_failed",
        }.get(state)
        if event_type:
            self._event(run, event_type, {"previous_state": previous, "state": state, "reason": reason})

    def _event(self, run: Mapping[str, Any], event_type: str, payload: Mapping[str, Any], *, workunit_id: str = "") -> dict[str, Any]:
        if event_type not in KNOWN_EVENT_TYPES:
            raise ResolutionRunValidationError(f"unknown runner event type: {event_type}")
        return self.event_log.append(
            str(run.get("run_id", "")),
            event_type,
            payload,
            producer_plane="Discovery",
            correlation_id=str(run.get("run_id", "")),
            workunit_id=workunit_id,
            authority="runner_only",
            privacy_posture="local_private",
            synthetic=bool(run.get("synthetic", False)),
        )


def run_e2e_reference_run(
    query: str,
    *,
    mode: str = "synthetic",
    projection_profile: str = "operator_workbench",
    fixture: str = DEFAULT_SYNTHETIC_FIXTURE,
    out_root: str | Path | None = None,
    write_bundle: bool = False,
    include_ia_hunt: bool = False,
    scheduler_kind: str = "synthetic_fixture",
    budget: RunnerBudget | None = None,
    allow_live_shadow: bool = False,
) -> dict[str, Any]:
    runner = E2EReferenceRunner()
    config = RunnerConfig(
        mode=mode,
        projection_profile=projection_profile,
        fixture=fixture,
        output_root=Path(out_root) if out_root is not None else None,
        write_bundle=write_bundle,
        include_ia_hunt=include_ia_hunt,
        scheduler_kind=scheduler_kind,
        budget=budget or RunnerBudget(),
        allow_live_shadow=allow_live_shadow,
    )
    return runner.run_to_completion(query, config)


def replay_run_bundle(run_dir: str | Path, *, strict: bool = True) -> dict[str, Any]:
    report = validate_run_bundle(run_dir, strict=strict, write_report=False)
    if report["status"] != "valid":
        replay_status = "replay_corrupt"
    elif report.get("unknown_event_types") and not strict:
        replay_status = "replay_verified_with_unknown_inert_events"
    else:
        replay_status = "replay_verified"
    replay_report = {
        "schema_version": "eureka.e2e_reference_replay_report.v0",
        "run_id": report.get("run_id", ""),
        "status": replay_status,
        "strict": strict,
        "errors": list(report.get("errors", [])),
        "unknown_event_types": list(report.get("unknown_event_types", [])),
        "provider_network_calls": False,
        "review_or_index_mutation": False,
        "accepted_truth_created": False,
    }
    _atomic_write_text(Path(run_dir) / "replay_report.json", json.dumps(replay_report, indent=2, sort_keys=True) + "\n")
    return replay_report


def validate_run_bundle(run_dir: str | Path, *, strict: bool = True, write_report: bool = False) -> dict[str, Any]:
    root = Path(run_dir)
    errors: list[str] = []
    unknown_event_types: list[str] = []
    manifest = _load_json(root / "run_manifest.json", errors)
    run_state = _load_json(root / "run_state.json", errors)
    events = _load_jsonl(root / "events.jsonl", errors)
    file_hashes = manifest.get("file_hashes") if isinstance(manifest.get("file_hashes"), Mapping) else {}
    for relative, expected_hash in file_hashes.items():
        path = root / str(relative)
        if not path.is_file():
            errors.append(f"missing bundle file: {relative}")
            continue
        actual_hash = sha256_hex(path.read_bytes())
        if actual_hash != expected_hash:
            errors.append(f"file hash mismatch: {relative}")
    errors.extend(validate_event_hash_chain(events))
    for event in events:
        event_type = str(event.get("event_type", ""))
        if event_type not in KNOWN_EVENT_TYPES:
            unknown_event_types.append(event_type)
    if strict and unknown_event_types:
        errors.append(f"unknown event types: {', '.join(sorted(set(unknown_event_types)))}")
    reconstructed_state = _state_from_events(events)
    recorded_state = str(run_state.get("state", ""))
    if reconstructed_state and recorded_state and reconstructed_state != recorded_state:
        if not (reconstructed_state == "completed" and recorded_state == "completed"):
            errors.append(f"replay divergence: reconstructed {reconstructed_state}, recorded {recorded_state}")
    report = {
        "schema_version": "eureka.e2e_reference_bundle_validation.v0",
        "run_id": str(manifest.get("run_id") or run_state.get("run_id") or ""),
        "status": "valid" if not errors else "invalid",
        "strict": strict,
        "event_count": len(events),
        "errors": errors,
        "unknown_event_types": sorted(set(unknown_event_types)),
        "reconstructed_state": reconstructed_state,
        "recorded_state": recorded_state,
        "provider_network_calls": False,
        "accepted_truth_created": False,
    }
    if write_report:
        _atomic_write_text(root / "bundle_validation_report.json", json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def load_synthetic_fixture(name: str) -> dict[str, Any]:
    safe_name = re.sub(r"[^a-zA-Z0-9_.-]", "", name or DEFAULT_SYNTHETIC_FIXTURE)
    root = Path(__file__).resolve().parents[2] / "evals" / "e2e_reference" / "fixtures"
    path = root / f"{safe_name}.json"
    if not path.is_file():
        return _builtin_fixture(safe_name)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ResolutionRunValidationError(f"synthetic fixture must be an object: {path}")
    return payload


def build_run_manifest(
    result: Mapping[str, Any],
    events: Sequence[Mapping[str, Any]],
    *,
    file_hashes: Mapping[str, str],
    run_dir: Path,
) -> dict[str, Any]:
    run = dict(result.get("run") or {})
    schedule = dict(result.get("workunit_schedule") or {})
    event_head = str(events[-1].get("event_hash", "")) if events else ""
    return {
        "schema_version": "eureka.e2e_reference_run_manifest.v0",
        "run_id": str(run.get("run_id", "")),
        "run_dir": run_dir.name,
        "mode": str(result.get("mode") or run.get("mode") or "synthetic"),
        "query": str(run.get("query", "")),
        "created_at": str(run.get("created_at", FIXED_CREATED_AT)),
        "updated_at": str(run.get("updated_at", FIXED_CREATED_AT)),
        "current_state": str(run.get("state", "")),
        "terminal_posture": str(run.get("terminal_posture", "")),
        "synthetic": bool(run.get("synthetic", False)),
        "source_provider_posture": "synthetic_or_replay_only",
        "budget": dict(run.get("budget") or {}),
        "workunit_count": int(schedule.get("workunit_count", 0) or 0),
        "event_count": len(events),
        "result_count": int(result.get("result_count", 0) or 0),
        "partial_failure_count": int(result.get("partial_failure_count", 0) or 0),
        "file_hashes": dict(file_hashes),
        "event_chain_head": event_head,
        "replay_eligible": True,
        "accepted_truth": False,
        "reviewed_record_creation": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "public_exposure": False,
        "network_provider_calls": False,
        "warnings": list(result.get("warnings", []) or []),
        "limitations": list(run.get("limitations", []) or []),
    }


def boundary_report(mode: str, *, policy_blocked: bool = False) -> dict[str, Any]:
    return {
        "schema_version": "resolution_run_boundary_report.v0",
        "policy_blocked": policy_blocked,
        "live_shadow_approved": False,
        "source_probe_executed": False,
        "live_ia_call_performed": False,
        "network_provider_calls": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "execution_performed": False,
        "model_provider_used": False,
        "source_cache_write_performed": False,
        "evidence_write_performed": False,
        "candidate_index_mutated": False,
        "review_queue_mutated": False,
        "review_decision_written": False,
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "public_index_mutated": False,
        "snapshot_publication": False,
        "operator_instance_mutated": False,
        "master_index_mutated": False,
        "public_exposure": False,
        "deployment_performed": False,
        "accepted_truth": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def command_run_bundle(run_dir: str | Path, command: str) -> dict[str, Any]:
    root = Path(run_dir)
    run_state = _load_json(root / "run_state.json", [])
    runner = E2EReferenceRunner()
    if command == "pause":
        updated = runner.pause(run_state)
    elif command == "resume":
        updated = runner.resume(run_state)
    elif command == "cancel":
        updated = runner.cancel(run_state)
    else:
        raise ResolutionRunValidationError(f"unsupported command: {command}")
    _atomic_write_text(root / "run_state.json", json.dumps(updated, indent=2, sort_keys=True) + "\n")
    return {"schema_version": "eureka.e2e_reference_command_result.v0", "run_id": updated["run_id"], "state": updated["state"], "command": command}


def _coverage_report(
    run: Mapping[str, Any],
    workunit_schedule: Mapping[str, Any],
    lane_snapshot: Mapping[str, Any],
    config: RunnerConfig,
) -> dict[str, Any]:
    return {
        "schema_version": "run_coverage_report.v0",
        "coverage_report_id": str(run.get("coverage_report_id") or stable_id("coverage", run.get("run_id"))),
        "run_id": str(run.get("run_id")),
        "created_at": FIXED_CREATED_AT,
        "checked_layers": [
            "reference_runner_created",
            "query_compiled",
            "workunit_scheduler_port",
            "event_hash_chain",
            "local_lane_projection",
            "boundary_report",
        ],
        "unchecked_layers": [
            "live_source_metadata",
            "downloads",
            "extraction",
            "review_promote_apply",
            "operator_instance_apply",
            "public_fanout",
        ],
        "workunit_count": int(workunit_schedule.get("workunit_count", 0) or 0),
        "lane_count": int(lane_snapshot.get("lane_count", 0) or 0),
        "accepted_truth": False,
        "review_required": True,
        "limitations": [
            f"Runner mode is {config.mode}.",
            "Live provider work remains separately gated.",
        ],
    }


def _result_for_bundle(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "eureka.e2e_reference_run_result.v0",
        "run_id": str(result.get("run_id", "")),
        "mode": str(result.get("mode", "")),
        "state": str((result.get("run") or {}).get("state", "")),
        "result_count": int(result.get("result_count", 0) or 0),
        "partial_failure_count": int(result.get("partial_failure_count", 0) or 0),
        "accepted_truth": False,
        "reviewed_record_created": False,
        "network_provider_calls": False,
        "records": [dict(record) for record in result.get("result_records", []) or []],
    }


def _synthetic_result_records(workunit: Mapping[str, Any], result: Mapping[str, Any]) -> list[dict[str, Any]]:
    count = int(result.get("result_count", 1) or 0)
    return [
        {
            "schema_version": "synthetic_result_record.v0",
            "record_id": stable_id("synthetic_result", {"workunit": workunit.get("workunit_id"), "index": index}),
            "source_family": "synthetic",
            "status": "candidate",
            "authority": "synthetic_preview_record",
            "accepted_truth": False,
            "reviewed_record_created": False,
        }
        for index in range(count)
    ]


def _terminal_posture(run: Mapping[str, Any]) -> str:
    state = str(run.get("state", ""))
    if state == "completed" and int(run.get("partial_failure_count", 0) or 0):
        return "completed_with_partial_failure"
    if state in TERMINAL_STATES:
        return state
    return "non_terminal"


def _blocked_actions() -> list[str]:
    return [
        "run_live_source_probe",
        "run_live_ia_metadata",
        "download",
        "upload",
        "extract",
        "execute",
        "call_model_provider",
        "mutate_operator_instance",
        "mutate_master_index",
        "mutate_public_index",
        "deploy",
        "promote_reviewed_record",
    ]


def _safe_run_id(run_id: str) -> str:
    if not run_id or "/" in run_id or "\\" in run_id or ".." in run_id:
        raise ResolutionRunValidationError("unsafe run_id for bundle path")
    return run_id


def _safe_child(root: Path, child: str) -> Path:
    resolved_root = root.resolve()
    path = (resolved_root / child).resolve()
    if resolved_root != path and resolved_root not in path.parents:
        raise ResolutionRunValidationError("bundle path escapes output root")
    return path


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, newline="") as handle:
        handle.write(text)
        temp_name = handle.name
    os.replace(temp_name, path)


def _load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {path.name}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON file {path.name}: {exc}")
        return {}
    return payload if isinstance(payload, dict) else {}


def _load_jsonl(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        errors.append(f"missing JSONL file: {path.name}")
        return []
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSONL line {line_number}: {exc}")
            continue
        if isinstance(payload, dict):
            records.append(payload)
    return records


def _state_from_events(events: Sequence[Mapping[str, Any]]) -> str:
    state = "created" if events else ""
    for event in events:
        event_type = event.get("event_type")
        if event_type == "run_started":
            state = "running"
        elif event_type == "run_paused":
            state = "paused"
        elif event_type == "run_resumed":
            state = "running"
        elif event_type == "run_cancelled":
            state = "cancelled"
        elif event_type == "run_failed":
            state = "failed"
        elif event_type == "run_completed":
            state = "completed"
        elif event_type == "live_shadow_policy_blocked":
            state = "policy_blocked"
    return state


def _builtin_fixture(name: str) -> dict[str, Any]:
    if name == "retry_then_success":
        return {
            "fixture_id": name,
            "workunits": [
                {
                    "workunit_id": "synthetic-workunit-retry",
                    "attempts": [
                        {"status": "retryable_failure", "reason": "synthetic_retry"},
                        {"status": "succeeded", "result_count": 1},
                    ],
                }
            ],
        }
    if name == "terminal_failure":
        return {"fixture_id": name, "workunits": [{"workunit_id": "synthetic-workunit-fail", "attempts": [{"status": "terminal_failure", "reason": "synthetic_terminal_failure"}]}]}
    if name == "partial_success":
        return {"fixture_id": name, "workunits": [{"workunit_id": "synthetic-workunit-partial", "attempts": [{"status": "partial_success", "result_count": 1}]}]}
    return {
        "fixture_id": DEFAULT_SYNTHETIC_FIXTURE,
        "workunits": [
            {"workunit_id": "synthetic-workunit-001", "attempts": [{"status": "succeeded", "result_count": 1}]},
            {"workunit_id": "synthetic-workunit-002", "attempts": [{"status": "succeeded", "result_count": 1}]},
        ],
    }
