from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


SITE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SITE_ROOT.parent
if str(SITE_ROOT) not in sys.path:
    sys.path.insert(0, str(SITE_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import build as site_build  # noqa: E402
from scripts.validate_public_static_site import validate_public_static_site  # noqa: E402


REQUIRED_PATHS = (
    "README.md",
    "build.py",
    "validate.py",
    "templates/base.html",
    "templates/page.html",
    "data/README.md",
    "assets/site.css",
)
FORBIDDEN_NAMES = {
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "node_modules",
    "vite.config.js",
    "next.config.js",
    "tailwind.config.js",
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the site/ generator tree.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_site_tree()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_site_tree() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    existing_paths: list[str] = []
    for relative in REQUIRED_PATHS:
        path = SITE_ROOT / relative
        if path.exists():
            existing_paths.append(relative)
        else:
            errors.append(f"site/{relative}: required generator file is missing.")

    for path in SITE_ROOT.rglob("*"):
        if path.name in FORBIDDEN_NAMES:
            errors.append(f"{_display_path(path)}: prohibited frontend dependency file.")

    page_configs: list[Mapping[str, Any]] = []
    try:
        page_configs = site_build.load_page_configs()
    except site_build.BuildError as exc:
        errors.append(str(exc))

    if page_configs:
        slugs = [str(page["slug"]) for page in page_configs]
        if slugs != list(site_build.PAGE_ORDER):
            errors.append(f"site/pages: page order mismatch: {slugs}.")
        for page in page_configs:
            if page.get("status") != "implemented":
                errors.append(f"site/pages/{page.get('slug')}.json: status must be implemented.")
            if not page.get("required_claims"):
                errors.append(f"site/pages/{page.get('slug')}.json: required_claims missing.")

    try:
        source_records = site_build.load_source_records()
        if not source_records:
            errors.append("control/inventory/sources: no source records found.")
    except site_build.BuildError as exc:
        errors.append(str(exc))

    dist_dir = site_build.DEFAULT_OUTPUT
    dist_validation: Mapping[str, Any] | None = None
    if dist_dir.exists() and any(dist_dir.glob("*.html")):
        dist_validation = validate_public_static_site(dist_dir)
        if dist_validation["status"] != "valid":
            errors.extend(f"site/dist validation: {error}" for error in dist_validation["errors"])
    else:
        warnings.append("site/dist has not been generated yet.")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "static_site_generation_migration_validator_v0",
        "site_root": str(SITE_ROOT),
        "required_paths": list(REQUIRED_PATHS),
        "existing_paths": existing_paths,
        "page_count": len(page_configs),
        "dist_validation_status": dist_validation.get("status") if dist_validation else None,
        "errors": errors,
        "warnings": warnings,
    }


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Static site generator validation",
        f"status: {report['status']}",
        f"page_count: {report['page_count']}",
        f"dist_validation: {report['dist_validation_status']}",
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


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
