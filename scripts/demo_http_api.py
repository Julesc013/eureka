from __future__ import annotations

import argparse
from contextlib import contextmanager
from pathlib import Path
import sys
from threading import Thread
from typing import Iterator
from urllib.parse import quote, urlencode
from urllib.request import HTTPError, urlopen
from wsgiref.simple_server import WSGIRequestHandler, make_server


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.gateway.public_api import (
    build_demo_acquisition_public_api,
    build_demo_action_plan_public_api,
    build_demo_archive_resolution_evals_public_api,
    build_demo_absence_public_api,
    build_demo_comparison_public_api,
    build_demo_compatibility_public_api,
    build_demo_decomposition_public_api,
    build_demo_local_index_public_api,
    build_demo_member_access_public_api,
    build_demo_public_search_public_api,
    build_demo_query_planner_public_api,
    build_demo_representation_selection_public_api,
    build_demo_resolution_actions_public_api,
    build_demo_resolution_bundle_inspection_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_representations_public_api,
    build_demo_search_public_api,
    build_demo_source_registry_public_api,
    build_demo_subject_states_public_api,
)
from surfaces.web.server import WebServerConfig, WorkbenchWsgiApp

DEFAULT_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"


class _SilentRequestHandler(WSGIRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch Eureka's local bootstrap HTTP API routes with stdlib-only tooling.",
    )
    parser.add_argument(
        "--base-url",
        help="Base URL for an already-running Eureka local server. If omitted, this script starts a temporary local server.",
    )
    parser.add_argument(
        "--mode",
        choices=("local_dev", "public_alpha"),
        help="Mode for the temporary local server when --base-url is omitted.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("index", help="Fetch the HTTP API index document.")
    subparsers.add_parser("status", help="Fetch the HTTP API safe-mode status document.")

    resolve_parser = subparsers.add_parser("resolve", help="Fetch machine-readable exact resolution.")
    resolve_parser.add_argument(
        "target_ref",
        nargs="?",
        default=DEFAULT_TARGET_REF,
    )
    resolve_parser.add_argument("--store-root")

    search_parser = subparsers.add_parser("search", help="Fetch deterministic machine-readable search results.")
    search_parser.add_argument("query")

    query_plan_parser = subparsers.add_parser(
        "query-plan",
        help="Fetch a machine-readable deterministic query plan.",
    )
    query_plan_parser.add_argument("query")

    public_search_parser = subparsers.add_parser(
        "public-search",
        help="Fetch governed local-index-only public search results.",
    )
    public_search_parser.add_argument("query")
    public_search_parser.add_argument("--limit", type=int)

    public_query_plan_parser = subparsers.add_parser(
        "public-query-plan",
        help="Fetch the governed public-search query-plan envelope.",
    )
    public_query_plan_parser.add_argument("query")

    subparsers.add_parser("public-status", help="Fetch governed public-search status.")
    subparsers.add_parser("public-sources", help="Fetch governed public-search source summaries.")

    public_source_parser = subparsers.add_parser(
        "public-source",
        help="Fetch one governed public-search source summary.",
    )
    public_source_parser.add_argument("source_id")

    index_build_parser = subparsers.add_parser(
        "index-build",
        help="Build or replace the bootstrap local SQLite index and return machine-readable status.",
    )
    index_build_parser.add_argument("--index-path", required=True)

    index_status_parser = subparsers.add_parser(
        "index-status",
        help="Fetch machine-readable bootstrap local index metadata.",
    )
    index_status_parser.add_argument("--index-path", required=True)

    index_query_parser = subparsers.add_parser(
        "index-query",
        help="Query the bootstrap local SQLite index and return machine-readable results.",
    )
    index_query_parser.add_argument("query")
    index_query_parser.add_argument("--index-path", required=True)

    tasks_parser = subparsers.add_parser(
        "tasks",
        help="Fetch machine-readable synchronous bootstrap local-task listings.",
    )
    tasks_parser.add_argument("--task-store-root", required=True)

    task_parser = subparsers.add_parser(
        "task",
        help="Fetch one machine-readable synchronous bootstrap local task by id.",
    )
    task_parser.add_argument("task_id")
    task_parser.add_argument("--task-store-root", required=True)

    task_validate_sources_parser = subparsers.add_parser(
        "task-run-validate-source-registry",
        help="Run one machine-readable synchronous bootstrap source-registry validation task.",
    )
    task_validate_sources_parser.add_argument("--task-store-root", required=True)

    task_build_index_parser = subparsers.add_parser(
        "task-run-build-local-index",
        help="Run one machine-readable synchronous bootstrap local-index build task.",
    )
    task_build_index_parser.add_argument("--task-store-root", required=True)
    task_build_index_parser.add_argument("--index-path", required=True)

    task_query_index_parser = subparsers.add_parser(
        "task-run-query-local-index",
        help="Run one machine-readable synchronous bootstrap local-index query task.",
    )
    task_query_index_parser.add_argument("--task-store-root", required=True)
    task_query_index_parser.add_argument("--index-path", required=True)
    task_query_index_parser.add_argument("--query", required=True)

    task_validate_evals_parser = subparsers.add_parser(
        "task-run-validate-archive-resolution-evals",
        help="Run one machine-readable synchronous bootstrap archive-resolution eval validation task.",
    )
    task_validate_evals_parser.add_argument("--task-store-root", required=True)

    runs_parser = subparsers.add_parser(
        "runs",
        help="Fetch machine-readable synchronous bootstrap resolution-run listings.",
    )
    runs_parser.add_argument("--run-store-root", required=True)

    memories_parser = subparsers.add_parser(
        "memories",
        help="Fetch machine-readable explicit local resolution-memory listings.",
    )
    memories_parser.add_argument("--memory-store-root", required=True)
    memories_parser.add_argument("--kind")
    memories_parser.add_argument("--run-id", dest="source_run_id")
    memories_parser.add_argument("--task-kind")
    memories_parser.add_argument("--source-id")

    memory_parser = subparsers.add_parser(
        "memory",
        help="Fetch one machine-readable explicit local resolution-memory record by id.",
    )
    memory_parser.add_argument("memory_id")
    memory_parser.add_argument("--memory-store-root", required=True)

    memory_create_parser = subparsers.add_parser(
        "memory-create",
        help="Create one machine-readable explicit local resolution-memory record from one existing run.",
    )
    memory_create_parser.add_argument("--run-store-root", required=True)
    memory_create_parser.add_argument("--memory-store-root", required=True)
    memory_create_parser.add_argument("--run-id", required=True)

    run_parser = subparsers.add_parser(
        "run",
        help="Fetch one machine-readable synchronous bootstrap resolution run by id.",
    )
    run_parser.add_argument("run_id")
    run_parser.add_argument("--run-store-root", required=True)

    run_resolve_parser = subparsers.add_parser(
        "run-resolve",
        help="Start one machine-readable synchronous bootstrap exact-resolution run.",
    )
    run_resolve_parser.add_argument("target_ref")
    run_resolve_parser.add_argument("--run-store-root", required=True)

    run_search_parser = subparsers.add_parser(
        "run-search",
        help="Start one machine-readable synchronous bootstrap deterministic-search run.",
    )
    run_search_parser.add_argument("query")
    run_search_parser.add_argument("--run-store-root", required=True)

    run_planned_search_parser = subparsers.add_parser(
        "run-planned-search",
        help="Start one machine-readable synchronous bootstrap planned-search run.",
    )
    run_planned_search_parser.add_argument("query")
    run_planned_search_parser.add_argument("--run-store-root", required=True)

    sources_parser = subparsers.add_parser("sources", help="Fetch machine-readable governed source-registry records.")
    sources_parser.add_argument("--status")
    sources_parser.add_argument("--family")
    sources_parser.add_argument("--role")
    sources_parser.add_argument("--surface")

    source_parser = subparsers.add_parser("source", help="Fetch one machine-readable governed source-registry record.")
    source_parser.add_argument("source_id")

    explain_resolve_parser = subparsers.add_parser(
        "explain-resolve-miss",
        help="Fetch a machine-readable bounded absence report for an exact-resolution miss.",
    )
    explain_resolve_parser.add_argument("target_ref")

    explain_search_parser = subparsers.add_parser(
        "explain-search-miss",
        help="Fetch a machine-readable bounded absence report for a search miss.",
    )
    explain_search_parser.add_argument("query")

    compare_parser = subparsers.add_parser("compare", help="Fetch machine-readable side-by-side comparison.")
    compare_parser.add_argument("left_target_ref")
    compare_parser.add_argument("right_target_ref")

    action_plan_parser = subparsers.add_parser(
        "action-plan",
        help="Fetch a machine-readable bounded action plan for one resolved target.",
    )
    action_plan_parser.add_argument("target_ref")
    action_plan_parser.add_argument("--host", dest="host_profile_id")
    action_plan_parser.add_argument("--strategy", dest="strategy_id")
    action_plan_parser.add_argument("--store-root")

    compatibility_parser = subparsers.add_parser(
        "compatibility",
        help="Fetch a machine-readable bounded compatibility verdict for one host preset.",
    )
    compatibility_parser.add_argument("target_ref")
    compatibility_parser.add_argument("--host", dest="host_profile_id", required=True)

    handoff_parser = subparsers.add_parser(
        "handoff",
        help="Fetch a machine-readable bounded representation-selection and handoff recommendation.",
    )
    handoff_parser.add_argument("target_ref")
    handoff_parser.add_argument("--host", dest="host_profile_id")
    handoff_parser.add_argument("--strategy", dest="strategy_id")

    fetch_parser = subparsers.add_parser(
        "fetch",
        help="Fetch a bounded local payload fixture for one explicit representation.",
    )
    fetch_parser.add_argument("target_ref")
    fetch_parser.add_argument("--representation", dest="representation_id", required=True)

    decompose_parser = subparsers.add_parser(
        "decompose",
        help="Inspect a bounded fetched representation into a compact member listing.",
    )
    decompose_parser.add_argument("target_ref")
    decompose_parser.add_argument("--representation", dest="representation_id", required=True)

    member_parser = subparsers.add_parser(
        "member",
        help="Read one bounded member from one decomposed representation.",
    )
    member_parser.add_argument("target_ref")
    member_parser.add_argument("--representation", dest="representation_id", required=True)
    member_parser.add_argument("--member", dest="member_path", required=True)
    member_parser.add_argument(
        "--raw",
        action="store_true",
        help="Return raw member bytes instead of the default JSON envelope.",
    )

    representations_parser = subparsers.add_parser(
        "representations",
        help="Fetch machine-readable bounded known representations/access paths for one target.",
    )
    representations_parser.add_argument("target_ref")

    states_parser = subparsers.add_parser("states", help="Fetch machine-readable bounded subject states.")
    states_parser.add_argument("subject_key")

    export_manifest_parser = subparsers.add_parser("export-manifest", help="Fetch manifest JSON.")
    export_manifest_parser.add_argument(
        "target_ref",
        nargs="?",
        default=DEFAULT_TARGET_REF,
    )

    export_bundle_parser = subparsers.add_parser("export-bundle", help="Fetch bundle ZIP bytes.")
    export_bundle_parser.add_argument(
        "target_ref",
        nargs="?",
        default=DEFAULT_TARGET_REF,
    )

    inspect_parser = subparsers.add_parser("inspect-bundle", help="Fetch bundle inspection JSON.")
    inspect_parser.add_argument("bundle_path")

    for command_name, help_text in (
        ("store-manifest", "Call the local manifest-store API route."),
        ("store-bundle", "Call the local bundle-store API route."),
        ("list-stored", "Call the local stored-exports listing API route."),
    ):
        command_parser = subparsers.add_parser(command_name, help=help_text)
        command_parser.add_argument(
            "target_ref",
            nargs="?",
            default=DEFAULT_TARGET_REF,
        )
        command_parser.add_argument("--store-root", required=True)

    read_stored_parser = subparsers.add_parser("read-stored", help="Read a stored artifact through the API.")
    read_stored_parser.add_argument("artifact_id")
    read_stored_parser.add_argument("--store-root", required=True)

    args = parser.parse_args(argv)
    server_config = WebServerConfig.from_environment(mode=args.mode)
    with _base_url_context(args.base_url, server_config=server_config) as base_url:
        return _fetch_command(base_url, args)


def _fetch_command(base_url: str, args: argparse.Namespace) -> int:
    if args.command == "index":
        path = "/api"
    elif args.command == "status":
        path = "/api/status"
    elif args.command == "resolve":
        path = _path("/api/resolve", target_ref=args.target_ref, store_root=args.store_root)
    elif args.command == "search":
        path = _path("/api/search", q=args.query)
    elif args.command == "query-plan":
        path = _path("/api/query-plan", q=args.query)
    elif args.command == "public-search":
        path = _path(
            "/api/v1/search",
            q=args.query,
            limit=str(args.limit) if args.limit is not None else None,
        )
    elif args.command == "public-query-plan":
        path = _path("/api/v1/query-plan", q=args.query)
    elif args.command == "public-status":
        path = "/api/v1/status"
    elif args.command == "public-sources":
        path = "/api/v1/sources"
    elif args.command == "public-source":
        path = "/api/v1/source/" + quote(args.source_id, safe="")
    elif args.command == "index-build":
        path = _path("/api/index/build", index_path=args.index_path)
    elif args.command == "index-status":
        path = _path("/api/index/status", index_path=args.index_path)
    elif args.command == "index-query":
        path = _path("/api/index/query", index_path=args.index_path, q=args.query)
    elif args.command == "tasks":
        path = _path("/api/tasks", task_store_root=args.task_store_root)
    elif args.command == "task":
        path = _path("/api/task", id=args.task_id, task_store_root=args.task_store_root)
    elif args.command == "task-run-validate-source-registry":
        path = _path(
            "/api/task/run/validate-source-registry",
            task_store_root=args.task_store_root,
        )
    elif args.command == "task-run-build-local-index":
        path = _path(
            "/api/task/run/build-local-index",
            task_store_root=args.task_store_root,
            index_path=args.index_path,
        )
    elif args.command == "task-run-query-local-index":
        path = _path(
            "/api/task/run/query-local-index",
            task_store_root=args.task_store_root,
            index_path=args.index_path,
            q=args.query,
        )
    elif args.command == "task-run-validate-archive-resolution-evals":
        path = _path(
            "/api/task/run/validate-archive-resolution-evals",
            task_store_root=args.task_store_root,
        )
    elif args.command == "runs":
        path = _path("/api/runs", run_store_root=args.run_store_root)
    elif args.command == "memories":
        path = _path(
            "/api/memories",
            memory_store_root=args.memory_store_root,
            kind=args.kind,
            source_run_id=args.source_run_id,
            task_kind=args.task_kind,
            source_id=args.source_id,
        )
    elif args.command == "memory":
        path = _path(
            "/api/memory",
            id=args.memory_id,
            memory_store_root=args.memory_store_root,
        )
    elif args.command == "memory-create":
        path = _path(
            "/api/memory/create",
            run_store_root=args.run_store_root,
            memory_store_root=args.memory_store_root,
            run_id=args.run_id,
        )
    elif args.command == "run":
        path = _path("/api/run", id=args.run_id, run_store_root=args.run_store_root)
    elif args.command == "run-resolve":
        path = _path(
            "/api/run/resolve",
            target_ref=args.target_ref,
            run_store_root=args.run_store_root,
        )
    elif args.command == "run-search":
        path = _path(
            "/api/run/search",
            q=args.query,
            run_store_root=args.run_store_root,
        )
    elif args.command == "run-planned-search":
        path = _path(
            "/api/run/planned-search",
            q=args.query,
            run_store_root=args.run_store_root,
        )
    elif args.command == "sources":
        path = _path(
            "/api/sources",
            status=args.status,
            family=args.family,
            role=args.role,
            surface=args.surface,
        )
    elif args.command == "source":
        path = _path("/api/source", id=args.source_id)
    elif args.command == "explain-resolve-miss":
        path = _path("/api/absence/resolve", target_ref=args.target_ref)
    elif args.command == "explain-search-miss":
        path = _path("/api/absence/search", q=args.query)
    elif args.command == "compare":
        path = _path("/api/compare", left=args.left_target_ref, right=args.right_target_ref)
    elif args.command == "action-plan":
        path = _path(
            "/api/action-plan",
            target_ref=args.target_ref,
            host=args.host_profile_id,
            strategy=args.strategy_id,
            store_root=args.store_root,
        )
    elif args.command == "compatibility":
        path = _path("/api/compatibility", target_ref=args.target_ref, host=args.host_profile_id)
    elif args.command == "handoff":
        path = _path(
            "/api/handoff",
            target_ref=args.target_ref,
            host=args.host_profile_id,
            strategy=args.strategy_id,
        )
    elif args.command == "fetch":
        path = _path(
            "/api/fetch",
            target_ref=args.target_ref,
            representation_id=args.representation_id,
        )
    elif args.command == "decompose":
        path = _path(
            "/api/decompose",
            target_ref=args.target_ref,
            representation_id=args.representation_id,
        )
    elif args.command == "member":
        path = _path(
            "/api/member",
            target_ref=args.target_ref,
            representation_id=args.representation_id,
            member_path=args.member_path,
            raw="1" if args.raw else None,
        )
    elif args.command == "representations":
        path = _path("/api/representations", target_ref=args.target_ref)
    elif args.command == "states":
        path = _path("/api/states", subject=args.subject_key)
    elif args.command == "export-manifest":
        path = _path("/api/export/manifest", target_ref=args.target_ref)
    elif args.command == "export-bundle":
        path = _path("/api/export/bundle", target_ref=args.target_ref)
    elif args.command == "inspect-bundle":
        path = _path("/api/inspect/bundle", bundle_path=args.bundle_path)
    elif args.command == "store-manifest":
        path = _path("/api/store/manifest", target_ref=args.target_ref, store_root=args.store_root)
    elif args.command == "store-bundle":
        path = _path("/api/store/bundle", target_ref=args.target_ref, store_root=args.store_root)
    elif args.command == "list-stored":
        path = _path("/api/stored", target_ref=args.target_ref, store_root=args.store_root)
    elif args.command == "read-stored":
        path = _path("/api/stored/artifact", artifact_id=args.artifact_id, store_root=args.store_root)
    else:
        raise AssertionError(f"Unhandled command '{args.command}'.")

    response = _open_url(base_url.rstrip("/") + path)
    content_type = response.headers.get("Content-Type", "")
    payload = response.read()
    if not content_type.startswith("application/json"):
        sys.stdout.buffer.write(payload)
        return 0

    sys.stdout.write(payload.decode("utf-8"))
    if not payload.endswith(b"\n"):
        sys.stdout.write("\n")
    return 0


def _path(route: str, **query: str | None) -> str:
    filtered = {key: value for key, value in query.items() if value is not None}
    if not filtered:
        return route
    return f"{route}?{urlencode(filtered)}"


def _open_url(url: str):
    try:
        return urlopen(url)
    except HTTPError as error:
        return error


@contextmanager
def _base_url_context(
    base_url: str | None,
    *,
    server_config: WebServerConfig,
) -> Iterator[str]:
    if base_url is not None:
        yield base_url
        return

    app = WorkbenchWsgiApp(
        build_demo_resolution_jobs_public_api(),
        acquisition_public_api=build_demo_acquisition_public_api(),
        action_plan_public_api=build_demo_action_plan_public_api(),
        archive_resolution_evals_public_api=build_demo_archive_resolution_evals_public_api(),
        absence_public_api=build_demo_absence_public_api(),
        comparison_public_api=build_demo_comparison_public_api(),
        compatibility_public_api=build_demo_compatibility_public_api(),
        decomposition_public_api=build_demo_decomposition_public_api(),
        member_access_public_api=build_demo_member_access_public_api(),
        query_planner_public_api=build_demo_query_planner_public_api(),
        handoff_public_api=build_demo_representation_selection_public_api(),
        subject_states_public_api=build_demo_subject_states_public_api(),
        representations_public_api=build_demo_representations_public_api(),
        actions_public_api=build_demo_resolution_actions_public_api(),
        bundle_inspection_public_api=build_demo_resolution_bundle_inspection_public_api(),
        local_index_public_api=build_demo_local_index_public_api(),
        search_public_api=build_demo_search_public_api(),
        public_search_public_api=build_demo_public_search_public_api(),
        source_registry_public_api=build_demo_source_registry_public_api(),
        default_target_ref=DEFAULT_TARGET_REF,
        server_config=server_config,
    )
    httpd = make_server("127.0.0.1", 0, app, handler_class=_SilentRequestHandler)
    thread = Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_port}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
