"""Operator token record persistence."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import uuid
from typing import Any, Mapping

from .auth import hash_operator_token
from .errors import LocalOperatorConfigError
from .validation import validate_operator_token, validate_token_record


TOKEN_RECORD_SCHEMA_VERSION = "local_operator_token.v0"


def operator_token_record_path(instance_root: str | Path) -> Path:
    return Path(instance_root).resolve() / "config" / "operator.json"


def load_operator_token_record(instance_root: str | Path) -> Mapping[str, Any] | None:
    path = operator_token_record_path(instance_root)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LocalOperatorConfigError("operator token record must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise LocalOperatorConfigError("operator token record must contain an object")
    return validate_token_record(payload)


def write_operator_token_record(instance_root: str | Path, token: str) -> Mapping[str, Any]:
    value = validate_operator_token(token)
    salt = uuid.uuid4().hex
    record = {
        "schema_version": TOKEN_RECORD_SCHEMA_VERSION,
        "token_hash": hash_operator_token(value, salt),
        "token_salt": salt,
        "updated_at": _utc_now(),
        "raw_token_stored": False,
        "token_logging_forbidden": True,
    }
    path = operator_token_record_path(instance_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
