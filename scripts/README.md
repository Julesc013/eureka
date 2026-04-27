# Scripts

This directory holds lightweight repo support scripts.

Current scripts:

- `check_architecture_boundaries.py`: runs the narrow bootstrap architectural-boundary checker for Python imports and enforces the current proven layering between surfaces, `runtime/gateway/public_api`, connectors, and engine; it emits readable text by default, supports `--json`, and remains a repo-local guardrail rather than a universal policy engine
- `run_archive_resolution_evals.py`: runs Archive Resolution Eval Runner v0 over `evals/archive_resolution/`, optionally selects one task with `--task`, optionally builds an explicit Local Index v0 path with `--index-path`, writes stable JSON with `--output`, and emits either a plain text summary or `--json`; it is a local deterministic regression harness and not a ranking, fuzzy, vector, semantic, LLM, crawling, or production relevance benchmark
- `run_search_usefulness_audit.py`: runs Search Usefulness Audit v0 over
  `evals/search_usefulness/`, optionally selects one query with `--query`,
  optionally builds an explicit Local Index v0 path with `--index-path`,
  writes stable JSON with `--output`, and emits either a plain text summary or
  `--json`; it classifies current Eureka usefulness, failure modes, and
  future-work labels while marking external baselines as pending manual
  observations
- `record_search_baseline_observation.py`: creates or validates manual
  external-baseline observation JSON for the search-usefulness audit; it does
  not perform web search, Google scraping, Internet Archive scraping, or
  network access
- `validate_external_baseline_observations.py`: validates the governed manual
  external-baseline observation area, pending slots, one explicit `--file`,
  and any future human observation records without querying external systems
- `report_external_baseline_status.py`: reports manual external-baseline
  pending/observed coverage, including Batch 0 progress and `--next-pending`
  summaries, without scraping, API calls, or automated searches
- `list_external_baseline_observations.py`: lists pending or observed manual
  baseline slots by batch, query id, system id, or status without opening
  browsers, fetching URLs, scraping, or querying external systems
- `create_external_baseline_observation.py`: creates one fillable pending
  manual observation JSON file from a batch slot or prints it with `--stdout`;
  it never marks the record observed, populates top results, fetches URLs, or
  automates external searches
- `public_alpha_smoke.py`: runs the local Public Alpha Deployment Readiness smoke checks directly against the stdlib WSGI app, verifies safe status/source/query/search/eval routes, verifies blocked local-path/readback routes, supports `--json`, and exits nonzero if the constrained public-alpha posture regresses
- `generate_public_alpha_hosting_pack.py`: reads `control/inventory/public_alpha_routes.json` and emits or checks the Public Alpha Hosting Pack route-safety summary; it supports `--check` for repeatable docs validation and does not deploy, host, or mutate route behavior
- `generate_python_oracle_golden.py`: generates or checks the Rust Parity Fixture Pack v0 Python-oracle golden outputs under `tests/parity/golden/python_oracle/v0/`; it supports `--check`, optional `--output-root`, and `--json`, normalizes unstable timestamps, local index paths, FTS mode, and generation metadata, and does not implement Rust behavior or replace Python runtime paths
- `demo_resolution_slice.py`: submits and reads the local deterministic gateway thin slice against the bounded demo corpus, with an optional shared workbench session view-model projection
- `demo_web_workbench.py`: renders the compatibility-first web workbench, deterministic search page, deterministic query-plan page, bootstrap local-index pages, bounded source-registry page, bounded source detail page, bounded synchronous local-task pages, bounded synchronous resolution-runs page, explicit local resolution-memory pages, bounded representations page, bounded compatibility page, bounded handoff page, bounded action-plan page, bounded acquisition page, bounded member-preview page, or bundle inspection page either once to stdout, or starts a tiny stdlib local server that also exposes the bounded subject/state page plus the bounded decomposition page, exports a bounded resolution manifest as JSON, exports a deterministic resolution bundle ZIP to stdout, builds and queries a bootstrap local SQLite index through shared public boundaries, fetches one bounded local payload fixture for one explicit representation, inspects one fetched bounded representation into a compact member listing when the format is supported, reads one bounded member from one decomposed representation as a compact preview when the member is text-like, stores manifest or bundle exports under a caller-provided local store root, prints bounded resolution-run URLs when a caller provides a bootstrap run-store root, prints bounded local-task URLs when a caller provides a bootstrap task-store root, prints bounded resolution-memory URLs when a caller provides a bootstrap memory-store root, lists stored exports for a target, reads stored artifacts by stable artifact identity, or inspects a local bundle path as JSON, while supporting `--mode local_dev` and `--mode public_alpha`; public-alpha mode blocks caller-provided local path controls and local write/readback route groups without adding auth, HTTPS/TLS, accounts, or production deployment semantics
- `demo_cli_workbench.py`: exposes the same bootstrap exact-resolution, deterministic search, deterministic query planning, bootstrap local-index build plus query plus status, synchronous local-task creation plus lookup plus listing, bounded synchronous resolution-run creation plus lookup, explicit local resolution-memory creation plus lookup plus listing, bounded source-registry listing/detail lookup plus coverage/capability filters, bounded representations listing, bounded handoff evaluation, bounded acquisition and fetch, bounded decomposition and member inspection, bounded member preview and readback, bounded action-plan evaluation, bounded strategy-aware action-plan evaluation, bounded compatibility evaluation with source-backed compatibility evidence where current fixtures support it, bounded absence reasoning, bounded subject/state listing, side-by-side comparison, manifest export, bundle export, bundle inspection, and local stored-export capabilities through the first stdlib-only native CLI surface, staying on the public side of the architecture without committing to a final CLI or TUI stack
- `demo_http_api.py`: fetches the first local stdlib machine-readable HTTP API slice over the same transport-neutral public boundary already reused by the HTML and CLI surfaces, including the bounded `/api/status`, `/api/query-plan`, `/api/index/build`, `/api/index/status`, `/api/index/query`, `/api/tasks`, `/api/task`, `/api/task/run/*`, `/api/runs`, `/api/run`, `/api/run/resolve`, `/api/run/search`, `/api/run/planned-search`, `/api/memories`, `/api/memory`, `/api/memory/create`, `/api/action-plan`, `/api/absence/*`, `/api/compare`, `/api/states`, `/api/sources`, `/api/source`, `/api/representations`, `/api/handoff`, `/api/fetch`, `/api/decompose`, `/api/member`, and `/api/compatibility` seams, returning JSON, ZIP, or bounded payload bytes and self-hosting a temporary local stdlib server when `--base-url` is omitted; `/api/sources` and `/api/source` include safe source capability and coverage-depth fields, and `--mode public_alpha status` exercises the constrained safe-mode status path

Current enforced checker rules:

- `surfaces/web/**` must not import `runtime/engine/**` or `runtime/connectors/**`
- `surfaces/native/**` currently follows the same surface-side rule, with the active concrete slice under `surfaces/native/cli/**`
- `surfaces/web/**` and `surfaces/native/**` may import runtime only through `runtime/gateway/public_api/**`
- `surfaces/web/**` and `surfaces/native/**` may import only same-surface helpers under `surfaces/**`
- `runtime/gateway/public_api/**` must not import `surfaces/**`
- `runtime/connectors/**` must not import `surfaces/**`
- `runtime/engine/**` must not import `surfaces/**`

These scripts are bootstrap utilities and repo-local checks, not stable product CLIs, durable network tooling, or a finalized policy stack.

The repo-level command registry and reusable verification lanes live under
`control/inventory/tests/`. That registry references the scripts above, the
major unittest discovery commands, public-alpha smoke checks, archive/search
eval runners, Python-oracle golden checks, Hard Test Pack v0 under
`tests/hardening/`, and optional Cargo checks without turning them into product
runtime behavior.

Deterministic tests and demo flows now cover a bounded mixed corpus composed from governed synthetic fixtures, small recorded GitHub Releases fixtures, tiny recorded Internet Archive-like fixtures, and committed local bundle fixtures. They also surface the first bounded evidence-summary seam, the first bounded comparison/disagreement seam, the first bounded object/state timeline seam, the first bounded absence-reasoning seam, the first bounded representation/access-path seam, the first bounded compatibility seam, the first bounded compatibility-evidence seam, the first bounded action-routing seam, the first bounded user-strategy seam, the first bounded representation-selection and handoff seam, the first bounded acquisition and fetch seam, the first bounded decomposition and package-member seam, the first bounded member-readback and preview seam, the first bounded synchronous local-task seam, the first bounded synchronous resolution-run seam, the first bounded explicit local resolution-memory seam, the first bounded deterministic query-planner seam, Old-Platform Software Planner Pack v0, the first bounded local SQLite index seam, the first executable archive-resolution eval-runner seam, the first public-alpha safe-mode seam, the first public-alpha readiness smoke seam, the first public-alpha hosting-pack summary seam, the first Python-oracle golden fixture-pack seam, the first high-risk hardening test pack, the first source coverage/capability metadata seam, Real Source Coverage Pack v0, Member-Level Synthetic Records v0, and Result Lanes + User-Cost Ranking v0 without implying a final provenance, trust, merge, object-identity, ranking, compatibility oracle, fuzzy retrieval, vector search, download, installer, extraction, runtime-routing, personalization, async scheduling, distributed workers, execution, streaming, cloud memory, production relevance benchmark, auth, HTTPS/TLS, accounts, rate limiting, production logging, production process management, deployment infrastructure, Rust runtime replacement, live source probing, crawling, live Internet Archive API access, arbitrary local filesystem ingestion, or full investigation-planning architecture. Live GitHub acquisition remains intentionally deferred.
