# Audit Packs

`control/audits/` holds repo-governance audit packs. These packs are evidence
and planning artifacts, not product runtime behavior and not public product
claims.

An audit pack should usually be grouped under a dated directory and should include:

- a baseline record
- commands run or intended for final verification
- structure, content, behavior, and test-gap audits
- structured findings using `control/audits/schemas/finding.schema.json`
- backlog and next-milestone recommendations
- explicit non-goals and deferred items

Audit findings should map to future-work labels and should avoid vague
"improve everything" recommendations. If a finding depends on external search
quality, mark the external observation as pending manual evidence rather than
fabricating a baseline.

Audit packs must not be used to claim production readiness. Public-alpha
material remains supervised-demo evidence only until a separate accepted
hosting decision exists.

Current packs:

- `2026-04-25-comprehensive-test-eval-audit/`: repo-wide structure, content,
  behavior, test-gap, and backlog audit.
- `search-usefulness-delta-v0/`: stable usefulness-delta report comparing
  current Search Usefulness Audit output to a historical reported aggregate
  baseline after the old-platform/member-discovery implementation sequence.
- `search-usefulness-delta-v1/`: stable usefulness-delta report comparing
  post-source-expansion audit output to the v0 delta aggregate baseline and
  recording archive-eval movement toward source-backed but still unsatisfied
  hard tasks.
- `hard-eval-satisfaction-v0/`: stable archive-resolution hard-eval report
  recording the move from `capability_gap=1, not_satisfied=5` to
  `capability_gap=1, partial=5` without weakening hard tasks or fabricating
  source evidence.
- `old-platform-result-refinement-v0/`: stable archive-resolution result-shape
  report recording the move to `capability_gap=1, partial=4, satisfied=1`
  after deterministic primary-candidate, expected-lane, and bad-result checks
  were added without weakening hard tasks or changing retrieval behavior.
- `more-source-coverage-expansion-v1/`: stable targeted source-expansion
  report recording the move to `capability_gap=1, satisfied=5` for current
  archive-resolution hard evals after tiny Firefox XP, blue FTP-client XP,
  Windows 98 registry repair, and Windows 7 utility/app fixture evidence was
  added without live source behavior, real binaries, or external baseline
  claims.
- `article-scan-fixture-pack-v0/`: stable article/scan fixture report
  recording the move to `satisfied=6` for current archive-resolution hard evals
  after a tiny synthetic article segment, page-range locator, and OCR-like text
  fixture were added without live source behavior, OCR engines, PDF/image
  parsing, real magazine scans, copyrighted article text, or external baseline
  claims.

- `post-queue-state-checkpoint-v0/`: post-queue repo-state checkpoint after the
  publication/static/live-alpha/Rust/snapshot queue. It records milestone
  evidence, command results, eval/audit status, external-baseline pending
  status, risks, deferrals, and next planning without adding product behavior.
- `native-client-project-readiness-v0/`: conservative readiness review for
  future native client project scaffolding. It records contract coverage, lane
  readiness, risks, a pre-native checklist, and a human-approval gate without
  adding Visual Studio/Xcode projects, native app code, GUI behavior, FFI,
  downloads, installers, cache runtime, relay runtime, or live probes.
- `windows-7-winforms-native-skeleton-planning-v0/`: planning pack for the
  first future Windows 7 SP1+ x64 WinForms .NET Framework 4.8 skeleton. It
  records proposed path, namespace, build-host requirements, allowed/prohibited
  initial scope, data inputs, and approval gates without creating `clients/`,
  Visual Studio project files, C# source, GUI behavior, FFI, downloads,
  installers, cache runtime, relay runtime, or live probes.
- `relay-prototype-planning-v0/`: planning pack for the first future relay
  prototype. It selects a localhost-only/read-only/static
  `local_static_http_relay_prototype`, records input/output contracts,
  security/privacy defaults, operator gates, risks, and implementation
  boundaries without creating a relay server, opening sockets, adding protocol
  support, serving private files, proxying a live backend, enabling live probes,
  or claiming old-client relay support.
- `full-project-state-audit-v0/`: full project checkpoint after the
  backend/source/eval/publication/snapshot/relay/native-policy/native-planning
  and Rust parity planning sequence. It records milestone status, verification
  results, eval/search status, external-baseline pending state,
  publication/static/public-alpha posture, source/retrieval state,
  snapshot/relay/native/Rust status, risks, blockers, human-operated work,
  explicit deferrals, and next milestone recommendations without changing
  product behavior.
- `public-data-contract-stability-review-v0/`: field-level public data
  stability review for generated static JSON under `site/dist/data/`. It
  classifies files and fields as `stable_draft`, `experimental`, `volatile`,
  `internal`, `deprecated`, or `future`, records versioning/breaking-change
  policy, and recommends Generated Artifact Drift Guard v0 without changing
  product behavior or claiming production API stability.
- `generated-artifact-drift-guard-v0/`: validation/audit pack for generated and
  generated-like artifact ownership. It covers public data, compatibility
  surfaces, static demos, seed snapshots, `site/dist`, Python oracle goldens,
  public-alpha rehearsal evidence, publication inventories, test registry
  metadata, and AIDE metadata without regenerating artifacts by default,
  changing product behavior, deploying, or calling external services.
- `static-artifact-promotion-review-v0/`: local promotion review for the
  generated `site/dist` artifact. It conditionally promotes `site/dist` as the
  active repo-local static artifact, records workflow/generated-artifact/safety
  and stale-reference evidence, and leaves GitHub Actions deployment evidence
  unverified without adding runtime behavior or production claims.
- `github-pages-run-evidence-v0/`: passive GitHub Actions evidence review for
  the static Pages workflow after `site/dist` promotion. It records the
  current-head run failure at Pages configuration, absence of an uploaded Pages
  artifact, failed deployment status, local validation evidence, and operator
  follow-up without triggering deployment or adding backend behavior.
- `public-search-rehearsal-v0/`: local/prototype public search rehearsal
  evidence. It records route coverage, safe-query outcomes, blocked-request
  outcomes, static handoff review, public-alpha review, contract alignment, and
  a structured report without deploying hosted search, calling external
  sources, enabling live probes, downloads, installs, uploads, local path
  search, accounts, telemetry, or production claims.
- `search-usefulness-source-expansion-v2/`: fixture-only source expansion
  evidence for selected broad search-usefulness gaps. It records baseline and
  final counts, selected query targets, source-family selection, fixture
  inventory, normalization/indexing notes, query impact, remaining gaps, risks,
  and next source work without live probes, scraping, crawling, external
  observations, real binaries, download/install/upload actions, local path
  search, hosted search, or production relevance claims.
- `search-usefulness-delta-v2/`: audit-only measurement of Source Expansion
  v2. It records baseline provenance, current counts, status deltas, selected
  query movement, current failure modes, source-family impact, public-search
  smoke status, hard-eval status, external-baseline pending status, remaining
  gaps, and Source Pack Contract v0 as the next recommendation without adding
  source/runtime behavior or external observations.
- `source-pack-contract-v0/`: contract/validation/example-only review for the
  first portable source-pack format. It records the manifest schema, file
  layout, privacy/rights posture, validation rules, synthetic example-pack
  review, and future import/submission path without implementing import,
  indexing, upload, live connectors, executable plugins, or master-index
  acceptance.
- `evidence-pack-contract-v0/`: contract/validation/example-only review for
  the first portable evidence-pack format. It records the manifest schema, file
  layout, claim/evidence types, snippet limits, privacy/rights posture,
  validation rules, synthetic example-pack review, and future
  import/submission path without implementing import, indexing, upload, live
  connectors, executable plugins, canonical truth selection, or master-index
  acceptance.
- `index-pack-contract-v0/`: contract/validation/example-only review for the
  first portable index-pack format. It records the manifest schema, file
  layout, index coverage model, record summary model, privacy/rights posture,
  validation rules, synthetic summary-only example-pack review, and future
  import/merge path without implementing import, merge, upload, raw
  SQLite/local-cache export, live connectors, executable plugins, canonical
  truth selection, or master-index acceptance.

Public Search API Contract v0 is governed under `contracts/api/`,
`control/inventory/publication/public_search_routes.json`, and
`docs/reference/PUBLIC_SEARCH_API_CONTRACT.md` rather than an audit pack.
Local Public Search Runtime v0 now implements the first local/prototype backend
routes for the governed contract through `runtime/gateway/public_api/` and
`surfaces/web/server/`. It adds no hosted deployment, live probes, downloads,
installs, uploads, local path search, accounts, telemetry, or production API
claim. Public Search Static Handoff v0 adds static/no-JS `site/dist` handoff
outputs and `data/search_handoff.json` without adding an audit pack, hosted
backend, fake hosted URL, live probes, downloads, uploads, or production claim.
- `public-search-result-card-contract-v0/`: contract-governance audit pack for
  the future public search result-card envelope. It records field stability,
  old-client/native/relay/snapshot rendering guidance, action/risk/rights
  posture, fixture-safe examples, and a structured report without implementing
  public search runtime, live routes, live probes, downloads, installers,
  execution, uploads, malware-safety claims, rights-clearance claims, or
  production ranking claims.
- `source-pack-contract-v0/`, `evidence-pack-contract-v0/`,
  `index-pack-contract-v0/`, and `contribution-pack-contract-v0/`: pack
  contract audit packs for future source/evidence/index/contribution workflows.
  Contribution Pack Contract v0 records review-candidate submission metadata,
  referenced pack posture, pending manual observation placeholders, validation
  rules, and future review-queue needs without upload/import/moderation
  runtime, accounts, automatic acceptance, live connectors, raw cache export,
  executable plugins, or master-index acceptance.
- `master-index-review-queue-contract-v0/`: review-queue governance contract
  audit pack for future contribution candidates. It records queue entries,
  decisions, state taxonomy, acceptance requirements, privacy/rights/risk
  review, conflict preservation, and publication policy without queue runtime,
  upload/import handling, moderation UI, accounts, hosted master index,
  master-index writes, automatic acceptance, live connectors, rights-clearance
  claims, malware-safety claims, or canonical-truth claims.
- `pack-import-planning-v0/`: planning audit pack for future local
  source/evidence/index/contribution pack import. It records validate-only as
  the first future mode, private local quarantine as the next mode, validation
  pipeline, staging/privacy/rights/risk posture, provenance model, no default
  local search/index impact, and master-index review separation without
  implementing import runtime, staging directories, uploads, canonical registry
  mutation, hosted/master-index mutation, automatic acceptance, live fetch,
  arbitrary directory scanning, or executable plugin behavior.
- `pack-import-validator-aggregator-v0/`: validate-only audit pack for the
  aggregate pack validator. It records the example-pack registry, current
  all-example validation results, mutation/safety posture, and future import
  pipeline relationship without implementing import, staging, local index
  mutation, uploads, hosted/master-index mutation, automatic acceptance,
  rights-clearance claims, malware-safety claims, or canonical-truth claims.
- `ai-provider-contract-v0/`: contract/validation/example-only audit pack for
  future optional AI providers. It records provider manifests, task request and
  typed output contracts, disabled stub example review, privacy/credential/
  logging policy, evidence/review policy, forbidden uses, and next steps
  without implementing model calls, provider runtime loading, API keys,
  credential storage, telemetry, AI in public search, AI-generated evidence
  acceptance, local index mutation, or master-index mutation.
- `typed-ai-output-validator-v0/`: validation-only audit pack for typed AI
  output candidates. It records the reusable offline validator module, CLI,
  example registry, required-review/prohibited-use checks, privacy/secret/path
  checks, relation to evidence/contribution/review workflows, and no-model-call
  runtime boundary without implementing provider runtime, API keys, telemetry,
  evidence import, contribution import, local-index mutation, public-search AI,
  upload, or master-index mutation.
- `ai-assisted-evidence-drafting-plan-v0/`: planning/example/validation audit
  pack for future optional AI-assisted evidence and contribution drafting. It
  records allowed/forbidden drafting tasks, input context policy, typed-output
  to candidate mappings, privacy/provider rules, required review, synthetic
  example flow review, and runtime boundaries without implementing AI runtime,
  model calls, API keys, telemetry, evidence/contribution acceptance,
  public-search mutation, local-index mutation, or master-index mutation.
- `pack-import-report-format-v0/`: format/validation/example-only audit pack
  for future validate-only import reports. It records the report schema,
  synthetic passed/failed/unknown examples, status/mode/pack-result/issue
  models, privacy/rights/risk summaries, mutation-safety fields, and future
  validate-only tooling path without implementing import, staging, indexing,
  upload, runtime mutation, model calls, network behavior, or master-index
  mutation.
- `validate-only-pack-import-tool-v0/`: validate-only tooling audit pack for
  the first report-producing pack import preflight. It records command usage,
  report generation, example run results, and no-mutation posture without
  implementing import, staging, indexing, uploads, runtime mutation, network
  calls, model calls, or master-index mutation.
- `local-quarantine-staging-model-v0/`: planning/governance audit pack for
  future local/private quarantine and staging. It records path policy, staged
  entity vocabulary, report linking, privacy/rights/risk posture, reset/delete/
  export requirements, native/relay/snapshot boundaries, and no-impact search
  and master-index defaults without creating staging runtime, staged state,
  local indexes, uploads, network calls, model calls, or master-index mutation.
- `staging-report-path-contract-v0/`: planning/governance audit pack for
  future report output locations. It records stdout defaults, explicit output
  paths, allowed and forbidden roots, filename safety, redaction, `.gitignore`
  protection, validate-only tool behavior, native/relay/snapshot impact, and
  no public-search/master-index impact without creating report path runtime,
  staging runtime, or staged state.
- `local-staging-manifest-format-v0/`: contract/validation/example-only audit
  pack for future local staging manifests. It records the manifest schema,
  synthetic example, staged pack references, staged entity candidates,
  no-mutation guarantees, reset/delete/export policy, privacy/rights/risk
  posture, and future staged-inspector path without creating staging runtime,
  staged state, `.eureka-local/` state, imports, indexes, uploads, network
  calls, model calls, or master-index mutation.
- `staged-pack-inspector-v0/`: read-only inspection audit pack for synthetic
  Local Staging Manifest v0 examples and explicit manifests. It records
  inspector command usage, JSON and human output models, redaction behavior,
  no-mutation review, example results, and the future staging-tool boundary
  without creating staging runtime, staged state, imports, indexes, uploads,
  network calls, model calls, public-search mutation, or master-index
  mutation.
- `post-p49-platform-audit-v0/`: P50 full platform checkpoint after the public
  search, source, pack, staging, and AI-assistance queue through P49. It
  records subsystem classifications, command evidence, blockers, human/
  approval/operator gates, query-intelligence gaps, language/runtime strategy,
  and next milestones without adding product runtime behavior, hosted search,
  live probes, pack import, AI runtime, external observations, or production
  claims.
- `post-p50-remediation-v0/`: P51 bounded remediation checkpoint for concrete
  P50 drift. It records minimal root governance docs, license selection as
  pending, pack-validator CLI alignment, GitHub Pages operator evidence gaps,
  command/test metadata updates, generated artifact rechecks, Cargo status, and
  remaining human/approval/operator gates without adding hosted backend
  behavior, live probes, source connectors, AI runtime, pack import, staging
  runtime, index mutation, external observations, or deployment-success claims.
- `static-deployment-evidence-v0/`: P52 static deployment evidence checkpoint
  for the GitHub Pages path. It records the configured `site/dist` workflow,
  passing local static artifact checks, unavailable local `gh` tooling,
  prior failed Pages configuration evidence, operator steps, and deployment
  unverified status without adding hosted backend behavior, public search
  hosting, live probes, credentials, telemetry, accounts, uploads, downloads,
  installers, or deployment-success claims.
- `public-search-production-contract-v0/`: P53 production-facing public search
  contract checkpoint for the future hosted local-index wrapper. It records
  route classifications, request/response/error/result-card/source-status/
  evidence-summary/absence/status schema alignment, safety limits, static
  handoff rules, P54 wrapper requirements, verification, and remaining gaps
  without adding hosted backend behavior, live probes, source connectors,
  telemetry runtime, accounts, uploads, downloads, installers, arbitrary URL
  fetching, index mutation, AI runtime, or hosted-search claims.
- `hosted-public-search-wrapper-v0/`: P54 hosted public search wrapper
  readiness checkpoint. It records the stdlib wrapper, local rehearsal check,
  environment defaults, route status, Docker/Render templates, operator
  deployment steps, and validation evidence without performing hosted
  deployment, enabling live probes, downloads, uploads, accounts, telemetry,
  arbitrary URL fetch, source connectors, AI runtime, index mutation, pack
  import, staging runtime, or hosted availability claims.
- `public-search-index-builder-v0/`: P55 generated public search index
  checkpoint. It records the deterministic builder, committed
  `data/public_index` JSON/NDJSON artifacts, source-family coverage,
  fallback lexical search posture, local public-search integration, hosted
  wrapper compatibility, drift checks, and validation evidence without live
  source calls, arbitrary URL fetching, private path ingestion, executable
  payloads, downloads, uploads, AI runtime, pack import, staging runtime,
  master-index mutation, hosted deployment, or production search-quality
  claims.
- `static-site-search-integration-v0/`: P56 static search integration
  checkpoint. It records generated `site/dist/search.html`, lite/text/files
  search surfaces, `data/search_config.json`, `data/public_index_summary.json`,
  backend-unconfigured status, no-JS/base-path posture, public claim review,
  generated artifact ownership, validation evidence, and next steps without
  hosted deployment, fake backend URLs, live probes, downloads, uploads,
  accounts, telemetry, arbitrary URL fetching, index mutation, pack import,
  staging runtime, AI runtime, or production search-quality claims.
- `public-search-safety-evidence-v0/`: P57 public search safety evidence
  checkpoint. It records safe-query, blocked-request, limit/status, static
  handoff, public-index, hosted-wrapper, privacy/redaction, and
  rate-limit/edge evidence without hosted deployment, live probes, downloads,
  uploads, installs, accounts, telemetry, arbitrary URL fetching, source
  connector runtime, AI runtime, index mutation, pack import, staging runtime,
  or production safety claims.

Public Search Safety / Abuse Guard v0 is governed under
`control/inventory/publication/public_search_safety.json`,
`docs/operations/PUBLIC_SEARCH_SAFETY_AND_ABUSE_GUARD.md`, and
`docs/operations/PUBLIC_SEARCH_RUNTIME_READINESS_CHECKLIST.md` rather than a
separate audit pack. It constrains the local runtime and future hosted review,
and adds no rate-limit middleware, auth/accounts, telemetry runtime, hosted
backend, live probes, downloads, uploads, local path search, arbitrary URL
fetch, or production safety claim.
## Hosted Public Search Rehearsal v0

- Path: `control/audits/hosted-public-search-rehearsal-v0/`
- Scope: local hosted-mode public search rehearsal over localhost HTTP.
- Status: local evidence only; no hosted deployment or production readiness
  claim.

## Query Observation Contract v0

- Path: `control/audits/query-observation-contract-v0/`
- Scope: P59 privacy-filtered query observation contract, example, validators, docs, and audit evidence.
- Status: contract-only; no telemetry, runtime persistence, public query logging, cache mutation, miss-ledger mutation, probe enqueueing, index mutation, or master-index mutation.

## Shared Query/Result Cache v0

- Path: `control/audits/shared-query-result-cache-v0/`
- Scope: P60 shared query/result cache contract, cache key model, examples,
  validators, docs, and audit evidence.
- Status: contract-only; no runtime cache writes, persistent cache storage,
  telemetry, public query logging, miss-ledger mutation, search-need mutation,
  probe enqueueing, candidate-index mutation, local-index mutation, or
  master-index mutation.

## Search Miss Ledger v0

- Path: `control/audits/search-miss-ledger-v0/`
- Scope: P61 search miss ledger contract, miss classification taxonomy,
  scoped no-hit and weak-hit examples, validators, docs, and audit evidence.
- Status: contract-only; no runtime ledger writes, persistent ledger storage,
  telemetry, public query logging, search-need creation, probe enqueueing,
  result-cache mutation, candidate-index mutation, local-index mutation, or
  master-index mutation.

## Search Need Record v0

- Path: `control/audits/search-need-record-v0/`
- Scope: P62 search need record contract, lifecycle model, synthetic examples,
  validators, docs, and audit evidence.
- Status: contract-only; no runtime need store, persistent need storage,
  telemetry, public query logging, demand-count runtime, probe enqueueing,
  candidate-index mutation, result-cache mutation, miss-ledger mutation,
  local-index mutation, or master-index mutation.

## Probe Queue v0

- Path: `control/audits/probe-queue-v0/`
- Scope: P63 probe queue item contract, probe kind taxonomy, source policy and
  approval model, synthetic examples, validators, docs, and audit evidence.
- Status: contract-only; no runtime queue, persistent queue, probe execution,
  live source calls, source cache mutation, evidence ledger mutation,
  candidate-index mutation, local-index mutation, or master-index mutation.

## Candidate Index v0

- Path: `control/audits/candidate-index-v0/`
- Scope: P64 candidate index record contract, lifecycle model,
  object/evidence/absence/conflict examples, validators, docs, and audit
  evidence.
- Status: contract-only; no runtime candidate index, persistent candidate
  store, public search candidate injection, candidate promotion runtime, source
  cache mutation, evidence ledger mutation, local-index mutation, or
  master-index mutation.

## Candidate Promotion Policy v0

P65 adds Candidate Promotion Policy v0 as contract-only governance. Candidate promotion policy is not promotion runtime; candidate confidence is not truth; automatic promotion is forbidden; destructive merge is forbidden; future promotion assessment requires evidence, provenance, source policy, privacy, rights, risk, conflict, human, policy, and operator gates. No candidate, source, evidence, public index, local index, or master-index state is mutated.

## P66 Known Absence Page v0

See `control/audits/known-absence-page-v0/` for the scoped absence contract/audit pack. It is not runtime known absence pages and makes no global absence claim.

<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-START -->
## P67 Query Privacy and Poisoning Guard

See `control/audits/query-privacy-poisoning-guard-v0/` for the P67 privacy and poisoning guard contract/audit pack. It is not a runtime guard, telemetry system, WAF/rate-limit layer, account/IP tracker, query logger, or production abuse protection claim.
<!-- P67-QUERY-PRIVACY-AND-POISONING-GUARD-END -->

## Demand Dashboard v0

`control/audits/demand-dashboard-v0/` records the P68 contract-only demand dashboard audit pack. It is not a production analytics, telemetry, or hosted-dashboard claim.

## Source Sync Worker Contract v0

`control/audits/source-sync-worker-contract-v0/` records the P69 contract-only source sync worker audit pack. It is not a worker runtime, connector, source-cache, evidence-ledger, or production-ops claim.

## P70 Source Cache and Evidence Ledger v0

See `control/audits/source-cache-evidence-ledger-v0/` for the contract-only source cache/evidence ledger audit pack.

<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-START -->
## P71 Internet Archive Metadata Connector Approval Pack v0

See `control/audits/internet-archive-metadata-connector-approval-v0/` for the approval-only Internet Archive metadata connector pack. It is not a connector runtime, does not call Internet Archive, does not scrape or download, and does not mutate source cache, evidence ledger, candidate index, public/local/master indexes, telemetry, or credentials.
<!-- P71-INTERNET-ARCHIVE-METADATA-CONNECTOR-APPROVAL-END -->

## P72 Wayback/CDX/Memento Connector Approval Pack v0

Completed as an approval-only contract pack. It adds no Wayback/CDX/Memento connector runtime, no external calls, no archived content fetch, no capture replay, no WARC download, no public-query fanout, no telemetry, no credentials, and no source cache/evidence ledger/candidate/index mutation. Next recommended branch: P73 GitHub Releases Connector Approval Pack v0.
