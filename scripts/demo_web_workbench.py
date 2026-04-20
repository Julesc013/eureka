from __future__ import annotations

import argparse
from pathlib import Path
import sys
from urllib.parse import quote
from wsgiref.simple_server import make_server

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.gateway import build_demo_resolution_jobs_public_api
from surfaces.web.server import WorkbenchWsgiApp, render_resolution_workspace_page


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
        "--render-once",
        action="store_true",
        help="Render one HTML page to stdout and exit instead of starting the local server.",
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

    target_ref = args.target_ref or SyntheticSoftwareConnector().default_target_ref()
    public_api = build_demo_resolution_jobs_public_api()

    if args.render_once:
        html = render_resolution_workspace_page(public_api, target_ref)
        sys.stdout.write(html)
        return 0

    app = WorkbenchWsgiApp(public_api, default_target_ref=target_ref)
    with make_server(args.host, args.port, app) as httpd:
        sys.stdout.write(
            "Serving Eureka compatibility workbench at "
            f"http://{args.host}:{args.port}/?target_ref={quote(target_ref, safe='')}\n"
        )
        sys.stdout.flush()
        httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
