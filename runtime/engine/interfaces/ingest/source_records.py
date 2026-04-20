from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SyntheticSourceRecord:
    target_ref: str
    source_name: str
    payload: dict[str, Any]
    source_locator: str
