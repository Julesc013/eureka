# Tool Discovery

## Sources Searched

- `.aide/scripts/**`, `.aide/tools/**`, `.aide/policies/**`, `.aide/queue/**`, `.aide/reports/**`
- `scripts/**`
- `tests/**`
- `evals/**`
- `control/inventory/**`
- `control/audits/**`
- `docs/architecture/**`, `docs/reference/**`, `docs/operations/**`
- `contracts/**` contract/schema surfaces relevant to validators
- `runtime/**` high-level source/evidence/index validation modules
- `site/**` static site validation/build surfaces
- `snapshots/**`

## Discovery Result

AIDE tool inventory discovered 2,164 tool candidates.

Generated outputs:

- `.aide/tools/latest-tool-inventory.json`
- `.aide/tools/latest-tool-inventory.md`
- `.aide/tools/eureka-tool-inventory.json`

Eureka-specific capability tags added in Q56:

- `architecture_policy`: 139 candidates
- `source_policy`: 446 candidates
- `evidence_policy`: 88 candidates
- `index_policy`: 55 candidates
- `snapshot_policy`: 15 candidates
- `site_policy`: 9 candidates
- `connector_policy`: 502 candidates

## Representative Candidate Paths

- `.aide/scripts/aide_lite.py`
- `scripts/check_architecture_boundaries.py`
- `scripts/validate_source_cache_contract.py`
- `scripts/validate_source_cache_evidence_ledger_contract.py`
- `scripts/validate_evidence_ledger_contract.py`
- `scripts/validate_public_search_index.py`
- `scripts/validate_static_snapshot.py`
- `scripts/validate_pack_set.py`
- `site/validate.py`
- `site/build.py`
- `runtime/source/observation/validation.py`
- `runtime/source/cache/validation.py`
- `runtime/evidence/ledger/validation.py`
- `runtime/index/public/validation.py`
- `control/inventory/tests/command_matrix.json`
- `docs/operations/TEST_AND_EVAL_LANES.md`

## Command Matrices / Catalogs Found

- `control/inventory/tests/command_matrix.json`
- `docs/operations/TEST_AND_EVAL_LANES.md`
- `.aide/evals/golden-tasks/catalog.yaml`
- `.aide/tools/*.schema.json`
- `.aide/policies/tool-*.yaml`

## Validation Reports Found

Existing AIDE and control audit reports were discovered under:

- `.aide/queue/**/evidence/validation.md`
- `.aide/reports/**`
- `control/audits/**`

## Discovered But Not Run

Q56 did not execute unknown discovered tools. The following families remain discovered-only unless a future reviewed wrapper explicitly authorizes them:

- Source cache initializers and recorders, including `scripts/init_source_cache_store.py`, `scripts/record_source_cache.py`, and source-cache dry-run runners.
- Evidence ledger initializers and recorders, including `scripts/init_evidence_ledger_store.py`, `scripts/record_evidence_ledger.py`, and evidence-ledger dry-run runners.
- Public index initializers/rebuilders, including `scripts/init_public_index_store.py` and `scripts/rebuild_reviewed_public_index.py`.
- Live/probe/provider/network-related validators and demos, including `validate_*_live_probe.py`, connector runtime plans, and provider-facing source observation files.
- Static site build and release/publication tooling.

## Safety Notes

Discovery and classification were performed from generated AIDE inventories and read-only file listing. Unknown tools were not executed. No product files or product validators were modified.
