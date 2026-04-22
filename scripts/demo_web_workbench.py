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

from runtime.gateway.public_api import (
    build_demo_absence_public_api,
    build_demo_comparison_public_api,
    InspectResolutionBundleRequest,
    build_demo_representations_public_api,
    ResolutionActionRequest,
    StoredArtifactRequest,
    StoredExportsTargetRequest,
    build_demo_resolution_actions_public_api,
    build_demo_resolution_bundle_inspection_public_api,
    build_demo_resolution_jobs_public_api,
    build_demo_search_public_api,
    build_demo_stored_exports_public_api,
    build_demo_subject_states_public_api,
)
from surfaces.web.server import (
    WorkbenchWsgiApp,
    render_bundle_inspection_page,
    render_resolution_workspace_page,
    render_search_results_page,
)

DEFAULT_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"


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
        "--store-root",
        metavar="PATH",
        help="Local bootstrap store root used for storing, listing, and reading exported artifacts.",
    )
    parser.add_argument(
        "--store-manifest",
        action="store_true",
        help="Store the bounded resolution manifest for the selected target in the local export store.",
    )
    parser.add_argument(
        "--store-bundle",
        action="store_true",
        help="Store the deterministic resolution bundle for the selected target in the local export store.",
    )
    parser.add_argument(
        "--list-stored",
        action="store_true",
        help="List stored exports for the selected target from the local export store.",
    )
    parser.add_argument(
        "--read-stored",
        metavar="ARTIFACT_ID",
        help="Read a stored artifact by artifact identity from the local export store.",
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
            args.store_manifest,
            args.store_bundle,
            args.list_stored,
            args.read_stored is not None,
        )
    ) > 1:
        parser.error(
            "--export-manifest, --export-bundle, --inspect-bundle, --render-inspection, "
            "--store-manifest, --store-bundle, --list-stored, and --read-stored are mutually exclusive."
        )

    target_ref = args.target_ref or DEFAULT_TARGET_REF
    actions_public_api = build_demo_resolution_actions_public_api()
    bundle_inspection_public_api = build_demo_resolution_bundle_inspection_public_api()
    comparison_public_api = build_demo_comparison_public_api()
    absence_public_api = build_demo_absence_public_api()
    resolution_public_api = build_demo_resolution_jobs_public_api()
    search_public_api = build_demo_search_public_api()
    stored_exports_public_api = (
        build_demo_stored_exports_public_api(args.store_root) if args.store_root is not None else None
    )

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

    if args.store_manifest:
        if stored_exports_public_api is None:
            return _write_store_unavailable()
        response = stored_exports_public_api.store_resolution_manifest(
            StoredExportsTargetRequest.from_parts(target_ref)
        )
        sys.stdout.write(json.dumps(response.body, indent=2, sort_keys=True))
        sys.stdout.write("\n")
        return 0

    if args.store_bundle:
        if stored_exports_public_api is None:
            return _write_store_unavailable()
        response = stored_exports_public_api.store_resolution_bundle(
            StoredExportsTargetRequest.from_parts(target_ref)
        )
        sys.stdout.write(json.dumps(response.body, indent=2, sort_keys=True))
        sys.stdout.write("\n")
        return 0

    if args.list_stored:
        if stored_exports_public_api is None:
            return _write_store_unavailable()
        response = stored_exports_public_api.list_stored_exports(
            StoredExportsTargetRequest.from_parts(target_ref)
        )
        sys.stdout.write(json.dumps(response.body, indent=2, sort_keys=True))
        sys.stdout.write("\n")
        return 0

    if args.read_stored is not None:
        if stored_exports_public_api is None:
            return _write_store_unavailable()
        response = stored_exports_public_api.get_stored_artifact_content(
            StoredArtifactRequest.from_parts(args.read_stored)
        )
        if response.status_code == 200 and not response.content_type.startswith("application/json"):
            sys.stdout.buffer.write(response.payload)
            return 0
        sys.stdout.write(response.payload.decode("utf-8"))
        return 0

    if args.render_once:
        if args.search_query is not None:
            html = render_search_results_page(search_public_api, args.search_query)
        else:
            html = render_resolution_workspace_page(
                resolution_public_api,
                target_ref,
                actions_public_api=actions_public_api,
                stored_exports_public_api=stored_exports_public_api,
            )
        sys.stdout.write(html)
        return 0

    app = WorkbenchWsgiApp(
        resolution_public_api,
        absence_public_api=absence_public_api,
        comparison_public_api=comparison_public_api,
        subject_states_public_api=build_demo_subject_states_public_api(),
        representations_public_api=build_demo_representations_public_api(),
        actions_public_api=actions_public_api,
        bundle_inspection_public_api=bundle_inspection_public_api,
        stored_exports_public_api=stored_exports_public_api,
        search_public_api=search_public_api,
        default_target_ref=target_ref,
    )
    with make_server(args.host, args.port, app) as httpd:
        lines = [
            "Serving Eureka compatibility workbench at "
            f"http://{args.host}:{args.port}/?target_ref={quote(target_ref, safe='')}",
            "Serving Eureka compatibility search at "
            f"http://{args.host}:{args.port}/search?q={quote('synthetic', safe='')}",
            "Serving Eureka bootstrap HTTP API index at "
            f"http://{args.host}:{args.port}/api",
            "Serving Eureka bootstrap HTTP API resolve route at "
            f"http://{args.host}:{args.port}/api/resolve?target_ref={quote(target_ref, safe='')}",
            "Serving Eureka comparison page at "
            f"http://{args.host}:{args.port}/compare?left={quote('fixture:software/archivebox@0.8.5', safe='')}&right={quote('github-release:archivebox/archivebox@v0.8.5', safe='')}",
            "Serving Eureka bootstrap HTTP API compare route at "
            f"http://{args.host}:{args.port}/api/compare?left={quote('fixture:software/archivebox@0.8.5', safe='')}&right={quote('github-release:archivebox/archivebox@v0.8.5', safe='')}",
            "Serving Eureka representations page at "
            f"http://{args.host}:{args.port}/representations?target_ref={quote(target_ref, safe='')}",
            "Serving Eureka bootstrap HTTP API representations route at "
            f"http://{args.host}:{args.port}/api/representations?target_ref={quote(target_ref, safe='')}",
            "Serving Eureka subject states page at "
            f"http://{args.host}:{args.port}/subject?key={quote('archivebox', safe='')}",
            "Serving Eureka bootstrap HTTP API subject states route at "
            f"http://{args.host}:{args.port}/api/states?subject={quote('archivebox', safe='')}",
            "Serving Eureka bootstrap HTTP API search route at "
            f"http://{args.host}:{args.port}/api/search?q={quote('synthetic', safe='')}",
            "Serving Eureka resolve miss explanation page at "
            f"http://{args.host}:{args.port}/absence/resolve?target_ref={quote('fixture:software/archivebox@9.9.9', safe='')}",
            "Serving Eureka bootstrap HTTP API resolve miss route at "
            f"http://{args.host}:{args.port}/api/absence/resolve?target_ref={quote('fixture:software/archivebox@9.9.9', safe='')}",
            "Serving Eureka search miss explanation page at "
            f"http://{args.host}:{args.port}/absence/search?q={quote('archive box', safe='')}",
            "Serving Eureka bootstrap HTTP API search miss route at "
            f"http://{args.host}:{args.port}/api/absence/search?q={quote('archive box', safe='')}",
            "Serving Eureka manifest export at "
            f"http://{args.host}:{args.port}/actions/export-resolution-manifest?target_ref={quote(target_ref, safe='')}",
            "Serving Eureka bootstrap HTTP API manifest export at "
            f"http://{args.host}:{args.port}/api/export/manifest?target_ref={quote(target_ref, safe='')}",
            "Serving Eureka bundle export at "
            f"http://{args.host}:{args.port}/actions/export-resolution-bundle?target_ref={quote(target_ref, safe='')}",
            "Serving Eureka bootstrap HTTP API bundle export at "
            f"http://{args.host}:{args.port}/api/export/bundle?target_ref={quote(target_ref, safe='')}",
            "Serving Eureka bundle inspection at "
            f"http://{args.host}:{args.port}/inspect/bundle?bundle_path={quote(str((Path.cwd() / 'example-resolution-bundle.zip')), safe='')}",
            "Serving Eureka bootstrap HTTP API bundle inspection at "
            f"http://{args.host}:{args.port}/api/inspect/bundle?bundle_path={quote(str((Path.cwd() / 'example-resolution-bundle.zip')), safe='')}",
        ]
        if args.store_root is not None:
            lines.extend(
                [
                    "Serving Eureka local manifest store action at "
                    f"http://{args.host}:{args.port}/store/manifest?target_ref={quote(target_ref, safe='')}",
                    "Serving Eureka local bundle store action at "
                    f"http://{args.host}:{args.port}/store/bundle?target_ref={quote(target_ref, safe='')}",
                    "Serving Eureka bootstrap HTTP API local store listing at "
                    f"http://{args.host}:{args.port}/api/stored?target_ref={quote(target_ref, safe='')}&store_root={quote(args.store_root, safe='')}",
                ]
            )
        sys.stdout.write("\n".join(lines) + "\n")
        sys.stdout.flush()
        httpd.serve_forever()
    return 0


def _write_store_unavailable() -> int:
    sys.stdout.write(
        json.dumps(
            {
                "status": "blocked",
                "code": "export_store_unavailable",
                "message": "Provide --store-root to enable bootstrap stored-export operations.",
            },
            indent=2,
            sort_keys=True,
        )
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
