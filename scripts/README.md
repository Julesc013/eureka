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
- `validate_public_static_site.py`: validates the no-JS `site/dist/` static
  public-site pack by default, or a generated artifact with `--site-root`,
  including its manifest, required pages, local links,
  source matrix coverage, required cautionary phrases, prohibited claims, and
  public-alpha limitations; it supports `--json`, performs no network calls,
  starts no server, and deploys nothing
- `validate_publication_inventory.py`: validates the governed publication-plane
  inventory under `control/inventory/publication/`, including required contract
  files, route stability vocabulary, public status taxonomy, current
  `site/dist/` page coverage, future reserved routes, client profiles,
  deployment target semantics, public data entries, empty redirect policy, and
  claim traceability docs; it supports `--json`, performs no network calls,
  starts no server, adds no provider configuration, creates no generator, and
  deploys nothing
- `check_github_pages_static_artifact.py`: validates that `site/dist/` is safe
  to upload as the GitHub Pages artifact, including required files, publication
  target settings, base-path-safe links, no runtime/source/secrets/local-store
  files, no backend, and no live probes; it supports `--json`, performs no
  network calls, starts no server, adds no custom domain, and does not claim a
  successful deployment
- `validate_static_host_readiness.py`: validates domain and alternate-static-host
  readiness inventories, confirms no `site/dist/CNAME`, DNS/provider config,
  custom-domain claim, backend hosting, live probes, or root-relative static
  links are present, supports `--json`, performs no network calls, and deploys
  nothing
- `validate_live_backend_handoff.py`: validates the Live Backend Handoff
  Contract v0 inventories, reserved `/api/v1` route registry, disabled live
  capability flags, error-envelope docs, and static-page no-live-backend
  claims; it supports `--json`, performs no network calls, starts no backend,
  adds no route handlers, and does not make `/api/v1` live
- `validate_live_probe_gateway.py`: validates the Live Probe Gateway Contract
  v0 inventory, disabled candidate-source gates, cache/evidence policies,
  Google-manual-baseline-only posture, public-alpha wrapper live-probe closure,
  live backend handoff alignment, and docs/static-page no-live-probe claims; it
  supports `--json`, performs no network calls, implements no adapters, fetches
  no URLs, enables no downloads, and does not call Internet Archive or any
  external source
- `validate_compatibility_surfaces.py`: validates Compatibility Surface
  Strategy v0 inventories, including the surface capability matrix, route
  matrix, client-profile alignment, implemented static route roots, future
  snapshot/relay/native/API posture, old-client degradation docs, and static
  page no-live/no-production claims; it supports `--json`, performs no network
  calls, adds no runtime behavior, and does not make snapshots, relay services,
  native clients, live backend routes, or live probes available
- `generate_public_data_summaries.py`: generates, updates, or checks
  deterministic static JSON summaries under `site/dist/data/` by default,
  including site, page-registry, source, eval, route, and build summaries; it
  supports `--update`, `--check`, `--output-root`, and `--json`, performs no
  network calls, runs no live probes, records no external observations, starts
  no server, deploys nothing, and does not create live API semantics
- `generate_compatibility_surfaces.py`: generates, updates, or checks static
  lite/text/files compatibility seed surfaces under `site/dist/lite/`,
  `site/dist/text/`, and `site/dist/files/` by default from generated
  public data summaries; it supports `--update`, `--check`, `--output-root`,
  `--data-root`, and `--json`, generates a file-tree manifest and SHA256SUMS,
  performs no network calls, runs no live search or probes, records no external
  observations, adds no executable downloads, and does not create production
  signed snapshots, a public `/snapshots/` route, relay behavior,
  native-client runtime, or live API semantics
- `generate_static_snapshot.py`: generates, updates, or checks the
  deterministic Signed Snapshot Format v0 seed example under
  `snapshots/examples/static_snapshot_v0/`; it supports `--update`, `--check`,
  `--output-root`, `--data-root`, and `--json`, generates
  `SNAPSHOT_MANIFEST.json`, `BUILD_MANIFEST.json`, uppercase public-data
  projections, `CHECKSUMS.SHA256`, and `SIGNATURES.README.txt`, performs no
  network calls, includes no real signing keys or executable downloads, and
  does not publish a public `/snapshots/` route
- `validate_post_queue_checkpoint.py`: validates the committed post-queue
  checkpoint audit pack under `control/audits/post-queue-state-checkpoint-v0/`,
  including required files, structured JSON report shape, command results,
  eval/audit status, external-baseline representation, next milestones,
  human-operated work, and no production/live/external-observation claims; it
  supports `--json`, performs no network calls, and adds no product behavior
- `validate_static_snapshot.py`: validates the Signed Snapshot Format v0
  contract and seed example, checks JSON parsing and SHA256SUMS entries,
  rejects private keys, env files, executables, large/binary artifacts, local
  absolute paths, live backend/probe claims, external-observation claims, and
  production signing claims; it supports `--json` and performs no network calls
- `validate_snapshot_consumer_contract.py`: validates the Signed Snapshot
  Consumer Contract v0 inventories, docs, required read order against the seed
  snapshot, disabled production/native/relay consumer flags, checksum and v0
  signature-placeholder language, profile limits, and no-key posture; it
  supports `--json`, performs no network calls, and implements no consumer,
  relay, native client, production signing, executable download, live backend,
  or live probe behavior
- `validate_native_client_contract.py`: validates the Native Client Contract v0
  inventories, Windows/Mac lane registry, CLI current-state flag, snapshot and
  public-data dependencies, readiness checklist, no native project-file
  posture, no install/download automation claims, and no Rust FFI/runtime
  wiring; it supports `--json`, performs no network calls, and implements no
  native client, GUI, installer, relay, FFI, live backend, or live probe
  behavior
- `validate_action_policy.py`: validates the Native Action / Download /
  Install Policy v0 inventory, action/download/install policy docs,
  executable-risk and rights/access docs, install-handoff contract,
  public-alpha/static defaults, and related native/snapshot/relay references;
  it supports `--json`, performs no network calls, and implements no downloads,
  installers, package-manager integration, malware scanning, rights clearance,
  native clients, relay runtime, public download surface, or executable trust
  claim
- `validate_local_cache_privacy_policy.py`: validates the Native Local Cache /
  Privacy Policy v0 inventory, local cache/privacy docs, native cache contract,
  telemetry/logging policy, disabled cache/private-ingestion/telemetry/account/
  cloud-sync flags, prohibited private-data behaviors, and native/snapshot/
  relay/public-alpha references; it supports `--json`, performs no network
  calls, and implements no cache runtime, private file ingestion, local archive
  scanning, telemetry, analytics, accounts, cloud sync, uploads, native clients,
  or relay runtime
- `validate_native_project_readiness_review.py`: validates the Native Client
  Project Readiness Review v0 audit pack, JSON decision, first candidate lane,
  pre-native checklist, human-approval gate, and no-native-project-file posture;
  it supports `--json`, performs no network calls, and implements no Visual
  Studio/Xcode project, native app, GUI behavior, FFI, downloads, installers,
  cache runtime, relay runtime, live probes, or runtime wiring
- `validate_windows_winforms_skeleton_plan.py`: validates the Windows 7
  WinForms Native Skeleton Planning v0 pack, proposed path/namespace, build-host
  requirements, human-approval gate, allowed static-data/snapshot-demo scope,
  prohibited features, and no-native-project-file posture; it supports `--json`,
  performs no network calls, and implements no Visual Studio solution, C#
  project, C# source, GUI behavior, FFI, downloads, installers, cache runtime,
  telemetry, relay runtime, live probes, or runtime wiring
- `validate_relay_surface_design.py`: validates the Relay Surface Design v0
  inventory, docs, unsigned future operator checklist, surface capability
  alignment, route-matrix posture, and disabled-by-default relay safety flags;
  it supports `--json`, performs no network calls, opens no sockets, and adds
  no relay runtime, protocol server, local HTTP relay, proxy, private data path,
  write/admin route, live-probe passthrough, native sidecar, or production relay
  claim
- `validate_relay_prototype_plan.py`: validates the Relay Prototype Planning v0
  pack, local static HTTP first-candidate decision, allowed/prohibited
  input/output contracts, localhost-only/read-only/static security defaults,
  human-approval gate, and no-runtime/no-socket posture; it supports `--json`,
  performs no network calls, opens no sockets, and adds no relay server, local
  HTTP relay, protocol support, private file serving, live backend proxying,
  live probes, native sidecar, snapshot mount, downloads, installers, telemetry,
  or relay runtime wiring
- `generate_static_resolver_demos.py`: generates, updates, or checks static
  resolver demo snapshots under `site/dist/demo/` by default from generated
  public data summaries and fixture-backed Python-oracle outputs; it supports
  `--update`, `--check`, `--output-root`, `--data-root`, and `--json`, performs
  no network calls, runs no live search or probes, records no external
  observations, starts no backend, and does not create live API semantics,
  snapshots, relay behavior, native-client runtime, or production behavior
- `site/build.py` and `site/validate.py`: build and validate the stdlib-only
  static-site source tree into canonical `site/dist/`; `site/build.py` also
  emits generated public data summaries into
  `site/dist/data/` and generated lite/text/files seed surfaces into
  `site/dist/lite/`, `site/dist/text/`, `site/dist/files/`, and static resolver
  demo snapshots into `site/dist/demo/`; they keep `site/dist/` as the single
  generated deployment artifact and add no Node/npm, frontend framework, live
  backend calls, live probes, external web APIs, downloads, or production
  deployment claim
- `generate_public_alpha_rehearsal_evidence.py`: summarizes, updates, or
  checks Public Alpha Rehearsal Evidence v0 by validating the static site,
  running the in-process public-alpha smoke checks, counting route inventory
  classifications, running archive/search eval summaries, and checking manual
  external-baseline status without deployment, browser automation, network
  calls, live probes, scraping, or external observation collection
- `run_public_alpha_server.py`: validates or starts the existing stdlib web/API
  backend through the LIVE_ALPHA_01 public-alpha wrapper with safe defaults,
  localhost binding, explicit nonlocal-bind acknowledgement, live probes and
  live Internet Archive access disabled, local path controls refused,
  downloads/readback and user storage disabled or route-blocked, and
  JSON-safe config/status summaries; it does not deploy, add provider
  configuration, add auth/TLS/rate limiting/process management, scrape, crawl,
  or call external APIs
- `public_alpha_smoke.py`: runs the local Public Alpha Deployment Readiness smoke checks directly against the stdlib WSGI app, verifies safe status/source/query/search/eval routes, verifies blocked local-path/readback routes, supports `--json`, and exits nonzero if the constrained public-alpha posture regresses
- `generate_public_alpha_hosting_pack.py`: reads `control/inventory/public_alpha_routes.json` and emits or checks the Public Alpha Hosting Pack route-safety summary; it supports `--check` for repeatable docs validation and does not deploy, host, or mutate route behavior
- `generate_python_oracle_golden.py`: generates or checks the Rust Parity Fixture Pack v0 Python-oracle golden outputs under `tests/parity/golden/python_oracle/v0/`; it supports `--check`, optional `--output-root`, and `--json`, normalizes unstable timestamps, local index paths, FTS mode, and generation metadata, and does not implement Rust behavior or replace Python runtime paths
- `check_rust_source_registry_parity.py`: validates the Rust Source Registry
  Parity Catch-up v0 fixture map and isolated Rust source structure against
  the current nine-source Python oracle shape; it supports `--json` and
  `--require-cargo`, runs crate-local Rust source-registry tests only when
  Cargo is available, reports Cargo as skipped otherwise, and does not wire
  Rust into Python runtime, web, CLI, HTTP API, workers, or public-alpha paths
- `check_rust_query_planner_parity.py`: validates the Rust Query Planner
  Parity Candidate v0 fixture map and isolated Rust source structure; it
  supports `--json` and `--require-cargo`, runs crate-local Rust
  query-planner tests only when Cargo is available, reports Cargo as skipped
  otherwise, and does not wire Rust into Python runtime, web, CLI, HTTP API,
  workers, or public-alpha paths
- `validate_rust_local_index_parity_plan.py`: validates the Rust Local Index
  Parity Planning v0 plan, fixture map, acceptance schema, current Python
  local-index golden references, and no-runtime-wiring posture; it supports
  `--json`, requires no Cargo, and does not implement Rust local-index,
  SQLite/indexing, or runtime behavior
- `validate_full_project_state_audit.py`: validates the Full Project State
  Audit v0 pack under `control/audits/full-project-state-audit-v0/`, including
  required files, structured report fields, milestone/verification summaries,
  external-baseline and eval/search status, risk register, next milestone plan,
  human-operated work, explicit deferrals, command results, and no-overclaim
  guardrails; it supports `--json` and adds no product behavior
- `validate_public_data_stability.py`: validates Public Data Contract
  Stability Review v0 under
  `control/audits/public-data-contract-stability-review-v0/`, including
  generated public data file coverage, field stability classes, stable-draft
  field presence, public-data contract policy references, snapshot/native/relay
  policy references, and no production API stability claims; it supports
  `--json` and adds no product behavior
- `check_generated_artifact_drift.py`: validates Generated Artifact Drift Guard
  v0 by reading `control/inventory/generated_artifacts/`, checking declared
  artifact paths, resolving check commands, and delegating to existing
  generator/validator commands for public data, compatibility surfaces, static
  demos, seed snapshots, `site/dist`, Python oracle goldens, public-alpha
  rehearsal evidence, publication inventories, test registry metadata, and AIDE
  metadata; it supports `--json`, `--list`, `--artifact`, and `--strict`, does
  not run update commands, and adds no product behavior
- `validate_static_artifact_promotion_review.py`: validates Static Artifact
  Promotion Review v0, enforcing the audit pack, `site/dist` as active static
  artifact, the `static_site_dist` generated-artifact group, the `site/dist`
  workflow upload path, stale-reference review coverage, and honest unverified
  GitHub Actions status without network calls or deployment
- `validate_github_pages_run_evidence.py`: validates GitHub Pages Run Evidence
  Review v0, enforcing the audit pack, `site/dist` workflow upload path,
  static-only posture, recorded Actions status, no deployment-success claim
  unless evidence is verified, and required operator actions for failed or
  unavailable evidence; it performs no network calls and deploys nothing
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

Deterministic tests and demo flows now cover a bounded mixed corpus composed
from governed synthetic fixtures, small recorded GitHub Releases fixtures, tiny
recorded Internet Archive-like fixtures, and committed local bundle fixtures.
They also surface the current bounded engine, public-alpha, publication,
GitHub Pages artifact, generated public-data summary, and stdlib static-site
generator checks plus static snapshot generation/validation, static-host
readiness, live-backend handoff, live probe gateway, compatibility-surface strategy, and isolated Rust query-planner
parity structure checks,
without implying
a final provenance, trust, merge, object-identity, ranking, compatibility
oracle, fuzzy retrieval, vector search, download, installer, extraction,
runtime-routing, personalization, async scheduling, distributed workers,
execution, streaming, cloud memory, production relevance benchmark, auth,
HTTPS/TLS, accounts, rate limiting, production logging, production process
management, backend deployment infrastructure, generated-artifact deployment,
custom-domain configuration, alternate-host deployment, DNS changes, CNAME
configuration, live `/api/v1` backend, production API guarantee, Rust runtime
replacement, Rust planner runtime wiring, production signed snapshot release,
real signing keys, public `/snapshots/` route, relay service, native app project, live source probing, live probe adapters,
crawling, live Internet Archive API access, arbitrary local filesystem
ingestion, or full
investigation-planning architecture. Live GitHub acquisition remains
intentionally deferred.
