"""Ports used by the local E2E reference runner.

These protocols keep nondeterminism, persistence, scheduling, execution,
projection, and replay at the edge of the existing ResolutionRun kernel.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence


class RunnerClock(Protocol):
    def now(self) -> str:
        """Return the current wall-clock timestamp for persisted packets."""

    def monotonic(self) -> float:
        """Return monotonic seconds for timeout checks."""


class RunIdFactory(Protocol):
    def new_run_id(self, query: str, mode: str, projection_profile: str) -> str:
        """Return a stable run ID for a query/mode/profile tuple."""


class RunStore(Protocol):
    def create(self, query: str, projection_profile: str = "operator_workbench") -> dict[str, Any]:
        """Create a run packet."""

    def get(self, run_id: str) -> dict[str, Any]:
        """Return a run packet."""

    def update(self, run: Mapping[str, Any]) -> dict[str, Any]:
        """Persist a run packet update."""


class RunEventStore(Protocol):
    def append(self, run_id: str, event_type: str, payload: Mapping[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        """Append one event."""

    def list_events(self, run_id: str | None = None) -> list[dict[str, Any]]:
        """List events, optionally scoped to a run."""


class WorkUnitScheduler(Protocol):
    def schedule(self, query: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """Return a WorkUnit schedule without executing provider code."""


class WorkUnitExecutor(Protocol):
    def execute(self, workunit: Mapping[str, Any], attempt: int) -> dict[str, Any]:
        """Execute or simulate one WorkUnit attempt."""


class RunPolicyEvaluator(Protocol):
    def evaluate(self, command_type: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """Return a policy decision."""


class RunProjector(Protocol):
    def project(
        self,
        run: Mapping[str, Any],
        workunit_schedule: Mapping[str, Any],
        *,
        projection_profile: str,
    ) -> dict[str, Any]:
        """Build a lane or result projection for the run."""


class RunBundleWriter(Protocol):
    def write_bundle(self, result: Mapping[str, Any], events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        """Persist a run bundle and return its manifest."""


class ReplayReader(Protocol):
    def replay(self, run_dir: str | Path, *, strict: bool = True) -> dict[str, Any]:
        """Validate and replay a local run bundle."""
