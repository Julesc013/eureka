from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.gateway import build_demo_resolution_jobs_public_api
from runtime.gateway.public_api import SubmitResolutionJobRequest, resolution_job_envelope_to_workbench_session


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the local deterministic Eureka thin-slice resolution demo.",
    )
    parser.add_argument(
        "target_ref",
        nargs="?",
        help="Bounded target reference to resolve. Defaults to the known synthetic fixture target.",
    )
    parser.add_argument(
        "--requested-output",
        action="append",
        dest="requested_outputs",
        default=[],
        help="Optional bounded output label to include in the request envelope.",
    )
    parser.add_argument(
        "--include-workbench-session",
        action="store_true",
        help="Also map the read job envelope into the shared workbench session view model.",
    )
    parser.add_argument(
        "--session-id",
        default="session.synthetic-demo",
        help="Session identifier to use when emitting a workbench session view model.",
    )
    args = parser.parse_args()

    connector = SyntheticSoftwareConnector()
    target_ref = args.target_ref or connector.default_target_ref()

    public_api = build_demo_resolution_jobs_public_api()
    submit_response = public_api.submit_resolution_job(
        SubmitResolutionJobRequest.from_parts(
            target_ref=target_ref,
            requested_outputs=args.requested_outputs,
        )
    )
    read_response = public_api.read_resolution_job(submit_response.body["job_id"])

    payload = {
        "submit_response": submit_response.to_dict(),
        "read_response": read_response.to_dict(),
    }
    if args.include_workbench_session:
        payload["workbench_session"] = resolution_job_envelope_to_workbench_session(
            read_response.body,
            session_id=args.session_id,
        )

    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
