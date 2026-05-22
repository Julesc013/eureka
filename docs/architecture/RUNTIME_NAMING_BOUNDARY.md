# Runtime Naming Boundary

R0-02 separates work-control vocabulary from production/domain vocabulary.
Task IDs, prompt IDs, audit bundle names, and negative assertion labels are
valid control-plane language. They are not valid names for production runtime
packages, functions, public contracts, or user-facing surfaces.

## Path Classes

Production-looking paths:

- `runtime/**`
- `surfaces/**`
- `site/**`
- `native/**`
- `crates/**`
- `contracts/domain/**`
- `contracts/runtime/**`
- `contracts/api/**`
- `contracts/snapshot/**`
- `contracts/native/**`
- public-facing contract paths under `contracts/**`

Control, audit, and fixture paths:

- `.aide/**`
- `control/audits/**`
- `control/inventory/**`
- `control/policies/**`
- `docs/operations/**`
- `examples/**`
- `tests/**`
- `scripts/audit_*.py`
- `scripts/validate_*.py`

Control paths may mention task IDs such as `R0-02`, audit bundles such as
`H14-BUNDLE-04`, and negative assertion terms such as `truth_boundary` when
they are documenting, testing, or enforcing governance. Product paths should
name the domain capability they implement.

## Forbidden Production Vocabulary

The leakage gate reports task-shaped or audit-shaped terms in production paths,
including:

- `H0` through `H14`
- `BUNDLE`, `IA-BUNDLE`, `F-BUNDLE`, `G-BUNDLE`
- `MVP`, `LOCAL-MVP`
- `AIDE`, `prompt`, `agent`, `human_obs`
- `fixture_only`, `preview_only`
- `truth_boundary`, `product_boundary`, `review_seed`
- `next_phase`, `quality_delta`, `integration_audit`

These terms can remain in audit packs, test fixtures, validators, and operating
docs. They must not define production packages, public API names, runtime class
names, or stable product semantics.

## Why This Boundary Exists

Task IDs are useful for sequencing work, but they age quickly. A package named
after `H1` or `H14` encodes a prompt history into product architecture. That
makes future refactors harder because the runtime shape is named after how it
was produced, not what it does.

Prompt and audit language has the same problem. A validator can assert that a
fixture does not cross a `truth_boundary`, but a production API should expose
domain terms such as evidence acceptance, review decisions, source policy, and
normalized observations.

## Examples

Bad:

- `runtime/connectors/h1_metadata_wave/`
- `normalize_h1_fixture`
- `build_h14_rollup_dry_run_result`
- `truth_boundary`
- `product_boundary`
- `review_seed`

Quarantined legacy paths may still contain these names under
`archive/prototypes/legacy_runtime/`; that location marks them as non-production
prototype material, not a production runtime pattern to copy.

Good:

- `runtime/source_observation/`
- `normalize_source_observation`
- `build_metadata_request`
- `build_evidence_candidate`
- `validate_source_policy`
- `connector_health`

## Replacement Vocabulary

- Use `source_observation` for source-facing observation capture.
- Use `metadata_request` and `metadata_response` for bounded source requests.
- Use `normalized_observation` for canonicalized source data.
- Use `evidence_candidate` and `evidence_ledger` for claims and evidence events.
- Use `review_item`, `review_queue`, and `review_decision` for review state.
- Use `connector_health` for source connector status.
- Use `source_policy` and `policy_decision` for request gating.

R0-02 reports existing leakage but does not rename or move files. R0-03 and
R0-04 decide which contracts and runtime seams should be moved, renamed, or
rewritten.
