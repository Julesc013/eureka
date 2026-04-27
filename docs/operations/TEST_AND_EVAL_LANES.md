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
- `public_alpha`: route inventory, smoke, and hosting-pack safety checks
- `parity`: Python oracle, source-registry, and source coverage/capability
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

Current Rust commands are optional. Cargo may not be installed in every
execution environment, and Python remains the reference/oracle lane.

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

The validation checks the satisfaction report, `capability_gap=1` and
`partial=5` archive-eval posture, source-backed evidence for moved tasks, the
unchanged article-inside-scan capability gap, and the absence of overall
satisfied hard tasks while lane/bad-result checks remain not evaluable.

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
