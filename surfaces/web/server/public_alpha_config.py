from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping

from surfaces.web.server.server_config import WebServerConfig


CREATED_BY_SLICE = "live_alpha_01_public_alpha_wrapper"
DEFAULT_BIND_HOST = "127.0.0.1"
DEFAULT_PORT = 8781
MAX_QUERY_LEN_LIMIT = 160
MAX_RESULTS_PER_SOURCE_LIMIT = 10
SOURCE_TIMEOUT_MS_LIMIT = 5000
GLOBAL_TIMEOUT_MS_LIMIT = 10000
LOCAL_BIND_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
PATH_ENV_VARS = (
    "EUREKA_WEB_INDEX_ROOT",
    "EUREKA_WEB_RUN_STORE_ROOT",
    "EUREKA_WEB_TASK_STORE_ROOT",
    "EUREKA_WEB_MEMORY_STORE_ROOT",
    "EUREKA_WEB_EXPORT_STORE_ROOT",
    "EUREKA_INDEX_ROOT",
    "EUREKA_RUN_STORE_ROOT",
    "EUREKA_TASK_STORE_ROOT",
    "EUREKA_MEMORY_STORE_ROOT",
    "EUREKA_EXPORT_STORE_ROOT",
)


@dataclass(frozen=True)
class PublicAlphaWrapperConfig:
    mode: str = "public_alpha"
    host: str = DEFAULT_BIND_HOST
    port: int = DEFAULT_PORT
    allow_nonlocal_bind: bool = False
    allow_live_probes: bool = False
    allow_live_ia: bool = False
    disable_downloads: bool = True
    disable_local_paths: bool = True
    disable_user_storage: bool = True
    max_query_len: int = MAX_QUERY_LEN_LIMIT
    max_results_per_source: int = MAX_RESULTS_PER_SOURCE_LIMIT
    source_timeout_ms: int = SOURCE_TIMEOUT_MS_LIMIT
    global_timeout_ms: int = GLOBAL_TIMEOUT_MS_LIMIT
    configured_path_env_vars: tuple[str, ...] = ()
    created_by_slice: str = CREATED_BY_SLICE

    @property
    def is_local_bind(self) -> bool:
        return self.host.strip().casefold() in LOCAL_BIND_HOSTS

    @property
    def bind_scope(self) -> str:
        return "local" if self.is_local_bind else "nonlocal"

    def validation_errors(self) -> tuple[str, ...]:
        errors: list[str] = []
        if self.mode != "public_alpha":
            errors.append("mode must be public_alpha for the public-alpha wrapper")
        if not self.host.strip():
            errors.append("host must be non-empty")
        if not (1 <= self.port <= 65535):
            errors.append("port must be between 1 and 65535")
        if not self.is_local_bind and not self.allow_nonlocal_bind:
            errors.append(
                "nonlocal bind hosts require --allow-nonlocal-bind or EUREKA_ALLOW_NONLOCAL_BIND=1"
            )
        if self.allow_live_probes:
            errors.append("live probes are not supported by this milestone and must remain disabled")
        if self.allow_live_ia:
            errors.append("live Internet Archive access is not supported by this milestone")
        if not self.disable_downloads:
            errors.append("downloads/export/readback controls must remain disabled or route-blocked")
        if not self.disable_local_paths:
            errors.append("local path controls must remain disabled")
        if not self.disable_user_storage:
            errors.append("user storage must remain disabled")
        if self.max_query_len > MAX_QUERY_LEN_LIMIT:
            errors.append(f"max query length must be <= {MAX_QUERY_LEN_LIMIT}")
        if self.max_results_per_source > MAX_RESULTS_PER_SOURCE_LIMIT:
            errors.append(f"max results per source must be <= {MAX_RESULTS_PER_SOURCE_LIMIT}")
        if self.source_timeout_ms > SOURCE_TIMEOUT_MS_LIMIT:
            errors.append(f"source timeout must be <= {SOURCE_TIMEOUT_MS_LIMIT} ms")
        if self.global_timeout_ms > GLOBAL_TIMEOUT_MS_LIMIT:
            errors.append(f"global timeout must be <= {GLOBAL_TIMEOUT_MS_LIMIT} ms")
        if self.configured_path_env_vars:
            joined = ", ".join(self.configured_path_env_vars)
            errors.append(
                f"public-alpha wrapper refuses configured local path root env vars: {joined}"
            )
        return tuple(errors)

    def warnings(self) -> tuple[str, ...]:
        warnings: list[str] = []
        if not self.is_local_bind and self.allow_nonlocal_bind:
            warnings.append(
                "nonlocal bind requested; this is still not deployment approval or production readiness"
            )
        return tuple(warnings)

    def to_summary_dict(self) -> dict[str, object]:
        errors = self.validation_errors()
        warnings = self.warnings()
        return {
            "config_kind": "eureka.public_alpha_wrapper_config",
            "status": "valid" if not errors else "invalid",
            "created_by_slice": self.created_by_slice,
            "mode": self.mode,
            "host": self.host,
            "port": self.port,
            "bind_scope": self.bind_scope,
            "allow_nonlocal_bind": self.allow_nonlocal_bind,
            "live_probes_enabled": self.allow_live_probes,
            "live_internet_archive_enabled": self.allow_live_ia,
            "downloads_enabled": not self.disable_downloads,
            "local_paths_enabled": not self.disable_local_paths,
            "user_storage_enabled": not self.disable_user_storage,
            "deployment_performed": False,
            "deployment_approved": False,
            "production_ready": False,
            "limits": {
                "max_query_len": self.max_query_len,
                "max_results_per_source": self.max_results_per_source,
                "source_timeout_ms": self.source_timeout_ms,
                "global_timeout_ms": self.global_timeout_ms,
            },
            "configured_path_env_vars": list(self.configured_path_env_vars),
            "route_policy": {
                "local_path_controls": "disabled",
                "live_probes": "disabled",
                "downloads": "disabled_or_route_blocked",
                "user_storage": "disabled",
            },
            "errors": list(errors),
            "warnings": list(warnings),
        }

    def to_web_server_config(self) -> WebServerConfig:
        return WebServerConfig.public_alpha(
            allow_live_probes=False,
            allow_live_internet_archive=False,
            downloads_enabled=False,
            user_storage_enabled=False,
            wrapper_config_summary=self.to_summary_dict(),
        )


def load_public_alpha_wrapper_config(
    environ: Mapping[str, str] | None = None,
    *,
    mode: str | None = None,
    host: str | None = None,
    port: int | None = None,
    allow_nonlocal_bind: bool | None = None,
) -> PublicAlphaWrapperConfig:
    env = environ or os.environ
    configured_paths = tuple(
        name
        for name in PATH_ENV_VARS
        if _optional_env(env, name) is not None
    )
    return PublicAlphaWrapperConfig(
        mode=mode or _optional_env(env, "EUREKA_MODE") or "public_alpha",
        host=host or _optional_env(env, "EUREKA_BIND_HOST") or DEFAULT_BIND_HOST,
        port=port if port is not None else _int_env(env, "EUREKA_PORT", DEFAULT_PORT),
        allow_nonlocal_bind=(
            allow_nonlocal_bind
            if allow_nonlocal_bind is not None
            else _bool_env(env, "EUREKA_ALLOW_NONLOCAL_BIND", False)
        ),
        allow_live_probes=_bool_env(env, "EUREKA_ALLOW_LIVE_PROBES", False),
        allow_live_ia=_bool_env(env, "EUREKA_ALLOW_LIVE_IA", False),
        disable_downloads=_bool_env(env, "EUREKA_DISABLE_DOWNLOADS", True),
        disable_local_paths=_bool_env(env, "EUREKA_DISABLE_LOCAL_PATHS", True),
        disable_user_storage=_bool_env(env, "EUREKA_DISABLE_USER_STORAGE", True),
        max_query_len=_int_env(env, "EUREKA_MAX_QUERY_LEN", MAX_QUERY_LEN_LIMIT),
        max_results_per_source=_int_env(
            env,
            "EUREKA_MAX_RESULTS_PER_SOURCE",
            MAX_RESULTS_PER_SOURCE_LIMIT,
        ),
        source_timeout_ms=_int_env(env, "EUREKA_SOURCE_TIMEOUT_MS", SOURCE_TIMEOUT_MS_LIMIT),
        global_timeout_ms=_int_env(env, "EUREKA_GLOBAL_TIMEOUT_MS", GLOBAL_TIMEOUT_MS_LIMIT),
        configured_path_env_vars=configured_paths,
    )


def _optional_env(environ: Mapping[str, str], name: str) -> str | None:
    value = environ.get(name)
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _bool_env(environ: Mapping[str, str], name: str, default: bool) -> bool:
    value = _optional_env(environ, name)
    if value is None:
        return default
    normalized = value.casefold()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean-like value.")


def _int_env(environ: Mapping[str, str], name: str, default: int) -> int:
    value = _optional_env(environ, name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer.") from error
