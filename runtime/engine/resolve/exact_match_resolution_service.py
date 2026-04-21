from __future__ import annotations

from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.public import Notice, ResolutionRequest, ResolutionResult
from runtime.engine.interfaces.service import ResolutionOutcome, ResolutionService
from runtime.engine.resolve.object_summary import normalized_record_to_object_summary
from runtime.engine.resolve.resolved_resource_identity import resolved_resource_id_for_record


class ExactMatchResolutionService(ResolutionService):
    def __init__(self, catalog: NormalizedCatalog) -> None:
        self._catalog = catalog

    def resolve(self, request: ResolutionRequest) -> ResolutionOutcome:
        record = self._catalog.find_by_target_ref(request.target_ref)
        if record is None:
            return ResolutionOutcome(
                status="blocked",
                notices=(
                    Notice(
                        code="fixture_target_not_found",
                        severity="warning",
                        message=f"No governed synthetic record matched target_ref '{request.target_ref}'.",
                    ),
                ),
            )

        return ResolutionOutcome(
            status="completed",
            result=ResolutionResult(
                resolved_resource_id=resolved_resource_id_for_record(record),
                primary_object=normalized_record_to_object_summary(record),
            ),
        )
