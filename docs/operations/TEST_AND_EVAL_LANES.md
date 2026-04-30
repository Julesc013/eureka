# Test and Eval Lanes

Eureka now has a repo-native test/eval operating layer under
`control/inventory/tests/`.

The layer exists to help humans, AIDE-style operators, and Codex workers choose
the right checks for a task. It is not a product runtime feature and it is not
a production-readiness claim.

## Taxonomy

Command records use these categories:

- `unit`: component-local Python tests
- `integration`: cross-component repo tests
- `architecture`: import and layering guardrails
- `contract`: governed schema or inventory validation
- `eval`: archive-resolution executable benchmark checks
- `audit`: usefulness or repo-governance audit checks
- `parity`: Python oracle and optional Rust candidate checks
- `operations`: public-alpha, hosting-pack, and audit-pack checks
- `publication`: publication-plane, route/data/client inventory, and static
  site artifact checks
- `public_alpha`: constrained demo posture checks
- `golden`: committed Python-oracle fixture checks
- `smoke`: narrow end-to-end posture checks
- `regression`: broad drift guards
- `hard_query`: future hard-query-specific checks

## Command Lanes

The command matrix defines these lanes:

- `fast`: architecture boundary plus whitespace diff checks
- `standard`: runtime, surfaces, repo tests, boundary checks, and operating
  layer validation
- `full`: standard checks plus public-alpha smoke, hosting-pack check, Python
  oracle golden check, archive eval runner, and search usefulness audit
- `docs_only`: docs/audit/index validation plus whitespace diff checks
- `public_alpha`: route inventory, smoke, wrapper, and hosting-pack safety checks
- `publication_static_site`: publication inventory plus current static-site
  artifact and generated-site checks before deployment or artifact migration
- `parity`: Python oracle, source-registry, Rust query-planner parity
  structure, Rust local-index parity planning, and source coverage/capability
  validation checks, plus current Python-oracle shape guards such as planner,
  member, result-lane, and compatibility-evidence fields
- `audit`: archive-resolution and search-usefulness eval/audit runners
- `hardening`: high-risk regression guards for eval truth, path safety,
  route/docs/README drift, parity/golden discipline, and AIDE/test registry
  consistency
- `rust_optional`: Cargo checks only when the local toolchain exists

## Required vs Advisory

Required commands are expected in the lane that names them. Optional commands
are useful local evidence but must not block Python verification when the
required local tooling is unavailable.

Current Cargo commands are optional. Cargo may not be installed in every
execution environment, and Python remains the reference/oracle lane. The Rust
source-registry and query-planner parity scripts are required Python-side
structure checks; when Cargo is unavailable they report Rust execution as
skipped instead of failing normal Python verification. The Rust local-index
parity plan validator is planning-only and does not require Cargo because no
Rust local-index implementation exists yet.

## Network Policy

Required lanes must stay local and deterministic. Search Usefulness Audit v0
does not scrape Google, Internet Archive, or any other external system.

External baseline observations are manual evidence records. If a future human
records one, the observation must say who observed it, what was observed, and
which system was used. A missing observation remains
`pending_manual_observation`.

## Codex Completion Expectations

For non-trivial tasks:

1. Inspect relevant paths.
2. Plan the bounded changes.
3. Implement only the requested layer.
4. Run the lane that matches the task.
5. Report exactly what passed, what was skipped, and why.
6. Sync origin at the end when the environment supports it.

Large tasks should use a two-pass flow: implementation first, hardening second.
The hardening pass should reread changed files, check claims against evidence,
and make sure hard evals or manual baselines were not weakened or fabricated.

## Hard Test Pack

Hard Test Pack v0 lives under `tests/hardening/` and is documented in
`docs/operations/HARD_TEST_PACK.md`.

Run it with:

```bash
python -m unittest discover -s tests/hardening -t .
```

These tests are regression guards, not product features. They should be run
before syncing changes that affect eval fixtures, external baseline wording,
public-alpha route policy, route inventory, README commands, docs links,
Python-oracle goldens, Rust parity scaffolding, source registry honesty,
resolution memory privacy claims, or AIDE/test metadata.

## Search Usefulness Backlog Triage

Search Usefulness Backlog Triage v0 is validated with:

```bash
python -m unittest tests.operations.test_search_usefulness_backlog_triage
```

The validation checks the selected wedges, next milestone, backlog item count,
deferred-work list, and no-fake-baseline/no-runtime-behavior claims.

## Search Usefulness Audit Delta

Search Usefulness Audit Delta v0 is validated with:

```bash
python -m unittest tests.operations.test_search_usefulness_audit_delta
```

The validation checks the stable delta pack, historical reported baseline
limitations, selected wedges, current local audit counts, pending/manual
external baseline posture, and the Old-Platform Source Coverage Expansion v0
recommendation. It is audit/reporting only and does not change retrieval
behavior.

Search Usefulness Audit Delta v1 is validated with:

```bash
python -m unittest tests.operations.test_search_usefulness_audit_delta_v1
```

The validation checks the v1 pack, v0 baseline reference, current local audit
counts, archive-eval movement, pending/manual external baseline posture, and
the Hard Eval Satisfaction Pack v0 recommendation. It is audit/reporting only
and does not change retrieval behavior.

Hard Eval Satisfaction Pack v0 is validated with:

```bash
python -m unittest tests.evals.test_hard_eval_satisfaction_pack
```

The validation checks the satisfaction report, its historical
`capability_gap=1` and `partial=5` archive-eval posture, source-backed evidence
for moved tasks, and the unchanged article-inside-scan capability gap.

Old-Platform Result Refinement Pack v0 is validated with:

```bash
python -m unittest tests.evals.test_old_platform_result_refinement
```

The validation checks the result-refinement report,
`capability_gap=1`/`partial=4`/`satisfied=1` archive-eval posture, strict
result-shape checks, expected-lane checks, bad-result avoidance, and explicit
remaining partial/capability-gap explanations. It does not validate production
ranking or retrieval behavior.

More Source Coverage Expansion v1 is validated with:

```bash
python -m unittest tests.evals.test_more_source_coverage_expansion_v1
```

The validation checks the targeted source-expansion report,
`capability_gap=1`/`satisfied=5` archive-eval posture, source-backed evidence
for the four old-platform tasks that moved, and the unchanged
article-inside-scan capability gap. It does not add live source behavior,
scraping, arbitrary local ingestion, real binaries, or external baseline
claims.

Article/Scan Fixture Pack v0 is validated with:

```bash
python -m unittest tests.evals.test_article_scan_fixture_pack
```

The validation checks the article/scan fixture report, the `satisfied=6`
archive-eval posture, source-backed article-segment evidence, page-range
evidence, OCR-like fixture text evidence, and no-live/no-OCR/no-real-scan
guardrails. It does not add live source behavior, scraping, OCR engines,
PDF/image parsing, real scans, copyrighted article text, or external baseline
claims.

Search Usefulness Source Expansion v2 is validated with:

```bash
python scripts/validate_source_expansion_v2.py
python scripts/validate_source_expansion_v2.py --json
python -m unittest tests.operations.test_search_usefulness_source_expansion_v2 tests.scripts.test_validate_source_expansion_v2 tests.evals.test_search_usefulness_source_expansion_v2 runtime.connectors.source_expansion_recorded.tests.test_connector runtime.engine.index.tests.test_source_expansion_v2 runtime.gateway.tests.test_public_search_source_expansion_v2
```

The validation checks the fixture-only audit pack, selected query targets,
source inventory records, committed fixture files, local-index/public-search
projection, final broad audit counts, pending/manual external baseline posture,
and no-live/no-download/no-local-path guardrails. It does not add live source
behavior, scraping, crawling, URL fetching, real binaries, arbitrary local
ingestion, hosted search, or production relevance claims.

Search Usefulness Delta v2 is validated with:

```bash
python scripts/validate_search_usefulness_delta_v2.py
python scripts/validate_search_usefulness_delta_v2.py --json
python -m unittest tests.operations.test_search_usefulness_delta_v2 tests.scripts.test_validate_search_usefulness_delta_v2
```

The validation checks the audit-only delta pack, P32 baseline provenance,
current broad audit counts, status deltas, selected query movement,
source-family impact, current failure-mode counts, hard-eval status,
public-search smoke status, pending/manual external baselines, remaining gaps,
and next recommendations. It adds no source/runtime behavior and records no
external observations.

Source Pack Contract v0 is validated with:

```bash
python scripts/validate_source_pack.py
python scripts/validate_source_pack.py --json
python -m unittest tests.operations.test_source_pack_contract tests.scripts.test_validate_source_pack
```

The validation checks the source-pack manifest schema, synthetic example pack,
JSONL records, rights/privacy docs, checksum coverage, disabled live/network
posture, no import/index/upload behavior, no private paths, and no executable
payloads.

Evidence Pack Contract v0 is validated with:

```bash
python scripts/validate_evidence_pack.py
python scripts/validate_evidence_pack.py --json
python -m unittest tests.operations.test_evidence_pack_contract tests.scripts.test_validate_evidence_pack
```

The validation checks the evidence-pack manifest schema, synthetic example
pack, evidence/source-reference JSONL records, evidence id uniqueness, allowed
evidence kinds and claim types, snippet limits, rights/privacy docs, checksum
coverage, disabled live/network posture, no import/index/upload behavior, no
private paths, and no executable payloads.

Index Pack Contract v0 is validated with:

```bash
python scripts/validate_index_pack.py
python scripts/validate_index_pack.py --json
python -m unittest tests.operations.test_index_pack_contract tests.scripts.test_validate_index_pack
```

The validation checks the index-pack manifest schema, synthetic summary-only
example pack, index/source/field coverage JSON, record-summary JSONL, query
examples, record id uniqueness, source references, record kinds, privacy/rights
docs, checksum coverage, disabled live/network posture, no import/merge/upload
or raw SQLite/local-cache export behavior, no private paths, and no executable
payloads.

Contribution Pack Contract v0 is validated with:

```bash
python scripts/validate_contribution_pack.py
python scripts/validate_contribution_pack.py --json
python -m unittest tests.operations.test_contribution_pack_contract tests.scripts.test_validate_contribution_pack
```

The validation checks the contribution-pack manifest schema, synthetic
review-candidate example pack, contribution item JSONL, referenced pack records,
pending manual-observation placeholders, allowed contribution types, allowed
proposed actions, privacy/rights docs, checksum coverage, disabled live/network
posture, no upload/import/moderation/automatic-acceptance behavior, no private
paths, no raw SQLite/cache files, no fake observed external observations, and no
executable payloads.

Master Index Review Queue Contract v0 is validated with:

```bash
python scripts/validate_master_index_review_queue.py
python scripts/validate_master_index_review_queue.py --json
python -m unittest tests.operations.test_master_index_review_queue_contract tests.scripts.test_validate_master_index_review_queue
```

The validation checks the master-index review queue schemas, inventory files,
synthetic example queue, queue-entry JSONL, decision JSONL, checksum coverage,
allowed validation/review/decision states, privacy/rights/risk posture, no
auto-acceptance, no hosted queue/runtime/upload/account behavior, no private
paths, no raw SQLite/cache files, and no executable payloads.

Source/Evidence/Index Pack Import Planning v0 is validated with:

```bash
python scripts/validate_pack_import_planning.py
python scripts/validate_pack_import_planning.py --json
python -m unittest tests.operations.test_pack_import_planning tests.scripts.test_validate_pack_import_planning
```

The validation checks the planning audit pack and report, confirms
`import_runtime_implemented=false`, `validate_only` as the first future mode,
`stage_local_quarantine` as the next mode, supported source/evidence/index/
contribution pack types, references to existing pack validators, prohibited
import behaviors, private staging posture, no default local search/index
impact, no master-index auto-acceptance, and no import-runtime claims.

Pack Import Validator Aggregator v0 is validated with:

```bash
python scripts/validate_pack_set.py --list-examples
python scripts/validate_pack_set.py --all-examples
python scripts/validate_pack_set.py --all-examples --json
python -m unittest tests.operations.test_pack_import_validator_aggregator tests.scripts.test_validate_pack_set
```

The validation checks the example-pack registry, all known source/evidence/
index/contribution/master-index review queue examples, explicit one-pack
validation, unknown-type handling, unavailable-validator reporting, JSON output,
and no mutation/import/staging/indexing/network side effects.

AI Provider Contract v0 is validated with:

```bash
python scripts/validate_ai_provider_contract.py
python scripts/validate_ai_provider_contract.py --json
python -m unittest tests.operations.test_ai_provider_contract tests.scripts.test_validate_ai_provider_contract
```

The validation checks AI schemas, provider inventory, disabled stub example,
typed output examples, checksums, disabled-by-default provider posture,
privacy/credential/logging defaults, required review, forbidden truth/rights/
malware/auto-acceptance uses, no API keys/secrets, no model calls, and no AI
runtime/public-search/master-index mutation claims.

Typed AI Output Validator v0 is validated with:

```bash
python scripts/validate_ai_output.py --all-examples
python scripts/validate_ai_output.py --all-examples --json
python -m unittest runtime.engine.ai.tests.test_typed_output_validator tests.operations.test_typed_ai_output_validator tests.scripts.test_validate_ai_output
```

The validation checks standalone typed AI output examples, required review,
forbidden truth/rights/malware/auto-acceptance uses, provider alignment,
private-path and secret rejection, generated-text bounds, and no
model/network/import/mutation side effects.

Pack Import Report Format v0 is validated with:

```bash
python scripts/validate_pack_import_report.py --all-examples
python scripts/validate_pack_import_report.py --all-examples --json
python -m unittest tests.operations.test_pack_import_report_format tests.scripts.test_validate_pack_import_report
```

The validation checks the report schema, synthetic passed/failed/unknown
reports, pack-result statuses, issue types, next actions, redacted
private-path failures, no secrets, no authority claims, and hard false
import/staging/index/upload/runtime/master-index/network mutation fields.

Validate-Only Pack Import Tool v0 is validated with:

```bash
python scripts/validate_only_pack_import.py --list-examples
python scripts/validate_only_pack_import.py --all-examples
python scripts/validate_only_pack_import.py --all-examples --json
python -m unittest tests.operations.test_validate_only_pack_import_tool tests.scripts.test_validate_only_pack_import
```

The validation checks explicit-root and all-example validate-only preflight,
Pack Import Report v0 generation, optional typed AI output example inclusion,
strict unknown-type failure handling, explicit `--output` report writing, and
hard false import/staging/index/upload/runtime/master-index/network/model
mutation fields. It does not import, stage, index, upload, mutate runtime
state, mutate public search, call networks, call models, or accept anything
into the master index.

Manual External Baseline Observation Pack v0 is validated with:

```bash
python -m unittest tests.evals.test_external_baseline_observations
python -m unittest tests.scripts.test_external_baseline_observation_scripts
python scripts/validate_external_baseline_observations.py
python scripts/validate_external_baseline_observations.py --json
python scripts/report_external_baseline_status.py
python scripts/report_external_baseline_status.py --json
```

The lane checks that the manual-only baseline systems, schema, template,
instructions, and pending observation manifest exist; that all 64 queries have
pending slots for Google web search, Internet Archive metadata search, and
Internet Archive full-text/OCR search; and that no pending slot is counted as
observed evidence.

Manual Observation Batch 0 is validated with:

```bash
python -m unittest tests.evals.test_manual_observation_batch_0
python scripts/validate_external_baseline_observations.py
python scripts/report_external_baseline_status.py
```

The lane checks that the first prioritized batch selects 13 existing query IDs,
covers all three manual-only baseline systems, produces 39 pending batch slots,
and keeps every slot pending with no top results. It prepares human observation
only; it does not scrape, automate external searches, or fabricate external
baseline evidence.

Manual Observation Entry Helper v0 is validated with:

```bash
python -m unittest tests.scripts.test_external_baseline_entry_helpers
python scripts/list_external_baseline_observations.py --batch batch_0
python scripts/list_external_baseline_observations.py --batch batch_0 --json
python scripts/create_external_baseline_observation.py --batch batch_0 --query-id windows_7_apps --system-id google_web_search --stdout
python scripts/validate_external_baseline_observations.py --file <path>
python scripts/report_external_baseline_status.py --batch batch_0 --next-pending --json
```

The helper lane checks local entry tooling only. It lists pending slots,
creates fillable pending JSON, validates one file or all files, and summarizes
Batch 0 progress without opening browsers, fetching URLs, scraping, automated
external searches, or observed-baseline fabrication.

## LIVE_ALPHA_00 Static Public Site Pack

LIVE_ALPHA_00 Static Public Site Pack is validated with:

```bash
python scripts/validate_public_static_site.py
python scripts/validate_public_static_site.py --json
python -m unittest tests.operations.test_public_static_site_pack tests.scripts.test_validate_public_static_site
```

The lane checks the committed no-JS `site/dist/` pack, manifest, local links,
source matrix coverage, required cautionary phrases, prohibited claims, and
public-alpha limitations. It performs no network calls, starts no server,
deploys nothing, and does not add backend hosting, live probes, scraping, or
production-readiness claims.

## Public Alpha Rehearsal Evidence

Public Alpha Rehearsal Evidence v0 is validated with:

```bash
python scripts/generate_public_alpha_rehearsal_evidence.py
python scripts/generate_public_alpha_rehearsal_evidence.py --json
python scripts/generate_public_alpha_rehearsal_evidence.py --check
python -m unittest tests.operations.test_public_alpha_rehearsal_evidence tests.scripts.test_public_alpha_rehearsal_evidence_script
```

The lane checks the supervised local rehearsal evidence pack under
`docs/operations/public_alpha_rehearsal_evidence_v0/`, including static-site
validation, public-alpha smoke evidence, route inventory counts, eval/audit
status, external-baseline pending/observed counts, blockers, and unsigned
operator signoff. It does not deploy, approve production, add live probes, or
record external observations.

## LIVE_ALPHA_01 Public Alpha Wrapper

LIVE_ALPHA_01 Production Public-Alpha Wrapper is validated with:

```bash
python scripts/run_public_alpha_server.py --check-config
python scripts/run_public_alpha_server.py --print-config-json
python -m unittest tests.scripts.test_public_alpha_wrapper
python -m unittest surfaces.web.tests.test_public_alpha_wrapper_config
python -m unittest tests.operations.test_public_alpha_wrapper_docs
```

The lane checks the stdlib public-alpha entrypoint, safe default config,
nonlocal-bind guard, live-probe/live-IA closed gates, local path refusal,
download/readback and user-storage disablement, status projection, and docs
caveats. It does not start a persistent server during validation, deploy
Eureka, add provider files, enable live probes, add auth/TLS/rate limiting, or
approve production.

## Public Publication Plane Contracts

Public Publication Plane Contracts v0 is validated with:

```bash
python scripts/validate_publication_inventory.py
python scripts/validate_publication_inventory.py --json
python -m unittest tests.operations.test_publication_inventory tests.scripts.test_validate_publication_inventory
```

The lane checks `control/inventory/publication/`, route stability vocabulary,
public status taxonomy, current `site/dist/` page coverage, future reserved
routes, client profiles, deployment target semantics, public data contract
entries, empty redirect policy, and claim traceability docs. It performs no
network calls, deploys nothing, adds no provider files, creates no static site
generator, enables no live backend, and records no external observations.

## GitHub Pages Deployment Enablement

GitHub Pages Deployment Enablement v0 is validated with:

```bash
python scripts/check_github_pages_static_artifact.py --path site/dist
python scripts/check_github_pages_static_artifact.py --path site/dist --json
python -m unittest tests.operations.test_github_pages_deployment_enablement tests.scripts.test_check_github_pages_static_artifact
```

The lane checks `.github/workflows/pages.yml`, the `github_pages_project`
deployment target, the current `site/dist/` artifact, base-path-safe links,
and artifact exclusion rules for runtime source, secrets, local stores, cache
directories, Python files, and SQLite databases. It performs no network calls,
does not manually deploy anything, uploads no backend, adds no live probes,
adds no custom domain, adds no generator, and makes no deployment-success claim
without GitHub Actions evidence.

## Static Site Generation Migration

Static Site Generation Migration v0 is validated with:

```bash
python site/build.py --check
python site/build.py --json
python site/validate.py
python site/validate.py --json
python -m unittest tests.operations.test_static_site_generation_migration tests.scripts.test_static_site_generator
python scripts/validate_public_static_site.py --site-root site/dist
```

The lane checks the stdlib-only `site/` source tree, templates, page JSON,
generated `site/dist/` output, no-JS pages, relative links, source-list
coverage, and manifest posture. Repository Shape Consolidation v0 keeps
`site/dist/` as the single generated GitHub Pages artifact. The lane performs
no network calls, adds no Node/npm or frontend framework, starts no backend,
enables no live probes, and makes no production-readiness claim.

## Generated Public Data Summaries

Generated Public Data Summaries v0 is validated with:

```bash
python scripts/generate_public_data_summaries.py --check
python scripts/generate_public_data_summaries.py --json
python -m unittest tests.operations.test_generated_public_data_summaries tests.scripts.test_generate_public_data_summaries
```

The lane checks deterministic static JSON under `site/dist/data/`, public-data
contract coverage, source-summary placeholder honesty, eval/audit counts,
route-summary posture, and build
manifest no-deployment claims. It performs no network calls, starts no backend,
adds no live API, enables no live probes, records no external observations, and
does not change the GitHub Pages artifact.

## Public Data Stability

Public Data Contract Stability Review v0 is validated with:

```bash
python scripts/validate_public_data_stability.py
python scripts/validate_public_data_stability.py --json
python -m unittest tests.operations.test_public_data_contract_stability_review tests.scripts.test_validate_public_data_stability
```

The lane checks field-level stability classifications for generated public JSON
under `site/dist/data/`. It keeps public JSON from being treated as a
production API, separates stable-draft fields from experimental and volatile
fields, and changes no runtime behavior.

## Generated Artifact Drift Guard

Generated Artifact Drift Guard v0 is validated with:

```bash
python scripts/check_generated_artifact_drift.py
python scripts/check_generated_artifact_drift.py --json
python scripts/check_generated_artifact_drift.py --list
python scripts/check_generated_artifact_drift.py --artifact static_site_dist
python -m unittest tests.operations.test_generated_artifact_drift_guard tests.scripts.test_check_generated_artifact_drift
```

The lane checks committed generated and generated-like artifacts against their
owning check commands: public data, lite/text/files surfaces, static demos,
static snapshot seed files, `site/dist`, Python oracle goldens, public-alpha
rehearsal evidence, publication inventories, test registry metadata, and AIDE
metadata. It is validation/audit only; default mode does not run update
commands, mutate artifacts, deploy, call external services, open sockets, or add
runtime behavior.

## Repository Shape Consolidation

Repository Shape Consolidation v0 is validated with:

```bash
python scripts/validate_repository_layout.py
python scripts/validate_repository_layout.py --json
python scripts/check_generated_artifact_drift.py --artifact static_site_dist
python -m unittest tests.operations.test_repository_shape_consolidation tests.scripts.test_validate_repository_layout
```

The lane checks that `site/dist/` is the single generated static artifact,
the retired legacy static artifact path is absent, `external/` is the
outside-reference root, the Pages workflow uploads `site/dist/`, publication
and generated-artifact inventories point at `site/dist/`, and historical audit
references remain separate from active configuration.

## Lite/Text/Files Seed Surfaces

Lite/Text/Files Seed Surfaces v0 is validated with:

```bash
python scripts/generate_compatibility_surfaces.py --check
python scripts/generate_compatibility_surfaces.py --json
python -m unittest tests.operations.test_lite_text_files_surfaces tests.scripts.test_generate_compatibility_surfaces
```

The lane checks static no-JS compatibility surfaces under `site/dist/lite/`,
plain-text files under `site/dist/text/`, file-tree manifests and SHA256SUMS
under `site/dist/files/`, generated copies under `site/dist/`, relative-link
posture, public data references, and no-download/no-live-search caveats. It
performs no network calls, starts no backend, adds no live search, adds no
executable downloads, creates no signed snapshot, and adds no relay or native
runtime behavior.

## Static Resolver Demo Snapshots

Static Resolver Demo Snapshots v0 is validated with:

```bash
python scripts/generate_static_resolver_demos.py --check
python scripts/generate_static_resolver_demos.py --json
python -m unittest tests.operations.test_static_resolver_demo_snapshots tests.scripts.test_generate_static_resolver_demos
```

The lane checks static no-JS demo pages under `site/dist/demo/`, generated
copies under `site/dist/demo/`, the static demo manifest, relative-link posture,
fixture-backed limitation text, and publication-inventory coverage. It performs
no network calls, starts no backend, adds no live search, creates no live API,
records no external observations, and makes no production-readiness claim.

## Custom Domain And Alternate Host Readiness

Custom Domain / Alternate Host Readiness v0 is validated with:

```bash
python scripts/validate_static_host_readiness.py
python scripts/validate_static_host_readiness.py --json
python -m unittest tests.operations.test_custom_domain_alternate_host_readiness tests.scripts.test_validate_static_host_readiness
```

The lane checks `domain_plan.json`, `static_hosting_targets.json`, `/eureka/`
and `/` base-path policy, no `site/dist/CNAME`, no DNS/provider config,
relative static links, and no custom-domain/backend/live-probe/production
claims. It performs no network calls, DNS lookups, URL fetches, provider
actions, deployments, backend hosting, or live source probing.

## Live Backend Handoff Contract

Live Backend Handoff Contract v0 is validated with:

```bash
python scripts/validate_live_backend_handoff.py
python scripts/validate_live_backend_handoff.py --json
python -m unittest tests.operations.test_live_backend_handoff_contract tests.scripts.test_validate_live_backend_handoff
```

The lane checks `live_backend_handoff.json`, `live_backend_routes.json`,
`surface_capabilities.json`, reserved `/api/v1` endpoint posture, disabled
live backend/probe capability flags, error-envelope docs, static page claims,
and absence of backend deployment config. It performs no network calls, starts
no backend, adds no route handlers, enables no live probes, and creates no
production API guarantee.

## Live Probe Gateway Contract

Live Probe Gateway Contract v0 is validated with:

```bash
python scripts/validate_live_probe_gateway.py
python scripts/validate_live_probe_gateway.py --json
python -m unittest tests.operations.test_live_probe_gateway_contract tests.scripts.test_validate_live_probe_gateway
```

The lane checks `live_probe_gateway.json`, disabled candidate source posture,
global and per-source limits, cache/evidence policy, Google manual-baseline-only
status, public-alpha wrapper live-probe closure, `/api/v1/live-probe` remaining
blocked, and docs/static pages for no-live-probe claims. It performs no network
calls, implements no adapters, fetches no URLs, enables no downloads, calls no
external sources, and does not make Internet Archive live probing available.

## Compatibility Surface Strategy

Compatibility Surface Strategy v0 is validated with:

```bash
python scripts/validate_compatibility_surfaces.py
python scripts/validate_compatibility_surfaces.py --json
python -m unittest tests.operations.test_compatibility_surface_strategy tests.scripts.test_validate_compatibility_surfaces
```

The lane checks `surface_capabilities.json`, `surface_route_matrix.json`,
client-profile alignment, implemented static route roots, future snapshot,
relay, native, app, and `/api/v1` posture, old-client degradation docs,
native-client readiness docs, and static page no-live/no-production claims. It
performs no network calls, adds no runtime behavior, implements no snapshots,
relay service, native app, live backend, live probes, or frontend framework,
and keeps `site/dist/` as the current static artifact.

## Signed Snapshot Format

Signed Snapshot Format v0 is validated with:

```bash
python scripts/generate_static_snapshot.py --check
python scripts/generate_static_snapshot.py --json
python scripts/validate_static_snapshot.py
python scripts/validate_static_snapshot.py --json
python -m unittest tests.operations.test_signed_snapshot_format tests.scripts.test_static_snapshot_tools
```

The lane checks `snapshot_contract.json`, snapshot format/signature policy
docs, the deterministic seed example under
`snapshots/examples/static_snapshot_v0/`, checksums, signature-placeholder
language, no-key/no-binary/no-live claims, and files-surface references. It
performs no network calls, adds no real signing keys, creates no production
signatures, publishes no executable downloads, adds no public `/snapshots/`
route, and implements no relay or native-client runtime.

## Signed Snapshot Consumer Contract

Signed Snapshot Consumer Contract v0 is validated with:

```bash
python scripts/validate_snapshot_consumer_contract.py
python scripts/validate_snapshot_consumer_contract.py --json
python -m unittest tests.operations.test_signed_snapshot_consumer_contract tests.scripts.test_validate_snapshot_consumer_contract
```

The lane checks `snapshot_consumer_contract.json`,
`snapshot_consumer_profiles.json`, `SNAPSHOT_CONSUMER_CONTRACT.md`, the
required read order against `snapshots/examples/static_snapshot_v0/`, checksum
and v0 signature-placeholder language, disabled production/native/relay
consumer flags, profile limits, and no-key posture. It performs no network
calls, implements no snapshot reader runtime, creates no relay or native
client, adds no production signing, real signing keys, executable downloads,
live backend behavior, or live probes.

## Relay Surface Design

Relay Surface Design v0 is validated with:

```bash
python scripts/validate_relay_surface_design.py
python scripts/validate_relay_surface_design.py --json
python -m unittest tests.operations.test_relay_surface_design tests.scripts.test_validate_relay_surface_design
```

The lane checks `relay_surface.json`, protocol candidates, disabled defaults,
relay architecture/reference/security docs, the unsigned future operator
checklist, surface capability alignment, route-matrix posture, and no-runtime
claims. It performs no network calls, opens no sockets, implements no relay
runtime, adds no FTP, SMB, WebDAV, AFP, NFS, Gopher, local HTTP relay, protocol
proxy, private data exposure, write/admin route, live-probe passthrough, native
sidecar, backend hosting, or production relay claim.

## Relay Prototype Planning

Relay Prototype Planning v0 is validated with:

```bash
python scripts/validate_relay_prototype_plan.py
python scripts/validate_relay_prototype_plan.py --json
python -m unittest tests.operations.test_relay_prototype_planning tests.scripts.test_validate_relay_prototype_plan
```

The lane checks the planning pack under
`control/audits/relay-prototype-planning-v0/`, the local static HTTP first
candidate decision, allowed/prohibited input/output contracts,
localhost-only/read-only/static security defaults, explicit human approval
gate, and no-runtime/no-socket posture. It performs no network calls, opens no
sockets, implements no relay server, local HTTP relay, protocol support,
private file serving, live backend proxying, live probes, native sidecar,
snapshot mount, downloads, installers, telemetry, or relay runtime wiring.

## Native Client Contract

Native Client Contract v0 is validated with:

```bash
python scripts/validate_native_client_contract.py
python scripts/validate_native_client_contract.py --json
python -m unittest tests.operations.test_native_client_contract tests.scripts.test_validate_native_client_contract
```

The lane checks `native_client_contract.json`, `native_client_lanes.json`,
Native Client reference docs, the unsigned readiness checklist, CLI current
state, snapshot/public-data dependencies, future Windows/Mac lane posture,
absence of Visual Studio/Xcode project files, and no installer/download/Rust
wiring claims. It performs no network calls, creates no native app project,
implements no GUI, adds no FFI, relay sidecar, package-manager behavior,
native snapshot reader runtime, executable download/execution automation, live
backend behavior, or live probes.

## Native Action / Download / Install Policy

Native Action / Download / Install Policy v0 is validated with:

```bash
python scripts/validate_action_policy.py
python scripts/validate_action_policy.py --json
python -m unittest tests.operations.test_action_download_install_policy tests.scripts.test_validate_action_policy
```

The lane checks `action_policy.json`, action/download/install policy docs,
executable-risk docs, rights/access docs, install-handoff docs, related
native/snapshot/relay contract references, and public-alpha/static defaults.
It performs no network calls and implements no downloads, installers,
package-manager integration, malware scanning, rights clearance, native
clients, relay runtime, public download surface, or executable trust claim.

## Native Local Cache / Privacy Policy

Native Local Cache / Privacy Policy v0 is validated with:

```bash
python scripts/validate_local_cache_privacy_policy.py
python scripts/validate_local_cache_privacy_policy.py --json
python -m unittest tests.operations.test_native_local_cache_privacy_policy tests.scripts.test_validate_local_cache_privacy_policy
```

The lane checks `local_cache_privacy_policy.json`, local cache/privacy docs,
native cache contract docs, telemetry/logging policy docs, related
native/snapshot/relay/public-alpha references, disabled telemetry/account/cloud
sync flags, and prohibited private-data behavior. It performs no network calls
and implements no cache runtime, private file ingestion, local archive scanning,
telemetry, analytics, accounts, cloud sync, uploads, native clients, relay
runtime, or private-data relay behavior.

## Native Project Readiness Review

Native Client Project Readiness Review v0 is validated with:

```bash
python scripts/validate_native_project_readiness_review.py
python scripts/validate_native_project_readiness_review.py --json
python -m unittest tests.operations.test_native_project_readiness_review tests.scripts.test_validate_native_project_readiness_review
```

The lane checks the audit pack under
`control/audits/native-client-project-readiness-v0/`, its JSON readiness
decision, first candidate lane, pre-native checklist, human-approval gate, and
the absence of Visual Studio/Xcode project files. It performs no network calls
and implements no native app, GUI behavior, FFI, cache runtime, downloads,
installers, relay runtime, live probes, or runtime wiring.

## Source Coverage And Capability

Source Coverage and Capability Model v0 is validated with:

```bash
python -m unittest runtime.source_registry.tests.test_source_capability_coverage
```

This check verifies coverage-depth vocabulary, capability booleans, placeholder
honesty, recorded-fixture posture, and source-registry filtering. It is a
metadata/projection guard only; it does not add source connectors, live probing,
crawling, or source acquisition behavior.

## Real Source Coverage Pack

Real Source Coverage Pack v0 is validated with:

```bash
python -m unittest runtime.connectors.internet_archive_recorded.tests.test_connector runtime.connectors.local_bundle_fixtures.tests.test_connector runtime.engine.index.tests.test_real_source_coverage_pack tests.integration.test_real_source_coverage_pack
```

This check verifies the recorded Internet Archive-like fixture loader, committed
local bundle fixture loader, local-index visibility, public projection, and
bounded member readback. It does not perform live Internet Archive API calls,
scraping, crawling, broad source federation, or arbitrary local filesystem
ingestion.

## Old-Platform Source Coverage Expansion

Old-Platform Source Coverage Expansion v0 is validated with:

```bash
python -m unittest runtime.connectors.internet_archive_recorded.tests.test_connector runtime.connectors.local_bundle_fixtures.tests.test_connector runtime.engine.synthetic_records.tests.test_member_record_synthesis runtime.engine.index.tests.test_real_source_coverage_pack runtime.engine.compatibility.tests.test_compatibility_evidence tests.integration.test_old_platform_source_coverage_expansion
```

This check verifies the expanded committed Internet-Archive-shaped records,
local bundle ZIP fixtures, member synthesis, compatibility evidence, and
local-index/public projection for the old-platform wedge. It does not perform
live source calls, scraping, crawling, broad source federation, arbitrary local
filesystem ingestion, or real binary handling.

## Old-Platform Software Planner Pack

Old-Platform Software Planner Pack v0 is validated with:

```bash
python -m unittest runtime.engine.query_planner.tests.test_old_platform_planner
```

This check verifies deterministic OS aliases, platform-as-constraint handling,
latest-compatible release intent, driver/hardware/OS intent, vague identity
uncertainty, documentation intent, member-discovery hints, and app-vs-OS-media
suppression hints. It improves planner interpretation only; it does not add
ranking, fuzzy/vector retrieval, LLM planning, live source behavior, source
connectors, or planner-owned retrieval routing.

## Member-Level Synthetic Records

Member-Level Synthetic Records v0 is validated with:

```bash
python -m unittest runtime.engine.synthetic_records.tests.test_member_record_synthesis runtime.engine.index.tests.test_member_level_synthetic_records tests.integration.test_member_level_synthetic_records_slice
```

This check verifies deterministic member target refs, parent lineage,
source/evidence preservation, and local-index visibility for bounded
fixture-backed bundle members. It does not add broad archive extraction,
arbitrary local filesystem ingestion, ranking, or live source behavior.

## Result Lanes And User Cost

Result Lanes + User-Cost Ranking v0 is validated with:

```bash
python -m unittest runtime.engine.ranking.tests.test_result_lanes runtime.engine.ranking.tests.test_user_cost runtime.engine.index.tests.test_member_level_synthetic_records tests.integration.test_github_release_http_api_slice
```

This check verifies deterministic lane assignment, user-cost explanations,
member-vs-parent cost behavior, and public search projection for current
result records. It validates bounded usefulness annotations only; it does not
add production ranking, fuzzy/vector retrieval, LLM scoring, live source
behavior, or source connectors.

## Compatibility Evidence

Compatibility Evidence Pack v0 is validated with:

```bash
python -m unittest runtime.engine.compatibility.tests.test_compatibility_evidence runtime.engine.compatibility.tests.test_service runtime.engine.index.tests.test_member_level_synthetic_records surfaces.web.tests.test_compatibility_rendering surfaces.native.cli.tests.test_local_index_cli
```

This check verifies source-backed compatibility evidence extraction,
compatibility verdict projection, index/search evidence fields, and current
surface rendering for bounded fixture-backed records. It preserves unknown
compatibility and does not add a compatibility oracle, installer/runtime
execution, live source behavior, scraping, fuzzy/vector retrieval, LLM
behavior, Rust behavior, or source connectors.

## Post-Queue Checkpoint Lane

Post-Queue State Checkpoint v0 is validated with:

- `python scripts/validate_post_queue_checkpoint.py`
- `python scripts/validate_post_queue_checkpoint.py --json`
- `python -m unittest tests.operations.test_post_queue_state_checkpoint tests.scripts.test_validate_post_queue_checkpoint`

The checkpoint lane is audit/reporting only. It records command outcomes,
eval/audit state, external-baseline pending status, risks, deferrals, and next
planning without adding product runtime behavior or live network behavior.

## Full Project State Audit Lane

Full Project State Audit v0 is validated with:

- `python scripts/validate_full_project_state_audit.py`
- `python scripts/validate_full_project_state_audit.py --json`
- `python -m unittest tests.operations.test_full_project_state_audit tests.scripts.test_validate_full_project_state_audit`

The audit lane records the post-relay-planning project state, broad
verification, Cargo availability status, external-baseline pending status,
risks, blockers, human-operated work, deferrals, and next milestone
recommendations. It does not add product behavior, live network behavior,
native project files, relay runtime, downloads, installers, telemetry, or
deployment changes.
