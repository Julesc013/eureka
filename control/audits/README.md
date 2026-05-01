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

Public Search Safety / Abuse Guard v0 is governed under
`control/inventory/publication/public_search_safety.json`,
`docs/operations/PUBLIC_SEARCH_SAFETY_AND_ABUSE_GUARD.md`, and
`docs/operations/PUBLIC_SEARCH_RUNTIME_READINESS_CHECKLIST.md` rather than a
separate audit pack. It constrains the local runtime and future hosted review,
and adds no rate-limit middleware, auth/accounts, telemetry runtime, hosted
backend, live probes, downloads, uploads, local path search, arbitrary URL
fetch, or production safety claim.
