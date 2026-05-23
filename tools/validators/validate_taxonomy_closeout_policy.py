from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY = REPO_ROOT / "control" / "policies" / "taxonomy_closeout_policy.json"
AIDE_POLICY = REPO_ROOT / "control" / "policies" / "aide_ledger_size_policy.json"

REQUIRED_FILES = [
    "control/audits/generated-artifact-visibility-v1/tracked_generated_paths.json",
    "control/audits/generated-artifact-visibility-v1/excluded_dir_policy.json",
    "control/audits/generated-artifact-visibility-v1/generated_artifact_risk_report.md",
    "control/audits/taxonomy-closeout-v1/runtime_taxonomy_closeout.json",
    "control/audits/taxonomy-closeout-v1/runtime_taxonomy_closeout.md",
    "control/audits/taxonomy-closeout-v1/contracts_taxonomy_migration_map.json",
    "control/audits/taxonomy-closeout-v1/contracts_taxonomy_closeout.md",
    "control/audits/taxonomy-closeout-v1/examples_taxonomy_closeout.json",
    "control/audits/taxonomy-closeout-v1/examples_taxonomy_closeout.md",
    "control/audits/taxonomy-closeout-v1/aide_ledger_size_report.json",
    "control/audits/taxonomy-closeout-v1/aide_ledger_size_report.md",
    "docs/architecture/PATH_TAXONOMY_CLOSEOUT.md",
    "contracts/control_schemas/README.md",
    "runtime/README.md",
    "examples/README.md",
    ".aide/README.md",
]

FORBIDDEN_ACTIVE_PATHS = [
    "data",
    "deploy",
    "release/render",
    "surfaces/native/cli",
]


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Eureka taxonomy closeout policy and evidence.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_taxonomy_closeout_policy(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_taxonomy_closeout_policy(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    tracked = git_ls_files(root)
    tracked_set = set(tracked)

    policy = load_json(root / rel_policy(POLICY), errors)
    aide_policy = load_json(root / rel_policy(AIDE_POLICY), errors)

    for relative in REQUIRED_FILES:
        if not (root / relative).exists():
            errors.append(f"{relative}: required closeout file is missing.")

    for forbidden in FORBIDDEN_ACTIVE_PATHS:
        if forbidden in tracked_set or any(path.startswith(f"{forbidden}/") for path in tracked):
            errors.append(f"{forbidden}: forbidden active path is tracked.")

    validate_policy_shape(policy, errors)
    validate_aide_policy_shape(aide_policy, errors)
    validate_readme_phrases(root, errors)
    validate_runtime_pages(root, tracked, errors)
    validate_generated_visibility(root, errors)

    return {
        "schema_version": "taxonomy_closeout_policy_validation.v1",
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "policy": "control/policies/taxonomy_closeout_policy.json",
        "aide_policy": "control/policies/aide_ledger_size_policy.json",
        "required_file_count": len(REQUIRED_FILES),
        "forbidden_active_paths": FORBIDDEN_ACTIVE_PATHS,
        "runtime_pages_checked": True,
        "network_used": False,
        "product_behavior_changed": False,
    }


def validate_policy_shape(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "active_closeout_policy":
        errors.append("control/policies/taxonomy_closeout_policy.json: status must be active_closeout_policy.")
    if policy.get("product_behavior_change_allowed") is not False:
        errors.append("control/policies/taxonomy_closeout_policy.json: product_behavior_change_allowed must be false.")
    for key in ["runtime", "contracts", "examples"]:
        section = policy.get(key)
        if not isinstance(section, Mapping):
            errors.append(f"control/policies/taxonomy_closeout_policy.json: missing {key} section.")
            continue
        if section.get("closeout_mode") not in {"freeze_current_names", "migration_map_first"}:
            errors.append(f"control/policies/taxonomy_closeout_policy.json: {key}.closeout_mode is invalid.")
        targets = section.get("target_families")
        if not isinstance(targets, list) or not targets:
            errors.append(f"control/policies/taxonomy_closeout_policy.json: {key}.target_families must be non-empty.")


def validate_aide_policy_shape(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "active_control_plane_policy":
        errors.append("control/policies/aide_ledger_size_policy.json: status must be active_control_plane_policy.")
    required_classes = {"active_authority", "generated", "export_only", "cache", "retention_capped"}
    actual = {str(item.get("class")) for item in list_of_mappings(policy.get("areas"))}
    missing = sorted(required_classes - actual)
    if missing:
        errors.append(f"control/policies/aide_ledger_size_policy.json: missing area classes {missing}.")


def validate_readme_phrases(root: Path, errors: list[str]) -> None:
    required = {
        "contracts/control_schemas/README.md": ["compatibility", "canonical target", "not active runtime"],
        "runtime/README.md": ["runtime/engine", "taxonomy closeout", "current names are frozen"],
        "examples/README.md": ["durable families", "taxonomy closeout", "public-safe"],
        ".aide/README.md": ["not product truth", "export-only", "retention-capped"],
        "docs/architecture/PATH_TAXONOMY_CLOSEOUT.md": ["no behavior change", "migration map first", "runtime/engine"],
    }
    for relative, phrases in required.items():
        text = read_text(root / relative, errors).lower()
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{relative}: missing required phrase {phrase!r}.")


def validate_runtime_pages(root: Path, tracked: Sequence[str], errors: list[str]) -> None:
    runtime_page_files = [path for path in tracked if path.startswith("runtime/pages/")]
    forbidden_suffixes = (".html", ".css", ".jinja", ".j2")
    offenders = [path for path in runtime_page_files if path.endswith(forbidden_suffixes)]
    if offenders:
        errors.append(f"runtime/pages: presentation files are tracked in runtime: {offenders}.")
    readme = read_text(root / "runtime/pages/README.md", errors).lower()
    for phrase in ["runtime metadata", "not presentation", "surfaces/web"]:
        if phrase not in readme:
            errors.append(f"runtime/pages/README.md: missing required phrase {phrase!r}.")


def validate_generated_visibility(root: Path, errors: list[str]) -> None:
    report = load_json(root / "control/audits/generated-artifact-visibility-v1/tracked_generated_paths.json", errors)
    if report and report.get("status") != "valid":
        errors.append("generated-artifact-visibility-v1/tracked_generated_paths.json: status must be valid.")
    if report and report.get("tracked_tmp_count") != 0:
        errors.append("generated-artifact-visibility-v1/tracked_generated_paths.json: tracked_tmp_count must be 0.")


def git_ls_files(root: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def load_json(path: Path, errors: list[str]) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{rel(path)}: missing JSON file.")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"{rel(path)}: invalid JSON: {exc}.")
        return {}
    return value if isinstance(value, Mapping) else {}


def list_of_mappings(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"{rel(path)}: missing text file.")
        return ""


def rel_policy(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        f"Taxonomy closeout policy: {report['status']}",
        f"required_file_count: {report['required_file_count']}",
    ]
    for error in report["errors"]:
        lines.append(f"error: {error}")
    for warning in report["warnings"]:
        lines.append(f"warning: {warning}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
