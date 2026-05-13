"""Validation helpers for local operator authentication."""

from typing import Any, Mapping

from .errors import LocalOperatorConfigError


def validate_operator_token(token: str) -> str:
    value = str(token or "")
    if not value.strip():
        raise LocalOperatorConfigError("operator token must not be empty")
    if len(value) < 8:
        raise LocalOperatorConfigError("operator token must be at least 8 characters")
    return value


def validate_token_record(record: Mapping[str, Any]) -> Mapping[str, Any]:
    if record.get("schema_version") != "local_operator_token.v0":
        raise LocalOperatorConfigError("operator token record schema_version mismatch")
    if not str(record.get("token_hash", "")).strip():
        raise LocalOperatorConfigError("operator token hash is required")
    if not str(record.get("token_salt", "")).strip():
        raise LocalOperatorConfigError("operator token salt is required")
    if "token" in record or "raw_token" in record:
        raise LocalOperatorConfigError("raw operator token storage is forbidden")
    return record
