"""Stable identifiers for source observation runtime."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from .errors import SourceObservationValidationError


SOURCE_ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_digest(value: Any, length: int = 16) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()[:length]


@dataclass(frozen=True, slots=True)
class SourceId:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not SOURCE_ID_RE.match(self.value):
            raise SourceObservationValidationError(
                "source id must be lowercase and contain only letters, numbers, dots, underscores, or hyphens"
            )

    def __str__(self) -> str:
        return self.value

    def to_dict(self) -> dict[str, str]:
        return {"id": self.value}

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | str) -> "SourceId":
        if isinstance(data, str):
            return cls(data)
        return cls(str(data.get("id", "")))

    @classmethod
    def from_json(cls, text: str) -> "SourceId":
        return cls.from_dict(json.loads(text))
