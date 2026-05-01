from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
PUBLIC_SITE = REPO_ROOT / "site/dist"

DOMAIN_PLAN = PUBLICATION_DIR / "domain_plan.json"
STATIC_HOSTING_TARGETS = PUBLICATION_DIR / "static_hosting_targets.json"
DEPLOYMENT_TARGETS = PUBLICATION_DIR / "deployment_targets.json"
READINESS_DOC = REPO_ROOT / "docs" / "operations" / "CUSTOM_DOMAIN_AND_ALTERNATE_HOST_READINESS.md"
CHECKLIST_DOC = REPO_ROOT / "docs" / "operations" / "CUSTOM_DOMAIN_OPERATOR_CHECKLIST.md"
BASE_PATH_DOC = REPO_ROOT / "docs" / "reference" / "BASE_PATH_PORTABILITY.md"

COMMON_PROVIDER_CONFIG_PATHS = (
    "CNAME",
    "site/dist/CNAME",
    ".cloudflare",
    ".vercel",
    "wrangler.toml",
    "vercel.json",
    "netlify.toml",
    "render.yaml",
    "fly.toml",
    "Dockerfile",
    "docker-compose.yml",
)
PROHIBITED_POSITIVE_PATTERNS = (
    re.compile(r"\bcustom domain is configured\b", re.IGNORECASE),
    re.compile(r"\balternate host is configured\b", re.IGNORECASE),
    re.compile(r"\bdns records (are )?applied\b", re.IGNORECASE),
    re.compile(r"\bcname (file )?committed\b", re.IGNORECASE),
    re.compile(r"\bbackend (is )?deployed\b", re.IGNORECASE),
    re.compile(r"\blive probes (are )?enabled\b", re.IGNORECASE),
    re.compile(r"\bproduction ready\b", re.IGNORECASE),
    re.compile(r"\bpublic deployment succeeded\b", re.IGNORECASE),
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key.lower() in {"href", "src"} and value:
                self.references.append((key.lower(), value))


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate static-host, custom-domain, and base-path readiness without network access."
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root to validate.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_static_host_readiness(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_static_host_readiness(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    publication_dir = repo_root / "control" / "inventory" / "publication"
    site_root = repo_root / "site" / "dist"
    domain_plan = _load_json(publication_dir / "domain_plan.json", repo_root, errors)
    static_targets = _load_json(publication_dir / "static_hosting_targets.json", repo_root, errors)
    deployment_targets = _load_json(publication_dir / "deployment_targets.json", repo_root, errors)

    _validate_domain_plan(domain_plan, errors)
    target_summary = _validate_static_hosting_targets(static_targets, errors)
    _validate_deployment_targets(deployment_targets, errors)
    provider_paths = _validate_no_provider_config(repo_root, errors)
    root_relative_links = _validate_no_root_relative_links(site_root, repo_root, errors)
    _validate_docs(repo_root, errors)
    _validate_prohibited_claims(repo_root, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "static_host_readiness_validator_v0",
        "repo_root": str(repo_root),
        "domain_plan": _rel(publication_dir / "domain_plan.json", repo_root),
        "static_hosting_targets": _rel(publication_dir / "static_hosting_targets.json", repo_root),
        "deployment_targets": _rel(publication_dir / "deployment_targets.json", repo_root),
        "github_pages_project_base_path": target_summary.get("github_pages_project_base_path"),
        "custom_domain_base_path": target_summary.get("github_pages_custom_domain_base_path"),
        "provider_config_paths_checked": provider_paths,
        "root_relative_link_count": len(root_relative_links),
        "root_relative_links": root_relative_links,
        "no_domain_configured": _mapping(domain_plan).get("no_domain_configured"),
        "no_dns_changes_performed": _mapping(domain_plan).get("no_dns_changes_performed"),
        "no_cname_file_committed": _mapping(domain_plan).get("no_cname_file_committed"),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_domain_plan(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("domain_plan.json: must be a JSON object.")
        return
    expected = {
        "schema_version": "0.1.0",
        "plan_id": "eureka-custom-domain-alternate-host-readiness",
        "status": "planned",
        "no_domain_configured": True,
        "no_dns_changes_performed": True,
        "no_cname_file_committed": True,
        "custom_domain_status": "future",
        "github_pages_project_status": "implemented",
        "custom_domain_static_status": "future",
        "domain_verification_required": True,
        "created_by_slice": "custom_domain_alternate_host_readiness_v0",
    }
    _expect_mapping_values("domain_plan.json", payload, expected, errors)
    transition = payload.get("base_path_transition")
    if not isinstance(transition, Mapping):
        errors.append("domain_plan.json: base_path_transition must be an object.")
    else:
        if transition.get("from") != "/eureka/":
            errors.append("domain_plan.json: base_path_transition.from must be /eureka/.")
        if transition.get("to") != "/":
            errors.append("domain_plan.json: base_path_transition.to must be /.")
        if transition.get("status") != "future":
            errors.append("domain_plan.json: base_path_transition.status must be future.")
    required_before = payload.get("required_before_custom_domain")
    if not isinstance(required_before, list) or len(required_before) < 6:
        errors.append("domain_plan.json: required_before_custom_domain must list future prerequisites.")
    prohibited = payload.get("prohibited_claims")
    if not isinstance(prohibited, list) or "custom domain configured" not in prohibited:
        errors.append("domain_plan.json: prohibited_claims must include custom domain configured.")


def _validate_static_hosting_targets(payload: Any, errors: list[str]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    if not isinstance(payload, Mapping):
        errors.append("static_hosting_targets.json: must be a JSON object.")
        return summary
    if payload.get("schema_version") != "0.1.0":
        errors.append("static_hosting_targets.json: schema_version must be 0.1.0.")
    targets = payload.get("targets")
    if not isinstance(targets, list):
        errors.append("static_hosting_targets.json: targets must be a list.")
        return summary
    by_id = {
        target.get("id"): target
        for target in targets
        if isinstance(target, Mapping) and isinstance(target.get("id"), str)
    }
    required_ids = {
        "github_pages_project",
        "github_pages_custom_domain",
        "cloudflare_pages_static",
        "generic_static_host",
        "local_file_preview",
    }
    missing = sorted(required_ids - set(by_id))
    if missing:
        errors.append(f"static_hosting_targets.json: missing targets {missing}.")

    project = by_id.get("github_pages_project")
    if isinstance(project, Mapping):
        summary["github_pages_project_base_path"] = project.get("base_path")
        expected = {
            "status": "implemented",
            "kind": "static",
            "base_path": "/eureka/",
            "artifact_root": "site/dist",
            "workflow_configured": True,
            "deployment_success_claimed": False,
            "backend_supported": False,
            "live_probes_supported": False,
            "custom_domain_status": "future",
        }
        _expect_mapping_values("static_hosting_targets.json: github_pages_project", project, expected, errors)

    custom = by_id.get("github_pages_custom_domain")
    if isinstance(custom, Mapping):
        summary["github_pages_custom_domain_base_path"] = custom.get("base_path")
        expected = {
            "status": "future",
            "kind": "static",
            "base_path": "/",
            "artifact_root": "site/dist",
            "requires_domain_verification": True,
            "requires_cname_or_pages_settings": True,
            "dns_config_not_in_repo": True,
            "backend_supported": False,
            "live_probes_supported": False,
            "provider_config_committed": False,
        }
        _expect_mapping_values("static_hosting_targets.json: github_pages_custom_domain", custom, expected, errors)

    for target_id in ("cloudflare_pages_static", "generic_static_host"):
        target = by_id.get(target_id)
        if not isinstance(target, Mapping):
            continue
        if target.get("status") != "future":
            errors.append(f"static_hosting_targets.json: {target_id}.status must be future.")
        if target.get("base_path") != "/":
            errors.append(f"static_hosting_targets.json: {target_id}.base_path must be /.")
        if target.get("provider_config_committed") is not False:
            errors.append(f"static_hosting_targets.json: {target_id}.provider_config_committed must be false.")
        if target.get("live_probes_supported") is not False:
            errors.append(f"static_hosting_targets.json: {target_id}.live_probes_supported must be false.")

    local_preview = by_id.get("local_file_preview")
    if isinstance(local_preview, Mapping) and local_preview.get("base_path") != "relative":
        errors.append("static_hosting_targets.json: local_file_preview.base_path must be relative.")
    return summary


def _validate_deployment_targets(payload: Any, errors: list[str]) -> None:
    if not isinstance(payload, Mapping):
        errors.append("deployment_targets.json: must be a JSON object.")
        return
    targets = payload.get("targets")
    if not isinstance(targets, list):
        errors.append("deployment_targets.json: targets must be a list.")
        return
    by_id = {
        target.get("id"): target
        for target in targets
        if isinstance(target, Mapping) and isinstance(target.get("id"), str)
    }
    project = by_id.get("github_pages_project")
    if not isinstance(project, Mapping):
        errors.append("deployment_targets.json: github_pages_project target is missing.")
    else:
        if project.get("base_path") != "/eureka/":
            errors.append("deployment_targets.json: github_pages_project.base_path must be /eureka/.")
        if project.get("artifact_root") != "site/dist":
            errors.append("deployment_targets.json: github_pages_project.artifact_root must be site/dist.")
        if project.get("no_backend") is not True:
            errors.append("deployment_targets.json: github_pages_project.no_backend must be true.")
        if project.get("no_live_probes") is not True:
            errors.append("deployment_targets.json: github_pages_project.no_live_probes must be true.")
    custom = by_id.get("custom_domain_static")
    if not isinstance(custom, Mapping):
        errors.append("deployment_targets.json: custom_domain_static target is missing.")
    else:
        if custom.get("status") != "future":
            errors.append("deployment_targets.json: custom_domain_static.status must be future.")
        if custom.get("base_path") != "/":
            errors.append("deployment_targets.json: custom_domain_static.base_path must be /.")
        if custom.get("requires_domain_verification") is not True:
            errors.append("deployment_targets.json: custom_domain_static.requires_domain_verification must be true.")
        if custom.get("no_backend") is not True or custom.get("no_live_probes") is not True:
            errors.append("deployment_targets.json: custom_domain_static must be static-only with no live probes.")


def _validate_no_provider_config(repo_root: Path, errors: list[str]) -> list[str]:
    checked: list[str] = []
    for relative in COMMON_PROVIDER_CONFIG_PATHS:
        path = repo_root / relative
        checked.append(relative)
        if path.exists():
            if relative == "Dockerfile" and _safe_p54_hosted_public_search_dockerfile(path):
                continue
            errors.append(f"{relative}: custom-domain, DNS, backend, or alternate-host config must not be committed in this slice.")
    return checked


def _safe_p54_hosted_public_search_dockerfile(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    required = (
        "scripts/run_hosted_public_search.py",
        "EUREKA_SEARCH_MODE=local_index_only",
        "EUREKA_ALLOW_LIVE_PROBES=0",
        "EUREKA_ALLOW_DOWNLOADS=0",
        "EUREKA_ALLOW_UPLOADS=0",
        "EUREKA_ALLOW_LOCAL_PATHS=0",
        "EUREKA_ALLOW_ARBITRARY_URL_FETCH=0",
        "EUREKA_ALLOW_TELEMETRY=0",
    )
    if not all(item in text for item in required):
        return False
    lowered = text.casefold()
    return not any(token in lowered for token in ("api_key", "auth_token", "password:", "secret:"))


def _validate_no_root_relative_links(
    site_root: Path, repo_root: Path, errors: list[str]
) -> list[str]:
    hits: list[str] = []
    if not site_root.exists():
        errors.append("site/dist: static artifact directory is missing.")
        return hits
    for path in sorted(site_root.rglob("*.html")):
        parser = LinkParser()
        parser.feed(path.read_text(encoding="utf-8"))
        for attr, value in parser.references:
            target = value.split("#", 1)[0]
            if not target:
                continue
            if target.startswith("/") and not target.startswith("//"):
                hit = f"{_rel(path, repo_root)}: {attr}={value!r}"
                hits.append(hit)
                errors.append(f"{hit}: root-relative internal link is not base-path portable.")
            if target.startswith("https://julesc013.github.io/"):
                errors.append(
                    f"{_rel(path, repo_root)}: {attr}={value!r}: Pages absolute URL should not be embedded before domain policy changes."
                )
    return hits


def _validate_docs(repo_root: Path, errors: list[str]) -> None:
    required_docs = {
        "readiness": repo_root / "docs" / "operations" / "CUSTOM_DOMAIN_AND_ALTERNATE_HOST_READINESS.md",
        "checklist": repo_root / "docs" / "operations" / "CUSTOM_DOMAIN_OPERATOR_CHECKLIST.md",
        "base_path": repo_root / "docs" / "reference" / "BASE_PATH_PORTABILITY.md",
    }
    for label, path in required_docs.items():
        if not path.exists():
            errors.append(f"{_rel(path, repo_root)}: required {label} document is missing.")
    readiness = required_docs["readiness"]
    if readiness.exists():
        text = readiness.read_text(encoding="utf-8").casefold()
        for phrase in (
            "no custom domain",
            "no dns",
            "cname",
            "no backend",
            "no live probes",
            "/eureka/",
            "/",
        ):
            if phrase not in text:
                errors.append(f"{_rel(readiness, repo_root)}: missing readiness phrase {phrase!r}.")
    checklist = repo_root / "docs" / "operations" / "CUSTOM_DOMAIN_OPERATOR_CHECKLIST.md"
    if checklist.exists():
        text = checklist.read_text(encoding="utf-8").casefold()
        if "status: unsigned/future" not in text:
            errors.append("docs/operations/CUSTOM_DOMAIN_OPERATOR_CHECKLIST.md: must be unsigned/future.")
        for phrase in ("dns", "cname", "no backend", "no live source probes", "no production-ready"):
            if phrase not in text:
                errors.append(f"{_rel(checklist, repo_root)}: missing checklist phrase {phrase!r}.")
    base_path = required_docs["base_path"]
    if base_path.exists():
        text = base_path.read_text(encoding="utf-8").casefold()
        for phrase in ("/eureka/", "future custom-domain", "relative", "root-relative"):
            if phrase not in text:
                errors.append(f"{_rel(base_path, repo_root)}: missing base-path phrase {phrase!r}.")


def _validate_prohibited_claims(repo_root: Path, errors: list[str]) -> None:
    checked_paths = [
        repo_root / "README.md",
        repo_root / "docs" / "operations" / "CUSTOM_DOMAIN_AND_ALTERNATE_HOST_READINESS.md",
        repo_root / "docs" / "operations" / "CUSTOM_DOMAIN_OPERATOR_CHECKLIST.md",
        repo_root / "docs" / "reference" / "BASE_PATH_PORTABILITY.md",
        repo_root / "site/dist" / "status.html",
        repo_root / "site/dist" / "limitations.html",
        repo_root / "site/dist" / "roadmap.html",
    ]
    for path in checked_paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in PROHIBITED_POSITIVE_PATTERNS:
            for match in pattern.finditer(text):
                before = text[max(0, match.start() - 512) : match.start()].casefold()
                context = text[max(0, match.start() - 16) : match.end() + 16].casefold()
                if "must not claim" in before or "prohibited claims" in before:
                    continue
                if "no " in before[-16:] or "not " in before[-16:]:
                    continue
                if "must not claim" in context or "not claim" in context or "must not" in context:
                    continue
                errors.append(f"{_rel(path, repo_root)}: prohibited positive claim: {match.group(0)!r}.")


def _expect_mapping_values(
    label: str, payload: Mapping[str, Any], expected: Mapping[str, Any], errors: list[str]
) -> None:
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append(f"{label}.{key} must be {value!r}.")


def _load_json(path: Path, repo_root: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path, repo_root)}: file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path, repo_root)}: invalid JSON: {exc}.")
    return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Static host readiness validation",
        f"status: {report['status']}",
        f"github_pages_project_base_path: {report.get('github_pages_project_base_path')}",
        f"custom_domain_base_path: {report.get('custom_domain_base_path')}",
        f"root_relative_link_count: {report.get('root_relative_link_count')}",
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


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
