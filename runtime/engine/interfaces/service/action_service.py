from __future__ import annotations

from typing import Any, Protocol


class ResolutionManifestService(Protocol):
    def has_manifest_available(self, target_ref: str) -> bool:
        """Return whether a bounded resolution manifest can be exported for the target."""

    def export_manifest(self, target_ref: str) -> dict[str, Any] | None:
        """Return a deterministic resolution manifest or ``None`` when unavailable."""
