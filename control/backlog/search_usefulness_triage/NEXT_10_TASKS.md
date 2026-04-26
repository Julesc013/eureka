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

## 5. Result Lanes + User-Cost Ranking v0

Why: once evidence exists, results need explicit lanes and user-cost explanation.

Prerequisite: source and member evidence improvements.

Likely files: `runtime/engine/evals/`, `docs/evals/`, `evals/archive_resolution/`.

Acceptance criteria: lane labels are deterministic, bad-result patterns remain visible, and user-cost scoring is evidence-bounded.

Tests to add first: lane assignment tests, user-cost explanation tests, bad-result guard tests.

Do not do: do not add fuzzy/vector/LLM ranking or hidden semantic relevance.

Expected audit effect: actionability and user-cost reduction improve for selected queries.

## 6. Compatibility Evidence Pack v0

Why: old-platform usefulness depends on compatibility clarity.

Prerequisite: recorded source evidence for old platforms.

Likely files: `contracts/archive/fixtures/`, `runtime/engine/compatibility/`, `evals/search_usefulness/`.

Acceptance criteria: Windows 98, Windows 2000, Windows XP, Vista, and Windows 7 / NT 6.1 evidence types are represented, with unknown compatibility preserved.

Tests to add first: known/unknown compatibility evidence tests, driver/app distinction tests.

Do not do: do not build a compatibility oracle or execute installers.

Expected audit effect: compatibility_evidence_gap decreases.

## 7. Search Usefulness Audit Delta v0

Why: future slices need before/after evidence.

Prerequisite: at least one source/planner/member improvement.

Likely files: `runtime/engine/evals/`, `evals/search_usefulness/`, `tests/operations/`.

Acceptance criteria: delta report captures status changes with evidence and keeps external baselines pending/manual.

Tests to add first: delta schema validation, status-change justification guard.

Do not do: do not weaken queries to improve deltas.

Expected audit effect: makes improvement or regression visible.

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
