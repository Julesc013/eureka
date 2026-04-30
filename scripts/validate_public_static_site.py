from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE_DIR = REPO_ROOT / "site/dist"
SOURCE_INVENTORY_DIR = REPO_ROOT / "control" / "inventory" / "sources"
LEGACY_STATIC_ARTIFACT_NAME = "public" + "_site"
REQUIRED_FILES = {
    ".nojekyll",
    "site_manifest.json",
    "index.html",
    "status.html",
    "sources.html",
    "evals.html",
    "demo-queries.html",
    "limitations.html",
    "roadmap.html",
    "local-quickstart.html",
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
REQUIRED_PUBLIC_DATA_FILES = (
    "data/site_manifest.json",
    "data/page_registry.json",
    "data/source_summary.json",
    "data/eval_summary.json",
    "data/route_summary.json",
    "data/build_manifest.json",
)
REQUIRED_COMPATIBILITY_FILES = (
    "lite/index.html",
    "lite/sources.html",
    "lite/evals.html",
    "lite/demo-queries.html",
    "lite/limitations.html",
    "lite/README.txt",
    "text/index.txt",
    "text/sources.txt",
    "text/evals.txt",
    "text/demo-queries.txt",
    "text/limitations.txt",
    "text/README.txt",
    "files/index.html",
    "files/index.txt",
    "files/README.txt",
    "files/manifest.json",
    "files/SHA256SUMS",
    "files/data/README.txt",
)
REQUIRED_DEMO_FILES = (
    "demo/index.html",
    "demo/query-plan-windows-7-apps.html",
    "demo/result-member-driver-inside-support-cd.html",
    "demo/result-firefox-xp.html",
    "demo/result-article-scan.html",
    "demo/absence-example.html",
    "demo/comparison-example.html",
    "demo/source-example.html",
    "demo/eval-summary.html",
    "demo/README.txt",
    "demo/data/demo_snapshots.json",
)
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
        "--site-root",
        dest="site_dir",
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
    if _is_legacy_static_artifact_path(site_dir):
        errors.append("legacy static artifact paths are not valid active site roots.")

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
        if manifest.get("site_pack_id") != "eureka_static_site_dist_v0":
            errors.append("site_manifest.json: unexpected site_pack_id.")
    else:
        warnings.append("Manifest could not be inspected beyond JSON parse status.")

    _validate_public_data_files(site_dir, errors)
    compatibility_report = _validate_compatibility_surfaces(site_dir, errors)
    demo_report = _validate_demo_snapshots(site_dir, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "eureka_static_site_dist_validator_v0",
        "site_dir": str(site_dir),
        "required_files": required_files,
        "existing_files": sorted(existing_files),
        "pages": pages,
        "page_reports": page_reports,
        "source_ids_checked": source_ids,
        "public_data_files_checked": list(REQUIRED_PUBLIC_DATA_FILES),
        "compatibility_surface_files_checked": list(REQUIRED_COMPATIBILITY_FILES),
        "compatibility_surface_report": compatibility_report,
        "demo_snapshot_files_checked": list(REQUIRED_DEMO_FILES),
        "demo_snapshot_report": demo_report,
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


def _is_legacy_static_artifact_path(path: Path) -> bool:
    return LEGACY_STATIC_ARTIFACT_NAME in path.as_posix().split("/")


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


def _validate_public_data_files(site_dir: Path, errors: list[str]) -> None:
    for relative in REQUIRED_PUBLIC_DATA_FILES:
        path = site_dir / relative
        payload = _load_json(path, errors)
        if not isinstance(payload, Mapping):
            errors.append(f"{_rel(path)}: public data file must contain a JSON object.")
            continue
        if payload.get("schema_version") != "0.1.0":
            errors.append(f"{relative}: schema_version must be 0.1.0.")
        if payload.get("generated_by") != "scripts/generate_public_data_summaries.py":
            errors.append(f"{relative}: generated_by must be scripts/generate_public_data_summaries.py.")
        text = json.dumps(payload, sort_keys=True)
        for marker in ("D:\\", "C:\\", "/Users/", "/home/"):
            if marker in text:
                errors.append(f"{relative}: private/local filesystem path marker is present.")
        for flag in ("contains_live_backend", "contains_live_probes", "contains_live_data"):
            if payload.get(flag) is True:
                errors.append(f"{relative}: {flag} must not be true.")
        if relative == "data/site_manifest.json":
            if payload.get("no_deployment_claim") is not True:
                errors.append("data/site_manifest.json: no_deployment_claim must be true.")
            if payload.get("contains_external_observations") is not False:
                errors.append(
                    "data/site_manifest.json: contains_external_observations must be false."
                )
        if relative == "data/build_manifest.json":
            if payload.get("deployment_performed") is not False:
                errors.append("data/build_manifest.json: deployment_performed must be false.")
        if relative == "data/eval_summary.json":
            baselines = payload.get("manual_external_baselines")
            if not isinstance(baselines, Mapping):
                errors.append("data/eval_summary.json: manual_external_baselines must be an object.")
            elif baselines.get("global_observed_count") != 0:
                errors.append(
                    "data/eval_summary.json: global_observed_count must remain 0 until manual evidence exists."
                )


def _validate_compatibility_surfaces(site_dir: Path, errors: list[str]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "lite_html_pages": [],
        "text_files": [],
        "files_manifest_status": None,
        "sha256_entries": [],
    }
    for relative in REQUIRED_COMPATIBILITY_FILES:
        path = site_dir / relative
        if not path.exists():
            errors.append(f"{_rel(path)}: required compatibility surface file is missing.")

    for relative in (
        "lite/index.html",
        "lite/sources.html",
        "lite/evals.html",
        "lite/demo-queries.html",
        "lite/limitations.html",
        "files/index.html",
    ):
        path = site_dir / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        parser = LinkParser()
        parser.feed(text)
        report["lite_html_pages"].append(relative)
        if parser.script_count:
            errors.append(f"{relative}: compatibility surfaces must not include JavaScript.")
        for link in parser.links:
            if link.startswith("/"):
                errors.append(f"{relative}: link must be relative for /eureka/ portability: {link}.")
            if _is_external_or_fragment(link):
                continue
            target = link.split("#", 1)[0]
            if target and not (path.parent / target).exists():
                errors.append(f"{relative}: local link does not resolve: {link}.")
        lowered = text.casefold()
        for phrase in ("no live search", "no live source probes"):
            if phrase not in lowered:
                errors.append(f"{relative}: missing static compatibility caveat {phrase!r}.")

    for relative in (
        "text/index.txt",
        "text/sources.txt",
        "text/evals.txt",
        "text/demo-queries.txt",
        "text/limitations.txt",
        "text/README.txt",
    ):
        path = site_dir / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        report["text_files"].append(relative)
        if "live search" not in text.casefold() and relative != "text/sources.txt":
            errors.append(f"{relative}: must state the no-live-search boundary.")

    manifest = _load_json(site_dir / "files" / "manifest.json", errors)
    if isinstance(manifest, Mapping):
        report["files_manifest_status"] = manifest.get("status")
        if manifest.get("generated_by") != "scripts/generate_compatibility_surfaces.py":
            errors.append("files/manifest.json: generated_by must be scripts/generate_compatibility_surfaces.py.")
        for flag in (
            "contains_live_backend",
            "contains_live_probes",
            "contains_live_data",
            "contains_external_observations",
            "contains_executable_downloads",
            "downloads_available",
        ):
            if manifest.get(flag) is not False:
                errors.append(f"files/manifest.json: {flag} must be false.")

    sha_path = site_dir / "files" / "SHA256SUMS"
    if sha_path.exists():
        report["sha256_entries"] = _validate_sha256sums(site_dir, sha_path, errors)
    return report


def _validate_demo_snapshots(site_dir: Path, errors: list[str]) -> dict[str, Any]:
    report: dict[str, Any] = {
        "demo_pages": [],
        "demo_count": None,
        "demo_data_status": None,
    }
    for relative in REQUIRED_DEMO_FILES:
        path = site_dir / relative
        if not path.exists():
            errors.append(f"{_rel(path)}: required demo snapshot file is missing.")

    data = _load_json(site_dir / "demo" / "data" / "demo_snapshots.json", errors)
    if isinstance(data, Mapping):
        report["demo_count"] = data.get("demo_count")
        report["demo_data_status"] = "parsed"
        if data.get("generated_by") != "scripts/generate_static_resolver_demos.py":
            errors.append("demo/data/demo_snapshots.json: generated_by must be scripts/generate_static_resolver_demos.py.")
        if data.get("no_live_backend") is not True:
            errors.append("demo/data/demo_snapshots.json: no_live_backend must be true.")
        if data.get("no_external_observations") is not True:
            errors.append("demo/data/demo_snapshots.json: no_external_observations must be true.")
        if data.get("no_deployment_claim") is not True:
            errors.append("demo/data/demo_snapshots.json: no_deployment_claim must be true.")
        if data.get("contains_live_data") is not False:
            errors.append("demo/data/demo_snapshots.json: contains_live_data must be false.")
        demos = data.get("demos")
        if not isinstance(demos, list) or len(demos) < 8:
            errors.append("demo/data/demo_snapshots.json: demos must contain at least 8 demo entries.")
        elif any(not isinstance(item, Mapping) for item in demos):
            errors.append("demo/data/demo_snapshots.json: demos entries must be objects.")
        else:
            for demo in demos:
                if demo.get("status") != "static_demo":
                    errors.append(f"demo/data/demo_snapshots.json: {demo.get('id')} status must be static_demo.")
                if demo.get("live_backend_required") is not False:
                    errors.append(f"demo/data/demo_snapshots.json: {demo.get('id')} live_backend_required must be false.")
                if demo.get("external_observation_required") is not False:
                    errors.append(f"demo/data/demo_snapshots.json: {demo.get('id')} external_observation_required must be false.")

    for relative in REQUIRED_DEMO_FILES:
        if not relative.endswith(".html"):
            continue
        path = site_dir / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        parser = LinkParser()
        parser.feed(text)
        report["demo_pages"].append(relative)
        if parser.script_count:
            errors.append(f"{relative}: demo snapshots must not include JavaScript.")
        lowered = text.casefold()
        for phrase in ("static demo snapshot", "fixture-backed", "not live search", "not production"):
            if phrase not in lowered:
                errors.append(f"{relative}: missing demo limitation phrase {phrase!r}.")
        for marker in ("D:\\", "C:\\", "/Users/", "/home/"):
            if marker in text:
                errors.append(f"{relative}: private/local filesystem path marker is present.")
        for link in parser.links:
            if link.startswith("/"):
                errors.append(f"{relative}: link must be relative for /eureka/ portability: {link}.")
            if _is_external_or_fragment(link):
                continue
            target = link.split("#", 1)[0]
            if target and not (path.parent / target).exists():
                errors.append(f"{relative}: local link does not resolve: {link}.")
    return report


def _validate_sha256sums(site_dir: Path, sha_path: Path, errors: list[str]) -> list[str]:
    entries: list[str] = []
    for line_number, line in enumerate(sha_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 2:
            errors.append(f"files/SHA256SUMS:{line_number}: expected '<sha256>  <path>'.")
            continue
        digest, relative = parts
        entries.append(relative)
        target = site_dir / relative
        if not target.exists() or not target.is_file():
            errors.append(f"files/SHA256SUMS:{line_number}: target is missing: {relative}.")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"files/SHA256SUMS:{line_number}: checksum mismatch for {relative}.")
    for required in (
        "data/site_manifest.json",
        "data/page_registry.json",
        "data/source_summary.json",
        "data/eval_summary.json",
        "data/route_summary.json",
        "data/build_manifest.json",
        "files/manifest.json",
        "files/index.txt",
        "files/README.txt",
    ):
        if required not in entries:
            errors.append(f"files/SHA256SUMS: missing checksum entry for {required}.")
    return entries


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
