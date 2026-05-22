#!/usr/bin/env python3
"""Run an in-memory source observation seam demonstration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.source_observation import (
    MetadataRequest,
    MetadataResponse,
    SourceCapability,
    SourceId,
    SourceLocator,
    SourcePolicy,
    SourceRecord,
    build_evidence_candidate,
    build_review_item,
    build_source_observation,
    evaluate_source_policy,
    normalize_metadata_response,
)


FORBIDDEN_OUTPUT_ROOTS = (
    "runtime",
    "contracts",
    "surfaces",
    "site",
    "native",
    "crates",
    "examples",
    ".git",
    ".env",
    "secrets",
    ".aide.local",
    ".local",
    ".cache",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    result = build_demo_result()
    text = json.dumps(result, indent=2, sort_keys=True)

    if args.output:
        output = resolve_output_path(root, args.output)
        if is_forbidden_output(root, output):
            print(f"refusing forbidden output root: {output}", file=stderr)
            return 2
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")

    if args.json:
        print(text, file=stdout)
    else:
        print("source observation seam demo", file=stdout)
        print(f"source_id: {result['source_record']['id']}", file=stdout)
        print(f"policy_status: {result['policy_decision']['status']}", file=stdout)
        print(f"observation_id: {result['source_observation']['observation_id']}", file=stdout)
        print(f"review_status: {result['review_item']['review_status']}", file=stdout)
    return 0


def build_demo_result() -> dict[str, Any]:
    source_record = SourceRecord(
        source_id=SourceId("source.example.metadata"),
        source_family="package_registry",
        trust_lane="synthetic",
        label="Synthetic package metadata source",
        locators=(
            SourceLocator(kind="synthetic", value="package/demo-project", label="demo-project"),
        ),
        capabilities=(
            SourceCapability(
                name="metadata_observation",
                operations=("metadata_observation",),
                limitations=("synthetic payload only",),
            ),
        ),
        limitations=("no durable write", "no live request"),
        metadata={"owner": "repo"},
    )
    policy = SourcePolicy(
        allowed_operations=("metadata_observation",),
        limitations=("metadata is a candidate until review",),
    )
    decision = evaluate_source_policy(
        source_record,
        "metadata_observation",
        {"policy": policy},
    )
    request = MetadataRequest.build(
        source_id=source_record.source_id,
        request_kind="package_metadata",
        target="demo-project",
        parameters={"name": "demo-project"},
        created_at="2026-05-12T00:00:00Z",
    )
    response = MetadataResponse.build(
        request_id=request.request_id,
        source_id=source_record.source_id,
        status="observed",
        payload={
            "name": "demo-project",
            "version": "1.0.0",
            "summary": "Synthetic metadata for seam validation",
        },
        observed_at="2026-05-12T00:00:01Z",
        limitations=("synthetic payload only",),
    )
    normalized = normalize_metadata_response(response, source_record, policy=policy)
    observation = build_source_observation(
        response,
        source_record,
        policy=policy,
        observed_fields=normalized.normalized_fields,
    )
    evidence_candidate = build_evidence_candidate(normalized)
    review_item = build_review_item(evidence_candidate)
    return {
        "source_record": source_record.to_dict(),
        "policy": policy.to_dict(),
        "policy_decision": decision.to_dict(),
        "metadata_request": request.to_dict(),
        "metadata_response": response.to_dict(),
        "source_observation": observation.to_dict(),
        "normalized_observation": normalized.to_dict(),
        "evidence_candidate": evidence_candidate.to_dict(),
        "review_item": review_item.to_dict(),
        "writes_enabled": {
            "durable_store": False,
            "public_index": False,
        },
    }


def resolve_output_path(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def is_forbidden_output(root: Path, output: Path) -> bool:
    try:
        rel = output.relative_to(root).as_posix()
    except ValueError:
        return False
    return any(rel == item or rel.startswith(item.rstrip("/") + "/") for item in FORBIDDEN_OUTPUT_ROOTS)


if __name__ == "__main__":
    raise SystemExit(main())
