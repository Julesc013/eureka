"""Metadata responses built from explicit payload material."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping

from .ids import SourceId, canonical_json, stable_digest, utc_now


def payload_to_text(payload: str | bytes | Mapping[str, Any]) -> str:
    if isinstance(payload, bytes):
        return payload.decode("utf-8")
    if isinstance(payload, str):
        return payload
    return canonical_json(dict(payload))


@dataclass(frozen=True, slots=True)
class ResponseFingerprint:
    algorithm: str
    value: str

    @classmethod
    def from_payload(cls, payload: str | bytes | Mapping[str, Any]) -> "ResponseFingerprint":
        text = payload_to_text(payload)
        return cls(algorithm="sha256", value=hashlib.sha256(text.encode("utf-8")).hexdigest())

    def to_dict(self) -> dict[str, str]:
        return {"algorithm": self.algorithm, "value": self.value}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ResponseFingerprint":
        return cls(algorithm=str(data.get("algorithm", "")), value=str(data.get("value", "")))


@dataclass(frozen=True, slots=True)
class MetadataResponse:
    response_id: str
    request_id: str
    source_id: SourceId
    status: str
    payload: str
    payload_format: str = "json"
    fingerprint: ResponseFingerprint = field(default_factory=lambda: ResponseFingerprint("sha256", ""))
    observed_at: str = field(default_factory=utc_now)
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @classmethod
    def build(
        cls,
        request_id: str,
        source_id: SourceId,
        status: str,
        payload: str | bytes | Mapping[str, Any],
        payload_format: str = "json",
        observed_at: str | None = None,
        warnings: tuple[str, ...] = (),
        limitations: tuple[str, ...] = (),
    ) -> "MetadataResponse":
        payload_text = payload_to_text(payload)
        fingerprint = ResponseFingerprint.from_payload(payload_text)
        response_id = "res_" + stable_digest(
            {
                "request_id": request_id,
                "source_id": str(source_id),
                "status": status,
                "fingerprint": fingerprint.to_dict(),
            }
        )
        return cls(
            response_id=response_id,
            request_id=request_id,
            source_id=source_id,
            status=status,
            payload=payload_text,
            payload_format=payload_format,
            fingerprint=fingerprint,
            observed_at=observed_at or utc_now(),
            warnings=warnings,
            limitations=limitations,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "response_id": self.response_id,
            "request_id": self.request_id,
            "source_id": str(self.source_id),
            "status": self.status,
            "payload_format": self.payload_format,
            "payload": self.payload,
            "fingerprint": self.fingerprint.to_dict(),
            "observed_at": self.observed_at,
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "MetadataResponse":
        return cls(
            response_id=str(data.get("response_id", "")),
            request_id=str(data.get("request_id", "")),
            source_id=SourceId.from_dict(str(data.get("source_id", ""))),
            status=str(data.get("status", "")),
            payload=str(data.get("payload", "")),
            payload_format=str(data.get("payload_format", "json")),
            fingerprint=ResponseFingerprint.from_dict(data.get("fingerprint", {}) or {}),
            observed_at=str(data.get("observed_at", "")),
            warnings=tuple(str(item) for item in data.get("warnings", []) or []),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
        )

    @classmethod
    def from_json(cls, text: str) -> "MetadataResponse":
        return cls.from_dict(json.loads(text))
