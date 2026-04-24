from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.interfaces.public import (
    DeterministicSearchRunRequest,
    ExactResolutionRunRequest,
    ResolutionRunRecord,
)
from runtime.engine.interfaces.service import ResolutionRunService
from runtime.engine.resolution_runs import ResolutionRunNotFoundError
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


@dataclass(frozen=True)
class ResolutionRunReadRequest:
    run_id: str

    @classmethod
    def from_parts(cls, run_id: str) -> "ResolutionRunReadRequest":
        normalized_run_id = run_id.strip()
        if not normalized_run_id:
            raise ValueError("run_id must be a non-empty string.")
        return cls(run_id=normalized_run_id)


class ResolutionRunsPublicApi:
    def __init__(self, run_service: ResolutionRunService) -> None:
        self._run_service = run_service

    def start_exact_resolution_run(self, request: ExactResolutionRunRequest) -> PublicApiResponse:
        run = self._run_service.run_exact_resolution(request)
        return PublicApiResponse(
            status_code=200,
            body=resolution_runs_to_public_envelope((run,), selected_run_id=run.run_id),
        )

    def start_deterministic_search_run(
        self,
        request: DeterministicSearchRunRequest,
    ) -> PublicApiResponse:
        run = self._run_service.run_deterministic_search(request)
        return PublicApiResponse(
            status_code=200,
            body=resolution_runs_to_public_envelope((run,), selected_run_id=run.run_id),
        )

    def get_run(self, request: ResolutionRunReadRequest) -> PublicApiResponse:
        try:
            run = self._run_service.get_run(request.run_id)
        except ResolutionRunNotFoundError:
            return PublicApiResponse(
                status_code=404,
                body=resolution_run_not_found_envelope(request.run_id),
            )
        return PublicApiResponse(
            status_code=200,
            body=resolution_runs_to_public_envelope((run,), selected_run_id=run.run_id),
        )

    def list_runs(self) -> PublicApiResponse:
        runs = self._run_service.list_runs()
        return PublicApiResponse(
            status_code=200,
            body=resolution_runs_to_public_envelope(runs),
        )


def resolution_runs_to_public_envelope(
    runs: tuple[ResolutionRunRecord, ...],
    *,
    selected_run_id: str | None = None,
) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "status": "available" if selected_run_id is not None else "listed",
        "run_count": len(runs),
        "runs": [resolution_run_to_public_entry(run) for run in runs],
    }
    if selected_run_id is not None:
        envelope["selected_run_id"] = selected_run_id
    return envelope


def resolution_run_not_found_envelope(run_id: str) -> dict[str, Any]:
    return {
        "status": "blocked",
        "run_count": 0,
        "selected_run_id": run_id,
        "runs": [],
        "notices": [
            {
                "code": "resolution_run_not_found",
                "severity": "warning",
                "message": f"Unknown resolution run '{run_id}'.",
            }
        ],
    }


def resolution_run_to_public_entry(run: ResolutionRunRecord) -> dict[str, Any]:
    return {
        "run_id": run.run_id,
        "run_kind": run.run_kind,
        "requested_value": run.requested_value,
        "status": run.status,
        "started_at": run.started_at,
        "completed_at": run.completed_at,
        "checked_source_ids": list(run.checked_source_ids),
        "checked_source_families": list(run.checked_source_families),
        "checked_sources": [source.to_dict() for source in run.checked_sources],
        "result_summary": run.result_summary.to_dict() if run.result_summary is not None else None,
        "absence_report": run.absence_report.to_dict() if run.absence_report is not None else None,
        "notices": [notice.to_dict() for notice in run.notices],
        "created_by_slice": run.created_by_slice,
    }
