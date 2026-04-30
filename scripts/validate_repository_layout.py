from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = REPO_ROOT / "site"
STATIC_ARTIFACT_ROOT = SITE_ROOT / "dist"
EXTERNAL_ROOT = REPO_ROOT / "external"
LEGACY_STATIC_ROOT_NAME = "public" + "_site"
LEGACY_EXTERNAL_ROOT_NAME = "third" + "_party"
LEGACY_HYPHEN_NAME = "third" + "-party"
LEGACY_TITLE_NAME = "Third" + " Party"
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "pages.yml"
GENERATED_ARTIFACTS = (
    REPO_ROOT / "control" / "inventory" / "generated_artifacts" / "generated_artifacts.json"
)
DRIFT_POLICY = (
    REPO_ROOT / "control" / "inventory" / "generated_artifacts" / "drift_policy.json"
)
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"

HISTORICAL_ALLOW_DIRS = {
    "control/audits",
    ".aide/reports",
}
ACTIVE_TEXT_ROOTS = (
    ".aide",
    ".github",
    "control/inventory",
    "docs",
    "scripts",
    "site",
    "tests",
    "README.md",
    "AGENTS.md",
)
REQUIRED_EXTERNAL_DIRS = (
    "licenses",
    "specs",
    "upstream_snapshots",
    "references",
)
REQUIRED_STATIC_FILES = (
    ".nojekyll",
    ".eureka-static-site-generated",
    "index.html",
    "status.html",
    "sources.html",
    "evals.html",
    "demo-queries.html",
    "limitations.html",
    "roadmap.html",
    "local-quickstart.html",
    "site_manifest.json",
    "assets/site.css",
    "data/site_manifest.json",
    "data/page_registry.json",
    "data/source_summary.json",
    "data/eval_summary.json",
    "data/route_summary.json",
    "data/build_manifest.json",
    "lite/index.html",
    "text/index.txt",
    "files/manifest.json",
    "files/SHA256SUMS",
    "demo/index.html",
    "demo/data/demo_snapshots.json",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Eureka repository layout consolidation without network access."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings as well as errors.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_repository_layout(strict=args.strict)
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_repository_layout(*, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    _validate_required_roots(errors)
    _validate_static_artifact(errors)
    _validate_external_root(errors)
    _validate_workflow(errors)
    _validate_publication_inventory(errors)
    _validate_generated_artifact_inventory(errors)
    stale_hits = _validate_no_active_legacy_references(errors)

    if strict and warnings:
        errors.extend(f"strict warning: {warning}" for warning in warnings)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "repository_shape_consolidation_v0",
        "site_root": _rel(SITE_ROOT),
        "static_artifact_root": _rel(STATIC_ARTIFACT_ROOT),
        "external_root": _rel(EXTERNAL_ROOT),
        "workflow_path": _rel(WORKFLOW_PATH),
        "generated_artifact_id": "static_site_dist",
        "historical_allow_dirs": sorted(HISTORICAL_ALLOW_DIRS),
        "active_legacy_reference_hits": stale_hits,
        "strict": strict,
        "errors": errors,
        "warnings": warnings,
    }


def _validate_required_roots(errors: list[str]) -> None:
    for path, label in (
        (SITE_ROOT, "site root"),
        (STATIC_ARTIFACT_ROOT, "static artifact root"),
        (EXTERNAL_ROOT, "external root"),
    ):
        if not path.is_dir():
            errors.append(f"{_rel(path)}: required {label} is missing.")
    if (REPO_ROOT / LEGACY_STATIC_ROOT_NAME).exists():
        errors.append("retired static artifact directory still exists.")
    if (REPO_ROOT / LEGACY_EXTERNAL_ROOT_NAME).exists():
        errors.append("retired outside-reference directory still exists.")


def _validate_static_artifact(errors: list[str]) -> None:
    if not STATIC_ARTIFACT_ROOT.is_dir():
        return
    for relative in REQUIRED_STATIC_FILES:
        path = STATIC_ARTIFACT_ROOT / relative
        if not path.exists():
            errors.append(f"{_rel(path)}: required static artifact file is missing.")
    if (STATIC_ARTIFACT_ROOT / "README.md").exists():
        errors.append("site/dist/README.md must not be part of the generated artifact.")
    prohibited_names = {
        ".env",
        ".pytest_cache",
        "__pycache__",
        "runtime",
        "tests",
        "scripts",
        "contracts",
        "control",
    }
    prohibited_suffixes = {".sqlite", ".sqlite3", ".db", ".py", ".pyc", ".pyo"}
    for path in STATIC_ARTIFACT_ROOT.rglob("*"):
        relative_parts = set(path.relative_to(STATIC_ARTIFACT_ROOT).parts)
        bad_parts = relative_parts & prohibited_names
        if bad_parts:
            errors.append(
                f"{_rel(path)}: prohibited runtime/private path inside static artifact: {sorted(bad_parts)}."
            )
        if path.is_file() and path.suffix.casefold() in prohibited_suffixes:
            errors.append(f"{_rel(path)}: prohibited file suffix inside static artifact.")


def _validate_external_root(errors: list[str]) -> None:
    readme = EXTERNAL_ROOT / "README.md"
    if not readme.is_file():
        errors.append("external/README.md: boundary README is missing.")
        return
    text = readme.read_text(encoding="utf-8").casefold()
    for phrase in (
        "pinned outside materials",
        "license notes",
        "must not contain",
        "generated site output",
        "user caches",
        "private user data",
    ):
        if phrase not in text:
            errors.append(f"external/README.md: missing boundary phrase {phrase!r}.")
    for relative in REQUIRED_EXTERNAL_DIRS:
        if not (EXTERNAL_ROOT / relative).is_dir():
            errors.append(f"external/{relative}: required outside-reference subroot is missing.")


def _validate_workflow(errors: list[str]) -> None:
    if not WORKFLOW_PATH.is_file():
        errors.append(".github/workflows/pages.yml: workflow is missing.")
        return
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    required_steps = (
        "python site/build.py",
        "python scripts/generate_public_data_summaries.py --check",
        "python scripts/generate_compatibility_surfaces.py --check",
        "python scripts/generate_static_resolver_demos.py --check",
        "python scripts/validate_publication_inventory.py",
        "python site/validate.py",
        "python scripts/check_github_pages_static_artifact.py --path site/dist",
        "python scripts/check_generated_artifact_drift.py --artifact static_site_dist",
        "path: site/dist",
    )
    for needle in required_steps:
        if needle not in text:
            errors.append(f".github/workflows/pages.yml: missing workflow command {needle!r}.")
    if "path: " + LEGACY_STATIC_ROOT_NAME in text:
        errors.append(".github/workflows/pages.yml: uploads the retired static artifact.")


def _validate_publication_inventory(errors: list[str]) -> None:
    contract = _load_json(PUBLICATION_DIR / "publication_contract.json", errors)
    targets = _load_json(PUBLICATION_DIR / "deployment_targets.json", errors)
    page_registry = _load_json(PUBLICATION_DIR / "page_registry.json", errors)
    public_data = _load_json(PUBLICATION_DIR / "public_data_contract.json", errors)

    if isinstance(contract, Mapping):
        expected = {
            "current_static_artifact": "site/dist",
            "future_generator_root": "site",
            "future_generated_artifact": "site/dist",
            "deploy_artifact_current": "site/dist",
        }
        for key, value in expected.items():
            if contract.get(key) != value:
                errors.append(f"publication_contract.json: {key} must be {value!r}.")
    if isinstance(targets, Mapping):
        project = _target_by_id(targets, "github_pages_project")
        if not project:
            errors.append("deployment_targets.json: github_pages_project is missing.")
        elif project.get("artifact_root") != "site/dist":
            errors.append("deployment_targets.json: github_pages_project.artifact_root must be site/dist.")
    if isinstance(page_registry, Mapping):
        artifact_root = page_registry.get("artifact_root")
        if artifact_root != "site/dist":
            errors.append("page_registry.json: artifact_root must be site/dist.")
    if isinstance(public_data, Mapping):
        entries = public_data.get("entries", [])
        if not isinstance(entries, list):
            errors.append("public_data_contract.json: entries must be a list.")
        else:
            for entry in entries:
                if not isinstance(entry, Mapping):
                    continue
                for source in entry.get("source_inputs", []):
                    if isinstance(source, str) and source == LEGACY_STATIC_ROOT_NAME:
                        errors.append("public_data_contract.json: legacy static root appears in source_inputs.")


def _validate_generated_artifact_inventory(errors: list[str]) -> None:
    inventory = _load_json(GENERATED_ARTIFACTS, errors)
    _load_json(DRIFT_POLICY, errors)
    if not isinstance(inventory, Mapping):
        return
    groups = inventory.get("artifact_groups")
    if not isinstance(groups, list):
        errors.append("generated_artifacts.json: artifact_groups must be a list.")
        return
    by_id = {
        group.get("artifact_id"): group
        for group in groups
        if isinstance(group, Mapping) and isinstance(group.get("artifact_id"), str)
    }
    group = by_id.get("static_site_dist")
    if not isinstance(group, Mapping):
        errors.append("generated_artifacts.json: static_site_dist artifact group is missing.")
        return
    if group.get("status") != "implemented":
        errors.append("generated_artifacts.json: static_site_dist.status must be implemented.")
    if group.get("artifact_paths") != ["site/dist", "site/dist/.eureka-static-site-generated", "site/dist/.nojekyll"]:
        errors.append("generated_artifacts.json: static_site_dist artifact_paths must own site/dist and markers.")
    if group.get("manual_edits_allowed") is not False:
        errors.append("generated_artifacts.json: static_site_dist.manual_edits_allowed must be false.")
    if group.get("deployment_target") != "github_pages_project":
        errors.append("generated_artifacts.json: static_site_dist.deployment_target must be github_pages_project.")
    commands = set(_string_list(group.get("validator_commands"))) | set(_string_list(group.get("check_commands")))
    if "python scripts/check_github_pages_static_artifact.py --path site/dist" not in commands:
        errors.append("generated_artifacts.json: static_site_dist must include the site/dist Pages artifact check.")


def _validate_no_active_legacy_references(errors: list[str]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    legacy_tokens = (
        LEGACY_STATIC_ROOT_NAME,
        LEGACY_EXTERNAL_ROOT_NAME,
        LEGACY_HYPHEN_NAME,
        LEGACY_TITLE_NAME,
    )
    for path in _active_text_files():
        text = _read_text(path)
        if text is None:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            matched = [token for token in legacy_tokens if token in line]
            if not matched:
                continue
            hit = {"path": _rel(path), "line": line_number, "tokens": matched}
            hits.append(hit)
            errors.append(
                f"{_rel(path)}:{line_number}: active legacy layout reference {matched}."
            )
    return hits


def _active_text_files() -> list[Path]:
    paths: list[Path] = []
    for root in ACTIVE_TEXT_ROOTS:
        path = REPO_ROOT / root
        if not path.exists():
            continue
        if path.is_file():
            paths.append(path)
            continue
        for child in path.rglob("*"):
            if child.is_file() and not _is_historical_allowed(child):
                paths.append(child)
    return sorted(set(paths))


def _is_historical_allowed(path: Path) -> bool:
    rel = _rel(path)
    return any(rel == prefix or rel.startswith(prefix + "/") for prefix in HISTORICAL_ALLOW_DIRS)


def _read_text(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _target_by_id(payload: Mapping[str, Any], target_id: str) -> Mapping[str, Any] | None:
    targets = payload.get("targets")
    if not isinstance(targets, list):
        return None
    for target in targets:
        if isinstance(target, Mapping) and target.get("id") == target_id:
            return target
    return None


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: JSON file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
    return None


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Repository layout validation",
        f"status: {report['status']}",
        f"static_artifact_root: {report['static_artifact_root']}",
        f"external_root: {report['external_root']}",
        f"generated_artifact_id: {report['generated_artifact_id']}",
    ]
    if report["errors"]:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.append("")
        lines.append("Warnings")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
