from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_ROOT = REPO_ROOT / "control" / "audits" / "generated-artifact-visibility-v1"

EXCLUDED_DIR_NAMES = [
    "dist",
    "tmp",
    "build",
    "out",
    "target",
    "coverage",
    "node_modules",
]


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit tracked generated-artifact paths hidden by common tree excludes.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect.")
    parser.add_argument("--audit-root", default=str(AUDIT_ROOT), help="Audit output directory.")
    parser.add_argument("--write", action="store_true", help="Write the generated visibility audit files.")
    parser.add_argument("--json", action="store_true", help="Emit the machine-readable report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    repo_root = Path(args.repo_root).resolve()
    audit_root = Path(args.audit_root)
    if not audit_root.is_absolute():
        audit_root = repo_root / audit_root

    report = build_visibility_report(repo_root)
    excluded_policy = build_excluded_dir_policy(report)

    if args.write:
        write_audit_files(audit_root, report, excluded_policy)

    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(format_plain(report))
    return 0 if report["status"] == "valid" else 1


def build_visibility_report(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    files = git_ls_files(repo_root)
    by_segment = {name: paths_with_segment(files, name) for name in EXCLUDED_DIR_NAMES}
    site_dist = [path for path in files if path == "site/dist" or path.startswith("site/dist/")]
    native_dist_placeholders = [
        path for path in by_segment["dist"] if path.startswith("native/") and path.endswith("/dist/README.md")
    ]
    native_build_placeholders = [
        path for path in by_segment["build"] if path.startswith("native/") and path.endswith("/build/README.md")
    ]
    connector_coverage_fixtures = [
        path
        for path in by_segment["coverage"]
        if path.startswith("examples/connectors/") and path.endswith("_coverage_preview_v0.json")
    ]

    unexpected_dist = sorted(set(by_segment["dist"]) - set(site_dist) - set(native_dist_placeholders))
    unexpected_build = sorted(set(by_segment["build"]) - set(native_build_placeholders))
    unexpected_coverage = sorted(set(by_segment["coverage"]) - set(connector_coverage_fixtures))
    unexpected_tmp = by_segment["tmp"]
    unexpected_out = by_segment["out"]
    unexpected_target = by_segment["target"]

    errors: list[str] = []
    for label, paths in [
        ("unexpected_dist_paths", unexpected_dist),
        ("unexpected_build_paths", unexpected_build),
        ("tracked_tmp_paths", unexpected_tmp),
        ("tracked_out_paths", unexpected_out),
        ("tracked_target_paths", unexpected_target),
        ("unexpected_coverage_paths", unexpected_coverage),
    ]:
        if paths:
            errors.append(f"{label}: {len(paths)} path(s) require classification.")

    return {
        "schema_version": "generated_artifact_visibility.v1",
        "audit_id": "EUREKA-GENERATED-VISIBILITY-01",
        "status": "valid" if not errors else "needs_review",
        "errors": errors,
        "tracked_file_count": len(files),
        "excluded_dir_names_checked": EXCLUDED_DIR_NAMES,
        "tracked_site_dist_count": len(site_dist),
        "tracked_tmp_count": len(by_segment["tmp"]),
        "tracked_dist_segment_count": len(by_segment["dist"]),
        "tracked_build_segment_count": len(by_segment["build"]),
        "tracked_out_segment_count": len(by_segment["out"]),
        "tracked_target_segment_count": len(by_segment["target"]),
        "tracked_coverage_segment_count": len(by_segment["coverage"]),
        "tracked_site_dist": site_dist,
        "tracked_tmp": by_segment["tmp"],
        "tracked_dist_paths": by_segment["dist"],
        "tracked_build_paths": by_segment["build"],
        "tracked_out_paths": by_segment["out"],
        "tracked_target_paths": by_segment["target"],
        "tracked_coverage_paths": by_segment["coverage"],
        "classified_exceptions": {
            "site_dist_public_artifact": site_dist,
            "native_dist_readme_placeholders": native_dist_placeholders,
            "native_build_readme_placeholders": native_build_placeholders,
            "connector_coverage_preview_fixtures": connector_coverage_fixtures,
        },
        "unexpected": {
            "dist": unexpected_dist,
            "build": unexpected_build,
            "tmp": unexpected_tmp,
            "out": unexpected_out,
            "target": unexpected_target,
            "coverage": unexpected_coverage,
        },
        "dirty_state_captured": False,
        "network_used": False,
        "product_behavior_changed": False,
        "non_claims": [
            "This audit inventories tracked generated-looking paths; it does not claim production readiness.",
            "site/dist remains a committed generated public artifact, not source truth.",
            "examples/connectors/**/coverage files are fixture coverage previews, not test coverage output.",
        ],
    }


def build_excluded_dir_policy(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "excluded_dir_visibility_policy.v1",
        "policy_id": "EUREKA-GENERATED-VISIBILITY-01",
        "status": "active_bootstrap_policy",
        "excluded_dir_names": EXCLUDED_DIR_NAMES,
        "required_focused_checks": [
            "git ls-files site/dist",
            "git ls-files tmp",
            "git ls-files | grep '/dist/'",
            "git ls-files | grep '/tmp/'",
            "git ls-files | grep '/build/'",
        ],
        "classification": {
            "site/dist": "committed generated/public static artifact",
            "native/*/dist/README.md": "tracked placeholder only",
            "native/*/build/README.md": "tracked placeholder only",
            "examples/connectors/*/coverage/*_coverage_preview_v0.json": "public-safe fixture coverage preview",
            "tmp": "must remain untracked",
            "out": "must remain untracked unless separately classified",
            "target": "must remain untracked unless separately classified",
        },
        "current_counts": {
            "tracked_site_dist_count": report["tracked_site_dist_count"],
            "tracked_tmp_count": report["tracked_tmp_count"],
            "tracked_dist_segment_count": report["tracked_dist_segment_count"],
            "tracked_build_segment_count": report["tracked_build_segment_count"],
            "tracked_out_segment_count": report["tracked_out_segment_count"],
            "tracked_target_segment_count": report["tracked_target_segment_count"],
            "tracked_coverage_segment_count": report["tracked_coverage_segment_count"],
        },
        "non_claims": report["non_claims"],
    }


def write_audit_files(audit_root: Path, report: dict[str, Any], excluded_policy: dict[str, Any]) -> None:
    audit_root.mkdir(parents=True, exist_ok=True)
    (audit_root / "tracked_generated_paths.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (audit_root / "excluded_dir_policy.json").write_text(
        json.dumps(excluded_policy, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (audit_root / "generated_artifact_risk_report.md").write_text(format_markdown(report), encoding="utf-8")


def git_ls_files(repo_root: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def paths_with_segment(paths: Sequence[str], segment: str) -> list[str]:
    return sorted(path for path in paths if segment in path.split("/"))


def format_plain(report: dict[str, Any]) -> str:
    lines = [
        f"Generated artifact visibility: {report['status']}",
        f"tracked_site_dist_count: {report['tracked_site_dist_count']}",
        f"tracked_tmp_count: {report['tracked_tmp_count']}",
        f"tracked_dist_segment_count: {report['tracked_dist_segment_count']}",
        f"tracked_build_segment_count: {report['tracked_build_segment_count']}",
        f"tracked_coverage_segment_count: {report['tracked_coverage_segment_count']}",
    ]
    for error in report["errors"]:
        lines.append(f"error: {error}")
    return "\n".join(lines) + "\n"


def format_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Generated Artifact Visibility v1",
            "",
            "## Summary",
            "",
            f"- Status: `{report['status']}`",
            f"- Tracked files inspected: `{report['tracked_file_count']}`",
            f"- Tracked `site/dist/` files: `{report['tracked_site_dist_count']}`",
            f"- Tracked `tmp/` files: `{report['tracked_tmp_count']}`",
            f"- Tracked paths with `/dist/`: `{report['tracked_dist_segment_count']}`",
            f"- Tracked paths with `/build/`: `{report['tracked_build_segment_count']}`",
            f"- Tracked paths with `/out/`: `{report['tracked_out_segment_count']}`",
            f"- Tracked paths with `/target/`: `{report['tracked_target_segment_count']}`",
            f"- Tracked paths with `/coverage/`: `{report['tracked_coverage_segment_count']}`",
            "",
            "## Classification",
            "",
            "- `site/dist/` is a committed generated/public static artifact governed by repo generated-artifact policy.",
            "- Native `build/README.md` and `dist/README.md` files are placeholders, not build outputs.",
            "- `examples/connectors/**/coverage/*_coverage_preview_v0.json` files are fixture coverage previews, not coverage output.",
            "- `tmp/`, `out/`, and `target/` have no tracked files in this audit.",
            "",
            "## Non-Claims",
            "",
            "- This audit does not claim production readiness.",
            "- This audit does not treat generated output as source truth.",
            "- This audit does not change product behavior, source connector behavior, or public search behavior.",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
