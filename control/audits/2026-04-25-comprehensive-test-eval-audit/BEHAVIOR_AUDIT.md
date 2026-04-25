# Behavior and Doctrine Audit

## Overall Read

Eureka's implemented behavior aligns with the accepted doctrine direction, but
most behavior remains bounded by a very small corpus. The repo is strongest on
structure: source inventory, evidence summaries, explicit absence, public
boundaries, action routing, evals, and public-alpha safety. It is weakest on
source breadth, planner coverage, member/article-level fixtures, compatibility
evidence, and hard-test density.

## Doctrine Checks

### Temporal object resolver

Status: `partial`.

Evidence: exact resolution, subject/state timelines, comparison, representation
summaries, action plans, and resolution memory exist. The current corpus is too
small to prove broad temporal object resolution.

### Search as investigation

Status: `partial`.

Evidence: Resolution Run Model v0 records exact, deterministic, and planned
search runs. Query Planner v0 compiles raw queries into structured tasks. The
system does not yet have investigation phases, budgets, checkpoints, or source
expansion.

### Smallest actionable unit

Status: `partial`.

Evidence: decomposition and member readback can expose ZIP members in bounded
fixtures. Hard queries such as drivers inside support media and articles inside
magazine scans still report capability/source gaps.

### Evidence and disagreement

Status: `implemented_but_underused`.

Evidence: provenance summaries and comparison/disagreement seams exist, but
the small corpus limits meaningful multi-source conflict examples.

### Absence explanation

Status: `partial`.

Evidence: absence reports and eval gap statuses exist. The next risk is making
absence stronger without pretending unchecked source families were searched.

### Strategy and truth

Status: `implemented`.

Evidence: strategy-aware action planning changes recommendation emphasis while
preserving the underlying resolved identity, evidence, and representation
truth.

### Public-alpha safety

Status: `partial`.

Evidence: public-alpha mode blocks arbitrary local path controls, has route
inventory and smoke checks, and has a hosting pack. It remains a constrained
demo posture, not production.

## Key Risks

- Search usefulness can look weak because source coverage is weak, not because
  the architecture is misdirected.
- Planner and source gaps are intertwined; adding sources without hard planner
  tests risks noisy outputs.
- Public-alpha route safety is manually inventoried; future route additions
  need stronger drift checks.
- Rust parity should not expand faster than Python-oracle fixture coverage.

## Next Behavior Work

The next behavior-facing work should be preceded by hard tests. The highest
leverage sequence is:

1. Hard Test Pack v0
2. Real Source Coverage Pack v0
3. Planner Gap Reduction Pack v0
4. Compatibility Evidence Fixture Pack v0

