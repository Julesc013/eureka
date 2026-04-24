from __future__ import annotations

import argparse
from contextlib import contextmanager
from pathlib import Path
import sys
from threading import Thread
from typing import Iterator
from urllib.parse import urlencode
from urllib.request import HTTPError, urlopen
from wsgiref.simple_server import WSGIRequestHandler, make_server


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.gateway.public_api import (
    build_demo_acquisition_public_api,
    build_demo_action_plan_public_api,
    build_demo_absence_public_api,
    build_demo_comparison_public_api,
    build_demo_compatibility_public_api,
    build_demo_decomposition_public_api,
    build_demo_member_access_public_api,
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
from surfaces.web.server import WorkbenchWsgiApp

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
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("index", help="Fetch the HTTP API index document.")

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

    runs_parser = subparsers.add_parser(
        "runs",
        help="Fetch machine-readable synchronous bootstrap resolution-run listings.",
    )
    runs_parser.add_argument("--run-store-root", required=True)

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
    with _base_url_context(args.base_url) as base_url:
        return _fetch_command(base_url, args)


def _fetch_command(base_url: str, args: argparse.Namespace) -> int:
    if args.command == "index":
        path = "/api"
    elif args.command == "resolve":
        path = _path("/api/resolve", target_ref=args.target_ref, store_root=args.store_root)
    elif args.command == "search":
        path = _path("/api/search", q=args.query)
    elif args.command == "query-plan":
        path = _path("/api/query-plan", q=args.query)
    elif args.command == "runs":
        path = _path("/api/runs", run_store_root=args.run_store_root)
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
def _base_url_context(base_url: str | None) -> Iterator[str]:
    if base_url is not None:
        yield base_url
        return

    app = WorkbenchWsgiApp(
        build_demo_resolution_jobs_public_api(),
        acquisition_public_api=build_demo_acquisition_public_api(),
        action_plan_public_api=build_demo_action_plan_public_api(),
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
        search_public_api=build_demo_search_public_api(),
        source_registry_public_api=build_demo_source_registry_public_api(),
        default_target_ref=DEFAULT_TARGET_REF,
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
