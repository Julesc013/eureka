from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
DEFAULT_SITE_DIR = REPO_ROOT / "public_site"
DEPLOYMENT_TARGETS = REPO_ROOT / "control" / "inventory" / "publication" / "deployment_targets.json"
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "pages.yml"

REQUIRED_STATIC_FILES = {
    "README.md",
    "site_manifest.json",
    "index.html",
    "status.html",
    "sources.html",
    "evals.html",
    "demo-queries.html",
    "limitations.html",
    "roadmap.html",
    "local-quickstart.html",
    "assets/README.md",
    "assets/site.css",
    "data/build_manifest.json",
    "data/eval_summary.json",
    "data/page_registry.json",
    "data/route_summary.json",
    "data/site_manifest.json",
    "data/source_summary.json",
    "files/README.txt",
    "files/SHA256SUMS",
    "files/data/README.txt",
    "files/index.html",
    "files/index.txt",
    "files/manifest.json",
    "lite/README.txt",
    "lite/demo-queries.html",
    "lite/evals.html",
    "lite/index.html",
    "lite/limitations.html",
    "lite/sources.html",
    "text/README.txt",
    "text/demo-queries.txt",
    "text/evals.txt",
    "text/index.txt",
    "text/limitations.txt",
    "text/sources.txt",
    "demo/README.txt",
    "demo/data/demo_snapshots.json",
    "demo/index.html",
    "demo/query-plan-windows-7-apps.html",
    "demo/result-member-driver-inside-support-cd.html",
    "demo/result-firefox-xp.html",
    "demo/result-article-scan.html",
    "demo/absence-example.html",
    "demo/comparison-example.html",
    "demo/source-example.html",
    "demo/eval-summary.html",
}
FORBIDDEN_DIR_NAMES = {
    ".aide",
    ".cache",
    ".git",
    ".github",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "cache",
    "contracts",
    "control",
    "crates",
    "evals",
    "node_modules",
    "runtime",
    "scripts",
    "site",
    "surfaces",
    "tests",
    "venv",
}
FORBIDDEN_FILE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "Dockerfile",
    "docker-compose.yml",
    "package-lock.json",
    "package.json",
    "pages.yml",
    "requirements.txt",
    "yarn.lock",
}
FORBIDDEN_SUFFIXES = {
    ".db",
    ".pyo",
    ".py",
    ".pyc",
    ".sqlite",
    ".sqlite3",
}
FORBIDDEN_TEXT_PATTERNS = (
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"/Users/[^/\s]+"),
    re.compile(r"/home/[^/\s]+"),
)
ALLOWED_EXTERNAL_LINK_PREFIXES = (
    "https://github.com/Julesc013/eureka",
)


class StaticLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key.lower() in {"href", "src"} and value:
                self.references.append((key.lower(), value))


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that public_site is safe to upload as a GitHub Pages artifact."
    )
    parser.add_argument(
        "--site-dir",
        default=str(DEFAULT_SITE_DIR),
        help="Static artifact directory to check.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = check_github_pages_static_artifact(Path(args.site_dir))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def check_github_pages_static_artifact(site_dir: Path = DEFAULT_SITE_DIR) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    static_site_report = _run_static_site_validator(site_dir)
    publication_report = _run_publication_inventory_validator(site_dir)
    _extend_prefixed_errors(errors, "static site validator", static_site_report)
    _extend_prefixed_errors(errors, "publication inventory validator", publication_report)

    existing_files: list[str] = []
    if not site_dir.is_dir():
        errors.append(f"{_rel(site_dir)}: public_site artifact directory is missing.")
    else:
        for relative in sorted(REQUIRED_STATIC_FILES):
            path = site_dir / relative
            if path.exists():
                existing_files.append(relative)
            else:
                errors.append(f"{_rel(path)}: required static artifact file is missing.")
        _validate_artifact_tree(site_dir, errors)
        _validate_base_path_safe_links(site_dir, errors)
        _validate_no_private_paths(site_dir, errors)
        _validate_manifest(site_dir, errors)

    deployment_target = _load_github_pages_target(errors)
    _validate_github_pages_target(deployment_target, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "github_pages_static_artifact_checker_v0",
        "site_dir": str(site_dir),
        "workflow_path": str(WORKFLOW_PATH),
        "required_static_files": sorted(REQUIRED_STATIC_FILES),
        "existing_static_files": sorted(existing_files),
        "deployment_target": deployment_target,
        "static_site_validator_status": static_site_report.get("status"),
        "publication_inventory_validator_status": publication_report.get("status"),
        "errors": errors,
        "warnings": warnings,
    }


def _run_static_site_validator(site_dir: Path) -> Mapping[str, Any]:
    from scripts.validate_public_static_site import validate_public_static_site

    return validate_public_static_site(site_dir)


def _run_publication_inventory_validator(site_dir: Path) -> Mapping[str, Any]:
    from scripts.validate_publication_inventory import validate_publication_inventory

    inventory_dir = REPO_ROOT / "control" / "inventory" / "publication"
    # The publication inventory governs the committed public_site artifact. For
    # temporary artifact copies used in checker tests, validate the committed
    # inventory against the committed artifact and validate the copy separately
    # with the artifact-specific checks below.
    governed_site_dir = site_dir if site_dir.resolve().is_relative_to(REPO_ROOT) else DEFAULT_SITE_DIR
    return validate_publication_inventory(inventory_dir, governed_site_dir, REPO_ROOT)


def _extend_prefixed_errors(
    errors: list[str], prefix: str, report: Mapping[str, Any]
) -> None:
    for error in report.get("errors", []):
        errors.append(f"{prefix}: {error}")


def _validate_artifact_tree(site_dir: Path, errors: list[str]) -> None:
    for path in sorted(site_dir.rglob("*")):
        relative = _rel(path)
        parts = set(path.relative_to(site_dir).parts)
        forbidden_dirs = parts & FORBIDDEN_DIR_NAMES
        if forbidden_dirs:
            errors.append(
                f"{relative}: forbidden directory name inside Pages artifact: {sorted(forbidden_dirs)}."
            )
        if path.is_dir():
            continue
        if path.name in FORBIDDEN_FILE_NAMES:
            errors.append(f"{relative}: forbidden deployment/runtime file in Pages artifact.")
        if path.suffix.casefold() in FORBIDDEN_SUFFIXES:
            errors.append(f"{relative}: forbidden runtime or local-data suffix in Pages artifact.")


def _validate_base_path_safe_links(site_dir: Path, errors: list[str]) -> None:
    for path in sorted(site_dir.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        parser = StaticLinkParser()
        parser.feed(text)
        for attr, value in parser.references:
            target = value.split("#", 1)[0]
            if not target:
                continue
            if target.startswith("/"):
                errors.append(
                    f"{_rel(path)}: {attr} uses root-relative link {value!r}; use a relative link for /eureka/ portability."
                )
            if target.startswith("https://julesc013.github.io/"):
                errors.append(
                    f"{_rel(path)}: {attr} uses a Pages absolute URL {value!r}; keep the artifact base-path portable."
                )
            if _is_external(target) and not _is_allowed_external_link(target):
                continue
            if _is_external(target):
                continue
            if target.startswith("mailto:"):
                continue
            local_target = (path.parent / target).resolve()
            try:
                local_target.relative_to(site_dir.resolve())
            except ValueError:
                errors.append(f"{_rel(path)}: {attr} escapes artifact root: {value!r}.")


def _validate_no_private_paths(site_dir: Path, errors: list[str]) -> None:
    for path in sorted(site_dir.rglob("*")):
        if not path.is_file() or _looks_binary(path):
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_TEXT_PATTERNS:
            if pattern.search(text):
                errors.append(f"{_rel(path)}: private/local filesystem path pattern is present.")


def _validate_manifest(site_dir: Path, errors: list[str]) -> None:
    manifest = _load_json(site_dir / "site_manifest.json", errors)
    if not isinstance(manifest, Mapping):
        return
    expected = {
        "github_pages_target": "github_pages_project",
        "github_pages_base_path": "/eureka/",
        "deployment_workflow_configured": True,
        "deployment_status": "workflow_configured_deployment_unverified",
        "static_only": True,
        "no_backend": True,
        "no_live_probes": True,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            errors.append(f"site_manifest.json: {key} must be {value!r}.")


def _load_github_pages_target(errors: list[str]) -> Mapping[str, Any]:
    payload = _load_json(DEPLOYMENT_TARGETS, errors)
    if not isinstance(payload, Mapping):
        return {}
    targets = payload.get("targets")
    if not isinstance(targets, list):
        errors.append("deployment_targets.json: targets must be a list.")
        return {}
    for target in targets:
        if isinstance(target, Mapping) and target.get("id") == "github_pages_project":
            return dict(target)
    errors.append("deployment_targets.json: missing github_pages_project target.")
    return {}


def _validate_github_pages_target(target: Mapping[str, Any], errors: list[str]) -> None:
    if not target:
        return
    expected = {
        "kind": "static",
        "status": "implemented",
        "artifact_root": "public_site",
        "base_path": "/eureka/",
        "canonical_base_url": "https://julesc013.github.io/eureka/",
        "requires_base_path_safe_links": True,
        "no_backend": True,
        "no_live_probes": True,
        "no_secrets": True,
        "deployment_workflow_path": ".github/workflows/pages.yml",
        "workflow_configured": True,
        "deployment_success_claimed": False,
    }
    for key, value in expected.items():
        if target.get(key) != value:
            errors.append(f"deployment_targets.json: github_pages_project.{key} must be {value!r}.")


def _is_external(target: str) -> bool:
    lowered = target.casefold()
    return lowered.startswith("http://") or lowered.startswith("https://")


def _is_allowed_external_link(target: str) -> bool:
    return any(target.startswith(prefix) for prefix in ALLOWED_EXTERNAL_LINK_PREFIXES)


def _looks_binary(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:1024]
    except OSError:
        return True
    return b"\0" in chunk


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
    return None


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "GitHub Pages static artifact check",
        f"status: {report['status']}",
        f"site_dir: {report['site_dir']}",
        f"static_site_validator: {report['static_site_validator_status']}",
        f"publication_inventory_validator: {report['publication_inventory_validator_status']}",
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
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
