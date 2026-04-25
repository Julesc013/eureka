# Audit Summary

## Baseline

Eureka is a Python reference backend prototype for temporal object resolution.
It has many bounded deterministic seams and a governed Rust parity lane, but it
is not a production service and not a broad archive search engine yet.

## What Is Healthy

- Architecture boundaries are explicit and have a checker.
- Source Registry v0 exists as a control plane.
- Public-alpha mode has route policy, inventory, smoke checks, and a hosting
  pack.
- Archive-resolution and search-usefulness evals report capability gaps
  honestly.
- Python oracle golden fixtures exist for future Rust parity.
- The first Rust behavior seam is isolated and not wired into runtime paths.

## Main Structural Findings

- Navigation roots are uneven for docs and AIDE metadata.
- Command metadata can drift between AIDE files, docs, scripts, and the new
  registry.
- Route inventory remains manually curated and should eventually gain a drift
  guard.

## Main Content and Source Findings

- Source coverage is the dominant blocker.
- Latest-compatible releases, drivers, manuals, article-inside-scan, dead-link,
  and vague-identity queries need recorded fixtures before broader behavior can
  be judged.
- External baselines are pending manual observation for all 64
  search-usefulness queries.

## Main Behavior Findings

- The doctrine direction is implemented in bounded form.
- The smallest actionable unit is only proven for narrow ZIP fixtures.
- Compatibility evidence exists but is not yet source-rich.
- Resolution memory is local/manual and should stay privacy-conscious.

## Main Test Findings

- Add hard tests for eval weakening, external baseline fabrication, public-alpha
  path leakage, docs command drift, planner misclassification, and Python oracle
  drift.
- Do not implement ranking, fuzzy/vector/LLM search, live crawling, or new
  connectors just to make audits greener.

## Biggest Risks

- Mistaking source gaps for ranking gaps.
- Treating public-alpha rehearsal evidence as hosting approval.
- Letting docs and command metadata drift as the repo grows.
- Expanding Rust behavior without enough Python-oracle parity fixtures.

## What Not To Do Next

- Do not scrape Google or Internet Archive.
- Do not add live source sync.
- Do not weaken hard evals.
- Do not port broad Rust behavior.
- Do not add deployment infrastructure.
- Do not make production-readiness claims.

