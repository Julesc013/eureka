from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping


SERVER_MODES = ("local_dev", "public_alpha")
CREATED_BY_SLICE = "public_alpha_safe_mode_v0"


@dataclass(frozen=True)
class WebServerConfig:
    mode: str = "local_dev"
    index_root: str | None = None
    run_store_root: str | None = None
    task_store_root: str | None = None
    memory_store_root: str | None = None
    export_store_root: str | None = None
    allow_local_paths: bool = True
    allow_write_actions: bool = True
    allow_eval_runner: bool = True
    allow_bundle_path_inspection: bool = True
    allow_live_probes: bool = False
    allow_live_internet_archive: bool = False
    downloads_enabled: bool = True
    user_storage_enabled: bool = True
    deployment_approved: bool = False
    production_ready: bool = False
    wrapper_config_summary: Mapping[str, object] | None = None
    public_base_url: str | None = None
    created_by_slice: str = CREATED_BY_SLICE

    def __post_init__(self) -> None:
        if self.mode not in SERVER_MODES:
            raise ValueError(
                f"Unsupported web server mode '{self.mode}'. Expected one of: {', '.join(SERVER_MODES)}."
            )
        if self.mode == "public_alpha":
            if self.allow_local_paths:
                raise ValueError("public_alpha mode must disable caller-provided local paths.")
            if self.allow_write_actions:
                raise ValueError("public_alpha mode must disable write-like actions.")
            if self.allow_bundle_path_inspection:
                raise ValueError("public_alpha mode must disable arbitrary bundle-path inspection.")
            if self.allow_live_probes:
                raise ValueError("public_alpha mode must disable live source probes.")
            if self.allow_live_internet_archive:
                raise ValueError("public_alpha mode must disable live Internet Archive access.")
            if self.downloads_enabled:
                raise ValueError("public_alpha mode must disable downloads and payload readback.")
            if self.user_storage_enabled:
                raise ValueError("public_alpha mode must disable user storage.")
            if self.deployment_approved or self.production_ready:
                raise ValueError("public_alpha mode must not claim deployment approval or production readiness.")
        for field_name in (
            "index_root",
            "run_store_root",
            "task_store_root",
            "memory_store_root",
            "export_store_root",
            "public_base_url",
        ):
            value = getattr(self, field_name)
            if value is not None and not value.strip():
                raise ValueError(f"{field_name} must be non-empty when provided.")

    @classmethod
    def local_dev(cls, **overrides: object) -> "WebServerConfig":
        values = {
            "mode": "local_dev",
            "allow_local_paths": True,
            "allow_write_actions": True,
            "allow_eval_runner": True,
            "allow_bundle_path_inspection": True,
            "allow_live_probes": False,
            "allow_live_internet_archive": False,
            "downloads_enabled": True,
            "user_storage_enabled": True,
            "deployment_approved": False,
            "production_ready": False,
        }
        values.update(overrides)
        return cls(**values)

    @classmethod
    def public_alpha(cls, **overrides: object) -> "WebServerConfig":
        values = {
            "mode": "public_alpha",
            "allow_local_paths": False,
            "allow_write_actions": False,
            "allow_eval_runner": True,
            "allow_bundle_path_inspection": False,
            "allow_live_probes": False,
            "allow_live_internet_archive": False,
            "downloads_enabled": False,
            "user_storage_enabled": False,
            "deployment_approved": False,
            "production_ready": False,
        }
        values.update(overrides)
        return cls(**values)

    @classmethod
    def from_environment(
        cls,
        environ: Mapping[str, str] | None = None,
        *,
        mode: str | None = None,
    ) -> "WebServerConfig":
        env = environ or os.environ
        selected_mode = mode or env.get("EUREKA_WEB_MODE") or "local_dev"
        fields: dict[str, object] = {
            "index_root": _optional_env(env, "EUREKA_WEB_INDEX_ROOT"),
            "run_store_root": _optional_env(env, "EUREKA_WEB_RUN_STORE_ROOT"),
            "task_store_root": _optional_env(env, "EUREKA_WEB_TASK_STORE_ROOT"),
            "memory_store_root": _optional_env(env, "EUREKA_WEB_MEMORY_STORE_ROOT"),
            "export_store_root": _optional_env(env, "EUREKA_WEB_EXPORT_STORE_ROOT"),
            "public_base_url": _optional_env(env, "EUREKA_WEB_PUBLIC_BASE_URL"),
        }
        allow_eval_runner = _optional_bool_env(env, "EUREKA_WEB_ALLOW_EVAL_RUNNER")
        if allow_eval_runner is not None:
            fields["allow_eval_runner"] = allow_eval_runner

        if selected_mode == "public_alpha":
            return cls.public_alpha(**fields)
        if selected_mode == "local_dev":
            allow_local_paths = _optional_bool_env(env, "EUREKA_WEB_ALLOW_LOCAL_PATHS")
            allow_write_actions = _optional_bool_env(env, "EUREKA_WEB_ALLOW_WRITE_ACTIONS")
            allow_bundle_path_inspection = _optional_bool_env(
                env,
                "EUREKA_WEB_ALLOW_BUNDLE_PATH_INSPECTION",
            )
            if allow_local_paths is not None:
                fields["allow_local_paths"] = allow_local_paths
            if allow_write_actions is not None:
                fields["allow_write_actions"] = allow_write_actions
            if allow_bundle_path_inspection is not None:
                fields["allow_bundle_path_inspection"] = allow_bundle_path_inspection
            return cls.local_dev(**fields)
        return cls(mode=selected_mode)

    @property
    def safe_mode_enabled(self) -> bool:
        return self.mode == "public_alpha"

    def to_status_dict(self) -> dict[str, object]:
        return {
            "status": "available",
            "mode": self.mode,
            "safe_mode_enabled": self.safe_mode_enabled,
            "created_by_slice": self.created_by_slice,
            "public_base_url_configured": self.public_base_url is not None,
            "live_probes_enabled": self.allow_live_probes,
            "live_internet_archive_enabled": self.allow_live_internet_archive,
            "downloads_enabled": self.downloads_enabled,
            "local_paths_enabled": self.allow_local_paths,
            "user_storage_enabled": self.user_storage_enabled,
            "deployment_approved": self.deployment_approved,
            "production_ready": self.production_ready,
            "configured_root_kinds": {
                "index_root": _root_state(self.index_root),
                "run_store_root": _root_state(self.run_store_root),
                "task_store_root": _root_state(self.task_store_root),
                "memory_store_root": _root_state(self.memory_store_root),
                "export_store_root": _root_state(self.export_store_root),
            },
            "enabled_capabilities": _enabled_capabilities(self),
            "disabled_capabilities": _disabled_capabilities(self),
            "external_baseline_observations": {
                "status": "pending_manual",
                "observed_count": 0,
                "pending_count": 192,
                "source": "evals/search_usefulness/external_baselines/",
                "notes": "Use scripts/report_external_baseline_status.py for the current committed manual-baseline status.",
            },
            "source_mode_summary": _source_mode_summary(self),
            "route_policy_summary": _route_policy_summary(self),
            "limitations": _limitations(self),
            "wrapper_config_summary": _safe_wrapper_summary(self.wrapper_config_summary),
            "notices": _mode_notices(self),
        }


def default_web_server_config() -> WebServerConfig:
    return WebServerConfig.local_dev()


def _optional_env(environ: Mapping[str, str], name: str) -> str | None:
    value = environ.get(name)
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _optional_bool_env(environ: Mapping[str, str], name: str) -> bool | None:
    value = _optional_env(environ, name)
    if value is None:
        return None
    normalized = value.casefold()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean-like value.")


def _root_state(value: str | None) -> str:
    return "configured" if value is not None else "not_configured"


def _enabled_capabilities(config: WebServerConfig) -> list[str]:
    capabilities = [
        "status",
        "source_registry_read",
        "query_planner",
        "deterministic_search",
        "exact_resolution",
        "bounded_absence_reports",
        "compatibility_views",
        "bounded_decomposition_listing",
    ]
    if config.allow_eval_runner:
        capabilities.append("archive_resolution_evals")
    if config.allow_local_paths:
        capabilities.extend(
            [
                "caller_local_index_paths",
                "caller_run_store_roots",
                "caller_task_store_roots",
                "caller_memory_store_roots",
                "caller_export_store_roots",
            ]
        )
    if config.allow_bundle_path_inspection:
        capabilities.append("caller_bundle_path_inspection")
    if config.allow_write_actions:
        capabilities.append("local_write_actions")
    if config.downloads_enabled:
        capabilities.append("payload_downloads")
    if config.user_storage_enabled:
        capabilities.append("user_storage")
    return capabilities


def _disabled_capabilities(config: WebServerConfig) -> list[str]:
    disabled: list[str] = []
    if not config.allow_local_paths:
        disabled.extend(
            [
                "caller_local_index_paths",
                "caller_run_store_roots",
                "caller_task_store_roots",
                "caller_memory_store_roots",
                "caller_export_store_roots",
            ]
        )
    if not config.allow_write_actions:
        disabled.append("local_write_actions")
    if not config.allow_bundle_path_inspection:
        disabled.append("caller_bundle_path_inspection")
    if not config.allow_eval_runner:
        disabled.append("archive_resolution_evals")
    if not config.allow_live_probes:
        disabled.append("live_source_probes")
    if not config.allow_live_internet_archive:
        disabled.append("live_internet_archive")
    if not config.downloads_enabled:
        disabled.append("payload_downloads")
    if not config.user_storage_enabled:
        disabled.append("user_storage")
    if not config.deployment_approved:
        disabled.append("deployment_approval")
    return disabled


def _route_policy_summary(config: WebServerConfig) -> dict[str, object]:
    return {
        "mode": config.mode,
        "local_path_controls": "enabled" if config.allow_local_paths else "disabled",
        "write_actions": "enabled" if config.allow_write_actions else "disabled",
        "bundle_path_inspection": "enabled" if config.allow_bundle_path_inspection else "disabled",
        "downloads": "enabled" if config.downloads_enabled else "disabled_or_route_blocked",
        "user_storage": "enabled" if config.user_storage_enabled else "disabled",
        "live_probes": "enabled" if config.allow_live_probes else "disabled",
    }


def _source_mode_summary(config: WebServerConfig) -> dict[str, object]:
    return {
        "active_source_posture": "fixture_backed_local_corpus",
        "live_source_probes_enabled": config.allow_live_probes,
        "live_internet_archive_enabled": config.allow_live_internet_archive,
        "manual_external_baselines": "pending_manual",
        "placeholder_sources": "remain_placeholders",
    }


def _limitations(config: WebServerConfig) -> list[str]:
    if config.mode != "public_alpha":
        return ["local_dev is trusted-operator bootstrap behavior, not production."]
    return [
        "Public alpha is not production.",
        "No deployment approval is represented by this server.",
        "Live source probes are disabled.",
        "Caller-provided local path controls are blocked.",
        "Downloads, payload readback, and user storage are disabled or route-blocked.",
        "Auth, TLS, rate limiting, and process supervision remain external future responsibilities.",
        "External baselines remain pending/manual unless a human records observations.",
    ]


def _safe_wrapper_summary(value: Mapping[str, object] | None) -> dict[str, object] | None:
    if value is None:
        return None
    allowed_keys = {
        "config_kind",
        "status",
        "created_by_slice",
        "mode",
        "host",
        "port",
        "bind_scope",
        "allow_nonlocal_bind",
        "live_probes_enabled",
        "live_internet_archive_enabled",
        "downloads_enabled",
        "local_paths_enabled",
        "user_storage_enabled",
        "deployment_performed",
        "deployment_approved",
        "production_ready",
        "limits",
        "configured_path_env_vars",
        "route_policy",
        "warnings",
    }
    return {key: item for key, item in value.items() if key in allowed_keys}


def _mode_notices(config: WebServerConfig) -> list[dict[str, str]]:
    if config.mode == "public_alpha":
        return [
            {
                "code": "public_alpha_not_production",
                "severity": "info",
                "message": (
                    "Public Alpha Safe Mode v0 is a constrained demo posture; it does not add "
                    "auth, HTTPS/TLS, accounts, or production deployment semantics."
                ),
            },
            {
                "code": "local_paths_blocked",
                "severity": "info",
                "message": "Caller-provided local filesystem path controls are blocked in public_alpha mode.",
            },
        ]
    return [
        {
            "code": "local_dev_trusted_operator",
            "severity": "info",
            "message": "local_dev mode preserves trusted local demo behavior, including local path controls.",
        }
    ]
