from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE_DIR = REPO_ROOT / "public_site"
SOURCE_INVENTORY_DIR = REPO_ROOT / "control" / "inventory" / "sources"
REQUIRED_FILES = {
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
}
REQUIRED_PHRASES = (
    "Python reference backend prototype",
    "not production",
    "no scraping",
    "external baselines pending/manual",
    "placeholders remain placeholders",
)
LIMITATION_PHRASES = (
    "No production hosting",
    "No live crawling",
    "No scraping",
    "No arbitrary local path access",
    "No auth",
    "No production Rust backend",
    "No native GUI apps",
    "No installer automation",
    "No universal compatibility oracle",
    "No trust, malware, safety, or reputation scoring",
    "Fixture-backed evidence is not global truth",
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.script_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "script":
            self.script_count += 1
        if tag.lower() not in {"a", "link"}:
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self.links.append(value)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the static public site pack without network access."
    )
    parser.add_argument(
        "--site-dir",
        default=str(DEFAULT_SITE_DIR),
        help="Static site directory to validate.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_public_static_site(Path(args.site_dir))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_public_static_site(site_dir: Path = DEFAULT_SITE_DIR) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    required_files = sorted(REQUIRED_FILES)
    existing_files: list[str] = []

    if not site_dir.exists():
        errors.append(f"{_rel(site_dir)}: site directory does not exist.")
    for relative in required_files:
        path = site_dir / relative
        if path.exists():
            existing_files.append(relative)
        else:
            errors.append(f"{_rel(path)}: required file is missing.")

    manifest_path = site_dir / "site_manifest.json"
    manifest = _load_json(manifest_path, errors)
    pages = _manifest_pages(manifest, errors)
    prohibited_claims = _manifest_prohibited_claims(manifest)

    page_reports: dict[str, dict[str, Any]] = {}
    for page in pages:
        path = site_dir / page
        if not path.exists():
            errors.append(f"{_rel(path)}: manifest page is missing.")
            continue
        text = path.read_text(encoding="utf-8")
        parser = LinkParser()
        parser.feed(text)
        page_report = {
            "missing_required_phrases": [
                phrase for phrase in REQUIRED_PHRASES if phrase not in text
            ],
            "prohibited_claims": _prohibited_claim_hits(text, prohibited_claims),
            "script_count": parser.script_count,
            "links": parser.links,
            "broken_local_links": _broken_local_links(site_dir, page, parser.links),
        }
        if page_report["missing_required_phrases"]:
            errors.append(
                f"{page}: missing required phrases {page_report['missing_required_phrases']}."
            )
        if page_report["prohibited_claims"]:
            errors.append(f"{page}: prohibited claims {page_report['prohibited_claims']}.")
        if parser.script_count:
            errors.append(f"{page}: static site pack should not require JavaScript.")
        for broken in page_report["broken_local_links"]:
            errors.append(f"{page}: local link does not resolve: {broken}.")
        page_reports[page] = page_report

    source_ids = _source_ids(errors)
    sources_text = _read_text(site_dir / "sources.html", errors)
    missing_source_ids = [source_id for source_id in source_ids if source_id not in sources_text]
    if missing_source_ids:
        errors.append(f"sources.html: missing source ids {missing_source_ids}.")
    for placeholder in (
        "internet-archive-placeholder",
        "wayback-memento-placeholder",
        "software-heritage-placeholder",
        "local-files-placeholder",
    ):
        if placeholder in sources_text and "placeholder" not in sources_text:
            errors.append(f"sources.html: {placeholder} must be marked as placeholder.")

    limitations_text = _read_text(site_dir / "limitations.html", errors)
    missing_limitations = [
        phrase for phrase in LIMITATION_PHRASES if phrase not in limitations_text
    ]
    if missing_limitations:
        errors.append(f"limitations.html: missing caveats {missing_limitations}.")

    if isinstance(manifest, Mapping):
        if manifest.get("no_network_required") is not True:
            errors.append("site_manifest.json: no_network_required must be true.")
        if manifest.get("no_deployment_performed") is not True:
            errors.append("site_manifest.json: no_deployment_performed must be true.")
        if manifest.get("site_pack_id") != "live_alpha_static_public_site_pack_v0":
            errors.append("site_manifest.json: unexpected site_pack_id.")
    else:
        warnings.append("Manifest could not be inspected beyond JSON parse status.")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "live_alpha_static_public_site_pack_validator_v0",
        "site_dir": str(site_dir),
        "required_files": required_files,
        "existing_files": sorted(existing_files),
        "pages": pages,
        "page_reports": page_reports,
        "source_ids_checked": source_ids,
        "missing_source_ids": missing_source_ids,
        "required_phrases": list(REQUIRED_PHRASES),
        "prohibited_claims": prohibited_claims,
        "errors": errors,
        "warnings": warnings,
    }


def _manifest_pages(manifest: Any, errors: list[str]) -> list[str]:
    if not isinstance(manifest, Mapping):
        errors.append("site_manifest.json: manifest must be a JSON object.")
        return []
    pages = manifest.get("pages")
    if not isinstance(pages, list) or not all(isinstance(page, str) for page in pages):
        errors.append("site_manifest.json: pages must be a list of strings.")
        return []
    return list(pages)


def _manifest_prohibited_claims(manifest: Any) -> list[str]:
    if not isinstance(manifest, Mapping):
        return []
    claims = manifest.get("prohibited_claims")
    if not isinstance(claims, list):
        return []
    return [claim for claim in claims if isinstance(claim, str)]


def _prohibited_claim_hits(text: str, claims: Sequence[str]) -> list[str]:
    hits: list[str] = []
    lowered = text.casefold()
    for claim in claims:
        claim_lower = claim.casefold()
        if claim_lower not in lowered:
            continue
        if claim_lower == "installer" and _only_negated_installer_mentions(lowered):
            continue
        hits.append(claim)
    return hits


def _only_negated_installer_mentions(lowered_text: str) -> bool:
    start = 0
    while True:
        index = lowered_text.find("installer", start)
        if index == -1:
            return True
        context = lowered_text[max(0, index - 16) : index + 32]
        if "no installer" not in context and "not an installer" not in context:
            return False
        start = index + len("installer")


def _broken_local_links(site_dir: Path, page: str, links: list[str]) -> list[str]:
    broken: list[str] = []
    base_dir = (site_dir / page).parent
    for link in links:
        if _is_external_or_fragment(link):
            continue
        target = link.split("#", 1)[0]
        if not target:
            continue
        if not (base_dir / target).exists():
            broken.append(link)
    return broken


def _is_external_or_fragment(link: str) -> bool:
    lowered = link.casefold()
    return (
        lowered.startswith("http://")
        or lowered.startswith("https://")
        or lowered.startswith("mailto:")
        or lowered.startswith("#")
    )


def _source_ids(errors: list[str]) -> list[str]:
    source_ids: list[str] = []
    if not SOURCE_INVENTORY_DIR.exists():
        errors.append(f"{_rel(SOURCE_INVENTORY_DIR)}: source inventory directory missing.")
        return source_ids
    for path in sorted(SOURCE_INVENTORY_DIR.glob("*.source.json")):
        payload = _load_json(path, errors)
        if isinstance(payload, Mapping):
            source_id = payload.get("source_id")
            if isinstance(source_id, str):
                source_ids.append(source_id)
            else:
                errors.append(f"{_rel(path)}: source_id must be a string.")
    return source_ids


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
    return None


def _read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: file is missing.")
        return ""


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Public static site validation",
        f"status: {report['status']}",
        f"pages: {len(report['pages'])}",
        f"source_ids_checked: {len(report['source_ids_checked'])}",
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
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
