# Test Gap Audit

## Current Test Health

The repo has broad stdlib Python coverage:

- runtime component tests
- surfaces tests
- integration tests
- architecture-boundary tests
- operations tests for public-alpha route inventory and hosting pack
- eval tests for archive-resolution and search-usefulness fixtures/runners
- parity tests for Python oracle goldens and Rust skeleton structure
- Rust source-registry parity tests under the optional Cargo lane

## Gaps

1. Hard eval weakening guard
   - Need a test that makes it hard to mark future-facing evals green by
     weakening expected fixtures or statuses.

2. External baseline fabrication guard
   - Search usefulness tests check pending baselines, but a dedicated future
     test should reject committed "observed" external records without evidence
     fields.

3. Route inventory drift guard
   - Current route inventory is validated, but not compared against full server
     route discovery.

4. Docs link and command drift guard
   - README and operations docs contain many command references. There is no
     link/command existence checker yet.

5. Privacy/path-leak regression guard
   - Public-alpha status is tested, but more fixtures should check sentinel
     local path leakage across memory, runs, local tasks, and generated reports.

6. Rust parity mismatch guard
   - Rust source-registry tests compare to Python goldens, but there is no
     generalized parity runner or allowed-divergence enforcement yet.

7. Planner misclassification hard tests
   - Query Planner v0 should gain targeted hard cases for future query-family
     expansion.

8. Container/member/actionable-unit hard tests
   - Current member access is ZIP-fixture-based. Hard support-media and
     article-inside-scan tests should enforce smallest actionable unit behavior
     once fixtures exist.

## What Not To Implement In This Audit

This audit does not add all hard tests. It records the proposals and adds
validation tests for the operating layer and audit pack only.

