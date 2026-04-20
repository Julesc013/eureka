from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import extract_synthetic_source_record
from runtime.engine.interfaces.normalize import normalize_extracted_record
from runtime.engine.resolve import ExactMatchResolutionService
from runtime.gateway.public_api import InMemoryResolutionJobService, SubmitResolutionJobRequest


def build_demo_resolution_job_service() -> InMemoryResolutionJobService:
    connector = SyntheticSoftwareConnector()
    normalized_records = tuple(
        normalize_extracted_record(extract_synthetic_source_record(record))
        for record in connector.load_source_records()
    )
    resolution_service = ExactMatchResolutionService(NormalizedCatalog(normalized_records))
    return InMemoryResolutionJobService(resolution_service)


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
    args = parser.parse_args()

    connector = SyntheticSoftwareConnector()
    target_ref = args.target_ref or connector.default_target_ref()

    service = build_demo_resolution_job_service()
    submitted_job = service.submit_resolution_job(
        SubmitResolutionJobRequest.from_parts(
            target_ref=target_ref,
            requested_outputs=args.requested_outputs,
        )
    )
    resolved_job = service.get_resolution_job(submitted_job["job_id"])

    json.dump(resolved_job, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
