from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CompatibilityRequirements:
    required_os_families: tuple[str, ...] = ()
    required_architectures: tuple[str, ...] = ()
    required_runtime_families: tuple[str, ...] = ()
    required_features: tuple[str, ...] = ()

    def has_constraints(self) -> bool:
        return bool(
            self.required_os_families
            or self.required_architectures
            or self.required_runtime_families
            or self.required_features
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.required_os_families:
            payload["required_os_families"] = list(self.required_os_families)
        if self.required_architectures:
            payload["required_architectures"] = list(self.required_architectures)
        if self.required_runtime_families:
            payload["required_runtime_families"] = list(self.required_runtime_families)
        if self.required_features:
            payload["required_features"] = list(self.required_features)
        return payload


@dataclass(frozen=True)
class CompatibilityReason:
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "message": self.message,
        }


@dataclass(frozen=True)
class CompatibilityVerdict:
    compatibility_status: str
    reasons: tuple[CompatibilityReason, ...] = ()
    next_steps: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "compatibility_status": self.compatibility_status,
            "reasons": [reason.to_dict() for reason in self.reasons],
            "next_steps": list(self.next_steps),
        }
