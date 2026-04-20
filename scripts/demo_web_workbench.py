from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from urllib.parse import quote
from wsgiref.simple_server import make_server

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.gateway import (
    build_demo_resolution_actions_public_api,
    build_demo_resolution_bundle_inspection_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
)
from runtime.gateway.public_api import InspectResolutionBundleRequest, ResolutionActionRequest
from surfaces.web.server import (
    WorkbenchWsgiApp,
    render_bundle_inspection_page,
    render_resolution_workspace_page,
    render_search_results_page,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the local compatibility-first Eureka web workbench demo.",
    )
    parser.add_argument(
        "target_ref",
        nargs="?",
        help="Bounded target reference to resolve. Defaults to the known synthetic fixture target.",
    )
    parser.add_argument(
        "--search-query",
        help="Render or demo the deterministic search page for a bounded query.",
    )
    parser.add_argument(
        "--render-once",
        action="store_true",
        help="Render one HTML page to stdout and exit instead of starting the local server.",
    )
    parser.add_argument(
        "--export-manifest",
        action="store_true",
        help="Export the bounded resolution manifest for the selected target and print JSON to stdout.",
    )
    parser.add_argument(
        "--export-bundle",
        action="store_true",
        help="Export the deterministic resolution bundle ZIP for the selected target to stdout.",
    )
    parser.add_argument(
        "--inspect-bundle",
        metavar="PATH",
        help="Inspect a local resolution bundle path and print the public inspection envelope as JSON.",
    )
    parser.add_argument(
        "--render-inspection",
        metavar="PATH",
        help="Render the compatibility-first bundle inspection page for a local bundle path.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface for the local bootstrap server.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8781,
        help="Port for the local bootstrap server.",
    )
    args = parser.parse_args()
    if sum(
        int(flag)
        for flag in (
            args.export_manifest,
            args.export_bundle,
            args.inspect_bundle is not None,
            args.render_inspection is not None,
        )
    ) > 1:
        parser.error(
            "--export-manifest, --export-bundle, --inspect-bundle, and --render-inspection are mutually exclusive."
        )

    target_ref = args.target_ref or SyntheticSoftwareConnector().default_target_ref()
    actions_public_api = build_demo_resolution_actions_public_api()
    bundle_inspection_public_api = build_demo_resolution_bundle_inspection_public_api()
    resolution_public_api = build_demo_resolution_jobs_public_api()
    search_public_api = build_demo_search_public_api()

    if args.export_manifest:
        response = actions_public_api.export_resolution_manifest(
            ResolutionActionRequest.from_parts(target_ref)
        )
        sys.stdout.write(json.dumps(response.body, indent=2, sort_keys=True))
        sys.stdout.write("\n")
        return 0

    if args.export_bundle:
        response = actions_public_api.export_resolution_bundle(
            ResolutionActionRequest.from_parts(target_ref)
        )
        if response.status_code == 200:
            sys.stdout.buffer.write(response.payload)
            return 0
        sys.stdout.write(response.payload.decode("utf-8"))
        return 0

    if args.inspect_bundle is not None:
        response = bundle_inspection_public_api.inspect_bundle(
            InspectResolutionBundleRequest.from_bundle_path(args.inspect_bundle)
        )
        sys.stdout.write(json.dumps(response.body, indent=2, sort_keys=True))
        sys.stdout.write("\n")
        return 0

    if args.render_inspection is not None:
        html = render_bundle_inspection_page(
            bundle_inspection_public_api,
            args.render_inspection,
        )
        sys.stdout.write(html)
        return 0

    if args.render_once:
        if args.search_query is not None:
            html = render_search_results_page(search_public_api, args.search_query)
        else:
            html = render_resolution_workspace_page(
                resolution_public_api,
                target_ref,
                actions_public_api=actions_public_api,
            )
        sys.stdout.write(html)
        return 0

    app = WorkbenchWsgiApp(
        resolution_public_api,
        actions_public_api=actions_public_api,
        bundle_inspection_public_api=bundle_inspection_public_api,
        search_public_api=search_public_api,
        default_target_ref=target_ref,
    )
    with make_server(args.host, args.port, app) as httpd:
        sys.stdout.write(
            "Serving Eureka compatibility workbench at "
            f"http://{args.host}:{args.port}/?target_ref={quote(target_ref, safe='')}\n"
            "Serving Eureka compatibility search at "
            f"http://{args.host}:{args.port}/search?q={quote('synthetic', safe='')}\n"
            "Serving Eureka manifest export at "
            f"http://{args.host}:{args.port}/actions/export-resolution-manifest?target_ref={quote(target_ref, safe='')}\n"
            "Serving Eureka bundle export at "
            f"http://{args.host}:{args.port}/actions/export-resolution-bundle?target_ref={quote(target_ref, safe='')}\n"
            "Serving Eureka bundle inspection at "
            f"http://{args.host}:{args.port}/inspect/bundle?bundle_path={quote(str((Path.cwd() / 'example-resolution-bundle.zip')), safe='')}\n"
        )
        sys.stdout.flush()
        httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
