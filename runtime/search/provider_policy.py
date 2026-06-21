"""Declarative discovery-provider policy loading and activation checks."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping


SUPPORTED_SCHEMA_VERSION = "eureka.discovery_provider_registry.v0"
DEFAULT_PROVIDER_POLICY_PATH = Path(__file__).resolve().parents[2] / "control" / "policies" / "discovery_provider_registry.json"


class ProviderPolicyError(ValueError):
    """Raised when a provider policy is missing, malformed, or rejects activation."""


@dataclass(frozen=True)
class ProviderPolicy:
    provider_id: str
    provider_kind: str
    adapter: str
    adapter_version: str
    enabled_state: str
    authentication: Mapping[str, Any]
    query_capabilities: Mapping[str, Any]
    pagination: Mapping[str, Any]
    freshness_support: Mapping[str, Any]
    allowed_operating_modes: tuple[str, ...]
    request_budgets: Mapping[str, Any]
    rate_limits: Mapping[str, Any]
    retention: Mapping[str, Any]
    persistent_fields_allowed: tuple[str, ...]
    redistribution: Mapping[str, Any]
    training_use_prohibited: bool
    fetch_handoff_policy: Mapping[str, Any]
    terms_source_reference: str
    last_policy_review: str
    live_canary_state: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "ProviderPolicy":
        provider_id = _required_string(payload, "provider_id")
        enabled_state = _required_string(payload, "enabled_state")
        policy = cls(
            provider_id=provider_id,
            provider_kind=_required_string(payload, "provider_kind"),
            adapter=_required_string(payload, "adapter"),
            adapter_version=_required_string(payload, "adapter_version"),
            enabled_state=enabled_state,
            authentication=_required_mapping(payload, "authentication"),
            query_capabilities=_required_mapping(payload, "query_capabilities"),
            pagination=_required_mapping(payload, "pagination"),
            freshness_support=_required_mapping(payload, "freshness_support"),
            allowed_operating_modes=tuple(_required_string_list(payload, "allowed_operating_modes", allow_empty=_non_activatable_state(enabled_state))),
            request_budgets=_required_mapping(payload, "request_budgets"),
            rate_limits=_required_mapping(payload, "rate_limits"),
            retention=_required_mapping(payload, "retention"),
            persistent_fields_allowed=tuple(str(item) for item in payload.get("persistent_fields_allowed") or []),
            redistribution=_required_mapping(payload, "redistribution"),
            training_use_prohibited=bool(payload.get("training_use_prohibited")),
            fetch_handoff_policy=_required_mapping(payload, "fetch_handoff_policy"),
            terms_source_reference=_required_string(payload, "terms_source_reference"),
            last_policy_review=_required_string(payload, "last_policy_review"),
            live_canary_state=_required_string(payload, "live_canary_state"),
        )
        policy.validate_manifest()
        return policy

    def validate_manifest(self) -> None:
        if not self.provider_id:
            raise ProviderPolicyError("provider manifest missing provider_id")
        if _non_activatable_state(self.enabled_state):
            return
        method = str(self.authentication.get("method") or "").strip()
        if method not in {"api_key_env", "none"}:
            raise ProviderPolicyError(f"{self.provider_id}: invalid credential posture")
        env_keys = [str(item).strip() for item in self.authentication.get("env_keys") or [] if str(item).strip()]
        if bool(self.authentication.get("required")) and not env_keys:
            raise ProviderPolicyError(f"{self.provider_id}: credential posture requires env keys")
        if bool(self.authentication.get("client_side_allowed")):
            raise ProviderPolicyError(f"{self.provider_id}: client-side credentials are not allowed")
        if bool(self.authentication.get("credential_persistence_allowed")):
            raise ProviderPolicyError(f"{self.provider_id}: credential persistence is not allowed")
        if not self.allowed_operating_modes:
            raise ProviderPolicyError(f"{self.provider_id}: allowed operating modes are required")
        for field in (
            "display_results",
            "transient_cache_ttl_seconds",
            "persist_urls",
            "persist_snippets",
            "persist_rank",
            "persist_raw_response",
            "redistribute",
            "use_for_model_training",
        ):
            if field not in self.retention:
                raise ProviderPolicyError(f"{self.provider_id}: retention policy missing {field}")
        if bool(self.retention.get("persist_raw_response")):
            raise ProviderPolicyError(f"{self.provider_id}: raw provider response persistence is forbidden")
        if self.training_use_prohibited and bool(self.retention.get("use_for_model_training")):
            raise ProviderPolicyError(f"{self.provider_id}: training-use policy is inconsistent")
        if "hard_max_provider_requests" not in self.request_budgets:
            raise ProviderPolicyError(f"{self.provider_id}: hard provider-request budget is required")

    def validate_activation(
        self,
        *,
        mode: str,
        requested_budget: Any | None = None,
        env: Mapping[str, str] | None = None,
        require_credentials: bool = False,
    ) -> None:
        self.validate_manifest()
        if _non_activatable_state(self.enabled_state):
            raise ProviderPolicyError(f"{self.provider_id}: provider is disabled by policy")
        clean_mode = str(mode or "").strip()
        if clean_mode not in self.allowed_operating_modes:
            raise ProviderPolicyError(f"{self.provider_id}: operating mode is not allowed by provider policy")
        if requested_budget is not None:
            _validate_budget(self.provider_id, self.request_budgets, requested_budget)
        if require_credentials and bool(self.authentication.get("required")):
            env_source = env or {}
            env_keys = [str(item).strip() for item in self.authentication.get("env_keys") or [] if str(item).strip()]
            if not any(bool(str(env_source.get(key) or "").strip()) for key in env_keys):
                raise ProviderPolicyError(f"{self.provider_id}: provider credential is not configured")

    def safe_status(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "provider_kind": self.provider_kind,
            "adapter": self.adapter,
            "adapter_version": self.adapter_version,
            "enabled_state": self.enabled_state,
            "authentication_method": str(self.authentication.get("method") or ""),
            "credential_env_keys": [str(item) for item in self.authentication.get("env_keys") or []],
            "credential_value_exposed": False,
            "query_capabilities": dict(self.query_capabilities),
            "pagination": dict(self.pagination),
            "freshness_support": dict(self.freshness_support),
            "allowed_operating_modes": list(self.allowed_operating_modes),
            "request_budgets": dict(self.request_budgets),
            "rate_limits": dict(self.rate_limits),
            "retention": dict(self.retention),
            "persistent_fields_allowed": list(self.persistent_fields_allowed),
            "redistribution": dict(self.redistribution),
            "training_use_prohibited": self.training_use_prohibited,
            "fetch_handoff_policy": dict(self.fetch_handoff_policy),
            "terms_source_reference": self.terms_source_reference,
            "last_policy_review": self.last_policy_review,
            "live_canary_state": self.live_canary_state,
        }


@dataclass(frozen=True)
class ProviderPolicyRegistry:
    schema_version: str
    policy_version: int
    default_operating_mode: str
    public_live_fanout_enabled: bool
    reviewed_truth_mutation_enabled: bool
    providers: Mapping[str, ProviderPolicy]
    source_path: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any], *, source_path: str = "") -> "ProviderPolicyRegistry":
        schema_version = _required_string(payload, "schema_version")
        if schema_version != SUPPORTED_SCHEMA_VERSION:
            raise ProviderPolicyError(f"unsupported provider registry schema: {schema_version}")
        providers = {}
        for item in payload.get("providers") or []:
            if not isinstance(item, Mapping):
                raise ProviderPolicyError("provider registry contains a non-object provider entry")
            policy = ProviderPolicy.from_mapping(item)
            if policy.provider_id in providers:
                raise ProviderPolicyError(f"duplicate provider policy: {policy.provider_id}")
            providers[policy.provider_id] = policy
        if not providers:
            raise ProviderPolicyError("provider registry must contain at least one provider")
        return cls(
            schema_version=schema_version,
            policy_version=int(payload.get("policy_version") or 0),
            default_operating_mode=_required_string(payload, "default_operating_mode"),
            public_live_fanout_enabled=bool(payload.get("public_live_fanout_enabled")),
            reviewed_truth_mutation_enabled=bool(payload.get("reviewed_truth_mutation_enabled")),
            providers=providers,
            source_path=source_path,
        )

    def provider(self, provider_id: str) -> ProviderPolicy:
        normalized = normalize_provider_id(provider_id)
        policy = self.providers.get(normalized)
        if policy is None:
            raise ProviderPolicyError(f"provider manifest missing for {provider_id}")
        return policy

    def validate_activation(
        self,
        provider_id: str,
        *,
        mode: str | None = None,
        requested_budget: Any | None = None,
        env: Mapping[str, str] | None = None,
        require_credentials: bool = False,
    ) -> None:
        self.provider(provider_id).validate_activation(
            mode=mode or self.default_operating_mode,
            requested_budget=requested_budget,
            env=env,
            require_credentials=require_credentials,
        )

    def selectable_provider_ids(self, provider_ids: tuple[str, ...], *, mode: str | None = None) -> tuple[str, ...]:
        allowed: list[str] = []
        for provider_id in provider_ids:
            normalized = normalize_provider_id(provider_id)
            try:
                self.validate_activation(normalized, mode=mode or self.default_operating_mode)
            except ProviderPolicyError:
                continue
            allowed.append(normalized)
        return tuple(allowed)

    def safe_status(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "policy_version": self.policy_version,
            "default_operating_mode": self.default_operating_mode,
            "public_live_fanout_enabled": self.public_live_fanout_enabled,
            "reviewed_truth_mutation_enabled": self.reviewed_truth_mutation_enabled,
            "source_path": self.source_path,
            "providers": {provider_id: policy.safe_status() for provider_id, policy in self.providers.items()},
        }


def load_provider_policy_registry(path: str | Path | None = None, *, payload: Mapping[str, Any] | None = None) -> ProviderPolicyRegistry:
    if payload is not None:
        return ProviderPolicyRegistry.from_mapping(payload, source_path="<memory>")
    policy_path = Path(path) if path is not None else DEFAULT_PROVIDER_POLICY_PATH
    try:
        loaded = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ProviderPolicyError(f"provider registry not found: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise ProviderPolicyError(f"provider registry is not valid JSON: {policy_path}") from exc
    if not isinstance(loaded, Mapping):
        raise ProviderPolicyError("provider registry root must be an object")
    return ProviderPolicyRegistry.from_mapping(loaded, source_path=str(policy_path))


def normalize_provider_id(provider_id: str) -> str:
    value = str(provider_id or "").strip().casefold()
    if value == "ia":
        return "internet_archive_metadata"
    return value


def _validate_budget(provider_id: str, hard_limits: Mapping[str, Any], requested_budget: Any) -> None:
    checks = (
        ("max_provider_requests", "hard_max_provider_requests"),
        ("timeout_seconds", "hard_max_timeout_seconds"),
        ("max_retries", "hard_max_retries"),
    )
    for attr, hard_field in checks:
        requested = _budget_value(requested_budget, attr)
        if requested is None:
            continue
        hard = int(hard_limits.get(hard_field) or 0)
        if hard > 0 and int(requested) > hard:
            raise ProviderPolicyError(f"{provider_id}: requested {attr} exceeds provider policy hard maximum")


def _budget_value(requested_budget: Any, attr: str) -> int | None:
    if isinstance(requested_budget, Mapping):
        if attr not in requested_budget:
            return None
        return int(requested_budget[attr])
    if hasattr(requested_budget, attr):
        return int(getattr(requested_budget, attr))
    return None


def _required_string(payload: Mapping[str, Any], key: str) -> str:
    value = str(payload.get(key) or "").strip()
    if not value:
        raise ProviderPolicyError(f"provider policy missing required field: {key}")
    return value


def _required_mapping(payload: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        raise ProviderPolicyError(f"provider policy missing object field: {key}")
    return value


def _required_string_list(payload: Mapping[str, Any], key: str, *, allow_empty: bool = False) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ProviderPolicyError(f"provider policy missing list field: {key}")
    result = [str(item).strip() for item in value if str(item).strip()]
    if not result and not allow_empty:
        raise ProviderPolicyError(f"provider policy missing list field: {key}")
    return result


def _non_activatable_state(enabled_state: str) -> bool:
    state = str(enabled_state or "").casefold()
    return state.startswith("disabled") or state == "deprecated_for_new_integration"
