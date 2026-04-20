from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from runtime.engine.interfaces.public import Notice, ResolutionRequest, ResolutionResult
from runtime.engine.interfaces.service import ResolutionOutcome, ResolutionService


@dataclass(frozen=True)
class SubmitResolutionJobRequest:
    target_ref: str
    requested_outputs: tuple[str, ...] = ()

    @classmethod
    def from_parts(
        cls,
        target_ref: str,
        requested_outputs: Sequence[str] | None = None,
    ) -> "SubmitResolutionJobRequest":
        normalized_target_ref = target_ref.strip()
        if not normalized_target_ref:
            raise ValueError("target_ref must be a non-empty string.")
        return cls(
            target_ref=normalized_target_ref,
            requested_outputs=tuple(requested_outputs or ()),
        )

    def to_engine_request(self) -> ResolutionRequest:
        return ResolutionRequest.from_parts(
            target_ref=self.target_ref,
            requested_outputs=self.requested_outputs,
        )


@dataclass(frozen=True)
class ResolutionJobRecord:
    job_id: str
    status: str
    target_ref: str
    requested_outputs: tuple[str, ...] = ()
    notices: tuple[Notice, ...] = ()
    result: ResolutionResult | None = None


class InMemoryResolutionJobService:
    def __init__(self, resolution_service: ResolutionService) -> None:
        self._resolution_service = resolution_service
        self._jobs: dict[str, ResolutionJobRecord] = {}
        self._job_counter = 0

    def submit_resolution_job(self, request: SubmitResolutionJobRequest) -> ResolutionJobRecord:
        self._job_counter += 1
        job_id = f"job-{self._job_counter:04d}"
        outcome = self._resolution_service.resolve(request.to_engine_request())
        job = self._build_job_record(job_id, request, outcome)
        self._jobs[job_id] = job
        return job

    def get_resolution_job(self, job_id: str) -> ResolutionJobRecord:
        try:
            return self._jobs[job_id]
        except KeyError as exc:
            raise KeyError(f"Unknown resolution job_id '{job_id}'.") from exc

    def _build_job_record(
        self,
        job_id: str,
        request: SubmitResolutionJobRequest,
        outcome: ResolutionOutcome,
    ) -> ResolutionJobRecord:
        return ResolutionJobRecord(
            job_id=job_id,
            status=outcome.status,
            target_ref=request.target_ref,
            requested_outputs=request.requested_outputs,
            notices=outcome.notices,
            result=outcome.result,
        )
