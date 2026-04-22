from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EvidenceSummary:
    claim_kind: str
    claim_value: str
    asserted_by_family: str
    evidence_kind: str
    evidence_locator: str
    asserted_by_label: str | None = None
    asserted_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "claim_kind": self.claim_kind,
            "claim_value": self.claim_value,
            "asserted_by_family": self.asserted_by_family,
            "evidence_kind": self.evidence_kind,
            "evidence_locator": self.evidence_locator,
        }
        if self.asserted_by_label is not None:
            payload["asserted_by_label"] = self.asserted_by_label
        if self.asserted_at is not None:
            payload["asserted_at"] = self.asserted_at
        return payload
