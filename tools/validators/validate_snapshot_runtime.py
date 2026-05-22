"""Validate D-BUNDLE-01 snapshot runtime artifacts."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Iterable, Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.snapshots.manifest import (
    detect_snapshot_boundary_violations,
    ensure_allowed_output_path,
    load_json,
    load_snapshot_policy,
)


CONTRACTS = [
    "contracts/snapshots/snapshot_envelope.v0.json",
    "contracts/snapshots/snapshot_manifest.v0.json",
    "contracts/snapshots/snapshot_record.v0.json",
    "contracts/control_schemas/audits/snapshots/snapshot_fixity_report.v0.json",
    "contracts/snapshots/snapshot_signature_envelope.v0.json",
    "contracts/control_schemas/audits/snapshots/snapshot_verification_report.v0.json",
    "contracts/control_schemas/audits/snapshots/snapshot_consumer_report.v0.json",
    "contracts/snapshots/snapshot_render_request.v0.json",
    "contracts/snapshots/snapshot_render_result.v0.json",
    "contracts/snapshots/snapshot_file_tree_index.v0.json",
]
POLICIES = [
    "control/inventory/snapshots/snapshot_envelope_policy.json",
    "control/inventory/snapshots/snapshot_manifest_policy.json",
    "control/inventory/snapshots/snapshot_record_policy.json",
    "control/inventory/snapshots/snapshot_fixity_policy.json",
    "control/inventory/snapshots/snapshot_signature_policy.json",
    "control/inventory/snapshots/snapshot_consumer_policy.json",
    "control/inventory/snapshots/snapshot_render_policy.json",
    "control/inventory/snapshots/snapshot_path_policy.json",
    "control/inventory/snapshots/snapshot_truth_policy.json",
    "control/inventory/snapshots/snapshot_no_live_access_policy.json",
    "control/inventory/snapshots/snapshot_semantic_parity_policy.json",
]
EXAMPLES = [
    "examples/snapshots/fixtures/minimal_snapshot_input_v0.json",
    "examples/snapshots/fixtures/search_snapshot_input_v0.json",
    "examples/snapshots/fixtures/object_snapshot_input_v0.json",
    "examples/snapshots/fixtures/source_need_action_snapshot_input_v0.json",
    "examples/snapshots/fixtures/policy_blocked_snapshot_input_v0.json",
    "examples/snapshots/manifests/minimal_snapshot_manifest_v0.json",
    "examples/snapshots/manifests/search_snapshot_manifest_v0.json",
    "examples/snapshots/manifests/object_snapshot_manifest_v0.json",
    "examples/snapshots/manifests/source_need_action_snapshot_manifest_v0.json",
    "examples/snapshots/manifests/policy_blocked_snapshot_manifest_v0.json",
    "examples/snapshots/records/search_result_snapshot_record_v0.json",
    "examples/snapshots/records/object_snapshot_record_v0.json",
    "examples/snapshots/records/source_snapshot_record_v0.json",
    "examples/snapshots/records/need_snapshot_record_v0.json",
    "examples/snapshots/records/action_manifest_snapshot_record_v0.json",
    "examples/snapshots/records/known_absence_snapshot_record_v0.json",
    "examples/snapshots/records/policy_blocked_snapshot_record_v0.json",
    "examples/snapshots/verification/minimal_snapshot_fixity_report_v0.json",
    "examples/snapshots/verification/minimal_snapshot_verification_report_v0.json",
    "examples/snapshots/verification/unsigned_snapshot_signature_envelope_v0.json",
    "examples/snapshots/verification/placeholder_snapshot_signature_envelope_v0.json",
    "examples/snapshots/verification/malformed_snapshot_signature_envelope_v0.json",
    "examples/snapshots/verification/policy_blocked_snapshot_verification_v0.json",
]
TEXT_EXAMPLES = [
    "examples/snapshots/rendered/search_snapshot_text_v0.txt",
    "examples/snapshots/rendered/search_snapshot_lite_html_v0.html",
    "examples/snapshots/rendered/search_snapshot_file_tree_index_v0.txt",
    "examples/snapshots/rendered/object_snapshot_text_v0.txt",
    "examples/snapshots/rendered/object_snapshot_lite_html_v0.html",
    "examples/snapshots/rendered/policy_blocked_snapshot_text_v0.txt",
]
MODULES = [
    "runtime.snapshots.envelope",
    "runtime.snapshots.manifest",
    "runtime.snapshots.fixity",
    "runtime.snapshots.signature",
    "runtime.snapshots.verify",
    "runtime.snapshots.consumer",
    "runtime.snapshots.render_text",
    "runtime.snapshots.render_lite_html",
    "runtime.snapshots.render_file_tree",
    "runtime.snapshots.summaries",
]
SCRIPTS = [
    "scripts/build_snapshot_fixture.py",
    "scripts/verify_snapshot_fixture.py",
    "scripts/render_snapshot_fixture.py",
    "scripts/summarize_snapshot_fixture.py",
]
FORBIDDEN_SOURCE_TOKENS = [
    "requests",
    "urllib.request",
    "socket",
    "http.client",
    "subprocess.run([\"curl\"",
    "openai",
]


def _json_files(paths: Iterable[str]) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for rel in paths:
        path = REPO_ROOT / rel
        if not path.exists():
            raise AssertionError(f"missing required file: {rel}")
        payloads.append(load_json(path))
    return payloads


def _assert_no_boundary_violations(payloads: Iterable[Mapping[str, Any]]) -> None:
    errors: list[str] = []
    for payload in payloads:
        errors.extend(detect_snapshot_boundary_violations(payload))
        text = json.dumps(payload, sort_keys=True).casefold()
        for forbidden in (
            "\"rights_clearance_claimed\": true",
            "\"malware_safety_claimed\": true",
            "\"verified_installability_claimed\": true",
            "\"production_ready\": true",
            "\"downloaded_file\": true",
            "\"mirrored_file\": true",
            "\"executed_file\": true",
        ):
            if forbidden in text:
                errors.append(f"forbidden claim appears: {forbidden}")
    if errors:
        raise AssertionError("; ".join(sorted(set(errors))))


def _run(args: list[str]) -> None:
    result = subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True)
    if result.returncode:
        raise AssertionError(f"{' '.join(args)} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")


def _assert_forbidden_outputs_rejected(policy: Mapping[str, Any]) -> None:
    for rel in ("site/dist/snapshot.txt", "site/dist/data/public_index/snapshot.json", "runtime/snapshots/generated.json"):
        try:
            ensure_allowed_output_path(rel, policy)
        except ValueError:
            continue
        raise AssertionError(f"forbidden output root was accepted: {rel}")


def _assert_no_forbidden_source_tokens() -> None:
    source_files = [
        *(rel for rel in SCRIPTS if not rel.endswith("validate_snapshot_runtime.py")),
        *(f"runtime/snapshots/{name}.py" for name in ("envelope", "manifest", "fixity", "signature", "verify", "consumer", "render_text", "render_lite_html", "render_file_tree", "summaries")),
    ]
    for rel in source_files:
        text = (REPO_ROOT / rel).read_text(encoding="utf-8").casefold()
        for token in FORBIDDEN_SOURCE_TOKENS:
            if token in text:
                raise AssertionError(f"forbidden source token {token!r} appears in {rel}")


def main() -> int:
    policy = load_snapshot_policy()
    payloads = _json_files(CONTRACTS + POLICIES + EXAMPLES + ["control/audits/d-bundle-01-snapshot-envelope-consumer-renderers-v0/d_bundle_01_report.json"])
    for rel in TEXT_EXAMPLES:
        path = REPO_ROOT / rel
        if not path.exists():
            raise AssertionError(f"missing required rendered example: {rel}")
    for module in MODULES:
        importlib.import_module(module)
    for rel in SCRIPTS:
        if not (REPO_ROOT / rel).exists():
            raise AssertionError(f"missing required script: {rel}")
    _assert_no_boundary_violations(payloads)
    _assert_forbidden_outputs_rejected(policy)
    _assert_no_forbidden_source_tokens()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _run([sys.executable, "scripts/build_snapshot_fixture.py", "--input", "examples/snapshots/fixtures/search_snapshot_input_v0.json", "--manifest-output", str(tmp_path / "manifest.json")])
        _run([sys.executable, "scripts/verify_snapshot_fixture.py", "--manifest", "examples/snapshots/manifests/search_snapshot_manifest_v0.json", "--output", str(tmp_path / "verify.json")])
        _run([sys.executable, "scripts/render_snapshot_fixture.py", "--input", "examples/snapshots/fixtures/search_snapshot_input_v0.json", "--profile", "text", "--output", str(tmp_path / "search.txt")])
        _run([sys.executable, "scripts/render_snapshot_fixture.py", "--input", "examples/snapshots/fixtures/search_snapshot_input_v0.json", "--profile", "lite_html", "--output", str(tmp_path / "search.html")])
        _run([sys.executable, "scripts/render_snapshot_fixture.py", "--input", "examples/snapshots/fixtures/search_snapshot_input_v0.json", "--profile", "file_tree", "--output", str(tmp_path / "tree.txt")])
        _run([sys.executable, "scripts/summarize_snapshot_fixture.py", "--input", "examples/snapshots", "--summary-output", str(tmp_path / "summary.md")])
    for private_root in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (REPO_ROOT / private_root).exists():
            raise AssertionError(f"local private root exists: {private_root}")
    print("validate_snapshot_runtime: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - script boundary
        print(f"validate_snapshot_runtime: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
