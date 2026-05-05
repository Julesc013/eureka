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
- `validate_public_search_contract.py`: validates Public Search API Contract
  v0 request, response, error, and local/prototype route envelopes, enforcing
  `local_index_only` as the only implemented mode, required error codes,
  forbidden URL/local-path/download/install/upload/credential parameters,
  disabled live probes, local runtime route status, and no hosted public-search
  or production API claim; it supports `--json` and performs no network calls
- `validate_public_search_result_card_contract.py`: validates Public Search
  Result Card Contract v0 schema, examples, audit pack, docs, response-schema
  alignment, required result lanes, user-cost bounds, action status separation,
  blocked/future-gated unsafe actions, rights/risk caveats, field stability,
  and no live-search, malware-safety, rights-clearance, download/install/execute
  or production-ranking claim; it supports `--json`, performs no network calls,
  and implements no runtime route behavior
- `validate_public_search_safety.py`: validates Public Search Safety / Abuse
  Guard v0 inventory, docs, request/error schema alignment, local runtime route status,
  disabled modes, request/result/time limits, forbidden URL/local-path/action
  and credential parameters, logging/privacy defaults, operator controls, and
  runtime-readiness checklist; it supports `--json`, performs no network calls,
  and implements no rate-limit middleware, telemetry runtime, hosted backend, or
  live search behavior
- `validate_local_public_search_runtime.py`: validates Local Public Search
  Runtime v0 files, route inventory, safety inventory, public-alpha route
  inventory, docs, and no prohibited live/download/install/upload behavior; it
  supports `--json`, performs no network calls, and does not deploy or host
  public search
- `validate_public_search_static_handoff.py`: validates Public Search Static
  Handoff v0 inventory, generated `site/dist/search.html`, lite/text/files
  handoff outputs, `data/search_handoff.json`, disabled hosted-search form,
  query-length safety alignment, no-JS posture, no fake hosted URL, and no
  live-probe/download/install/upload/local-path claim; it supports `--json`,
  performs no network calls, starts no server, and deploys nothing
- `validate_static_site_search_integration.py`: validates P56 static search
  integration, including the audit pack, generated search page, lite/text/files
  search surfaces, `data/search_config.json`, `data/public_index_summary.json`,
  backend-unconfigured honesty, no-JS posture, disabled live/download/upload/
  local-path/arbitrary-URL flags, docs, and public-index summary alignment; it
  supports `--json`, performs no network calls, starts no backend, and deploys
  nothing
- `run_public_search_safety_evidence.py`: collects P57 local public-search
  safety evidence through the hosted-wrapper in-process harness, including safe
  queries, blocked requests, limit checks, status checks, static handoff safety,
  public index safety, and privacy/redaction checks; it performs no external
  calls, starts no public listener, and deploys nothing
- `validate_public_search_safety_evidence.py`: validates the P57 audit pack,
  runner output, forbidden-parameter category coverage, hard false booleans,
  static handoff review, public index review, and operator-gated rate-limit/edge
  status; it supports `--json`, performs no network calls, and makes no hosted
  backend or production claim
- `validate_compatibility_surfaces.py`: validates Compatibility Surface
  Strategy v0 inventories, including the surface capability matrix, route
  matrix, client-profile alignment, implemented static route roots, future
  snapshot/relay/native/API posture, old-client degradation docs, and static
  page no-live/no-production claims; it supports `--json`, performs no network
  calls, adds no runtime behavior, and does not make snapshots, relay services,
  native clients, live backend routes, or live probes available
- `generate_public_data_summaries.py`: generates, updates, or checks
  deterministic static JSON summaries under `site/dist/data/` by default,
  including site, page-registry, source, eval, route, search-handoff, static
  search config, public index summary, and build summaries; it
  supports `--update`, `--check`, `--output-root`, and `--json`, performs no
  network calls, runs no live probes, records no external observations, starts
  no server, deploys nothing, and does not create live API semantics
- `generate_compatibility_surfaces.py`: generates, updates, or checks static
  lite/text/files compatibility seed surfaces under `site/dist/lite/`,
  `site/dist/text/`, and `site/dist/files/` by default from generated
  public data summaries, including the static search handoff pages for old
  clients; it supports `--update`, `--check`, `--output-root`,
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
- `public_search_smoke.py`: runs Local Public Search Runtime v0 smoke checks
  directly against the stdlib WSGI app without opening a listener, verifying
  status, search, query-plan, sources, HTML search, forbidden local path/URL
  parameters, disabled live probes, and query length limits; it supports
  `--json` and performs no external network calls
- `validate_search_usefulness_delta_v2.py`: validates the Search Usefulness
  Delta v2 audit pack, compares current counts to
  `run_search_usefulness_audit.py --json`, checks the P32 baseline/report
  relationship, confirms external baselines remain pending/manual, and enforces
  source-family impact, hard-eval status, public-search smoke status, remaining
  gaps, recommendations, and no unsupported superiority/hosted-readiness claims;
  it supports `--json` and performs no network calls
- `validate_source_pack.py`: validates Source Pack Contract v0 directories.
  By default it checks the synthetic example pack under
  `examples/source_packs/minimal_recorded_source_pack_v0/`, including
  `SOURCE_PACK.json`, JSONL records, rights/privacy posture, disabled
  live/network behavior, checksum coverage, private-path rejection, and
  executable payload rejection. It supports `--pack-root`, `--json`, and
  `--strict`, and does not import, index, upload, execute, or contact a
  network
- `validate_evidence_pack.py`: validates Evidence Pack Contract v0 directories.
  By default it checks the synthetic example pack under
  `examples/evidence_packs/minimal_evidence_pack_v0/`, including
  `EVIDENCE_PACK.json`, JSONL evidence/source-reference records, evidence id
  uniqueness, allowed claim types, snippet limits, rights/privacy posture,
  checksum coverage, private-path rejection, and executable payload rejection.
  It supports `--pack-root`, `--json`, and `--strict`, and does not import,
  index, upload, execute, fetch, scrape, or contact a network
- `validate_index_pack.py`: validates Index Pack Contract v0 directories. By
  default it checks the synthetic example pack under
  `examples/index_packs/minimal_index_pack_v0/`, including `INDEX_PACK.json`,
  index/source/field coverage JSON, record-summary JSONL, query examples,
  checksum coverage, privacy/status consistency, private-path rejection, raw
  SQLite/cache rejection, and executable payload rejection. It supports
  `--pack-root`, `--json`, and `--strict`, and does not import, merge, index,
  upload, export databases, execute, fetch, scrape, or contact a network
- `validate_contribution_pack.py`: validates Contribution Pack Contract v0
  directories. By default it checks the synthetic example pack under
  `examples/contribution_packs/minimal_contribution_pack_v0/`, including
  `CONTRIBUTION_PACK.json`, contribution-item JSONL, referenced pack JSONL,
  pending manual-observation placeholders, checksums, privacy/status
  consistency, private-path rejection, raw SQLite/cache rejection, executable
  payload rejection, and fake observed-observation rejection. It supports
  `--pack-root`, `--json`, and `--strict`, and does not upload, import, review,
  moderate, accept, execute, fetch, scrape, or contact a network
- `validate_master_index_review_queue.py`: validates Master Index Review Queue
  Contract v0 schemas, inventory files, and example queue directories. By
  default it checks
  `examples/master_index_review_queue/minimal_review_queue_v0/`, including
  `REVIEW_QUEUE_MANIFEST.json`, queue-entry JSONL, decision JSONL, checksums,
  privacy/status consistency, no auto-acceptance, private-path rejection, raw
  SQLite/cache rejection, executable payload rejection, and hosted-runtime
  claim rejection. It supports `--queue-root`, `--json`, and `--strict`, and
  does not implement queue runtime, upload, import, moderation, accounts,
  hosted master index writes, acceptance automation, execute, fetch, scrape,
  crawl, or contact a network
- `validate_pack_import_planning.py`: validates Source/Evidence/Index Pack
  Import Planning v0 under `control/audits/pack-import-planning-v0/`. It checks
  `import_runtime_implemented=false`, `validate_only` as the default future
  mode, `stage_local_quarantine` as the next mode, supported source/evidence/
  index/contribution pack types, prohibited import behaviors, references to
  existing pack validators, private staging posture, no default local search
  impact, and no master-index automatic acceptance. It supports `--json` and
  does not import, stage, index, upload, fetch, scrape, crawl, or contact a
  network
- `validate_pack_set.py`: validates known repo pack examples or one explicit
  pack root through the aggregate Pack Import Validator Aggregator v0. It
  supports `--list-examples`, `--all-examples`, `--pack-root`, `--pack-type`,
  `--strict`, and `--json`; detects pack type by manifest; delegates to the
  source/evidence/index/contribution/master-index review queue validators; and
  reports passed/failed/unavailable/unknown_type status. It does not import,
  stage, index, upload, submit, mutate a master index, fetch, scrape, crawl, or
  contact a network
- `validate_ai_provider_contract.py`: validates AI Provider Contract v0
  schemas, AI provider policy inventory, the disabled stub provider example,
  typed output examples, checksums, default-disabled posture,
  privacy/credential/logging/cache rules, forbidden tasks and prohibited uses,
  no API keys/secrets, and no AI provider runtime path. It supports `--provider-root`,
  `--strict`, and `--json`; it does not call models, load providers, open
  network connections, store credentials, emit telemetry, enable public-search
  AI, mutate local indexes, or mutate a master index
- `validate_ai_output.py`: validates Typed AI Output Validator v0 examples or
  one explicit typed output file. It supports `--output`, `--provider`,
  `--bundle-root`, `--all-examples`, `--strict`, and `--json`; checks
  disabled-by-default provider references, required review, prohibited uses,
  private-path and secret leakage, short generated text, and candidate-only
  structured claims; and does not call models, load providers, import evidence,
  draft contributions, stage packs, mutate local indexes, upload, or mutate a
  master index
- `validate_ai_assisted_drafting_plan.py`: validates AI-Assisted Evidence
  Drafting Plan v0. It checks the disabled-by-default drafting policy,
  synthetic example flow, typed output validation, evidence/contribution
  candidate-only examples, audit pack, docs, forbidden truth/rights/malware/
  auto-acceptance/web-fetch/scrape tasks, no API keys/secrets, no model calls,
  no provider runtime, and no public-search/local-index/master-index mutation;
  it supports `--json`
- `validate_pack_import_report.py`: validates Pack Import Report Format v0
  examples or one explicit report. It supports `--report`, `--all-examples`,
  `--strict`, and `--json`; checks report status and mode values, pack-result
  statuses, issue severities/types, next actions, hard false mutation-safety
  fields, private-path redaction, no secrets, and no positive truth/rights/
  malware authority claims; and does not import, stage, index, upload, call
  networks, call models, mutate runtime state, or mutate a master index
- `validate_only_pack_import.py`: runs Validate-Only Pack Import Tool v0. It
  supports repeatable `--pack-root`, `--all-examples`, `--include-ai-outputs`,
  `--output`, `--strict`, `--list-examples`, and `--json`; delegates to the
  existing pack validators through the aggregate validation layer; emits Pack
  Import Report v0 JSON; redacts local absolute paths; writes only an explicit
  report file when requested; and does not import, stage, index, upload, call
  networks, call models, mutate runtime state, mutate public search, or mutate
  a master index
- `validate_local_quarantine_staging_model.py`: validates Local
  Quarantine/Staging Model v0 inventory, audit pack, docs, ignore policy, and
  no-runtime posture. It supports `--json`; checks local_private defaults, no
  search/master-index impact, prohibited roots, ignored future local-state
  roots, reset/delete/export requirements, and absence of `.eureka-local/`,
  `.eureka-cache/`, or `.eureka-staging/` runtime directories.
- `validate_staging_report_path_contract.py`: validates Staging Report Path
  Contract v0 inventory, audit pack, docs, `.gitignore` policy, validate-only
  output-root enforcement, and no-runtime posture. It supports `--json`;
  checks stdout defaults, explicit output path policy, forbidden committed
  roots, ignored future local report roots, redaction documentation, and
  absence of `.eureka-local/` or `.eureka-reports/` runtime directories.
- `validate_local_staging_manifest.py`: validates Local Staging Manifest
  Format v0 examples or one explicit manifest/root. It supports `--manifest`,
  `--manifest-root`, `--all-examples`, `--strict`, and `--json`; checks
  schema fields, hard no-mutation guarantees, staged entity candidate
  semantics, count consistency, reset/delete/export policy, example
  checksums, private-path redaction, secret rejection, and no public-search,
  local-index, runtime, upload, or master-index mutation claims. It does not
  create staging runtime, staged state, `.eureka-local/` state, pack imports,
  local indexes, network calls, or model calls.
- `inspect_staged_pack.py`: read-only Staged Pack Inspector v0 for explicit
  local staging manifests, manifest roots, or committed synthetic examples.
  It supports `--manifest`, `--manifest-root`, `--all-examples`,
  `--list-examples`, `--strict`, `--no-validate`, and `--json`; validates
  manifests before inspection by default; emits human and JSON summaries of
  staged candidate packs, staged entity counts, privacy/rights/risk posture,
  reset/delete/export policy, and hard no-mutation guarantees; redacts obvious
  private paths and secret-like fields; and does not stage, import, index,
  upload, call networks, call models, mutate runtime state, mutate public
  search, or mutate a master index.
- `validate_staged_pack_inspector.py`: validates Staged Pack Inspector v0
  wiring. It supports `--json`; checks that the inspector, docs, audit pack,
  committed example inspection, hard false mutation flags, no-runtime claims,
  and absence of `.eureka-local/` runtime staging directories remain intact.
- `demo_http_api.py public-search`, `public-query-plan`, `public-status`,
  `public-sources`, and `public-source`: exercise the local public search
  runtime through the existing demo HTTP API harness without live probes,
  downloads, installs, uploads, caller-provided index paths, or hosted
  deployment
- `generate_public_alpha_hosting_pack.py`: reads `control/inventory/public_alpha_routes.json` and emits or checks the Public Alpha Hosting Pack route-safety summary; it supports `--check` for repeatable docs validation and does not deploy, host, or mutate route behavior
- `generate_python_oracle_golden.py`: generates or checks the Rust Parity Fixture Pack v0 Python-oracle golden outputs under `tests/parity/golden/python_oracle/v0/`; it supports `--check`, optional `--output-root`, and `--json`, normalizes unstable timestamps, local index paths, FTS mode, and generation metadata, and does not implement Rust behavior or replace Python runtime paths
- `check_rust_source_registry_parity.py`: validates the Rust Source Registry
  Parity Catch-up v0 fixture map and isolated Rust source structure against
  the current 15-source Python oracle shape; it supports `--json` and
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
- `validate_post_p49_platform_audit.py`: validates the P50 Post-P49 Platform
  Audit v0 pack under `control/audits/post-p49-platform-audit-v0/`, including
  required files, structured classification values, subsystem coverage,
  command results, query-intelligence gap recording, gated work lists, next 20
  milestones, and no-overclaim guardrails for production status, hosted search,
  live probes, external baselines, and AI runtime; it supports `--json` and
  adds no product behavior
- `validate_post_p50_remediation.py`: validates the P51 Post-P50 Remediation
  Pack v0 under `control/audits/post-p50-remediation-v0/`, including required
  files, remediation item IDs/statuses, P50 audit reference, root governance
  status, pack-validator CLI remediation, GitHub Pages evidence honesty, Cargo
  status, remaining blockers, next branch recommendation, and no product
  behavior expansion claims; it supports `--json` and performs no network calls
- `validate_static_deployment_evidence.py`: validates the P52 Static
  Deployment Evidence / GitHub Pages Repair v0 pack under
  `control/audits/static-deployment-evidence-v0/`, including required files,
  JSON report shape, `site/dist` artifact root, Pages workflow upload path,
  no deployment-success claim without evidence, operator steps for unverified
  deployment, static-only public claims, and no hosted backend/live-probe/
  dynamic-backend claims; it supports `--json` and performs no network calls
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
- `validate_public_search_rehearsal.py`: validates Public Search Rehearsal v0,
  enforcing the audit pack, `local_index_only` mode, safe-query evidence,
  blocked-request evidence, static handoff review, public-alpha review,
  contract alignment, no hosted-search claim, and disabled live probe/download/
  install/upload/local path/telemetry posture without network calls
- `validate_source_expansion_v2.py`: validates Search Usefulness Source
  Expansion v2, enforcing the audit pack, selected query targets, fixture-only
  source records, committed source-expansion fixtures, final audit counts,
  pending/manual external baselines, and no live source/download/local-path/
  hosted-search claims; it supports `--json` and performs no network calls
- `public_search_smoke.py`: runs the local/prototype public search rehearsal
  smoke checks in-process against the stdlib WSGI app, covering status, search,
  query-plan, sources, source detail, HTML search, representative safe queries,
  and blocked unsafe parameters without deploying, opening a public listener,
  calling external sources, or enabling live probes/downloads/uploads/local
  paths
- `validate_public_search_production_contract.py`: validates Public Search
  Production Contract v0 under
  `control/audits/public-search-production-contract-v0/`, including required
  audit files, JSON report shape, request/response/error/result-card/source/
  evidence/absence/status schemas, route classifications, forbidden
  parameters, disabled capability flags, safety docs, static handoff
  requirements, and P54 hosted wrapper requirements; it supports `--json`,
  performs no network calls, and does not deploy or host anything
- `run_hosted_public_search.py`: runs the P54 hosted public search wrapper in
  stdlib WSGI form. `--check-config` validates safe local_index_only defaults
  and refuses live probes, downloads, uploads, local paths, arbitrary URL fetch,
  install actions, telemetry, deployment evidence claims, and a tripped
  operator kill switch. Running the server is local/operator controlled and is
  not deployment evidence.
- `check_hosted_public_search_wrapper.py`: runs an in-process P54 wrapper
  rehearsal for `/healthz`, `/status`, `/api/v1/status`, search, query-plan,
  sources, HTML search, unsafe-parameter rejection, and too-long query
  rejection. It supports `--json`, opens no public listener, and performs no
  external calls.
- `validate_hosted_public_search_wrapper.py`: validates the P54 audit pack,
  wrapper scripts, safe config check, inert deployment templates, docs,
  inventory posture, disabled hard booleans, and no hosted deployment claim. It
  supports `--json` and performs no network calls.
- `build_public_search_index.py`: builds or drift-checks the P55 generated
  public search index under `data/public_index` from governed source inventory
  plus committed fixture/recorded metadata only. It writes JSON/NDJSON
  manifests, source coverage, stats, and checksums; `--check` regenerates in a
  temporary directory and compares without mutating the repo; `--json` emits a
  machine-readable report. It performs no network calls, does not read
  caller-selected source roots, and does not create live/source/import
  behavior.
- `validate_public_search_index.py`: validates the committed P55
  `data/public_index` bundle, including required files, document fields,
  source ids, checksums, count consistency, blocked actions, no private path or
  secret markers, no live-source flags, and no executable payload flags. It
  supports `--json` and performs no network calls.
- `validate_public_search_index_builder.py`: validates the P55 audit pack,
  builder/validator scripts, generated artifact inventory, docs, hard false
  booleans, `validate_public_search_index.py`, and
  `build_public_search_index.py --check`. It supports `--json` and performs no
  network calls.
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
## Hosted Public Search Rehearsal

- `python scripts/run_hosted_public_search_rehearsal.py`
- `python scripts/run_hosted_public_search_rehearsal.py --json`
- `python scripts/validate_hosted_public_search_rehearsal.py`
- `python scripts/validate_hosted_public_search_rehearsal.py --json`

These commands run and validate P58 local hosted-mode rehearsal evidence. They
start only a localhost wrapper process and do not deploy, call external source
APIs, enable live probes, or mutate indexes.

## Query Observation Contract

- `python scripts/validate_query_observation.py --all-examples`
- `python scripts/validate_query_observation.py --all-examples --json`
- `python scripts/validate_query_observation_contract.py`
- `python scripts/validate_query_observation_contract.py --json`
- `python scripts/dry_run_query_observation.py --query "windows 7 apps" --json`

These P59 commands validate contract-only query observation examples and docs, or emit a stdout-only dry-run observation. They do not persist query logs, add telemetry, mutate caches, write miss ledgers, enqueue probes, mutate indexes, or call external services.

## Shared Query/Result Cache Contract

- `python scripts/validate_search_result_cache_entry.py --all-examples`
- `python scripts/validate_search_result_cache_entry.py --all-examples --json`
- `python scripts/validate_shared_query_result_cache_contract.py`
- `python scripts/validate_shared_query_result_cache_contract.py --json`
- `python scripts/dry_run_search_result_cache_entry.py --query "windows 7 apps" --json`

These P60 commands validate contract-only shared query/result cache examples and
docs, or emit a stdout-only dry-run cache entry. They do not persist cache
state, add telemetry, write query logs, mutate miss ledgers or search needs,
enqueue probes, mutate candidate/local/master indexes, or call external
services.

## Search Miss Ledger Contract

- `python scripts/validate_search_miss_ledger_entry.py --all-examples`
- `python scripts/validate_search_miss_ledger_entry.py --all-examples --json`
- `python scripts/validate_search_miss_ledger_contract.py`
- `python scripts/validate_search_miss_ledger_contract.py --json`
- `python scripts/dry_run_search_miss_ledger_entry.py --query "no-such-local-index-hit" --miss-type no_hits --json`

These P61 commands validate contract-only search miss ledger examples and docs,
or emit a stdout-only dry-run miss entry. They do not persist ledger state, add
telemetry, write query logs, create search needs, enqueue probes, mutate result
caches, mutate candidate/local/master indexes, or call external services.

## Search Need Record Contract

- `python scripts/validate_search_need_record.py --all-examples`
- `python scripts/validate_search_need_record.py --all-examples --json`
- `python scripts/validate_search_need_record_contract.py`
- `python scripts/validate_search_need_record_contract.py --json`
- `python scripts/dry_run_search_need_record.py --label "Windows 7 compatible application" --object-kind software_version --json`

These P62 commands validate contract-only search need examples and docs, or
emit a stdout-only dry-run need record. They do not persist need state, add
telemetry, write query logs, claim demand counts, enqueue probes, mutate result
caches or miss ledgers, mutate candidate/local/master indexes, or call external
services.

## Probe Queue Contract

- `python scripts/validate_probe_queue_item.py --all-examples`
- `python scripts/validate_probe_queue_item.py --all-examples --json`
- `python scripts/validate_probe_queue_contract.py`
- `python scripts/validate_probe_queue_contract.py --json`
- `python scripts/dry_run_probe_queue_item.py --label "Check IA metadata for Windows 7 app query" --kind source_metadata_probe --json`

These P63 commands validate contract-only probe queue examples and docs, or
emit a stdout-only dry-run probe item. They do not persist queue state, execute
probes, call live sources, add telemetry, write query logs, mutate source
caches, evidence ledgers, candidate indexes, local indexes, master-index
records, result caches, miss ledgers, or search needs, or call external
services.

## Candidate Index Contract

- `python scripts/validate_candidate_index_record.py --all-examples`
- `python scripts/validate_candidate_index_record.py --all-examples --json`
- `python scripts/validate_candidate_index_contract.py`
- `python scripts/validate_candidate_index_contract.py --json`
- `python scripts/dry_run_candidate_index_record.py --label "Firefox ESR Windows XP compatibility candidate" --candidate-type compatibility_claim_candidate --json`

These P64 commands validate contract-only candidate index examples and docs, or
emit a stdout-only dry-run candidate record. They do not persist candidate
state, promote candidates, inject candidates into public search, add telemetry,
write query logs, mutate source caches, evidence ledgers, local indexes,
master-index records, result caches, miss ledgers, search needs, or probe
queues, or call external services.

## Candidate Promotion Policy Contract

- `python scripts/validate_candidate_promotion_assessment.py --all-examples`
- `python scripts/validate_candidate_promotion_assessment.py --all-examples --json`
- `python scripts/validate_candidate_promotion_policy.py`
- `python scripts/validate_candidate_promotion_policy.py --json`
- `python scripts/dry_run_candidate_promotion_assessment.py --candidate-label "Firefox ESR Windows XP compatibility candidate" --candidate-type compatibility_claim_candidate --json`

These P65 commands validate recommendation-only candidate promotion assessment
examples and policy docs, or emit a stdout-only dry-run promotion assessment.
They do not perform promotion, automatic acceptance, review queue writes,
candidate-index mutation, source-cache mutation, evidence-ledger mutation,
public-index mutation, local-index mutation, master-index mutation, telemetry,
external calls, or live probes.

## Known Absence Page Contract

P66 adds stdlib-only validators and a stdout-only dry-run helper: `python scripts/validate_known_absence_page.py --all-examples`, `python scripts/validate_known_absence_page.py --all-examples --json`, `python scripts/validate_known_absence_page_contract.py`, `python scripts/validate_known_absence_page_contract.py --json`, and `python scripts/dry_run_known_absence_page.py --query "no-such-local-index-hit" --absence-status scoped_absence --json`. They write no ledger, page store, source cache, evidence ledger, candidate index, query log, telemetry, public index, local index, or master index state.

<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-START -->
## P67 Query Privacy and Poisoning Guard

P67 adds `validate_query_guard_decision.py`, `validate_query_privacy_poisoning_guard_contract.py`, and `dry_run_query_guard.py`. The commands are `python scripts/validate_query_guard_decision.py --all-examples`, `python scripts/validate_query_guard_decision.py --all-examples --json`, `python scripts/validate_query_privacy_poisoning_guard_contract.py`, `python scripts/validate_query_privacy_poisoning_guard_contract.py --json`, and `python scripts/dry_run_query_guard.py --query "windows 7 apps" --json`. They are stdlib-only and write no guard store, telemetry, account/IP tracking, query logs, query-intelligence records, indexes, external calls, or live probes.
<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-END -->

## Demand Dashboard v0 Validators

P68 adds `validate_demand_dashboard_snapshot.py`, `validate_demand_dashboard_contract.py`, and `dry_run_demand_dashboard_snapshot.py`. Commands: `python scripts/validate_demand_dashboard_snapshot.py --all-examples`, `python scripts/validate_demand_dashboard_snapshot.py --all-examples --json`, `python scripts/validate_demand_dashboard_contract.py`, `python scripts/validate_demand_dashboard_contract.py --json`, and `python scripts/dry_run_demand_dashboard_snapshot.py --json`. They are stdlib-only and write no dashboard store, telemetry, account/IP tracking, query logs, query-intelligence records, indexes, external calls, or live probes.

## Source Sync Worker v0 Validators

P69 adds `validate_source_sync_worker_job.py`, `validate_source_sync_worker_contract.py`, and `dry_run_source_sync_worker_job.py`. Commands: `python scripts/validate_source_sync_worker_job.py --all-examples`, `python scripts/validate_source_sync_worker_job.py --all-examples --json`, `python scripts/validate_source_sync_worker_contract.py`, `python scripts/validate_source_sync_worker_contract.py --json`, and `python scripts/dry_run_source_sync_worker_job.py --label "IA metadata sync example" --kind internet_archive_metadata_sync --source-family internet_archive --json`. They are stdlib-only and write no worker queue, telemetry, credentials, source cache, evidence ledger, candidate index, public/local/master indexes, external calls, or live probes.

## Source Cache and Evidence Ledger v0 Validators

P70 adds `validate_source_cache_record.py`, `validate_source_cache_contract.py`, `validate_evidence_ledger_record.py`, `validate_evidence_ledger_contract.py`, `validate_source_cache_evidence_ledger_contract.py`, `dry_run_source_cache_record.py`, and `dry_run_evidence_ledger_record.py`. Commands: `python scripts/validate_source_cache_record.py --all-examples`, `python scripts/validate_source_cache_record.py --all-examples --json`, `python scripts/validate_source_cache_contract.py`, `python scripts/validate_source_cache_contract.py --json`, `python scripts/validate_evidence_ledger_record.py --all-examples`, `python scripts/validate_evidence_ledger_record.py --all-examples --json`, `python scripts/validate_evidence_ledger_contract.py`, `python scripts/validate_evidence_ledger_contract.py --json`, `python scripts/validate_source_cache_evidence_ledger_contract.py`, `python scripts/validate_source_cache_evidence_ledger_contract.py --json`, `python scripts/dry_run_source_cache_record.py --label "IA metadata cache example" --source-family internet_archive --kind source_metadata --json`, and `python scripts/dry_run_evidence_ledger_record.py --label "Windows XP compatibility evidence example" --evidence-kind compatibility_observation --json`. They are stdlib-only and write no source cache, evidence ledger, telemetry, credentials, candidate index, public/local/master indexes, external calls, or live probes.

<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-START -->
## Internet Archive Metadata Connector Approval v0 Validators

P71 adds `validate_internet_archive_metadata_connector_approval.py`, `validate_internet_archive_metadata_connector_contract.py`, and `dry_run_internet_archive_metadata_connector_approval.py`. Commands: `python scripts/validate_internet_archive_metadata_connector_approval.py --all-examples`, `python scripts/validate_internet_archive_metadata_connector_approval.py --all-examples --json`, `python scripts/validate_internet_archive_metadata_connector_contract.py`, `python scripts/validate_internet_archive_metadata_connector_contract.py --json`, and `python scripts/dry_run_internet_archive_metadata_connector_approval.py --json`. They are stdlib-only and write no connector runtime, telemetry, credentials, source cache, evidence ledger, candidate index, public/local/master indexes, external calls, live IA calls, downloads, file retrieval, mirroring, installs, or execution.
<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-END -->

## P72 Wayback/CDX/Memento Connector Approval Pack v0

Completed as an approval-only contract pack. It adds no Wayback/CDX/Memento connector runtime, no external calls, no archived content fetch, no capture replay, no WARC download, no public-query fanout, no telemetry, no credentials, and no source cache/evidence ledger/candidate/index mutation. Next recommended branch: P73 GitHub Releases Connector Approval Pack v0.

<!-- P73-GITHUB-RELEASES-SUMMARY-START -->
## P73 GitHub Releases Connector Approval Pack v0

Completed as an approval-only release metadata connector pack. It adds no live GitHub connector runtime, no external calls, no GitHub API calls, no repository clone, no release fetch, no release asset download, no source archive download, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. Next recommended branch: P74 PyPI Metadata Connector Approval Pack v0.
<!-- P73-GITHUB-RELEASES-SUMMARY-END -->

<!-- P74-PYPI-METADATA-SUMMARY-START -->
## P74 PyPI Metadata Connector Approval Pack v0

Completed as an approval-only package metadata connector pack. It adds no live PyPI connector runtime, no external calls, no PyPI API calls, no package metadata fetch, no release fetch, no wheel download, no sdist download, no package file download, no package install, no dependency resolution, no package archive inspection, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. Next recommended branch: P75 npm Metadata Connector Approval Pack v0.
<!-- P74-PYPI-METADATA-SUMMARY-END -->
<!-- P75-NPM-METADATA-CONNECTOR-APPROVAL-START -->
## P75 npm Metadata Connector Approval Pack v0

P75 adds `validate_npm_metadata_connector_approval.py`, `validate_npm_metadata_connector_contract.py`, and `dry_run_npm_metadata_connector_approval.py`. Commands: `python scripts/validate_npm_metadata_connector_approval.py --all-examples`, `python scripts/validate_npm_metadata_connector_approval.py --all-examples --json`, `python scripts/validate_npm_metadata_connector_contract.py`, `python scripts/validate_npm_metadata_connector_contract.py --json`, and `python scripts/dry_run_npm_metadata_connector_approval.py --json`. They are stdlib-only and write no connector runtime, telemetry, credentials, source cache, evidence ledger, candidate index, public/local/master indexes, external calls, live npm registry calls, npm/yarn/pnpm CLI calls, package downloads, package installs, dependency resolution, lifecycle script execution, npm audit, file retrieval, mirroring, installs, or execution.
<!-- P75-NPM-METADATA-CONNECTOR-APPROVAL-END -->
<!-- P76-SOFTWARE-HERITAGE-CONNECTOR-APPROVAL-START -->
## P76 Software Heritage Connector Approval Pack v0

P76 adds `validate_software_heritage_connector_approval.py`, `validate_software_heritage_connector_contract.py`, and `dry_run_software_heritage_connector_approval.py`. Commands: `python scripts/validate_software_heritage_connector_approval.py --all-examples`, `python scripts/validate_software_heritage_connector_approval.py --all-examples --json`, `python scripts/validate_software_heritage_connector_contract.py`, `python scripts/validate_software_heritage_connector_contract.py --json`, and `python scripts/dry_run_software_heritage_connector_approval.py --json`. They are stdlib-only and write no connector runtime, telemetry, credentials, source cache, evidence ledger, candidate index, public/local/master indexes, external calls, live Software Heritage API calls, SWHID resolution, origin lookup, source content/blob/directory fetch, repository clone, source archive download, source file retrieval, file retrieval, mirroring, installs, or execution.
<!-- P76-SOFTWARE-HERITAGE-CONNECTOR-APPROVAL-END -->

## Public Hosted Deployment Evidence

- `python scripts/verify_public_hosted_deployment.py --from-repo-config --json` checks only explicitly configured Eureka static/backend URLs and writes no files.
- `python scripts/verify_public_hosted_deployment.py --from-env --json` checks only URL environment variables.
- `python scripts/validate_public_hosted_deployment_evidence.py` validates the P77 audit pack without network calls.

<!-- P78-EXTERNAL-BASELINE-COMPARISON-START -->
## External Baseline Comparison Report v0

- `python scripts/run_external_baseline_comparison.py --batch batch_0 --json`
- `python scripts/validate_external_baseline_comparison_report.py`
- `python scripts/validate_external_baseline_comparison_report.py --json`

These P78 commands are stdlib/local-only. They read committed manual baseline records and local Eureka audit/index evidence, perform no web calls, no search-engine calls, no source API calls, no model calls, no live probes, and no index/cache/ledger/candidate/master-index mutation.
<!-- P78-EXTERNAL-BASELINE-COMPARISON-END -->

<!-- P79-OBJECT-PAGE-CONTRACT-START -->
## P79 Object Page Contract v0 Commands

- `python scripts/validate_object_page.py --all-examples`
- `python scripts/validate_object_page.py --all-examples --json`
- `python scripts/validate_object_page_contract.py`
- `python scripts/validate_object_page_contract.py --json`
- `python scripts/dry_run_object_page.py --label "Windows 7 compatible application" --object-kind software_version --json`

These commands are stdlib-only and local-only. They add no runtime object pages, live source calls, downloads, installs, execution, telemetry, or index/cache/ledger/candidate/master-index mutation.
<!-- P79-OBJECT-PAGE-CONTRACT-END -->

<!-- P80-SOURCE-PAGE-CONTRACT-START -->
## P80 Source Page Contract v0

Commands:

- `python scripts/validate_source_page.py --all-examples`
- `python scripts/validate_source_page.py --all-examples --json`
- `python scripts/validate_source_page_contract.py`
- `python scripts/validate_source_page_contract.py --json`
- `python scripts/dry_run_source_page.py --source-id internet-archive-placeholder --source-family internet_archive --json`

These are contract-only/source-page governance checks. They make no network calls, implement no runtime source pages, execute no source sync worker, enable no connector, mutate no cache/ledger/index, and enable no downloads, installs, or execution.
<!-- P80-SOURCE-PAGE-CONTRACT-END -->

<!-- P81-COMPARISON-PAGE-CONTRACT-START -->
## P81 Comparison Page Contract v0

- `python scripts/validate_comparison_page.py --all-examples`
- `python scripts/validate_comparison_page.py --all-examples --json`
- `python scripts/validate_comparison_page_contract.py`
- `python scripts/validate_comparison_page_contract.py --json`
- `python scripts/dry_run_comparison_page.py --label "Compare two Windows 7 compatible app candidates" --comparison-type object_identity_comparison --json`

These are contract-only comparison-page governance checks. They make no network calls, implement no runtime comparison pages, call no live source, execute no source sync worker, mutate no cache/ledger/index, select no winner, and enable no downloads, installs, or execution.
<!-- P81-COMPARISON-PAGE-CONTRACT-END -->

<!-- P82-CROSS-SOURCE-IDENTITY-RESOLUTION-START -->
## P82 Cross-Source Identity Resolution Contract v0

- `python scripts/validate_identity_resolution_assessment.py --all-examples`
- `python scripts/validate_identity_resolution_assessment.py --all-examples --json`
- `python scripts/validate_identity_cluster.py --all-examples`
- `python scripts/validate_identity_cluster.py --all-examples --json`
- `python scripts/validate_cross_source_identity_resolution_contract.py`
- `python scripts/validate_cross_source_identity_resolution_contract.py --json`
- `python scripts/dry_run_identity_resolution_assessment.py --left-label "Example App 1.0" --right-label "ExampleApp v1.0" --relation-type possible_same_object --json`

These are contract-only identity governance checks. They make no network calls, implement no identity resolver, merge no records, promote no candidates, mutate no cache/ledger/index, and enable no live sources, downloads, installs, or execution.
<!-- P82-CROSS-SOURCE-IDENTITY-RESOLUTION-END -->

<!-- P83-RESULT-MERGE-DEDUPLICATION-START -->
## P83 Result Merge and Deduplication Contract v0

- `python scripts/validate_result_merge_group.py --all-examples`
- `python scripts/validate_result_merge_group.py --all-examples --json`
- `python scripts/validate_deduplication_assessment.py --all-examples`
- `python scripts/validate_deduplication_assessment.py --all-examples --json`
- `python scripts/validate_result_merge_deduplication_contract.py`
- `python scripts/validate_result_merge_deduplication_contract.py --json`
- `python scripts/dry_run_result_merge_group.py --left-title "Example App 1.0" --right-title "ExampleApp v1.0" --relation-type near_duplicate_result --json`

These are contract-only result merge/deduplication checks. They make no network calls, implement no runtime grouping/deduplication, hide no results, change no ranking, merge no records, promote no candidates, mutate no cache/ledger/index, and enable no downloads, installs, or execution.
<!-- P83-RESULT-MERGE-DEDUPLICATION-END -->

<!-- P84-EVIDENCE-WEIGHTED-RANKING-START -->
## Evidence-Weighted Ranking Contract v0

- `python scripts/validate_evidence_weighted_ranking_assessment.py --all-examples`
- `python scripts/validate_evidence_weighted_ranking_assessment.py --all-examples --json`
- `python scripts/validate_ranking_explanation.py --all-examples`
- `python scripts/validate_ranking_explanation.py --all-examples --json`
- `python scripts/validate_evidence_weighted_ranking_contract.py`
- `python scripts/validate_evidence_weighted_ranking_contract.py --json`
- `python scripts/dry_run_evidence_weighted_ranking.py --left-title "Strong evidence result" --right-title "Weak evidence result" --json`

These are contract-only checks. They perform no network calls, implement no runtime ranking, change no public search order, suppress no results, promote no candidates, use no popularity/telemetry/ad/user-profile signals, mutate no index/cache/ledger, and enable no downloads, installs, or execution.
<!-- P84-EVIDENCE-WEIGHTED-RANKING-END -->
