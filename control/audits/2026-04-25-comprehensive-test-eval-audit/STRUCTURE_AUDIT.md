# Structure Audit

## Reviewed Areas

Top-level directories reviewed:

- `.aide/`
- `contracts/`
- `control/`
- `crates/`
- `docs/`
- `evals/`
- `runtime/`
- `scripts/`
- `surfaces/`
- `tests/`
- `third_party/`

Current inventory observations:

- 441 Python files
- 154 `test_*.py` files
- 6 governed source records under `control/inventory/sources/`
- 6 archive-resolution tasks
- 64 search-usefulness audit queries
- 89 public-alpha route inventory entries

## Healthy Structure

- The main control/contracts/runtime/surfaces split is present and reinforced
  by `AGENTS.md`.
- Runtime engine seams are component-local and usually have nearby tests.
- Public gateway boundaries are explicit and surfaces consume public API paths.
- `evals/` now has both hard archive-resolution fixtures and a broad
  search-usefulness audit area.
- `crates/` is present as an isolated Rust lane and is not wired into Python
  runtime behavior.
- Public-alpha operations docs, route inventory, smoke script, and hosting pack
  are grouped clearly.

## Structure Risks

- `.aide/` and `docs/` needed top-level README files because both have become
  important navigation roots. This audit adds concise pointers, but a future
  link/command drift guard is still needed.
- Command metadata exists in long `.aide/commands/*.yaml` files and is now
  mirrored by the test registry. Future drift is likely unless a guard checks
  the relationship.
- `docs/ROADMAP.md` and `docs/BOOTSTRAP_STATUS.md` are accurate but dense.
  They are useful historical ledgers, not quick navigation pages.
- Some governance artifacts are static inventories rather than generated from
  route or command discovery. That is acceptable now but should be made auditable
  before the repo grows much further.
- `tmp/` exists in the checkout and should remain outside committed operating
  truth.

## Allowed Tiny Fixes Made

This audit adds operating-layer indexes and AIDE task/report scaffolding. It
does not move runtime files or change product behavior.

## Findings

Structured structure findings live in `STRUCTURE_FINDINGS.json` and are also
aggregated in `findings.json`.
