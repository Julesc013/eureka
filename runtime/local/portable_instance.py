"""Portable local Eureka command composition.

This module owns the coherent command surface for a local source checkout and
an explicit local instance. Substantive product behavior remains in the
existing instance, runner, Preview Index, exploration, oracle, and service
modules.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import argparse
import json
import os
from pathlib import Path
import queue
import re
import secrets
import shutil
import sys
import tempfile
import threading
import time
from typing import Any, Mapping, Sequence, TextIO
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from evals.e2e_reference.oracle import (
    OracleError,
    run_oracle,
    validate_oracle_run,
    validate_registry,
)
from runtime.index.preview import (
    PreviewIndexError,
    build_preview_index,
    preview_stats_payload,
    search_preview_index,
    validate_preview_index,
)
from runtime.local.appliance import (
    resolve_default_instance_root,
    resolve_instance_root,
    resolve_repo_root,
)
from runtime.local.appliance.errors import LocalInstancePathError
from runtime.local.e2e_hunt_exploration import (
    E2EExploreOptions,
    build_explore_workspace,
)
from runtime.local.service.server import create_local_http_server
from runtime.resolution_run import (
    RunnerBudget,
    replay_run_bundle,
    run_e2e_reference_run,
    validate_run_bundle,
)
from runtime.resolution_run.errors import ResolutionRunValidationError
from runtime.search.live_service import LiveSearchService, live_hunt_run_id
from runtime.search.live_web import provider_status


REPO_ROOT = resolve_repo_root(Path(__file__))
TOOLS_GENERATORS = REPO_ROOT / "tools" / "generators"
if str(TOOLS_GENERATORS) not in sys.path:
    sys.path.insert(0, str(TOOLS_GENERATORS))

from eureka_init_instance import (  # noqa: E402
    CURRENT_INSTANCE_SCHEMA_VERSION,
    initialize_instance,
)
from eureka_instance_status import read_status as read_instance_status  # noqa: E402
from eureka_validate_instance import validate_instance as validate_local_instance  # noqa: E402


PORTABLE_PROFILE_SCHEMA_VERSION = "eureka.portable_instance.v0"
PORTABLE_RESULT_SCHEMA_VERSION = "eureka.portable_command_result.v0"
PORTABLE_STATUS_SCHEMA_VERSION = "eureka.portable_instance_status.v0"
PORTABLE_PROFILE_VERSION = 1
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_MODE = "exploration"
MAX_QUERY_LENGTH = 256
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]+$")
FORBIDDEN_INSTANCE_PARTS = {"runtime", "contracts", "surfaces", "site", "native", "crates"}
FORBIDDEN_INSTANCE_RELATIVE = {
    ("site", "dist"),
}


class PortableInstanceError(ValueError):
    """Raised for portable command configuration or runtime failures."""

    def __init__(self, code: str, message: str, *, exit_code: int = 1, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.exit_code = exit_code
        self.details = dict(details or {})


@dataclass(frozen=True)
class PortablePaths:
    root: Path
    config_dir: Path
    profile: Path
    run_root: Path
    run_bundles: Path
    preview_index: Path
    preview_current: Path
    eval_root: Path
    portable_status_dir: Path
    portable_status: Path
    tmp_root: Path
    logs_dir: Path
    log_file: Path
    exports_dir: Path
    backup_root: Path
    server_state: Path
    server_lock: Path


def resolve_portable_instance_root(instance_arg: str | Path | None = None, *, env: Mapping[str, str] | None = None) -> Path:
    """Resolve the local instance root using CLI, environment, then default."""

    source = instance_arg
    if source is None or not str(source).strip():
        source = (env or os.environ).get("EUREKA_INSTANCE")
    if source is None or not str(source).strip():
        root = resolve_default_instance_root(REPO_ROOT)
    else:
        root = Path(str(source)).expanduser()
    try:
        resolved = resolve_instance_root(root, REPO_ROOT)
    except LocalInstancePathError as exc:
        raise PortableInstanceError("forbidden_instance_path", str(exc), exit_code=2) from exc
    _reject_forbidden_instance_root(resolved)
    return resolved


def build_portable_paths(instance_root: str | Path) -> PortablePaths:
    root = Path(instance_root).expanduser().resolve()
    return PortablePaths(
        root=root,
        config_dir=_instance_child(root, "config"),
        profile=_instance_child(root, "config/portable_instance.json"),
        run_root=_instance_child(root, "run/e2e-reference"),
        run_bundles=_instance_child(root, "run/e2e-reference/runs"),
        preview_index=_instance_child(root, "db/e2e-reference/preview-index"),
        preview_current=_instance_child(root, "db/e2e-reference/preview-index/current.json"),
        eval_root=_instance_child(root, "run/e2e-reference/eval"),
        portable_status_dir=_instance_child(root, "run/e2e-reference/portable-instance"),
        portable_status=_instance_child(root, "run/e2e-reference/portable-instance/status.json"),
        tmp_root=_instance_child(root, "tmp/e2e-reference"),
        logs_dir=_instance_child(root, "logs"),
        log_file=_instance_child(root, "logs/eureka-portable.log"),
        exports_dir=_instance_child(root, "exports"),
        backup_root=_instance_child(root, "exports/backups"),
        server_state=_instance_child(root, "run/eureka-portable-server.json"),
        server_lock=_instance_child(root, "run/eureka-portable-server.lock"),
    )


def bootstrap_command(
    *,
    instance: str | Path | None = None,
    force: bool = False,
    dry_run: bool = False,
    no_demo: bool = False,
    with_demo: bool = False,
) -> dict[str, Any]:
    started = _now()
    root = resolve_portable_instance_root(instance)
    paths = build_portable_paths(root)
    if dry_run:
        init_result = initialize_instance(root, force=force, dry_run=True)
        return _result(
            "bootstrap",
            "pass" if init_result["status"] in {"pass", "pass_with_warnings"} else "fail",
            root,
            started_at=started,
            mutations=False,
            payload={
                "dry_run": True,
                "planned_actions": init_result.get("planned_actions", []),
                "portable_profile": str(paths.profile),
                "next_commands": _next_commands(root),
            },
        )

    init_result = initialize_instance(root, force=force, dry_run=False)
    validation = validate_local_instance(root)
    if validation.get("status") not in {"pass", "pass_with_warnings"}:
        raise PortableInstanceError(
            "instance_validation_failed",
            "local instance initialization did not validate",
            details={"validation": validation},
        )
    _ensure_portable_dirs(paths)
    profile = _load_json_optional(paths.profile) if paths.profile.exists() else {}
    created_at = str(profile.get("created_at") or started)
    profile_payload = _portable_profile(root, init_result.get("instance_id", ""), created_at, _now())
    _write_json(paths.profile, profile_payload)

    if no_demo and with_demo:
        raise PortableInstanceError("conflicting_demo_flags", "use either --with-demo or --no-demo, not both", exit_code=2)

    demo_result: dict[str, Any] = {"created": False}
    preview_result: dict[str, Any] = {"created": False}
    if with_demo:
        demo_result = _create_demo_run(paths)
        preview_result = build_preview_index(out_root=paths.preview_index, runs_root=paths.run_bundles, activate=True)
        validate_preview_index(paths.preview_current, strict=True)

    status = _write_portable_status(
        paths,
        command="bootstrap",
        status="pass",
        profile=profile_payload,
        extra={
            "instance_validation": _compact_validation(validation),
            "demo_run": _compact_demo(demo_result),
            "preview_index": _compact_preview(preview_result),
        },
    )
    return _result(
        "bootstrap",
        "pass_with_warnings" if init_result["status"] == "pass_with_warnings" else "pass",
        root,
        started_at=started,
        mutations=True,
        payload={
            "instance_init": _compact_init(init_result),
            "instance_validation": _compact_validation(validation),
            "portable_profile": _relative_to_instance(root, paths.profile),
            "portable_status": _relative_to_instance(root, paths.portable_status),
            "demo_run": _compact_demo(demo_result),
            "preview_index": _compact_preview(preview_result),
            "portable_status_payload": status,
            "next_commands": _next_commands(root),
        },
    )


def doctor_command(*, instance: str | Path | None = None, strict: bool = False) -> dict[str, Any]:
    started = _now()
    root = resolve_portable_instance_root(instance)
    paths = build_portable_paths(root)
    checks: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if not root.exists():
        errors.append(_issue("bootstrap_required", "Instance root does not exist.", f"python scripts/eureka.py --instance {root} bootstrap", data_risk=False, service_blocked=True))
    else:
        try:
            validation = validate_local_instance(root)
            checks.append({"id": "instance_validation", "status": validation.get("status"), "migration_needed": validation.get("migration_needed", False)})
            for error in validation.get("errors", []):
                errors.append(_issue("instance_validation_failed", str(error), f"python scripts/eureka.py --instance {root} bootstrap --force", data_risk=False, service_blocked=True))
            for warning in validation.get("warnings", []):
                warnings.append(_issue("instance_validation_warning", str(warning), "Inspect the local instance status.", data_risk=False, service_blocked=False))
        except Exception as exc:
            errors.append(_issue("instance_validation_failed", str(exc), f"python scripts/eureka.py --instance {root} bootstrap", data_risk=False, service_blocked=True))

    profile = _load_json_optional(paths.profile) if paths.profile.exists() else {}
    if not profile:
        errors.append(_issue("portable_profile_missing", "Portable profile is missing.", f"python scripts/eureka.py --instance {root} bootstrap", data_risk=False, service_blocked=True))
    else:
        checks.append({"id": "portable_profile", "status": "pass", "schema_version": profile.get("schema_version")})

    if paths.preview_current.exists():
        try:
            preview_validation = validate_preview_index(paths.preview_current, strict=True)
            checks.append({"id": "preview_index", "status": preview_validation.get("status")})
            if preview_validation.get("status") != "pass":
                errors.append(_issue("preview_index_invalid", "; ".join(preview_validation.get("errors", [])), f"python scripts/eureka.py --instance {root} bootstrap", data_risk=False, service_blocked=False))
        except Exception as exc:
            errors.append(_issue("preview_index_invalid", str(exc), f"python scripts/eureka.py --instance {root} bootstrap", data_risk=False, service_blocked=False))
    else:
        warnings.append(_issue("preview_index_absent", "Current Preview Index pointer is absent.", f"python scripts/eureka.py --instance {root} bootstrap", data_risk=False, service_blocked=False))

    registry = validate_registry()
    checks.append({"id": "oracle_registry", "status": registry.get("status"), "case_count": registry.get("case_count"), "suite_count": registry.get("suite_count")})
    if registry.get("status") != "pass":
        errors.append(_issue("oracle_registry_invalid", "; ".join(registry.get("errors", [])), "Repair the autonomous E2E oracle registry.", data_risk=False, service_blocked=False))

    lock_status = _server_lock_status(paths)
    checks.append({"id": "server_lock", **lock_status})
    if lock_status["state"] == "stale":
        warnings.append(_issue("stale_server_lock", "A stale portable server lock was found.", f"Remove {paths.server_lock} after confirming no server is running.", data_risk=False, service_blocked=False))
    elif lock_status["state"] == "running":
        warnings.append(_issue("server_running", "A portable server appears to be running.", "Use the running service or stop it before restart.", data_risk=False, service_blocked=False))

    route_check = _route_registration_check(root) if root.exists() and not errors else {"status": "skipped"}
    checks.append({"id": "exploration_routes", **route_check})
    live_provider_status = provider_status("brave")
    checks.append(
        {
            "id": "live_web_search_provider",
            "status": "configured" if live_provider_status.get("configured") else "not_configured",
            "provider": live_provider_status.get("provider"),
            "credential_value_exposed": False,
        }
    )

    backup = _backup_status(paths)
    checks.append({"id": "backup_root", **backup})
    disk = _disk_space(paths.root)
    checks.append({"id": "disk_space", **disk})
    if disk.get("status") == "warning":
        warnings.append(_issue("disk_space_warning", str(disk.get("message", "")), "Free local disk space before long runs.", data_risk=True, service_blocked=False))

    status = "fail" if errors else ("pass_with_warnings" if warnings or (strict and warnings) else "pass")
    if strict and warnings and not errors:
        status = "pass_with_warnings"
    return _result(
        "doctor",
        status,
        root,
        started_at=started,
        mutations=False,
        payload={
            "strict": strict,
            "checks": checks,
            "errors": errors,
            "warnings": warnings,
            "loopback_only": True,
            "public_exposure": False,
            "live_provider_status": live_provider_status,
            "live_provider_configured": bool(live_provider_status.get("configured")),
            "live_providers_enabled": True,
            "service_start_blocked": bool(errors),
            "recommended_next_command": _recommended_after_doctor(status, root),
        },
    )


def test_command(*, instance: str | Path | None = None, suite: str = "core", case: str | None = None, fail_on_advisory: bool = False) -> dict[str, Any]:
    started = _now()
    root = resolve_portable_instance_root(instance)
    paths = build_portable_paths(root)
    _require_initialized(paths)
    registry = validate_registry()
    if registry.get("status") != "pass":
        raise PortableInstanceError("oracle_registry_invalid", "; ".join(registry.get("errors", [])), exit_code=1)
    paths.eval_root.mkdir(parents=True, exist_ok=True)
    try:
        oracle_result = run_oracle(suite_id=None if case else suite, case_id=case, out_root=paths.eval_root, fail_on_advisory=fail_on_advisory)
    except OracleError as exc:
        raise PortableInstanceError("oracle_run_failed", str(exc), exit_code=1) from exc
    oracle_run_root = _oracle_run_root(paths, str(oracle_result.get("execution_id") or ""))
    validation = validate_oracle_run(oracle_run_root, strict=True)
    status = "pass" if oracle_result.get("overall_gate_status") == "PASS" and validation.get("status") == "pass" else "fail"
    if oracle_result.get("overall_gate_status") == "PASS_WITH_WARNINGS" and not fail_on_advisory:
        status = "pass_with_warnings"
    return _result(
        "test",
        status,
        root,
        started_at=started,
        mutations=True,
        payload={
            "suite": suite if not case else "case",
            "case": case or "",
            "oracle": _compact_oracle(oracle_result),
            "oracle_validation": validation,
            "result_path": _relative_to_instance(root, oracle_run_root),
            "full_unittest_discovery": False,
            "production_readiness_claimed": False,
        },
    )


def search_command(
    query: str,
    *,
    instance: str | Path | None = None,
    mode: str = "local",
    live: bool = False,
    index: str = "local",
    provider: str = "brave",
    page: int = 0,
    count: int = 10,
    freshness: str = "",
    country: str = "",
    language: str = "",
    safe_search: str = "moderate",
    timeout_seconds: int = 10,
) -> dict[str, Any]:
    started = _now()
    root = resolve_portable_instance_root(instance)
    paths = build_portable_paths(root)
    clean_query = str(query or "").strip()
    if not clean_query:
        raise PortableInstanceError("query_required", "search query is required", exit_code=2)
    if len(clean_query) > MAX_QUERY_LENGTH:
        raise PortableInstanceError("query_too_long", f"search query exceeds {MAX_QUERY_LENGTH} characters", exit_code=2)
    search_mode = _search_mode(mode, live=live)
    local = _search_portable_index(paths, clean_query, index=index, limit=count) if search_mode in {"local", "blended"} else _local_index_disabled(index)
    service_payload = LiveSearchService(provider_name=provider).search(
        clean_query,
        mode=search_mode,
        local_results=local,
        page=page,
        count=count,
        freshness=freshness,
        country=country,
        language=language,
        safe_search=safe_search,
        timeout_seconds=timeout_seconds,
    )
    warnings = list(local.get("warnings") or [])
    live_error = service_payload.get("error") if isinstance(service_payload.get("error"), Mapping) and service_payload.get("error") else None
    if live_error is not None:
        warnings.append(str(live_error.get("message") or "Live web search is not configured. Configure a provider or search the local index."))
    status = str(service_payload.get("status") or "fail")
    return _result(
        "search",
        status,
        root,
        started_at=started,
        mutations=False,
        payload={
            "query": clean_query,
            "mode": search_mode,
            "index_mode": index,
            "local_index": service_payload.get("local_index", local),
            "live": service_payload.get("live"),
            "result_count": int(service_payload.get("result_count") or 0),
            "results": list(service_payload.get("results") or []),
            "provider_status": service_payload.get("provider_status", provider_status(provider)),
            "live_error": live_error,
            "error": str(live_error.get("code")) if status == "fail" and live_error else "",
            "message": str(live_error.get("message")) if status == "fail" and live_error else "",
            "warnings": warnings,
            "network_provider_calls": bool(service_payload.get("network_provider_calls")),
            "live_results_transient": True,
            "provider_results_persisted": False,
            "review_required_for_display": False,
            "reviewed_master_mutation": False,
            "public_index_mutation": False,
            "production_truth_mutation": False,
        },
    )


def hunt_command(
    query: str,
    *,
    instance: str | Path | None = None,
    mode: str = "synthetic",
    step: bool = False,
    run_to_completion: bool = False,
    fixture: str | None = None,
    live: bool = False,
    max_queries: int = 20,
    max_fetches: int = 0,
) -> dict[str, Any]:
    started = _now()
    root = resolve_portable_instance_root(instance)
    paths = build_portable_paths(root)
    _require_initialized(paths)
    clean_query = str(query or "").strip()
    if not clean_query:
        raise PortableInstanceError("query_required", "hunt query is required", exit_code=2)
    if len(clean_query) > MAX_QUERY_LENGTH:
        raise PortableInstanceError("query_too_long", f"hunt query exceeds {MAX_QUERY_LENGTH} characters", exit_code=2)
    if live or mode == "live":
        return _live_hunt_command(
            clean_query,
            root=root,
            paths=paths,
            started_at=started,
            max_queries=max_queries,
            max_fetches=max_fetches,
        )
    if mode != "synthetic":
        raise PortableInstanceError("live_mode_forbidden", "portable v0 supports synthetic hunt mode only", exit_code=2)

    preview = _preview_for_query(paths, clean_query)
    budget = RunnerBudget(max_workunits=1) if step and not run_to_completion else RunnerBudget()
    try:
        run = run_e2e_reference_run(
            clean_query,
            mode="synthetic",
            projection_profile="operator_workbench",
            fixture=str(fixture or "success_two_workunits"),
            out_root=paths.run_bundles,
            write_bundle=True,
            include_ia_hunt=False,
            scheduler_kind="synthetic_fixture",
            budget=budget,
        )
    except ResolutionRunValidationError as exc:
        raise PortableInstanceError("hunt_failed", str(exc), exit_code=1) from exc
    run_id = str(run.get("run_id") or "")
    return _result(
        "hunt",
        "pass",
        root,
        started_at=started,
        mutations=True,
        payload={
            "query": clean_query,
            "mode": "synthetic",
            "step": bool(step),
            "run_id": run_id,
            "state": str((run.get("run") or {}).get("state") or ""),
            "workunit_count": int((run.get("workunit_schedule") or {}).get("workunit_count", 0) or 0),
            "event_count": int(run.get("event_count", 0) or 0),
            "result_count": int(run.get("result_count", 0) or 0),
            "preview_result_count": int(preview.get("result_count", 0) or 0),
            "preview_lane_counts": dict(preview.get("lane_counts") or {}),
            "run_directory": _relative_to_instance(root, paths.run_bundles / run_id),
            "replay_command": f"python scripts/eureka.py --instance {root} replay {run_id}",
            "exploration_url": f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/explore?run={run_id}",
            "provider_network_calls": False,
            "review_or_truth_mutation": False,
        },
    )


def replay_command(*, instance: str | Path | None = None, run_id: str = "", strict: bool = True) -> dict[str, Any]:
    started = _now()
    root = resolve_portable_instance_root(instance)
    paths = build_portable_paths(root)
    _require_initialized(paths)
    run_dir = _safe_run_dir(paths, run_id)
    validation = validate_run_bundle(run_dir, strict=strict, write_report=False)
    report = replay_run_bundle(run_dir, strict=strict)
    status = "pass" if report.get("status") in {"replay_verified", "replay_verified_with_unknown_inert_events"} else "fail"
    return _result(
        "replay",
        status,
        root,
        started_at=started,
        mutations=True,
        payload={
            "run_id": run_id,
            "run_directory": _relative_to_instance(root, run_dir),
            "strict": strict,
            "validation": validation,
            "replay": report,
            "event_count": int(validation.get("event_count", 0) or 0),
            "final_state": str(validation.get("recorded_state") or ""),
            "provider_network_calls": False,
            "review_or_index_mutation": False,
        },
    )


def serve_command(
    *,
    instance: str | Path | None = None,
    mode: str = DEFAULT_MODE,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    operator_token: str | None = None,
    smoke: bool = False,
    json_output: bool = False,
    stdout: TextIO = sys.stdout,
    live: bool = False,
) -> dict[str, Any]:
    started = _now()
    if mode != DEFAULT_MODE and not live:
        raise PortableInstanceError("unsupported_server_mode", "portable v0 supports --mode exploration only", exit_code=2)
    if host not in {"127.0.0.1", "localhost"}:
        raise PortableInstanceError("non_loopback_bind_forbidden", "portable v0 may bind only to loopback hosts", exit_code=2)
    root = resolve_portable_instance_root(instance)
    paths = build_portable_paths(root)
    _require_initialized(paths)
    lock_status = _server_lock_status(paths)
    if lock_status["state"] == "running":
        raise PortableInstanceError("server_already_running", "portable server lock indicates an active server", exit_code=1, details=lock_status)
    if lock_status["state"] == "stale":
        _remove_server_state(paths)
    token = operator_token or os.environ.get("EUREKA_OPERATOR_TOKEN") or secrets.token_urlsafe(24)
    generated_token = not (operator_token or os.environ.get("EUREKA_OPERATOR_TOKEN"))
    if smoke:
        smoke_payload = _serve_smoke(paths, host=host, port=port, mode=mode, token=token, live=live)
        return _result(
            "serve",
            "pass" if smoke_payload["smoke"]["status"] == "pass" else "fail",
            root,
            started_at=started,
            mutations=True,
            payload={
                "mode": "live" if live else mode,
                "host": host,
                "port": smoke_payload["port"],
                "url": f"http://{host}:{smoke_payload['port']}/" if live else f"http://{host}:{smoke_payload['port']}/explore",
                "smoke": smoke_payload["smoke"],
                "server_state": smoke_payload["server_state"],
                "operator_token_generated": generated_token,
                "operator_token_persisted": False,
                "loopback_only": True,
                "live_search_enabled": bool(live),
            },
        )
    handle = create_local_http_server(root, host=host, port=port, read_only=False, operator_token=token, bind_lan=False)
    _configure_runtime_for_portable(handle.runtime, paths, live=live)
    actual_port = handle.server_port
    server_state = _write_server_state(paths, host=host, port=actual_port, mode="live" if live else mode)
    url = f"http://{host}:{actual_port}/" if live else f"http://{host}:{actual_port}/explore"
    if not json_output:
        print(f"Eureka live search: {url}" if live else f"Eureka local exploration: {url}", file=stdout)
        if generated_token:
            print(f"Operator token for this process only: {token}", file=stdout)
        print("Press Ctrl+C to stop.", file=stdout)
    try:
        handle.httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        handle.close()
        _remove_server_state(paths)
    return _result(
        "serve",
        "pass",
        root,
        started_at=started,
        mutations=True,
        payload={"mode": "live" if live else mode, "host": host, "port": actual_port, "url": url, "stopped": True, "operator_token_persisted": False, "live_search_enabled": bool(live)},
    )


def status_command(*, instance: str | Path | None = None, include_paths: bool = False) -> dict[str, Any]:
    started = _now()
    root = resolve_portable_instance_root(instance)
    paths = build_portable_paths(root)
    if not root.exists():
        return _result(
            "status",
            "fail",
            root,
            started_at=started,
            mutations=False,
            payload={
                "state": "bootstrap_required",
                "message": "Instance root does not exist.",
                "recommended_next_command": f"python scripts/eureka.py --instance {root} bootstrap",
            },
        )
    instance_status: dict[str, Any] = {}
    try:
        instance_status = read_instance_status(root)
    except Exception as exc:
        instance_status = {"status": "fail", "error": str(exc)}
    preview = _current_preview_status(paths)
    runs = _run_bundle_status(paths)
    oracle = _latest_oracle_status(paths)
    server = _server_lock_status(paths)
    backup = _backup_status(paths)
    live_provider_status = provider_status("brave")
    payload = {
        "state": "ready" if instance_status.get("status") in {"pass", "pass_with_warnings"} else "degraded",
        "instance": {
            "instance_id": instance_status.get("instance_id", ""),
            "schema_version": instance_status.get("instance_schema_version"),
            "migration_needed": bool(instance_status.get("migration_needed", False)),
            "store_count": int(instance_status.get("store_count", 0) or 0),
            "store_status": instance_status.get("status", "fail"),
        },
        "portable_profile": _profile_status(paths),
        "preview_index": preview,
        "run_bundles": runs,
        "latest_oracle_result": oracle,
        "latest_synthetic_truth_result": {"status": "not_configured_in_portable_v0"},
        "server": server,
        "backup": backup,
        "live_provider_status": live_provider_status,
        "live_provider_configured": bool(live_provider_status.get("configured")),
        "provider_network_calls": False,
        "public_exposure": False,
        "review_truth_posture": {
            "real_review_decisions": False,
            "reviewed_records_created": False,
            "reviewed_master_mutation": False,
            "public_index_mutation": False,
        },
        "limitations": _limitations(),
        "recommended_next_command": _recommended_status_next(preview, runs, root),
    }
    if include_paths:
        payload["paths"] = _profile_paths(root)
    return _result("status", "pass" if instance_status.get("status") in {"pass", "pass_with_warnings"} else "fail", root, started_at=started, mutations=False, payload=payload)


def index_stats_command(*, instance: str | Path | None = None) -> dict[str, Any]:
    started = _now()
    root = resolve_portable_instance_root(instance)
    paths = build_portable_paths(root)
    preview = _current_preview_status(paths)
    return _result(
        "index stats",
        "pass" if preview.get("status") in {"pass", "absent"} else "fail",
        root,
        started_at=started,
        mutations=False,
        payload={
            "index_kind": "preview",
            "preview_index": preview,
            "local_private": True,
            "network_provider_calls": False,
            "reviewed_master_mutation": False,
            "public_index_mutation": False,
        },
    )


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    _ensure_common_defaults(args)
    try:
        payload = _dispatch(args, stdout=stdout)
        return _emit_result(payload, json_output=bool(args.json), stdout=stdout)
    except PortableInstanceError as exc:
        root = None
        try:
            root = resolve_portable_instance_root(getattr(args, "instance", None))
        except Exception:
            pass
        payload = _error_payload(exc, root)
        _emit_result(payload, json_output=True if getattr(args, "json", False) else False, stdout=stderr)
        return exc.exit_code


def _dispatch(args: argparse.Namespace, *, stdout: TextIO) -> dict[str, Any]:
    if args.command == "bootstrap":
        return bootstrap_command(instance=args.instance, force=args.force, dry_run=args.dry_run, no_demo=args.no_demo, with_demo=args.with_demo)
    if args.command == "doctor":
        return doctor_command(instance=args.instance, strict=args.strict)
    if args.command == "test":
        return test_command(instance=args.instance, suite=args.suite, case=args.case, fail_on_advisory=args.fail_on_advisory)
    if args.command == "search":
        return search_command(
            args.query,
            instance=args.instance,
            mode=args.mode,
            live=args.live,
            index=args.index,
            provider=args.provider,
            page=args.page,
            count=args.count,
            freshness=args.freshness,
            country=args.country,
            language=args.language,
            safe_search=args.safe_search,
            timeout_seconds=args.timeout,
        )
    if args.command == "hunt":
        return hunt_command(
            args.query,
            instance=args.instance,
            mode=args.mode,
            step=args.step,
            run_to_completion=args.run_to_completion,
            fixture=args.fixture,
            live=args.live,
            max_queries=args.max_queries,
            max_fetches=args.max_fetches,
        )
    if args.command == "replay":
        return replay_command(instance=args.instance, run_id=args.run_id, strict=args.strict)
    if args.command == "serve":
        return serve_command(instance=args.instance, mode=args.mode, host=args.host, port=args.port, operator_token=args.operator_token, smoke=args.smoke, json_output=args.json, stdout=stdout, live=args.live)
    if args.command == "status":
        return status_command(instance=args.instance, include_paths=args.paths)
    if args.command == "index" and args.index_command == "stats":
        return index_stats_command(instance=args.instance)
    raise PortableInstanceError("unsupported_command", f"unsupported command: {args.command}", exit_code=2)


def _parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--instance", default=argparse.SUPPRESS, help="Explicit local instance root. Defaults to EUREKA_INSTANCE or ../instances/default.")
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="Emit stable JSON.")
    common.add_argument("--verbose", action="store_true", default=argparse.SUPPRESS, help="Reserved for future detailed local output.")
    common.add_argument("--quiet", action="store_true", default=argparse.SUPPRESS, help="Reserved for future quiet local output.")

    parser = argparse.ArgumentParser(description="Portable local Eureka command surface.", parents=[common])
    sub = parser.add_subparsers(dest="command", required=True)

    boot = sub.add_parser("bootstrap", parents=[common], help="Initialize or refresh a portable local instance.")
    boot.add_argument("--force", action="store_true", help="Refresh portable metadata without destroying local stores.")
    boot.add_argument("--dry-run", action="store_true", help="Plan initialization without writing files.")
    boot.add_argument("--no-demo", action="store_true", help="Keep bootstrap fixture-free. This is the default.")
    boot.add_argument("--with-demo", action="store_true", help="Explicitly create the synthetic demo run and demo-derived Preview Index.")

    doc = sub.add_parser("doctor", parents=[common], help="Read-only portable instance diagnostics.")
    doc.add_argument("--strict", action="store_true", help="Report warnings distinctly.")

    test = sub.add_parser("test", parents=[common], help="Run the autonomous E2E oracle for this instance.")
    test.add_argument("--suite", default="core", choices=["core", "all", "semantic", "resilience", "parity", "boundaries", "resources"])
    test.add_argument("--case", help="Run a single oracle case.")
    test.add_argument("--fail-on-advisory", action="store_true")

    search = sub.add_parser("search", parents=[common], help="Search the local Preview Index and optionally live web leads.")
    search.add_argument("query")
    search.add_argument("--mode", default="local", choices=["local", "live", "blended", "replay"])
    search.add_argument("--live", action="store_true", help="Use the configured live web provider.")
    search.add_argument("--index", default="local", choices=["none", "local", "preview"])
    search.add_argument("--provider", default="brave")
    search.add_argument("--page", type=int, default=0)
    search.add_argument("--count", type=int, default=10)
    search.add_argument("--freshness", default="")
    search.add_argument("--country", default="")
    search.add_argument("--language", default="")
    search.add_argument("--safe-search", default="moderate", choices=["off", "moderate", "strict"])
    search.add_argument("--timeout", type=int, default=10)

    hunt = sub.add_parser("hunt", parents=[common], help="Run a deterministic synthetic Hunt or opt-in live Hunt.")
    hunt.add_argument("query")
    hunt.add_argument("--mode", default="synthetic")
    hunt.add_argument("--live", action="store_true", help="Use transient live web search query variants.")
    hunt.add_argument("--max-queries", type=int, default=20)
    hunt.add_argument("--max-fetches", type=int, default=0)
    hunt.add_argument("--step", action="store_true")
    hunt.add_argument("--run-to-completion", action="store_true")
    hunt.add_argument("--fixture")

    replay = sub.add_parser("replay", parents=[common], help="Replay a durable run bundle.")
    replay.add_argument("run_id")
    replay.add_argument("--strict", action=argparse.BooleanOptionalAction, default=True)

    serve = sub.add_parser("serve", parents=[common], help="Serve the local exploration workspace on loopback.")
    serve.add_argument("--mode", default=DEFAULT_MODE)
    serve.add_argument("--host", default=DEFAULT_HOST)
    serve.add_argument("--port", type=int, default=DEFAULT_PORT)
    serve.add_argument("--operator-token")
    serve.add_argument("--smoke", action="store_true")
    serve.add_argument("--live", action="store_true", help="Serve the live-search first screen on loopback.")

    status = sub.add_parser("status", parents=[common], help="Summarize the portable local instance.")
    status.add_argument("--paths", action="store_true", help="Include local absolute path details.")

    index = sub.add_parser("index", parents=[common], help="Inspect local indexes.")
    index_sub = index.add_subparsers(dest="index_command", required=True)
    index_sub.add_parser("stats", parents=[common], help="Show local Preview Index stats.")
    return parser


def _ensure_common_defaults(args: argparse.Namespace) -> None:
    for name, value in (("instance", None), ("json", False), ("verbose", False), ("quiet", False)):
        if not hasattr(args, name):
            setattr(args, name, value)


def _search_mode(mode: str, *, live: bool) -> str:
    normalized = str(mode or "").strip().lower()
    if live and normalized in {"", "local"}:
        return "blended"
    if normalized in {"local", "live", "blended", "replay"}:
        return normalized
    raise PortableInstanceError("unsupported_search_mode", f"unsupported search mode: {mode}", exit_code=2)


def _search_portable_index(paths: PortablePaths, query: str, *, index: str, limit: int) -> dict[str, Any]:
    normalized = str(index or "local").strip().lower()
    if normalized not in {"local", "preview"}:
        return _local_index_disabled(index)
    if not paths.preview_current.is_file():
        return {
            "status": "absent",
            "index": normalized,
            "path": _relative_to_instance(paths.root, paths.preview_current),
            "result_count": 0,
            "results": [],
            "warnings": ["Local Preview Index is absent. Run bootstrap --with-demo for replay data or persist live observations in a later milestone."],
        }
    try:
        payload = search_preview_index(paths.preview_current, query, limit=max(1, min(int(limit or 10), 25)), include_synthetic=False)
    except Exception as exc:
        return {
            "status": "invalid",
            "index": normalized,
            "path": _relative_to_instance(paths.root, paths.preview_current),
            "result_count": 0,
            "results": [],
            "warnings": [f"Local Preview Index search failed: {type(exc).__name__}"],
        }
    cards = [_preview_result_card(item) for item in payload.get("results") or [] if isinstance(item, Mapping)]
    return {
        "status": "pass",
        "index": normalized,
        "path": _relative_to_instance(paths.root, paths.preview_current),
        "preview_index_id": str(payload.get("preview_index_id") or ""),
        "generation_id": str(payload.get("generation_id") or ""),
        "result_count": len(cards),
        "results": cards,
        "warnings": [],
    }


def _local_index_disabled(index: str) -> dict[str, Any]:
    return {
        "status": "disabled",
        "index": str(index or "none"),
        "path": "",
        "result_count": 0,
        "results": [],
        "warnings": [],
    }


def _preview_result_card(item: Mapping[str, Any]) -> dict[str, Any]:
    title = str(item.get("title") or item.get("normalized_title") or item.get("candidate_id") or item.get("preview_record_id") or "Indexed discovery")
    summary = str(item.get("summary") or item.get("non_verified_reason") or "Local Preview Index record.")
    return {
        "state": "INDEXED - UNREVIEWED" if item.get("review_state") != "reviewed" else "REVIEWED",
        "title": title,
        "url": str(item.get("url") or ""),
        "snippet": summary,
        "provider": str(item.get("source_family") or "local_preview_index"),
        "retrieved_at": str(item.get("created_at") or item.get("updated_at") or ""),
        "query": "",
        "source": "local_preview_index",
        "review_state": str(item.get("review_state") or "unreviewed"),
        "result_id": str(item.get("preview_record_id") or item.get("candidate_id") or item.get("id") or ""),
        "retention_policy": {
            "persist_urls": True,
            "persist_snippets": True,
            "persist_rank": False,
            "terms_basis": "local_preview_index",
        },
    }


def _live_hunt_command(
    query: str,
    *,
    root: Path,
    paths: PortablePaths,
    started_at: str,
    max_queries: int,
    max_fetches: int,
) -> dict[str, Any]:
    run_id = live_hunt_run_id(query, started_at)
    hunt = LiveSearchService().start_hunt(
        query,
        run_id=run_id,
        max_queries=max_queries,
        max_fetches=max_fetches,
        count=10,
        timeout_seconds=10,
    )
    response_payload = dict(hunt.response)
    errors = response_payload.get("errors") if isinstance(response_payload.get("errors"), list) else []
    first_error = errors[0] if errors and isinstance(errors[0], Mapping) else {}
    if response_payload.get("status") == "fail" and not response_payload.get("network_provider_calls") and first_error.get("code") == "live_provider_not_configured":
        return _result(
            "hunt",
            "fail",
            root,
            started_at=started_at,
            mutations=False,
            payload={
                **response_payload,
                "error": "live_provider_not_configured",
                "message": str(first_error.get("message") or "Live web search is not configured. Configure a provider or search the local index."),
            },
        )
    run_dir = paths.run_bundles / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    _write_json(run_dir / "summary.json", hunt.persisted_summary)
    return _result(
        "hunt",
        str(response_payload.get("status") or "fail"),
        root,
        started_at=started_at,
        mutations=True,
        payload={
            **response_payload,
            "run_directory": _relative_to_instance(root, run_dir),
            "review_or_truth_mutation": False,
            "public_index_mutation": False,
            "reviewed_master_mutation": False,
            "warnings": [
                "Live Hunt currently searches provider query variants only; safe fetch, extraction, and persistence remain later milestones.",
                "Provider SearchLeads are display-only transient state and are not written to the run summary.",
            ],
        },
    )


def _reject_forbidden_instance_root(root: Path) -> None:
    resolved = root.resolve()
    repo = REPO_ROOT.resolve()
    if resolved == repo:
        raise PortableInstanceError("repo_root_instance_forbidden", "repository root may not be used as a local instance", exit_code=2)
    try:
        relative = resolved.relative_to(repo)
    except ValueError:
        relative = None
    if relative is not None:
        parts = tuple(part.casefold() for part in relative.parts)
        if parts[:1] in {(part,) for part in FORBIDDEN_INSTANCE_PARTS} or parts[:2] in FORBIDDEN_INSTANCE_RELATIVE:
            raise PortableInstanceError("repo_product_path_instance_forbidden", "product roots may not be used as local instance roots", exit_code=2)
    if resolved == Path.home().resolve() or any(part.startswith(".") and part not in {".", ".."} for part in resolved.parts):
        raise PortableInstanceError("hidden_or_home_instance_forbidden", "hidden or home-root instance paths are forbidden", exit_code=2)


def _instance_child(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise PortableInstanceError("instance_path_escape", f"portable path escapes instance root: {relative}", exit_code=2) from exc
    return path


def _ensure_portable_dirs(paths: PortablePaths) -> None:
    for path in (
        paths.config_dir,
        paths.run_bundles,
        paths.preview_index,
        paths.eval_root,
        paths.portable_status_dir,
        paths.tmp_root,
        paths.logs_dir,
        paths.backup_root,
    ):
        path.mkdir(parents=True, exist_ok=True)


def _portable_profile(root: Path, instance_id: str, created_at: str, updated_at: str) -> dict[str, Any]:
    return {
        "schema_version": PORTABLE_PROFILE_SCHEMA_VERSION,
        "portable_profile_version": PORTABLE_PROFILE_VERSION,
        "instance_id": instance_id,
        "instance_schema_version": CURRENT_INSTANCE_SCHEMA_VERSION,
        "instance_root": str(root),
        "created_at": created_at,
        "updated_at": updated_at,
        "mode": DEFAULT_MODE,
        "host_default": DEFAULT_HOST,
        "port_default": DEFAULT_PORT,
        "live_providers_enabled": False,
        "public_exposure_enabled": False,
        "public_alpha_enabled": False,
        "downloads_enabled": False,
        "execution_enabled": False,
        "telemetry_enabled": False,
        "account_cloud_sync_enabled": False,
        "paths": _profile_paths(root),
        "limitations": _limitations(),
        "non_claims": [
            "not a public service",
            "not production readiness",
            "not reviewed IA truth",
            "not a downloader or executor",
            "not a cloud-synced instance",
        ],
    }


def _profile_paths(root: Path) -> dict[str, str]:
    paths = build_portable_paths(root)
    return {
        "run_bundles": "run/e2e-reference/runs",
        "preview_index": "db/e2e-reference/preview-index",
        "oracle_results": "run/e2e-reference/eval",
        "portable_status": "run/e2e-reference/portable-instance/status.json",
        "logs": "logs/eureka-portable.log",
        "temporary_files": "tmp/e2e-reference",
        "exports": "exports",
        "backup_root": "exports/backups",
        "server_state": _relative_to_instance(root, paths.server_state),
        "server_lock": _relative_to_instance(root, paths.server_lock),
    }


def _create_demo_run(paths: PortablePaths) -> dict[str, Any]:
    result = run_e2e_reference_run(
        "portable Eureka local demo",
        mode="synthetic",
        projection_profile="operator_workbench",
        out_root=paths.run_bundles,
        write_bundle=True,
        include_ia_hunt=False,
        scheduler_kind="synthetic_fixture",
    )
    return result


def _write_portable_status(paths: PortablePaths, *, command: str, status: str, profile: Mapping[str, Any], extra: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "schema_version": PORTABLE_STATUS_SCHEMA_VERSION,
        "status": status,
        "command": command,
        "updated_at": _now(),
        "instance_id": profile.get("instance_id", ""),
        "instance_schema_version": profile.get("instance_schema_version"),
        "profile_path": _relative_to_instance(paths.root, paths.profile),
        "preview_index": _current_preview_status(paths),
        "run_bundles": _run_bundle_status(paths),
        "provider_network_calls": False,
        "public_exposure": False,
        "reviewed_truth_created": False,
        "details": dict(extra or {}),
    }
    _write_json(paths.portable_status, payload)
    return payload


def _current_preview_status(paths: PortablePaths) -> dict[str, Any]:
    if not paths.preview_current.exists():
        return {"status": "absent", "current_path": _relative_to_instance(paths.root, paths.preview_current), "record_count": 0, "warnings": ["Preview Index has not been bootstrapped yet."]}
    try:
        validation = validate_preview_index(paths.preview_current, strict=True)
        stats = preview_stats_payload(paths.preview_current)
        return {"status": "pass" if validation.get("status") == "pass" else "invalid", "validation": validation, **stats}
    except Exception as exc:
        return {"status": "invalid", "error": str(exc), "current_path": _relative_to_instance(paths.root, paths.preview_current)}


def _preview_for_query(paths: PortablePaths, query: str) -> dict[str, Any]:
    if not paths.preview_current.exists():
        return {"status": "absent", "result_count": 0, "lane_counts": {}, "warnings": ["Preview Index absent."]}
    try:
        return search_preview_index(paths.preview_current, query, limit=10, include_synthetic=True)
    except PreviewIndexError as exc:
        return {"status": "invalid", "result_count": 0, "lane_counts": {}, "warnings": [str(exc)]}


def _run_bundle_status(paths: PortablePaths) -> dict[str, Any]:
    valid = 0
    corrupt = 0
    latest = ""
    run_ids: list[str] = []
    if not paths.run_bundles.exists():
        return {"status": "absent", "total": 0, "valid": 0, "corrupt": 0, "latest": ""}
    for child in sorted((item for item in paths.run_bundles.iterdir() if item.is_dir()), key=lambda item: item.stat().st_mtime, reverse=True):
        if not (child / "run_manifest.json").is_file():
            continue
        report = validate_run_bundle(child, strict=True, write_report=False)
        if report.get("status") == "valid":
            valid += 1
        else:
            corrupt += 1
        run_ids.append(child.name)
        latest = latest or child.name
    return {"status": "pass" if corrupt == 0 else "degraded", "total": len(run_ids), "valid": valid, "corrupt": corrupt, "latest": latest, "run_ids": run_ids[:10]}


def _latest_oracle_status(paths: PortablePaths) -> dict[str, Any]:
    if not paths.eval_root.exists():
        return {"status": "absent"}
    candidates = sorted((path for path in paths.eval_root.iterdir() if path.is_dir() and (path / "summary.json").is_file()), key=lambda item: item.stat().st_mtime, reverse=True)
    if not candidates:
        return {"status": "absent"}
    summary = _load_json(candidates[0] / "summary.json")
    return {
        "status": "pass" if summary.get("overall_gate_status") == "PASS" else "degraded",
        "execution_id": summary.get("execution_id", candidates[0].name),
        "overall_gate_status": summary.get("overall_gate_status", ""),
        "case_count": summary.get("case_count", 0),
        "path": _relative_to_instance(paths.root, candidates[0]),
    }


def _safe_run_dir(paths: PortablePaths, run_id: str) -> Path:
    value = str(run_id or "").strip()
    if not value or not RUN_ID_PATTERN.match(value) or "/" in value or "\\" in value:
        raise PortableInstanceError("invalid_run_id", "run ID must be a direct bundle child name", exit_code=2)
    run_dir = (paths.run_bundles / value).resolve()
    try:
        run_dir.relative_to(paths.run_bundles.resolve())
    except ValueError as exc:
        raise PortableInstanceError("run_path_escape", "run ID escapes the run bundle root", exit_code=2) from exc
    if not (run_dir / "run_manifest.json").is_file():
        raise PortableInstanceError("run_bundle_missing", f"run bundle not found: {value}", exit_code=1)
    return run_dir


def _oracle_run_root(paths: PortablePaths, execution_id: str) -> Path:
    if not execution_id:
        raise PortableInstanceError("oracle_run_missing", "oracle did not return an execution id", exit_code=1)
    path = (paths.eval_root / execution_id).resolve()
    try:
        path.relative_to(paths.eval_root.resolve())
    except ValueError as exc:
        raise PortableInstanceError("oracle_path_escape", "oracle execution path escapes eval root", exit_code=1) from exc
    if not (path / "summary.json").is_file():
        raise PortableInstanceError("oracle_run_missing", f"oracle summary missing for {execution_id}", exit_code=1)
    return path


def _require_initialized(paths: PortablePaths) -> None:
    if not paths.root.exists():
        raise PortableInstanceError("bootstrap_required", f"Instance root does not exist: {paths.root}", exit_code=2)
    if not (paths.root / "config" / "instance.json").is_file():
        raise PortableInstanceError("bootstrap_required", f"Instance manifest is missing: {paths.root}", exit_code=2)
    validation = validate_local_instance(paths.root)
    if validation.get("status") not in {"pass", "pass_with_warnings"}:
        raise PortableInstanceError("instance_validation_failed", "; ".join(validation.get("errors", [])), exit_code=1, details={"validation": validation})


def _route_registration_check(root: Path) -> dict[str, Any]:
    paths = build_portable_paths(root)
    try:
        payload = build_explore_workspace("", options=E2EExploreOptions(preview_index_path=paths.preview_current, runs_root=paths.run_bundles), include_synthetic=True)
        return {"status": "pass", "endpoint": "explore_workspace", "schema_version": payload.get("schema_version", "")}
    except Exception as exc:
        return {"status": "fail", "error": str(exc)}


def _configure_runtime_for_portable(runtime: Any, paths: PortablePaths, *, live: bool = False) -> None:
    setattr(runtime, "e2e_explore_preview_index_path", paths.preview_current)
    setattr(runtime, "e2e_explore_runs_root", paths.run_bundles)
    setattr(runtime, "e2e_explore_default_fixture", "success_two_workunits")
    setattr(runtime, "e2e_explore_include_synthetic", not live)
    setattr(runtime, "public_alpha_enabled", False)
    setattr(runtime, "public_exposure_enabled", False)
    setattr(runtime, "live_providers_enabled", bool(live))
    setattr(runtime, "live_search_enabled", bool(live))
    setattr(runtime, "live_search_provider", "brave")


def _serve_smoke(paths: PortablePaths, *, host: str, port: int, mode: str, token: str, live: bool = False) -> dict[str, Any]:
    started: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=1)

    def _target() -> None:
        handle = None
        try:
            handle = create_local_http_server(paths.root, host=host, port=port, read_only=False, operator_token=token, bind_lan=False)
            _configure_runtime_for_portable(handle.runtime, paths, live=live)
            state = _write_server_state(paths, host=host, port=handle.server_port, mode="live" if live else mode)
            started.put({"status": "pass", "handle": handle, "port": handle.server_port, "server_state": state})
            handle.httpd.serve_forever()
        except Exception as exc:  # pragma: no cover - defensive thread boundary
            started.put({"status": "fail", "error": str(exc)})
        finally:
            if handle is not None:
                handle.close()
            _remove_server_state(paths)

    thread = threading.Thread(target=_target, daemon=True)
    thread.start()
    try:
        boot = started.get(timeout=10)
    except queue.Empty as exc:
        raise PortableInstanceError("server_smoke_start_timeout", "portable smoke server did not start", exit_code=1) from exc
    if boot.get("status") != "pass":
        raise PortableInstanceError("server_smoke_start_failed", str(boot.get("error", "server start failed")), exit_code=1)
    handle = boot["handle"]
    try:
        smoke = _smoke_server(host, int(boot["port"]), live=live)
    finally:
        handle.shutdown()
        thread.join(timeout=10)
        _remove_server_state(paths)
    return {"port": int(boot["port"]), "server_state": dict(boot.get("server_state") or {}), "smoke": smoke}


def _write_server_state(paths: PortablePaths, *, host: str, port: int, mode: str) -> dict[str, Any]:
    state = {
        "schema_version": "eureka.portable_server_state.v0",
        "pid": os.getpid(),
        "host": host,
        "port": port,
        "mode": mode,
        "instance_id": _load_json(paths.root / "config" / "instance.json").get("instance_id", ""),
        "started_at": _now(),
        "operator_token_persisted": False,
        "public_exposure": False,
    }
    _write_json(paths.server_state, state)
    _atomic_write_text(paths.server_lock, json.dumps({"pid": os.getpid(), "created_at": state["started_at"]}, sort_keys=True) + "\n")
    return state


def _remove_server_state(paths: PortablePaths) -> None:
    for path in (paths.server_state, paths.server_lock):
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def _server_lock_status(paths: PortablePaths) -> dict[str, Any]:
    if not paths.server_lock.exists():
        return {"status": "pass", "state": "stopped", "lock_path": _relative_to_instance(paths.root, paths.server_lock)}
    payload = _load_json_optional(paths.server_lock)
    pid = int(payload.get("pid", 0) or 0) if isinstance(payload, Mapping) else 0
    alive = _pid_alive(pid)
    state = "running" if alive else "stale"
    extra: dict[str, Any] = {}
    if paths.server_state.exists():
        extra["server_state"] = _load_json_optional(paths.server_state)
    return {"status": "warning" if state == "stale" else "running", "state": state, "pid": pid, "lock_path": _relative_to_instance(paths.root, paths.server_lock), **extra}


def _smoke_server(host: str, port: int, *, live: bool = False) -> dict[str, Any]:
    if live:
        endpoints = (
            {"endpoint": "/health", "statuses": {200}, "contains": ("\"status\"",), "follow_redirects": True},
            {
                "endpoint": "/",
                "statuses": {200},
                "contains": ("Eureka", "Search", "Hunt deeper"),
                "forbidden": ("review packet", "architecture", "workunit"),
                "follow_redirects": True,
            },
            {
                "endpoint": "/api/search",
                "statuses": {200},
                "contains": ("live_web_search_response", "Enter a query"),
                "follow_redirects": True,
            },
        )
    else:
        endpoints = (
            {"endpoint": "/health", "statuses": {200}, "contains": ("\"status\"",), "follow_redirects": True},
            {"endpoint": "/", "statuses": {302}, "location": "/explore", "contains": (), "follow_redirects": False},
            {
                "endpoint": "/explore",
                "statuses": {200},
                "contains": ("What are you looking for?", "Example Searches", "Searching...", "Blocked Here"),
                "forbidden": ("json", "audit", "architecture", "preview index", "e2e reference", "workunit", "run_id", "EUREKA-FIRST-RUN"),
                "follow_redirects": True,
            },
            {
                "endpoint": "/explore?q=old%20blue%20FTP%20client%20for%20XP",
                "statuses": {200},
                "contains": ("Results Found", "Start Hunt", "A Hunt is a local investigation"),
                "forbidden": ("json", "audit", "architecture", "preview index", "e2e reference", "workunit", "run_id", "EUREKA-FIRST-RUN"),
                "follow_redirects": True,
            },
            {
                "endpoint": "/explore?q=zzzxqvblorp",
                "statuses": {200},
                "contains": ("No Local Matches Yet", "Start Hunt", "Blocked Here"),
                "forbidden": ("json", "audit", "architecture", "preview index", "e2e reference", "workunit", "run_id", "EUREKA-FIRST-RUN"),
                "follow_redirects": True,
            },
        )
    results = []
    errors = []
    base = f"http://{host}:{port}"
    deadline = time.time() + 10
    for check in endpoints:
        endpoint = str(check["endpoint"])
        last_error = ""
        while time.time() < deadline:
            try:
                probe = _http_get(base + endpoint, follow_redirects=bool(check.get("follow_redirects", True)))
                ok, failures = _smoke_check(probe, check)
                results.append({"endpoint": endpoint, "status_code": probe["status_code"], "ok": ok, "failures": failures, "body_sample": probe["body"][:240]})
                break
            except (OSError, URLError) as exc:
                last_error = str(exc)
                time.sleep(0.1)
        else:
            errors.append({"endpoint": endpoint, "error": last_error or "timeout"})
    return {"schema_version": "eureka.portable_server_smoke.v0", "status": "pass" if not errors and all(item["ok"] for item in results) else "fail", "endpoints": results, "errors": errors, "loopback_only": True}


def _http_get(url: str, *, follow_redirects: bool) -> dict[str, Any]:
    request = Request(url, method="GET")
    opener = build_opener() if follow_redirects else build_opener(_NoRedirectHandler)
    try:
        with opener.open(request, timeout=2) as response:  # noqa: S310 - bounded loopback smoke only
            body = response.read(65536).decode("utf-8", errors="replace")
            return {"status_code": int(response.status), "headers": dict(response.headers.items()), "body": body}
    except HTTPError as exc:
        if 300 <= exc.code < 400 and not follow_redirects:
            body = exc.read(65536).decode("utf-8", errors="replace")
            return {"status_code": int(exc.code), "headers": dict(exc.headers.items()), "body": body}
        raise


def _smoke_check(probe: Mapping[str, Any], check: Mapping[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    status_code = int(probe.get("status_code", 0) or 0)
    expected_statuses = {int(item) for item in check.get("statuses", {200})}
    if status_code not in expected_statuses:
        failures.append(f"expected status {sorted(expected_statuses)}, got {status_code}")
    headers = {str(key).lower(): str(value) for key, value in dict(probe.get("headers") or {}).items()}
    if check.get("location") and headers.get("location") != check.get("location"):
        failures.append(f"expected Location {check.get('location')}, got {headers.get('location', '')}")
    body = str(probe.get("body") or "")
    body_lower = body.lower()
    for needle in check.get("contains", ()):
        if str(needle).lower() not in body_lower:
            failures.append(f"missing body text: {needle}")
    for needle in check.get("forbidden", ()):
        if str(needle).lower() in body_lower:
            failures.append(f"forbidden first-use text: {needle}")
    return not failures, failures


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


def _backup_status(paths: PortablePaths) -> dict[str, Any]:
    paths.backup_root.mkdir(parents=True, exist_ok=True) if paths.root.exists() else None
    backups = sorted((item for item in paths.backup_root.iterdir() if item.exists()), key=lambda item: item.stat().st_mtime, reverse=True) if paths.backup_root.exists() else []
    latest = datetime.fromtimestamp(backups[0].stat().st_mtime, timezone.utc).isoformat().replace("+00:00", "Z") if backups else ""
    return {"status": "present" if paths.backup_root.exists() else "absent", "backup_root": _relative_to_instance(paths.root, paths.backup_root), "backup_count": len(backups), "latest_backup_timestamp": latest, "automatic_cloud_backup": False}


def _disk_space(root: Path) -> dict[str, Any]:
    try:
        usage = shutil.disk_usage(root if root.exists() else root.parent)
        free_mb = usage.free // (1024 * 1024)
        return {"status": "pass" if free_mb > 256 else "warning", "free_mb": free_mb, "message": "less than 256 MiB free" if free_mb <= 256 else ""}
    except Exception as exc:
        return {"status": "unknown", "message": str(exc)}


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        try:
            return _pid_alive_windows(pid)
        except (OSError, SystemError):
            return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False
    except SystemError:
        return False


def _pid_alive_windows(pid: int) -> bool:
    import ctypes

    error_access_denied = 5
    process_query_limited_information = 0x1000
    still_active = 259

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
    kernel32.OpenProcess.restype = ctypes.c_void_p
    kernel32.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
    kernel32.GetExitCodeProcess.restype = ctypes.c_int
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.CloseHandle.restype = ctypes.c_int

    handle = kernel32.OpenProcess(process_query_limited_information, 0, pid)
    if not handle:
        return ctypes.get_last_error() == error_access_denied
    try:
        exit_code = ctypes.c_ulong()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return True
        return exit_code.value == still_active
    finally:
        kernel32.CloseHandle(handle)


def _result(command: str, status: str, instance_root: Path, *, started_at: str, mutations: bool, payload: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result.update(
        {
        "schema_version": PORTABLE_RESULT_SCHEMA_VERSION,
        "command": command,
        "status": status,
        "instance_root": str(instance_root),
        "instance_root_posture": "explicit_local_private",
        "started_at": started_at,
        "completed_at": _now(),
        "mutations_performed": bool(mutations),
        "network_provider_calls": bool(payload.get("network_provider_calls", False)),
        "model_provider_calls": bool(payload.get("model_provider_calls", False)),
        "public_exposure": False,
        "reviewed_master_mutation": bool(payload.get("reviewed_master_mutation", False)),
        "public_index_mutation": bool(payload.get("public_index_mutation", False)),
        "production_truth_mutation": bool(payload.get("production_truth_mutation", False)),
        "warnings": list(payload.get("warnings", [])) if isinstance(payload.get("warnings"), list) else [],
        "limitations": _limitations(),
        }
    )
    return result


def _error_payload(exc: PortableInstanceError, root: Path | None) -> dict[str, Any]:
    return {
        "schema_version": PORTABLE_RESULT_SCHEMA_VERSION,
        "command": "error",
        "status": "fail",
        "error": exc.code,
        "message": exc.message,
        "instance_root": str(root) if root else "",
        "details": exc.details,
        "network_provider_calls": False,
        "public_exposure": False,
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "production_truth_mutation": False,
    }


def _emit_result(payload: Mapping[str, Any], *, json_output: bool, stdout: TextIO) -> int:
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print(_text_summary(payload), file=stdout)
    status = str(payload.get("status", "fail"))
    if status in {"pass", "pass_with_warnings"}:
        return 0
    if str(payload.get("error", "")).endswith("forbidden") or payload.get("error") in {
        "unsupported_command",
        "query_required",
        "query_too_long",
        "invalid_run_id",
        "live_mode_forbidden",
        "unsupported_search_mode",
        "live_provider_not_configured",
    }:
        return 2
    return 1


def _text_summary(payload: Mapping[str, Any]) -> str:
    lines = [f"status: {payload.get('status', '')}", f"command: {payload.get('command', '')}"]
    if payload.get("instance_root"):
        lines.append(f"instance: {payload.get('instance_root')}")
    for key in ("run_id", "state", "result_path", "recommended_next_command"):
        if payload.get(key):
            lines.append(f"{key}: {payload.get(key)}")
    if payload.get("error"):
        lines.append(f"error: {payload.get('error')}")
        lines.append(f"message: {payload.get('message')}")
    if payload.get("next_commands"):
        lines.append("next:")
        lines.extend(f"- {item}" for item in payload["next_commands"])
    if payload.get("results"):
        lines.append("results:")
        for index, item in enumerate(payload.get("results") or [], start=1):
            if not isinstance(item, Mapping):
                continue
            state = str(item.get("state") or "")
            title = str(item.get("title") or item.get("url") or "result")
            url = str(item.get("url") or "")
            snippet = str(item.get("snippet") or "")
            provider = str(item.get("provider") or "")
            retrieved_at = str(item.get("retrieved_at") or "")
            lines.append(f"{index}. {state} {title}".rstrip())
            if url:
                lines.append(f"   {url}")
            if snippet:
                lines.append(f"   {snippet}")
            if provider or retrieved_at:
                lines.append(f"   provider: {provider or 'local'} retrieved_at: {retrieved_at or 'n/a'}")
    return "\n".join(lines)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    _atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
        handle.write(text)
        temp = Path(handle.name)
    temp.replace(path)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_json_optional(path: Path) -> dict[str, Any]:
    try:
        return _load_json(path)
    except Exception:
        return {}


def _relative_to_instance(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _limitations() -> list[str]:
    return [
        "Python source checkout portability only.",
        "Loopback-only exploration service.",
        "Synthetic replay Hunts remain available only in explicit replay/demo paths.",
        "Live providers require explicit --live flags and local credentials.",
        "No downloads, public exposure, or production truth mutation.",
        "Backups are documented filesystem copies in v0.",
    ]


def _next_commands(root: Path) -> list[str]:
    base = f"python scripts/eureka.py --instance {root}"
    return [f"{base} doctor", f"{base} test", f"{base} hunt \"old blue FTP client for XP\"", f"{base} serve --mode exploration"]


def _recommended_after_doctor(status: str, root: Path) -> str:
    if status == "fail":
        return f"python scripts/eureka.py --instance {root} bootstrap"
    return f"python scripts/eureka.py --instance {root} test"


def _recommended_status_next(preview: Mapping[str, Any], runs: Mapping[str, Any], root: Path) -> str:
    if preview.get("status") in {"absent", "invalid"}:
        return f"python scripts/eureka.py --instance {root} bootstrap"
    if int(runs.get("total", 0) or 0) == 0:
        return f"python scripts/eureka.py --instance {root} hunt \"old blue FTP client for XP\""
    return f"python scripts/eureka.py --instance {root} serve --mode exploration"


def _issue(code: str, explanation: str, remediation: str, *, data_risk: bool, service_blocked: bool) -> dict[str, Any]:
    return {"code": code, "explanation": explanation, "remediation_command": remediation, "data_at_risk": data_risk, "service_start_blocked": service_blocked}


def _compact_init(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {"status": payload.get("status"), "instance_id": payload.get("instance_id"), "instance_schema_version": payload.get("instance_schema_version"), "store_count": len(payload.get("stores", {}) or {})}


def _compact_validation(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {"status": payload.get("status"), "migration_needed": payload.get("migration_needed", False), "errors": list(payload.get("errors", [])), "warnings": list(payload.get("warnings", []))}


def _compact_demo(payload: Mapping[str, Any]) -> dict[str, Any]:
    created = bool(payload.get("created", bool(payload.get("run_id"))))
    return {"created": created, "run_id": payload.get("run_id", ""), "result_count": payload.get("result_count", 0), "event_count": payload.get("event_count", 0), "synthetic": created}


def _compact_preview(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not payload or payload.get("created") is False:
        return {"created": False}
    return {"created": True, "status": payload.get("status", ""), "generation_id": payload.get("generation_id", ""), "record_count": payload.get("record_count", 0), "current_path": payload.get("current_path", "")}


def _compact_oracle(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "overall_gate_status": payload.get("overall_gate_status", ""),
        "execution_id": payload.get("execution_id", ""),
        "case_count": payload.get("case_count", 0),
        "critical_failures": payload.get("critical_failures", 0),
        "required_failures": payload.get("required_failures", 0),
        "advisory_warnings": payload.get("advisory_warnings", 0),
        "network_provider_calls": payload.get("network_provider_calls", False),
        "model_calls": payload.get("model_calls", False),
    }


def _profile_status(paths: PortablePaths) -> dict[str, Any]:
    if not paths.profile.exists():
        return {"status": "absent", "path": _relative_to_instance(paths.root, paths.profile)}
    payload = _load_json_optional(paths.profile)
    status = "pass" if payload.get("schema_version") == PORTABLE_PROFILE_SCHEMA_VERSION else "invalid"
    return {"status": status, "path": _relative_to_instance(paths.root, paths.profile), "schema_version": payload.get("schema_version", "")}
