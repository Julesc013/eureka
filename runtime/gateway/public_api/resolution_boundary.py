from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from runtime.gateway.public_api.resolution_jobs import InMemoryResolutionJobService, ResolutionJobRecord, SubmitResolutionJobRequest


@dataclass(frozen=True)
class PublicApiResponse:
    status_code: int
    body: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status_code": self.status_code,
            "body": deepcopy(self.body),
        }


class ResolutionJobsPublicApi:
    def __init__(self, job_service: InMemoryResolutionJobService) -> None:
        self._job_service = job_service

    def submit_resolution_job(self, request: SubmitResolutionJobRequest) -> PublicApiResponse:
        job = self._job_service.submit_resolution_job(request)
        return PublicApiResponse(
            status_code=202,
            body=accepted_resolution_job_to_public_envelope(job),
        )

    def read_resolution_job(self, job_id: str) -> PublicApiResponse:
        try:
            job = self._job_service.get_resolution_job(job_id)
        except KeyError:
            return PublicApiResponse(
                status_code=404,
                body=resolution_job_not_found_error(job_id),
            )

        return PublicApiResponse(
            status_code=200,
            body=resolution_job_to_public_envelope(job),
        )


def accepted_resolution_job_to_public_envelope(job: ResolutionJobRecord) -> dict[str, Any]:
    envelope = {
        "job_id": job.job_id,
        "status": "accepted",
        "target_ref": job.target_ref,
        "requested_outputs": list(job.requested_outputs),
        "notices": [],
    }
    resolved_resource_id = _job_resolved_resource_id(job)
    if resolved_resource_id is not None:
        envelope["resolved_resource_id"] = resolved_resource_id
    return envelope


def resolution_job_to_public_envelope(job: ResolutionJobRecord) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "job_id": job.job_id,
        "status": job.status,
        "target_ref": job.target_ref,
        "requested_outputs": list(job.requested_outputs),
        "notices": [notice.to_dict() for notice in job.notices],
    }
    resolved_resource_id = _job_resolved_resource_id(job)
    if resolved_resource_id is not None:
        envelope["resolved_resource_id"] = resolved_resource_id
    if job.result is not None:
        envelope["result"] = job.result.to_dict()
    return envelope


def resolution_job_not_found_error(job_id: str) -> dict[str, str]:
    return {
        "code": "resolution_job_not_found",
        "message": f"Unknown resolution job_id '{job_id}'.",
    }


def _job_resolved_resource_id(job: ResolutionJobRecord) -> str | None:
    if job.result is None:
        return None
    return job.result.resolved_resource_id
