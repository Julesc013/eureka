from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.engine.evals import (  # noqa: E402
    build_default_archive_resolution_eval_runner,
    build_default_search_usefulness_audit_runner,
)
from scripts.public_alpha_smoke import run_public_alpha_smoke  # noqa: E402
from scripts.validate_external_baseline_observations import (  # noqa: E402
    DEFAULT_BATCHES_DIR,
    DEFAULT_OBSERVATIONS_DIR,
    PENDING_STATUS,
    validate_external_baseline_observations,
)
from scripts.validate_public_static_site import (  # noqa: E402
    DEFAULT_SITE_DIR,
    validate_public_static_site,
)


PACK_DIR = REPO_ROOT / "docs" / "operations" / "public_alpha_rehearsal_evidence_v0"
MANIFEST_NAME = "rehearsal_evidence_manifest.json"
ROUTE_INVENTORY_PATH = REPO_ROOT / "control" / "inventory" / "public_alpha_routes.json"
NORMALIZED_RECORDED_AT = "2026-04-27 static rehearsal evidence snapshot"
CREATED_BY_SLICE = "public_alpha_rehearsal_evidence_v0"
CLASSIFICATION_ORDER = (
    "safe_public_alpha",
    "blocked_public_alpha",
    "local_dev_only",
    "review_required",
    "deferred",
)
REQUIRED_FILES = (
    "README.md",
    "REHEARSAL_SCOPE.md",
    "COMMIT_AND_ARTIFACTS.md",
    "STATIC_SITE_EVIDENCE.md",
    "SAFE_MODE_EVIDENCE.md",
    "ROUTE_INVENTORY_EVIDENCE.md",
    "EVAL_AND_AUDIT_EVIDENCE.md",
    "EXTERNAL_BASELINE_STATUS.md",
    "OPERATOR_CHECKLIST_STATUS.md",
    "BLOCKERS_AND_LIMITATIONS.md",
    "NEXT_DEPLOYMENT_REQUIREMENTS.md",
    "SIGNOFF_TEMPLATE.md",
    MANIFEST_NAME,
)
LIMITATIONS = (
    "no real deployment",
    "no auth/accounts",
    "no TLS/DNS/process manager supplied by this repo",
    "no rate limiting or abuse controls",
    "no live source probes",
    "no production logging or monitoring",
    "no external baseline observations",
    "source coverage remains bounded",
    "native apps deferred",
    "Rust is not the active runtime",
)
REQUIRED_BEFORE_REAL_DEPLOYMENT = (
    "validate Public Publication Plane Contracts v0",
    "validate GitHub Pages static artifact readiness if publishing public_site",
    "keep GitHub Pages static publishing separate from backend hosting",
    "keep public_site as the current static artifact until a generator is deliberately introduced",
    "choose a hosting target",
    "deploy from a reviewed commit",
    "configure HTTPS/TLS",
    "configure rate limits and abuse controls",
    "set environment mode to public_alpha",
    "keep live probes disabled unless a future gateway contract approves them",
    "run smoke checks after deployment",
    "record operator signoff",
    "define rollback path",
    "define logging and privacy posture",
    "review all review-required routes",
)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate or check Public Alpha Rehearsal Evidence v0."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the committed rehearsal evidence pack.",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Refresh committed rehearsal evidence files.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    output = stdout or sys.stdout
    summary = build_rehearsal_summary()
    if args.update and args.check:
        output.write("--update and --check cannot be used together.\n")
        return 2
    if args.update:
        manifest = build_manifest(summary)
        write_pack(manifest)
        output.write(format_plain_summary(summary, manifest, "updated"))
        return 0
    if args.check:
        check_report = check_pack(summary)
        if args.json:
            output.write(json.dumps(check_report, indent=2, sort_keys=True) + "\n")
        else:
            output.write(format_check_report(check_report))
        return 0 if check_report["status"] == "valid" else 1

    manifest = build_manifest(summary)
    if args.json:
        output.write(json.dumps({"status": "ready", "summary": summary, "manifest": manifest}, indent=2, sort_keys=True) + "\n")
    else:
        output.write(format_plain_summary(summary, manifest, "ready"))
    return 0


def build_rehearsal_summary() -> dict[str, Any]:
    route_inventory = _load_json(ROUTE_INVENTORY_PATH)
    routes = _routes(route_inventory)
    route_counts = Counter(str(route["classification"]) for route in routes)
    static_site = validate_public_static_site(DEFAULT_SITE_DIR)
    smoke = run_public_alpha_smoke()
    archive = build_default_archive_resolution_eval_runner().run_suite().to_dict()
    search = build_default_search_usefulness_audit_runner().run_suite().to_dict()
    baseline = validate_external_baseline_observations(
        observations_dir=DEFAULT_OBSERVATIONS_DIR,
        batches_dir=DEFAULT_BATCHES_DIR,
    )
    batch_0 = baseline.get("batches", {}).get("batch_0", {})
    global_pending = sum(
        counts.get(PENDING_STATUS, 0)
        for counts in baseline["status_counts_by_system"].values()
    )
    global_observed = sum(
        counts.get("observed", 0)
        for counts in baseline["status_counts_by_system"].values()
    )
    return {
        "repository": "Julesc013/eureka",
        "branch": _git_value("rev-parse", "--abbrev-ref", "HEAD"),
        "commit_sha": _git_value("rev-parse", "HEAD"),
        "static_site": {
            "path": "public_site/",
            "status": static_site["status"],
            "pages": len(static_site["pages"]),
            "source_ids_checked": len(static_site["source_ids_checked"]),
            "errors": static_site["errors"],
        },
        "public_alpha_smoke": {
            "status": smoke["status"],
            "passed_checks": smoke["passed_checks"],
            "total_checks": smoke["total_checks"],
        },
        "route_inventory": {
            "path": "control/inventory/public_alpha_routes.json",
            "route_counts": {
                classification: route_counts.get(classification, 0)
                for classification in CLASSIFICATION_ORDER
            },
            "total_routes": len(routes),
            "review_required_routes": _routes_by_class(routes, "review_required"),
            "blocked_public_alpha_routes": _routes_by_class(routes, "blocked_public_alpha"),
        },
        "eval_audit": {
            "archive_eval_status": {
                "task_count": archive["total_task_count"],
                "status_counts": archive["status_counts"],
            },
            "search_usefulness_status": {
                "query_count": search["total_query_count"],
                "status_counts": search["eureka_status_counts"],
                "external_pending_counts": search["external_baseline_pending_counts"],
                "top_failure_modes": _top_counts(search["failure_mode_counts"], limit=5),
            },
        },
        "external_baseline_status": {
            "validation_status": baseline["status"],
            "global_pending_slots": global_pending,
            "global_observed_slots": global_observed,
            "batch_0_pending_slots": batch_0.get("pending_observation_count", 0),
            "batch_0_observed_slots": batch_0.get("observed_observation_count", 0),
            "batch_0_expected_slots": batch_0.get("expected_observation_count", 0),
        },
    }


def build_manifest(
    summary: Mapping[str, Any],
    *,
    commit_sha: str | None = None,
    generated_or_recorded_at: str = NORMALIZED_RECORDED_AT,
) -> dict[str, Any]:
    route_inventory = summary["route_inventory"]
    eval_audit = summary["eval_audit"]
    external = summary["external_baseline_status"]
    return {
        "evidence_pack_id": "public_alpha_rehearsal_evidence_v0",
        "created_by_slice": CREATED_BY_SLICE,
        "repository": summary["repository"],
        "branch": summary["branch"],
        "commit_sha": commit_sha or summary["commit_sha"],
        "generated_or_recorded_at": generated_or_recorded_at,
        "no_deployment_performed": True,
        "no_external_network_required": True,
        "static_site_pack": {
            "path": "public_site/",
            "validator_command": "python scripts/validate_public_static_site.py",
            "validation_status": summary["static_site"]["status"],
        },
        "public_alpha_smoke": {
            "command": "python scripts/public_alpha_smoke.py",
            "status": summary["public_alpha_smoke"]["status"],
            "summary": {
                "passed_checks": summary["public_alpha_smoke"]["passed_checks"],
                "total_checks": summary["public_alpha_smoke"]["total_checks"],
            },
        },
        "route_inventory": {
            "path": route_inventory["path"],
            "route_counts": route_inventory["route_counts"],
            "review_required_routes": route_inventory["review_required_routes"],
            "blocked_public_alpha_routes": route_inventory["blocked_public_alpha_routes"],
        },
        "eval_audit": {
            "archive_eval_status": eval_audit["archive_eval_status"],
            "search_usefulness_status": eval_audit["search_usefulness_status"],
            "external_baseline_status": external,
        },
        "limitations": list(LIMITATIONS),
        "required_before_real_deployment": list(REQUIRED_BEFORE_REAL_DEPLOYMENT),
        "signoff_status": "unsigned",
        "notes": [
            "This evidence pack is for supervised local rehearsal only.",
            "No public deployment happened.",
            "No live source probes, crawling, or scraping occurred; external baseline observations remain pending.",
            "The commit_sha field records the commit used when this pack was refreshed; rerun --json for the current local HEAD.",
        ],
    }


def check_pack(summary: Mapping[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (PACK_DIR / relative).exists():
            errors.append(f"missing required evidence file: {relative}")
    manifest_path = PACK_DIR / MANIFEST_NAME
    committed_manifest = _load_json(manifest_path) if manifest_path.exists() else {}
    commit_sha = str(committed_manifest.get("commit_sha", summary["commit_sha"]))
    recorded_at = str(
        committed_manifest.get("generated_or_recorded_at", NORMALIZED_RECORDED_AT)
    )
    expected_manifest = build_manifest(
        summary,
        commit_sha=commit_sha,
        generated_or_recorded_at=recorded_at,
    )
    if committed_manifest != expected_manifest:
        errors.append(f"{MANIFEST_NAME} is stale or malformed")

    expected_files = render_pack_files(expected_manifest)
    for filename, expected_text in expected_files.items():
        path = PACK_DIR / filename
        if not path.exists():
            continue
        if path.read_text(encoding="utf-8") != expected_text:
            errors.append(f"{filename} is stale")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by_slice": CREATED_BY_SLICE,
        "pack_dir": str(PACK_DIR),
        "errors": errors,
        "summary": summary,
    }


def write_pack(manifest: Mapping[str, Any]) -> None:
    PACK_DIR.mkdir(parents=True, exist_ok=True)
    for filename, text in render_pack_files(manifest).items():
        (PACK_DIR / filename).write_text(text, encoding="utf-8")
    (PACK_DIR / MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def render_pack_files(manifest: Mapping[str, Any]) -> dict[str, str]:
    route_inventory = manifest["route_inventory"]
    eval_audit = manifest["eval_audit"]
    external = eval_audit["external_baseline_status"]
    route_counts = route_inventory["route_counts"]
    archive = eval_audit["archive_eval_status"]
    search = eval_audit["search_usefulness_status"]
    review_routes = route_inventory["review_required_routes"]
    blocked_routes = route_inventory["blocked_public_alpha_routes"]

    return {
        "README.md": _lines(
            "# Public Alpha Rehearsal Evidence v0",
            "",
            "This pack records supervised local rehearsal evidence for Eureka's current static site and public-alpha safe-mode posture.",
            "",
            "It is evidence and runbook material only. It does not deploy Eureka, approve production, add live probes, or record external baseline observations.",
            "",
            "No public deployment happened.",
            "",
            "LIVE_ALPHA_01 adds a public alpha wrapper after this evidence snapshot; it still performs no deployment, keeps live probes disabled, and does not approve production.",
            "",
            "Public Publication Plane Contracts v0 sits after the wrapper and governs static generation plus any later live backend handoff. It governs routes, client profiles, public data, base-path portability, deployment targets, redirects, and public claim traceability without enabling live backend behavior.",
            "",
            "GitHub Pages Deployment Enablement v0 now configures a static-only workflow for public_site. It does not host the Python backend, enable live probes, add a custom domain, or prove deployment success without GitHub Actions evidence.",
            "",
            "Static Site Generation Migration v0 now adds a stdlib-only site generator and site/dist validation output, but public_site remains the deployable GitHub Pages artifact. The generated output is not a backend, live probe, custom domain, or production-readiness claim.",
            "",
            "Generated Public Data Summaries v0 now adds deterministic static JSON under public_site/data and site/dist/data. Those files are static summaries only; they are not a live API, live probe, external observation record, or production JSON stability claim.",
            "",
            "Lite/Text/Files Seed Surfaces v0 now adds static compatibility outputs under public_site/lite, public_site/text, and public_site/files, with generated copies under site/dist. These surfaces are no-JS/no-download publication artifacts only; they are not live search, executable mirrors, signed snapshots, relay runtime, native-client runtime, or public-alpha backend approval.",
            "",
            "## Contents",
            "",
            *[f"- `{name}`" for name in REQUIRED_FILES if name != "README.md"],
            "",
            "## Current Summary",
            "",
            f"- branch: `{manifest['branch']}`",
            f"- recorded commit sha: `{manifest['commit_sha']}`",
            f"- static site validation: `{manifest['static_site_pack']['validation_status']}`",
            f"- public-alpha smoke: `{manifest['public_alpha_smoke']['status']}`",
            f"- signoff status: `{manifest['signoff_status']}`",
            "",
            "Run `python scripts/generate_public_alpha_rehearsal_evidence.py --check` to validate the pack.",
            "",
        ),
        "REHEARSAL_SCOPE.md": _lines(
            "# Rehearsal Scope",
            "",
            "This is a supervised local rehearsal evidence pack only.",
            "",
            "- not a public deployment",
            "- not production",
            "- no live source probes",
            "- no crawling",
            "- no auth, TLS, rate limiting, or process manager",
            "- no external observations executed",
            "- no user accounts",
            "- no arbitrary local path access in public-alpha mode",
            "- no Google or Internet Archive scraping",
            "- no hosted service claim",
            "",
        ),
        "COMMIT_AND_ARTIFACTS.md": _lines(
            "# Commit And Artifacts",
            "",
            f"- repository: `{manifest['repository']}`",
            f"- branch: `{manifest['branch']}`",
            f"- recorded commit sha: `{manifest['commit_sha']}`",
            f"- recorded at: `{manifest['generated_or_recorded_at']}`",
            "",
            "## Referenced Artifacts",
            "",
            "- static site pack: `public_site/`",
            "- GitHub Pages artifact checker: `scripts/check_github_pages_static_artifact.py`",
            "- static validator: `scripts/validate_public_static_site.py`",
            "- route inventory: `control/inventory/public_alpha_routes.json`",
            "- smoke script: `scripts/public_alpha_smoke.py`",
            "- readiness review: `docs/operations/PUBLIC_ALPHA_READINESS_REVIEW.md`",
            "- operator checklist: `docs/operations/PUBLIC_ALPHA_OPERATOR_CHECKLIST.md`",
            "- hosting pack: `docs/operations/public_alpha_hosting_pack/`",
            "- archive eval packet: `evals/archive_resolution/`",
            "- search usefulness audit: `evals/search_usefulness/`",
            "- manual observation pack: `evals/search_usefulness/external_baselines/`",
            "",
            "This commit record is evidence metadata, not a deployment record.",
            "",
        ),
        "STATIC_SITE_EVIDENCE.md": _lines(
            "# Static Site Evidence",
            "",
            f"- path: `{manifest['static_site_pack']['path']}`",
            f"- validator command: `{manifest['static_site_pack']['validator_command']}`",
            f"- validator status: `{manifest['static_site_pack']['validation_status']}`",
            "",
            "The validator confirms required pages, local links, current source IDs, required cautionary claims, prohibited-claim absence, no-JS posture, and public-alpha limitation coverage.",
            "",
            "Required cautionary claims include Python reference backend prototype, not production, no scraping, external baselines pending/manual, and placeholders remain placeholders.",
            "",
            "The static site pack is static-only. GitHub Pages may upload it through the configured workflow after validation, but the artifact itself starts no server and hosts no Python backend.",
            "",
        ),
        "SAFE_MODE_EVIDENCE.md": _lines(
            "# Safe Mode Evidence",
            "",
            "Public Alpha Safe Mode exists as constrained local stdlib web/API behavior.",
            "",
            f"- smoke command: `{manifest['public_alpha_smoke']['command']}`",
            f"- smoke status: `{manifest['public_alpha_smoke']['status']}`",
            f"- passed checks: {manifest['public_alpha_smoke']['summary']['passed_checks']} / {manifest['public_alpha_smoke']['summary']['total_checks']}",
            "",
            "The smoke checks verify safe read-only/search/eval routes and blocked caller-provided local path controls.",
            "",
            "Unsafe route variants remain blocked, local-dev-only, or review-required according to the route inventory.",
            "",
            "This evidence does not make a production claim.",
            "",
        ),
        "ROUTE_INVENTORY_EVIDENCE.md": _lines(
            "# Route Inventory Evidence",
            "",
            f"- route inventory: `{route_inventory['path']}`",
            f"- total routes: {sum(route_counts.values())}",
            f"- safe_public_alpha: {route_counts['safe_public_alpha']}",
            f"- blocked_public_alpha: {route_counts['blocked_public_alpha']}",
            f"- local_dev_only: {route_counts['local_dev_only']}",
            f"- review_required: {route_counts['review_required']}",
            f"- deferred: {route_counts['deferred']}",
            "",
            "## Review-Required Routes",
            "",
            *(_bullet_code_list(review_routes) or ["- none"]),
            "",
            "## Blocked Public-Alpha Routes",
            "",
            *(_bullet_code_list(blocked_routes) or ["- none"]),
            "",
        ),
        "EVAL_AND_AUDIT_EVIDENCE.md": _lines(
            "# Eval And Audit Evidence",
            "",
            f"- archive eval task count: {archive['task_count']}",
            f"- archive eval status counts: `{json.dumps(archive['status_counts'], sort_keys=True)}`",
            f"- search usefulness query count: {search['query_count']}",
            f"- search usefulness status counts: `{json.dumps(search['status_counts'], sort_keys=True)}`",
            f"- external pending counts: `{json.dumps(search['external_pending_counts'], sort_keys=True)}`",
            "",
            "Archive hard evals are internally satisfied against the current fixture-backed corpus. This is regression evidence, not production relevance proof.",
            "",
            "Search Usefulness Audit still records source gaps, capability gaps, compatibility-evidence gaps, planner gaps, representation gaps, and member-access gaps.",
            "",
            "Python oracle golden checks and hardening tests remain separate verification lanes.",
            "",
        ),
        "EXTERNAL_BASELINE_STATUS.md": _lines(
            "# External Baseline Status",
            "",
            f"- validation status: `{external['validation_status']}`",
            f"- global pending slots: {external['global_pending_slots']}",
            f"- global observed slots: {external['global_observed_slots']}",
            f"- Batch 0 expected slots: {external['batch_0_expected_slots']}",
            f"- Batch 0 pending slots: {external['batch_0_pending_slots']}",
            f"- Batch 0 observed slots: {external['batch_0_observed_slots']}",
            "",
            "No Google or Internet Archive observations were performed for this pack.",
            "",
            "No comparison report should be created until a human records observations with the governed manual process.",
            "",
        ),
        "OPERATOR_CHECKLIST_STATUS.md": _lines(
            "# Operator Checklist Status",
            "",
            "- checklist: `docs/operations/PUBLIC_ALPHA_OPERATOR_CHECKLIST.md`",
            "- status: `unsigned`",
            "- rehearsal evidence pack prepared: yes",
            "- real deployment approved: no",
            "",
            "The checklist must be completed by an operator before any real public hosting decision.",
            "",
        ),
        "BLOCKERS_AND_LIMITATIONS.md": _lines(
            "# Blockers And Limitations",
            "",
            *[f"- {item}" for item in manifest["limitations"]],
            "",
            "These blockers remain explicit. This pack does not waive or resolve them.",
            "",
        ),
        "NEXT_DEPLOYMENT_REQUIREMENTS.md": _lines(
            "# Next Deployment Requirements",
            "",
            "Before any real public hosting, a separate future milestone must:",
            "",
            *[f"- {item}" for item in manifest["required_before_real_deployment"]],
            "",
            "Live probes must remain disabled until a future source-probe gateway contract and abuse-control posture exist.",
            "",
        ),
        "SIGNOFF_TEMPLATE.md": _lines(
            "# Signoff Template",
            "",
            "- operator: `<operator>`",
            "- date/time: `<manual timestamp>`",
            f"- commit sha: `{manifest['commit_sha']}`",
            "- hosting target, if any: `<none for this pack>`",
            "- static validator status: `<pass/fail>`",
            "- public-alpha smoke status: `<pass/fail>`",
            "- route inventory reviewed: `<yes/no>`",
            "- external baselines status reviewed: `<yes/no>`",
            "- blockers accepted: `<yes/no>`",
            "- approval status: `unsigned/unapproved`",
            "- notes: `<operator notes>`",
            "",
            "This template is unsigned by default and does not approve deployment.",
            "",
        ),
    }


def format_plain_summary(
    summary: Mapping[str, Any],
    manifest: Mapping[str, Any],
    status: str,
) -> str:
    route_counts = summary["route_inventory"]["route_counts"]
    archive = summary["eval_audit"]["archive_eval_status"]
    search = summary["eval_audit"]["search_usefulness_status"]
    external = summary["external_baseline_status"]
    return _lines(
        "Public Alpha Rehearsal Evidence",
        f"status: {status}",
        f"branch: {manifest['branch']}",
        f"commit_sha: {manifest['commit_sha']}",
        f"static_site: {manifest['static_site_pack']['validation_status']}",
        f"public_alpha_smoke: {manifest['public_alpha_smoke']['status']}",
        f"routes: safe={route_counts['safe_public_alpha']}, blocked={route_counts['blocked_public_alpha']}, local_dev_only={route_counts['local_dev_only']}, review_required={route_counts['review_required']}",
        f"archive_evals: task_count={archive['task_count']}, status_counts={archive['status_counts']}",
        f"search_usefulness: query_count={search['query_count']}, status_counts={search['status_counts']}",
        f"external_baselines: pending={external['global_pending_slots']}, observed={external['global_observed_slots']}",
        f"signoff_status: {manifest['signoff_status']}",
        "",
    )


def format_check_report(report: Mapping[str, Any]) -> str:
    lines = [
        "Public Alpha Rehearsal Evidence Check",
        f"status: {report['status']}",
        f"pack_dir: {report['pack_dir']}",
    ]
    if report["errors"]:
        lines.append("")
        lines.append("Errors")
        lines.extend(f"- {error}" for error in report["errors"])
    lines.append("")
    return "\n".join(lines)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _routes(inventory: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    routes = inventory.get("routes")
    if not isinstance(routes, list):
        raise ValueError("public_alpha_routes.json must contain a routes list")
    return [route for route in routes if isinstance(route, Mapping)]


def _routes_by_class(
    routes: Sequence[Mapping[str, Any]],
    classification: str,
) -> list[str]:
    return [
        str(route["route_pattern"])
        for route in routes
        if route.get("classification") == classification
    ]


def _top_counts(counts: Mapping[str, int], *, limit: int) -> dict[str, int]:
    ordered = sorted(counts.items(), key=lambda item: (-int(item[1]), item[0]))
    return {key: int(value) for key, value in ordered[:limit]}


def _git_value(*args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return completed.stdout.strip() or "unknown"


def _bullet_code_list(values: Sequence[str]) -> list[str]:
    return [f"- `{value}`" for value in values]


def _lines(*lines: str) -> str:
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
