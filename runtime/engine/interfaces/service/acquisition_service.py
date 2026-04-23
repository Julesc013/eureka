from __future__ import annotations

from typing import Protocol

from runtime.engine.acquisition.acquisition_result import AcquisitionResult
from runtime.engine.interfaces.public.acquisition import AcquisitionRequest


class AcquisitionService(Protocol):
    def fetch_representation(self, request: AcquisitionRequest) -> AcquisitionResult:
        """Fetch one bounded representation payload for one resolved target."""
