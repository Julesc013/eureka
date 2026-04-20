from __future__ import annotations

from runtime.engine.core import FixtureCatalog, load_default_fixture_catalog
from runtime.engine.interfaces.public import Notice, ResolutionRequest, ResolutionResult
from runtime.engine.interfaces.service import ResolutionOutcome, ResolutionService
from runtime.engine.resolve.object_summary import fixture_entry_to_object_summary


class FixtureBackedResolutionService(ResolutionService):
    def __init__(self, catalog: FixtureCatalog) -> None:
        self._catalog = catalog

    def resolve(self, request: ResolutionRequest) -> ResolutionOutcome:
        entry = self._catalog.find_by_target_ref(request.target_ref)
        if entry is None:
            return ResolutionOutcome(
                status="blocked",
                notices=(
                    Notice(
                        code="fixture_target_not_found",
                        severity="warning",
                        message=f"No governed synthetic fixture matched target_ref '{request.target_ref}'.",
                    ),
                ),
            )

        return ResolutionOutcome(
            status="completed",
            result=ResolutionResult(primary_object=fixture_entry_to_object_summary(entry)),
        )


def build_default_resolution_service() -> FixtureBackedResolutionService:
    return FixtureBackedResolutionService(load_default_fixture_catalog())
