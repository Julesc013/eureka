# Next Milestone Recommendations

## 1. Hard Test Pack v0

Why: convert the most important audit proposals into executable guardrails.

Prerequisite: this audit pack merged and green.

Acceptance criteria: tests catch eval weakening, baseline fabrication,
public-alpha path leakage, docs command drift, and Python oracle drift.

Likely files: `tests/operations/`, `tests/evals/`, `tests/parity/`.

Tests to add first: HTP-004, HTP-006, HTP-007, HTP-008.

Do not do: do not add product features.

## 2. Rust Query Planner Parity Candidate v0

Why: query planner is the next small Rust seam after source registry.

Prerequisite: Python oracle query planner goldens stay stable.

Acceptance criteria: Rust candidate emits JSON matching Python query-planner
goldens without being wired into runtime paths.

Likely files: `crates/eureka-core/`, `tests/parity/`.

Tests to add first: planner JSON mismatch and allowed-divergence rejection.

Do not do: do not replace Python planner behavior.

## 3. Real Source Coverage Pack v0

Why: source gaps dominate current usefulness results.

Prerequisite: source registry validation and source fixture policy.

Acceptance criteria: recorded fixture families are added for one or two high
value query families, with no live crawling.

Likely files: `control/inventory/sources/`, `runtime/connectors/*/fixtures/`,
`evals/search_usefulness/`.

Tests to add first: placeholder-not-implemented and recorded-fixture validation.

Do not do: do not scrape or add live connectors.

## 4. Public Alpha Rehearsal Evidence v0

Why: hosting pack exists but has not captured a rehearsal evidence artifact.

Prerequisite: public-alpha smoke and hosting-pack checks pass.

Acceptance criteria: an operator fills smoke evidence and signoff templates for
a supervised rehearsal.

Likely files: `docs/operations/public_alpha_hosting_pack/`.

Tests to add first: evidence template validation if evidence is committed.

Do not do: do not deploy or claim hosting approval.

## 5. Planner Gap Reduction Pack v0

Why: search-usefulness audit reports many query interpretation and planner
gaps.

Prerequisite: hard tests for representative query families.

Acceptance criteria: deterministic planner handles selected additional
families and remains explicit about unknowns.

Likely files: `runtime/engine/query_planner/`, `evals/search_usefulness/`.

Tests to add first: query family expected task-kind tests.

Do not do: do not add LLM, fuzzy, vector, or ranking behavior.

## 6. Internet Archive Recorded Fixture Connector v0

Why: article, manual, and archive metadata gaps need a governed recorded
fixture lane.

Prerequisite: Real Source Coverage Pack v0 and no-scraping policy.

Acceptance criteria: small recorded fixtures load deterministically and remain
marked as recorded, not live.

Likely files: `runtime/connectors/`, `control/inventory/sources/`.

Tests to add first: no-network fixture loader tests.

Do not do: do not call Internet Archive APIs in required tests.

## 7. Wayback/Memento Recorded Fixture Connector v0

Why: dead-link queries need timestamped archived-page evidence.

Prerequisite: recorded fixture source policy.

Acceptance criteria: recorded memento fixtures support safe dead-link evidence.

Likely files: `runtime/connectors/`, `control/inventory/sources/`.

Tests to add first: snapshot-date evidence checks.

Do not do: do not crawl Wayback.

## 8. Local Files Fixture Connector v0

Why: package/container/member queries need local fixture support-media examples.

Prerequisite: hard tests for private path handling.

Acceptance criteria: local fixture paths are governed and never arbitrary
public-alpha parameters.

Likely files: `runtime/connectors/`, `contracts/archive/fixtures/`.

Tests to add first: support-media manifest and local-path privacy tests.

Do not do: do not expose arbitrary local filesystem reads.

## 9. Compatibility Evidence Fixture Pack v0

Why: compatibility clarity is a major usefulness dimension.

Prerequisite: source fixture records with OS/platform evidence.

Acceptance criteria: compatibility verdicts cite source-backed evidence for
selected fixtures.

Likely files: `contracts/archive/fixtures/`, `runtime/engine/compatibility/`.

Tests to add first: evidence-backed known/unknown compatibility outcomes.

Do not do: do not create a compatibility oracle from guesses.

## 10. Eval Capability Gap Reduction Pack v0

Why: selected capability gaps should become implemented or better classified
after fixtures land.

Prerequisite: hard test pack and source coverage pack.

Acceptance criteria: chosen hard queries move from gap to partial/covered only
when evidence supports it.

Likely files: `evals/archive_resolution/`, `evals/search_usefulness/`,
`runtime/engine/evals/`.

Tests to add first: status-change justification tests.

Do not do: do not weaken expected fields.

## 11. Rust Local Index Parity Candidate v0

Why: after planner parity, local index record shape is a useful Rust seam.

Prerequisite: stable local-index Python goldens and query planner parity.

Acceptance criteria: Rust candidate matches normalized local-index JSON shapes
without replacing Python.

Likely files: `crates/`, `tests/parity/`.

Tests to add first: FTS-normalized parity checks.

Do not do: do not add database-backed Rust runtime services.

## 12. Docs Link/Command Drift Guard v0

Why: the repo now has many docs and command references.

Prerequisite: test registry and command matrix.

Acceptance criteria: required docs links and script command references are
checked with stdlib tests.

Likely files: `tests/operations/`, `control/inventory/tests/`.

Tests to add first: command-file existence and required README/index checks.

Do not do: do not build a full documentation site.

