# Next 10 Recommended Tasks

## 1. Source Coverage and Capability Model v0

Why: source coverage is the dominant gap, and capability depth must be governed before adding fixtures.

Prerequisite: current Source Registry v0 and Hard Test Pack v0 remain green.

Likely files: `contracts/source_registry/`, `control/inventory/sources/`, `docs/architecture/`, `tests/operations/`.

Acceptance criteria: source capability fields exist, source families map to query families, placeholders remain honest, and no live crawling is introduced.

Tests to add first: source capability schema validation, placeholder honesty expansion, query-family-to-source-capability tests.

Do not do: do not add connectors or mark placeholders implemented.

Expected audit effect: no immediate status change, but creates the model required for useful source-gap reduction.

Status: implemented as bounded metadata and projection only. It added no
connectors, live probing, crawling, or source acquisition behavior.

## 2. Real Source Coverage Pack v0

Why: old-platform-compatible software search needs recorded source evidence.

Prerequisite: Source Coverage and Capability Model v0.

Likely files: `control/inventory/sources/`, `runtime/connectors/`, `contracts/archive/fixtures/`, `evals/search_usefulness/`.

Acceptance criteria: small recorded fixture families exist for selected old-platform queries; no required tests use network access.

Tests to add first: recorded fixture parse tests, no-network loader tests, source status honesty tests.

Do not do: do not scrape, crawl, or claim global recall.

Expected audit effect: selected source_gap queries may become partial/covered when evidence supports it.

Status: implemented with tiny committed Internet Archive-like recorded
metadata/file-list fixtures and local bundle ZIP fixtures. It added no live
Internet Archive API calls, scraping, crawling, broad source federation, or
arbitrary local filesystem ingestion.

## 3. Old-Platform Software Planner Pack v0

Why: planner/query-interpretation gaps are the second largest failure family.

Prerequisite: source capability model and first recorded fixtures.

Likely files: `runtime/engine/query_planner/`, `evals/search_usefulness/`, `tests/parity/golden/python_oracle/v0/query_planner/`.

Acceptance criteria: OS aliases, latest-compatible intent, driver/hardware/OS intent, vague identity clues, and app-vs-OS-media suppression are deterministic and tested.

Tests to add first: planner expected task-kind tests, Windows NT alias tests, app-vs-OS suppression tests.

Do not do: do not add LLM planning, fuzzy retrieval, vector search, or ranking.

Expected audit effect: planner_gap and query_interpretation_gap decrease for old-platform queries.

Status: implemented as deterministic planner interpretation only. The current
audit now reports `planner_gap=24` and `query_interpretation_gap=21`, while
source coverage, compatibility evidence, representation, decomposition, and
member-access gaps remain honest future work.

## 4. Member-Level Synthetic Records v0

Why: many hard queries require a member inside a parent bundle or scan.

Prerequisite: source capability model, Real Source Coverage Pack v0, and
Old-Platform Software Planner Pack v0.

Likely files: `contracts/archive/fixtures/`, `runtime/engine/index/`, `runtime/engine/decomposition/`, `evals/search_usefulness/`.

Acceptance criteria: member target refs, parent lineage, member path/content type, and member-level index records exist for bounded fixtures.

Tests to add first: member target-ref validation, parent lineage tests, member index tests.

Do not do: do not add arbitrary filesystem reads or broad extraction frameworks.

Expected audit effect: selected package/container/member capability gaps improve.

Status: implemented for bounded committed local bundle fixtures. It adds
deterministic `member:sha256:<digest>` target refs, parent lineage, member
metadata, evidence, exact resolution, local-index/search visibility, and public
projection without broad extraction, arbitrary local filesystem ingestion,
ranking, live source behavior, or new connectors.

## 5. Result Lanes + User-Cost Ranking v0

Why: once evidence exists, results need explicit lanes and user-cost explanation.

Prerequisite: source and member evidence improvements. Member-Level Synthetic
Records v0 now satisfies the first bounded member-evidence prerequisite.

Likely files: `runtime/engine/evals/`, `docs/evals/`, `evals/archive_resolution/`.

Acceptance criteria: lane labels are deterministic, bad-result patterns remain visible, and user-cost scoring is evidence-bounded.

Tests to add first: lane assignment tests, user-cost explanation tests, bad-result guard tests.

Do not do: do not add fuzzy/vector/LLM ranking or hidden semantic relevance.

Expected audit effect: actionability and user-cost reduction improve for selected queries.

Status: implemented as a bounded deterministic annotation seam over existing
result records. It adds result lanes, user-cost scores, reasons, and public
projection without adding production ranking, fuzzy/vector retrieval, LLM
scoring, live source behavior, or new connectors.

## 6. Compatibility Evidence Pack v0

Why: old-platform usefulness depends on compatibility clarity.

Prerequisite: recorded source evidence for old platforms plus bounded
result-lane/user-cost projection. Both prerequisites now exist at v0 scope.

Likely files: `contracts/archive/fixtures/`, `runtime/engine/compatibility/`, `evals/search_usefulness/`.

Acceptance criteria: Windows 98, Windows 2000, Windows XP, Vista, and Windows 7 / NT 6.1 evidence types are represented, with unknown compatibility preserved.

Tests to add first: known/unknown compatibility evidence tests, driver/app distinction tests.

Do not do: do not build a compatibility oracle or execute installers.

Expected audit effect: compatibility_evidence_gap decreases.

Status: implemented as a bounded source-backed evidence seam over current
fixture metadata, member paths, README text, and compatibility notes. It keeps
unknown compatibility valid and adds no runtime execution, installer behavior,
live source calls, scraping, fuzzy/vector retrieval, LLM behavior, Rust behavior
ports, native apps, deployment infrastructure, or new connectors.

## 7. Search Usefulness Audit Delta v0

Why: future slices need before/after evidence.

Prerequisite: source, planner, member, lane/user-cost, and compatibility
evidence slices are implemented at v0 scope.

Likely files: `runtime/engine/evals/`, `evals/search_usefulness/`, `tests/operations/`.

Acceptance criteria: delta report captures status changes with evidence and keeps external baselines pending/manual.

Tests to add first: delta schema validation, status-change justification guard.

Do not do: do not weaken queries to improve deltas.

Expected audit effect: makes improvement or regression visible.

Status: implemented as Search Usefulness Audit Delta v0 under
`control/audits/search-usefulness-delta-v0/`. The measured aggregate movement
is partial `+4`, source_gap `-2`, and capability_gap `-2` against the
historical reported baseline. The report recommends Old-Platform Source
Coverage Expansion v0 next because source coverage remains dominant.

## 7a. Old-Platform Source Coverage Expansion v0

Why: source coverage remains the largest current failure family after the
audit delta.

Prerequisite: Search Usefulness Audit Delta v0 and the existing recorded
fixture/source-capability guardrails.

Likely files: `control/inventory/sources/`, `runtime/connectors/`,
`evals/search_usefulness/`, `tests/integration/`, `tests/hardening/`.

Acceptance criteria: recorded old-platform utility, driver, support-media,
manual, and latest-compatible release fixtures exist; placeholder sources
remain honest; audit status changes are evidence-backed; no required command
uses network access.

Tests to add first: recorded fixture provenance tests, placeholder honesty
guards, and search-usefulness status-change justification tests.

Do not do: do not add live crawling, scraping, broad source federation,
arbitrary local filesystem ingestion, or hard-eval weakening.

Expected audit effect: selected source_gap queries should become partial only
when current source evidence supports the movement.

Status: implemented with expanded committed Internet-Archive-shaped fixture
records and three tiny local bundle ZIP fixtures for Windows 98 registry
repair, Windows XP browser/tools notes, Creative CT1740, and 3Com 3C905
driver-support cases. Current Search Usefulness Audit output reports
`covered=5`, `partial=20`, `source_gap=28`, `capability_gap=9`, and
`unknown=2`; external baselines remain pending/manual.

## 7b. Search Usefulness Audit Delta v1

Why: the old-platform source expansion moved several source-backed queries to
partial, and the repo should record that machine-derived movement before the
next implementation slice.

Prerequisite: Old-Platform Source Coverage Expansion v0 and full verification
remain green.

Likely files: `control/audits/`, `evals/search_usefulness/`,
`tests/operations/`, `.aide/tasks/`.

Acceptance criteria: delta report records current counts, query movement,
remaining source/compatibility/member/ranking gaps, and next recommendation
without changing retrieval behavior or external baseline status.

Tests to add first: delta v1 pack validation, no fake external-baseline guard,
and audit movement sanity checks.

Do not do: do not weaken search-usefulness queries, hard evals, or external
baseline pending/manual posture.

Expected audit effect: no new retrieval behavior; clearer evidence for whether
the next implementation should be compatibility expansion, result-lane
refinement, or another recorded source pack.

Status: implemented as Search Usefulness Audit Delta v1 under
`control/audits/search-usefulness-delta-v1/`. It records `partial +15`,
`source_gap -13`, `capability_gap -2`, archive eval movement to
`capability_gap=1` and `not_satisfied=5`, and recommends Hard Eval
Satisfaction Pack v0 next.

## 7c. Hard Eval Satisfaction Pack v0

Why: at Delta v1, five archive-resolution hard tasks had local source-backed
candidates but remained `not_satisfied`; the precision gap was satisfying hard
expected outcomes honestly, not adding another broad source pack.

Prerequisite: Search Usefulness Audit Delta v1 and all hardening tests remain
green.

Likely files: `evals/archive_resolution/`, `runtime/engine/evals/`,
`runtime/engine/index/`, `runtime/engine/ranking/`, `tests/hardening/`.

Acceptance criteria: hard eval task IDs and expected-result hints remain intact;
source-backed candidates satisfy hard checks only where evidence supports them;
`not_satisfied` remains available for insufficient evidence; no external
baselines are fabricated.

Tests to add first: hard expected-result fixture tests, source-backed candidate
selection tests, result-lane/member-target preference tests, and hard eval
weakening guard expansion.

Do not do: do not weaken hard evals, fabricate exact evidence, add live
crawling, scrape external systems, add fuzzy/vector/LLM retrieval, or call this
production search.

Expected audit effect: selected archive hard tasks may move from
`not_satisfied` only when current fixture-backed results satisfy exact expected
checks; search-usefulness partials should become more actionable.

Status: implemented as Hard Eval Satisfaction Pack v0 under
`control/audits/hard-eval-satisfaction-v0/`. Archive evals now report
`capability_gap=1` and `partial=5`; five source-backed hard tasks moved from
`not_satisfied` to `partial`, and no task is marked overall satisfied.

## 7d. Old-Platform Result Refinement Pack v0

Why: five archive hard tasks now have source-backed partials, but expected
result lanes, bad-result pattern avoidance, and best-actionable-unit result
shape are still not scored. The next step should make those checks explicit
without pretending this is production ranking.

Prerequisite: Hard Eval Satisfaction Pack v0 and hardening tests remain green.

Likely files: `runtime/engine/evals/`, `runtime/engine/ranking/`,
`runtime/engine/index/`, `evals/archive_resolution/`, `tests/evals/`, and
surface projection tests if report fields are exposed.

Acceptance criteria: expected lanes are evaluated deterministically; bad-result
patterns remain strict; member/direct artifact results are distinguished from
parent bundles; overall `satisfied` is allowed only when lane, bad-result, and
evidence checks all pass.

Tests to add first: lane-check fixture tests, bad-result guard tests,
member-vs-parent result-shape tests, and no-fake-satisfied hardening guards.

Do not do: do not add production ranking, fuzzy/vector/LLM retrieval, live
source calls, external scraping, or weaken hard expected-result patterns.

Expected audit effect: selected hard eval partials may move toward satisfied
only if deterministic lane/bad-result/result-shape checks pass.

Status: implemented as Old-Platform Result Refinement Pack v0 under
`control/audits/old-platform-result-refinement-v0/`. Archive evals now report
`capability_gap=1`, `partial=4`, and `satisfied=1`; the driver support-CD
member task is satisfied, while four old-platform hard tasks remain partial.

## 7e. More Source Coverage Expansion v1

Why: result refinement proved one hard task can satisfy strict checks, but the
remaining old-platform partials still need exact latest-compatible release
evidence, concrete old-software identity evidence, direct artifact evidence,
and broader source-backed fixture material.

Prerequisite: Old-Platform Result Refinement Pack v0 and hardening tests remain
green.

Likely files: `runtime/connectors/internet_archive_recorded/`,
`runtime/connectors/local_bundle_fixtures/`, `evals/archive_resolution/`,
`tests/evals/`, and `tests/hardening/`.

Acceptance criteria: fixtures remain tiny and deterministic; exact version and
identity claims require explicit source-backed evidence; placeholder sources
remain placeholders; external baselines remain pending/manual; any hard-eval
movement is source-backed.

Tests to add first: recorded fixture evidence tests, no-fake-exact-version
guards, hard eval source-backed movement tests, and external baseline pending
guards.

Do not do: do not add live source calls, scrape external systems, add arbitrary
local filesystem ingestion, weaken hard evals, or fabricate latest-version or
identity evidence.

Expected audit effect: selected remaining old-platform hard partials may move
toward satisfied only if the new bounded evidence satisfies existing strict
checks.

Status: implemented as More Source Coverage Expansion v1 under
`control/audits/more-source-coverage-expansion-v1/`. Archive evals now report
`capability_gap=1` and `satisfied=5`; the four old-platform hard partials are
now source/evidence-backed satisfied under the current strict checks. The
broader Search Usefulness Audit reports `covered=5`, `partial=21`,
`source_gap=27`, `capability_gap=9`, and `unknown=2`, with external baselines
still pending/manual.

## 7f. Article/Scan Fixture Pack v0

Why: More Source Coverage Expansion v1 satisfied the old-platform hard partials
and left `article_inside_magazine_scan` as the only archive-resolution hard
capability gap. That gap needs bounded scan/page/article evidence, not live
source behavior or another old-platform app fixture.

Prerequisite: More Source Coverage Expansion v1 and hardening tests remain
green.

Likely files: `runtime/connectors/internet_archive_recorded/`,
`runtime/engine/synthetic_records/`, `evals/archive_resolution/`,
`tests/evals/`, and `tests/hardening/`.

Acceptance criteria: article/page/scan fixtures are tiny and deterministic;
source-backed parent/source lineage is preserved; hard eval movement happens
only with explicit article/page evidence; external baselines remain
pending/manual.

Tests to add first: article fixture provenance tests, page/member lineage tests,
no-fake-OCR/article guard tests, and archive hard eval movement tests.

Do not do: do not scrape Internet Archive, call live source APIs, add broad OCR,
fabricate article text, weaken hard evals, or claim broad scan search.

Expected audit effect: `article_inside_magazine_scan` may leave
`capability_gap` only if bounded fixture evidence satisfies the strict hard
checks; broader source gaps may remain dominant.

## 8. Rust Query Planner Parity Candidate v0

Why: Rust parity should preserve useful Python planner behavior after it stabilizes.

Prerequisite: Old-Platform Software Planner Pack v0 and updated Python-oracle goldens.

Likely files: `crates/eureka-core/`, `tests/parity/`, `docs/architecture/RUST_BACKEND_LANE.md`.

Acceptance criteria: Rust planner candidate matches Python oracle output and is not wired into runtime paths.

Tests to add first: parity JSON comparison, allowed-divergence rejection.

Do not do: do not replace Python behavior or add Rust gateway/CLI/FFI.

Expected audit effect: no usefulness delta; migration discipline improves.

## 9. Public Alpha Rehearsal Evidence v0

Why: hosting pack exists, but operator evidence remains separate from implementation.

Prerequisite: public-alpha smoke and hardening tests remain green.

Likely files: `docs/operations/public_alpha_hosting_pack/`.

Acceptance criteria: operator evidence records smoke, route inventory, blockers, and signoff/failure without claiming production approval.

Tests to add first: evidence record validation if committed.

Do not do: do not deploy or add auth/TLS/process management.

Expected audit effect: no search delta; improves operator confidence.

## 10. Compatibility Surface Strategy v0

Why: once compatibility evidence exists, surfaces need a consistent way to present known, unknown, inferred, and incompatible outcomes.

Prerequisite: Compatibility Evidence Pack v0.

Likely files: `docs/architecture/`, `surfaces/web/README.md`, `surfaces/native/cli/README.md`.

Acceptance criteria: compatibility presentation rules exist and preserve truth regardless of user strategy.

Tests to add first: view-model rendering tests for unknown/known compatibility.

Do not do: do not build a modern app shell or native app.

Expected audit effect: prepares actionability and UX improvement.
