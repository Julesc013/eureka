"""Token verification for localhost operator mutations."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
from typing import Any, Mapping

from .errors import LocalOperatorAuthError


@dataclass(frozen=True)
class OperatorAuthState:
    configured: bool
    token_hash: str = ""
    token_salt: str = ""
    source: str = "none"

    def to_dict(self) -> dict[str, Any]:
        return {
            "configured": self.configured,
            "source": self.source,
            "raw_token_stored": False,
            "token_logging_forbidden": True,
        }


def hash_operator_token(token: str, salt: str) -> str:
    value = str(token or "")
    salt_value = str(salt or "")
    return hashlib.sha256((salt_value + "\0" + value).encode("utf-8")).hexdigest()


def verify_operator_token(token: str, token_hash: str, salt: str) -> bool:
    if not token or not token_hash or not salt:
        return False
    candidate = hash_operator_token(token, salt)
    return hmac.compare_digest(candidate, str(token_hash))


def build_operator_auth_state(config: Any) -> OperatorAuthState:
    from .tokens import load_operator_token_record

    record = load_operator_token_record(config.instance_root)
    if not record:
        return OperatorAuthState(configured=False)
    return OperatorAuthState(
        configured=True,
        token_hash=str(record.get("token_hash", "")),
        token_salt=str(record.get("token_salt", "")),
        source="instance_config_hash",
    )


def build_cli_operator_auth_state(token: str | None) -> OperatorAuthState:
    if not token:
        return OperatorAuthState(configured=False)
    salt = hashlib.sha256(b"eureka-local-operator-session").hexdigest()[:32]
    return OperatorAuthState(
        configured=True,
        token_hash=hash_operator_token(token, salt),
        token_salt=salt,
        source="cli_session",
    )


def require_operator_token(request: Any, config: Any, auth_state: OperatorAuthState | None = None) -> OperatorAuthState:
    state = auth_state if auth_state and auth_state.configured else build_operator_auth_state(config)
    if not state.configured:
        raise LocalOperatorAuthError("operator token is not configured")
    token = _extract_token(request)
    if not token:
        raise LocalOperatorAuthError("operator token is required")
    if not verify_operator_token(token, state.token_hash, state.token_salt):
        raise LocalOperatorAuthError("operator token is invalid")
    return state


def _extract_token(request: Any) -> str:
    headers = _mapping(getattr(request, "headers", {}))
    for key in ("x-eureka-operator-token", "X-Eureka-Operator-Token"):
        if key in headers:
            return str(headers[key])
    for params in (
        _mapping(getattr(request, "body_params", {})),
        _mapping(getattr(request, "params", {})),
    ):
        values = params.get("operator_token")
        if isinstance(values, (list, tuple)) and values:
            return str(values[0])
        if values:
            return str(values)
    return ""


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
