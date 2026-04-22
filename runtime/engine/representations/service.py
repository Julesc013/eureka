from __future__ import annotations

from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.public import (
    RepresentationsRequest,
    RepresentationsResult,
    ResolutionRequest,
)
from runtime.engine.interfaces.service import RepresentationsService, ResolutionService
from runtime.engine.resolve import ExactMatchResolutionService


class DeterministicRepresentationsService(RepresentationsService):
    def __init__(
        self,
        catalog: NormalizedCatalog,
        *,
        resolution_service: ResolutionService | None = None,
    ) -> None:
        self._catalog = catalog
        self._resolution_service = resolution_service or ExactMatchResolutionService(catalog)

    def list_representations(self, request: RepresentationsRequest) -> RepresentationsResult:
        outcome = self._resolution_service.resolve(ResolutionRequest.from_parts(request.target_ref))
        if outcome.status != "completed" or outcome.result is None:
            return RepresentationsResult(
                status="blocked",
                target_ref=request.target_ref,
                notices=outcome.notices,
            )

        return RepresentationsResult(
            status="available",
            target_ref=request.target_ref,
            resolved_resource_id=outcome.result.resolved_resource_id,
            primary_object=outcome.result.primary_object,
            source=outcome.result.source,
            representations=outcome.result.representations,
            notices=outcome.result.notices,
        )
