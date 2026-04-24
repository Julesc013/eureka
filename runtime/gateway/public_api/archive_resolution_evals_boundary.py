from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


class ArchiveResolutionEvalRunnerLike(Protocol):
    def run_suite(
        self,
        *,
        task_id: str | None = None,
        index_path: str | None = None,
        use_local_index: bool = True,
    ) -> Any:
        """Run the bounded archive-resolution eval suite synchronously."""


@dataclass(frozen=True)
class ArchiveResolutionEvalRunRequest:
    task_id: str | None = None
    index_path: str | None = None

    @classmethod
    def from_parts(
        cls,
        *,
        task_id: str | None = None,
        index_path: str | None = None,
    ) -> "ArchiveResolutionEvalRunRequest":
        normalized_task_id = (task_id or "").strip() or None
        normalized_index_path = (index_path or "").strip() or None
        return cls(task_id=normalized_task_id, index_path=normalized_index_path)


class ArchiveResolutionEvalsPublicApi:
    def __init__(self, eval_runner: ArchiveResolutionEvalRunnerLike) -> None:
        self._eval_runner = eval_runner

    def run_suite(
        self,
        request: ArchiveResolutionEvalRunRequest | None = None,
    ) -> PublicApiResponse:
        normalized_request = request or ArchiveResolutionEvalRunRequest()
        result = self._eval_runner.run_suite(
            task_id=normalized_request.task_id,
            index_path=normalized_request.index_path,
        )
        if normalized_request.task_id is not None and result.total_task_count == 0:
            return PublicApiResponse(
                status_code=404,
                body=archive_resolution_eval_not_found_envelope(
                    normalized_request.task_id,
                    result,
                ),
            )
        return PublicApiResponse(
            status_code=200,
            body=archive_resolution_eval_suite_to_public_envelope(result),
        )

    def run_task(
        self,
        request: ArchiveResolutionEvalRunRequest,
    ) -> PublicApiResponse:
        if request.task_id is None:
            return PublicApiResponse(
                status_code=400,
                body={
                    "status": "blocked",
                    "eval_suite": None,
                    "notices": [
                        {
                            "code": "task_id_required",
                            "severity": "warning",
                            "message": "Provide a non-empty archive-resolution eval task_id.",
                        }
                    ],
                },
            )
        return self.run_suite(request)


def archive_resolution_eval_suite_to_public_envelope(
    result: Any,
) -> dict[str, Any]:
    return {
        "status": "evaluated",
        "eval_suite": result.to_dict(),
    }


def archive_resolution_eval_not_found_envelope(
    task_id: str,
    result: Any,
) -> dict[str, Any]:
    return {
        "status": "blocked",
        "eval_suite": result.to_dict(),
        "notices": [
            {
                "code": "eval_task_not_found",
                "severity": "warning",
                "message": f"Archive-resolution eval task '{task_id}' was not found.",
            }
        ],
    }
