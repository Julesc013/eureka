from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ResolutionBundleArtifact:
    filename: str
    content_type: str
    payload: bytes


class ResolutionBundleService(Protocol):
    def has_bundle_available(self, target_ref: str) -> bool:
        """Return whether a bounded resolution bundle can be exported for the target."""

    def export_bundle(self, target_ref: str) -> ResolutionBundleArtifact | None:
        """Return a deterministic resolution bundle artifact or ``None`` when unavailable."""
