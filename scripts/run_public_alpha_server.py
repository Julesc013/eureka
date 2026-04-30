from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence, TextIO
from urllib.parse import quote
from wsgiref.simple_server import make_server


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.gateway.public_api import (  # noqa: E402
    build_demo_absence_public_api,
    build_demo_action_plan_public_api,
    build_demo_archive_resolution_evals_public_api,
    build_demo_comparison_public_api,
    build_demo_compatibility_public_api,
    build_demo_decomposition_public_api,
    build_demo_public_search_public_api,
    build_demo_query_planner_public_api,
    build_demo_representation_selection_public_api,
    build_demo_representations_public_api,
    build_demo_resolution_actions_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
    build_demo_source_registry_public_api,
    build_demo_subject_states_public_api,
)
from surfaces.web.server import (  # noqa: E402
    PublicAlphaWrapperConfig,
    WorkbenchWsgiApp,
    load_public_alpha_wrapper_config,
)


DEFAULT_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run Eureka's stdlib web/API backend through the public-alpha wrapper.",
    )
    parser.add_argument("--host", help="Bind host. Defaults to EUREKA_BIND_HOST or 127.0.0.1.")
    parser.add_argument("--port", type=int, help="Bind port. Defaults to EUREKA_PORT or 8781.")
    parser.add_argument(
        "--mode",
        help="Wrapper mode. Only public_alpha is accepted by this entrypoint.",
    )
    parser.add_argument(
        "--allow-nonlocal-bind",
        action="store_true",
        default=None,
        help="Allow binding outside localhost. This is not deployment approval.",
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Validate wrapper configuration and exit without starting a server.",
    )
    parser.add_argument(
        "--print-config-json",
        action="store_true",
        help="Print JSON-safe wrapper configuration and exit without starting a server.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    output = stdout or sys.stdout

    try:
        config = load_public_alpha_wrapper_config(
            mode=args.mode,
            host=args.host,
            port=args.port,
            allow_nonlocal_bind=args.allow_nonlocal_bind,
        )
    except ValueError as error:
        output.write(f"Invalid public-alpha wrapper configuration: {error}\n")
        return 2

    summary = config.to_summary_dict()
    if args.print_config_json:
        output.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        return 0 if summary["status"] == "valid" else 2

    if args.check_config:
        output.write(format_config_check(summary))
        return 0 if summary["status"] == "valid" else 2

    if summary["status"] != "valid":
        output.write(format_config_check(summary))
        return 2

    app = build_public_alpha_wsgi_app(config)
    output.write(format_startup_summary(summary))
    output.flush()
    with make_server(config.host, config.port, app) as httpd:
        httpd.serve_forever()
    return 0


def build_public_alpha_wsgi_app(config: PublicAlphaWrapperConfig) -> WorkbenchWsgiApp:
    return WorkbenchWsgiApp(
        build_demo_resolution_jobs_public_api(),
        absence_public_api=build_demo_absence_public_api(),
        action_plan_public_api=build_demo_action_plan_public_api(),
        actions_public_api=build_demo_resolution_actions_public_api(),
        archive_resolution_evals_public_api=build_demo_archive_resolution_evals_public_api(),
        comparison_public_api=build_demo_comparison_public_api(),
        compatibility_public_api=build_demo_compatibility_public_api(),
        decomposition_public_api=build_demo_decomposition_public_api(),
        handoff_public_api=build_demo_representation_selection_public_api(),
        query_planner_public_api=build_demo_query_planner_public_api(),
        representations_public_api=build_demo_representations_public_api(),
        search_public_api=build_demo_search_public_api(),
        public_search_public_api=build_demo_public_search_public_api(),
        source_registry_public_api=build_demo_source_registry_public_api(),
        subject_states_public_api=build_demo_subject_states_public_api(),
        default_target_ref=DEFAULT_TARGET_REF,
        server_config=config.to_web_server_config(),
    )


def format_config_check(summary: dict[str, object]) -> str:
    lines = [
        "Public Alpha Wrapper Config",
        f"status: {summary['status']}",
        f"mode: {summary['mode']}",
        f"bind: {summary['host']}:{summary['port']} ({summary['bind_scope']})",
        f"live_probes_enabled: {summary['live_probes_enabled']}",
        f"live_internet_archive_enabled: {summary['live_internet_archive_enabled']}",
        f"downloads_enabled: {summary['downloads_enabled']}",
        f"local_paths_enabled: {summary['local_paths_enabled']}",
        f"user_storage_enabled: {summary['user_storage_enabled']}",
        f"deployment_approved: {summary['deployment_approved']}",
        f"production_ready: {summary['production_ready']}",
    ]
    errors = summary.get("errors")
    if isinstance(errors, list) and errors:
        lines.extend(["", "Errors"])
        lines.extend(f"- {item}" for item in errors)
    warnings = summary.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.extend(["", "Warnings"])
        lines.extend(f"- {item}" for item in warnings)
    lines.append("")
    return "\n".join(lines)


def format_startup_summary(summary: dict[str, object]) -> str:
    return "\n".join(
        [
            "Eureka public-alpha wrapper starting",
            f"bind: http://{summary['host']}:{summary['port']}/",
            f"status: http://{summary['host']}:{summary['port']}/status",
            f"api_status: http://{summary['host']}:{summary['port']}/api/status",
            f"demo_query: http://{summary['host']}:{summary['port']}/search?q={quote('Windows 7 apps', safe='')}",
            "mode: public_alpha",
            "live_probes_enabled: False",
            "live_internet_archive_enabled: False",
            "downloads_enabled: False",
            "local_paths_enabled: False",
            "user_storage_enabled: False",
            "deployment_approved: False",
            "production_ready: False",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
