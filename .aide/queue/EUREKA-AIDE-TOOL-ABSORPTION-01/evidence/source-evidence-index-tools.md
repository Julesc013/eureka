# Source / Evidence / Index Tools

## Paths Found

Representative source/evidence/index systems discovered:

- `runtime/source_observation/**`
- `runtime/source_cache/**`
- `runtime/evidence_ledger/**`
- `runtime/public_index/**`
- `runtime/local_foundry/source_cache.py`
- `runtime/local_foundry/source_cache_to_evidence.py`
- `runtime/local_foundry/evidence_ledger.py`
- `contracts/source_cache/**`
- `contracts/evidence_ledger/**`
- `contracts/stores/*source_cache*`
- `contracts/stores/*evidence_ledger*`
- `contracts/stores/*public_index*`
- `contracts/master_index/**`
- `control/inventory/source_cache/**`
- `control/inventory/evidence_ledger/**`
- `control/inventory/review/**`
- `control/inventory/connectors/**`
- `scripts/validate_source_*`
- `scripts/validate_evidence_*`
- `scripts/validate_public_search_index.py`
- `scripts/validate_reviewed_public_index.py`
- `scripts/*source_cache*`
- `scripts/*evidence_ledger*`
- `scripts/*public_index*`

## Validators Found

Representative validators:

- `scripts/validate_source_cache_contract.py`
- `scripts/validate_source_cache_record.py`
- `scripts/validate_source_cache_store.py`
- `scripts/validate_source_cache_dry_run_report.py`
- `scripts/validate_source_cache_evidence_ledger_contract.py`
- `scripts/validate_source_observation_seam.py`
- `scripts/validate_source_pack.py`
- `scripts/validate_source_page.py`
- `scripts/validate_evidence_ledger_contract.py`
- `scripts/validate_evidence_ledger_record.py`
- `scripts/validate_evidence_ledger_store.py`
- `scripts/validate_evidence_ledger_dry_run_report.py`
- `scripts/validate_evidence_pack.py`
- `scripts/validate_public_search_index.py`
- `scripts/validate_public_search_index_builder.py`
- `scripts/validate_reviewed_public_index.py`
- `scripts/validate_candidate_index_contract.py`
- `scripts/validate_candidate_index_record.py`
- runtime validation modules under `runtime/source_observation`, `runtime/source_cache`, `runtime/evidence_ledger`, and `runtime/public_index`.

## Risk Classification

- Source mutation risks: source cache writes, source sync, source registry mutation, source observation live/probe flows.
- Evidence mutation risks: evidence ledger append/write, evidence conversion from source cache, evidence ranking/report writes.
- Index mutation risks: public index rebuild/write, reviewed public index rebuild, candidate/master index changes.
- Network/live risks: connector runtime plans, live probes, provider-facing source observation, registry/API-facing source discovery.

## Preservation Requirement

These systems are target truth or target safety systems. They must be preserved and wrapped before any adaptation. They must never be treated as junk due to generic AIDE inventory status.

Do not run live probes, provider/model calls, source-cache writes, evidence-ledger writes, public-index writes, registry mutation, or source sync during tool absorption.

## Future Wrapper / Adaptation Plan

Q57 should inspect source observation planning in read-only mode first. Future wrappers should start with contract validators and dry-run report validators before any runtime runner is considered. Live, write, rebuild, provider, and registry actions require a separate reviewed queue phase.

## What Not To Do

- Do not execute `record_*`, `init_*`, `rebuild_*`, `bridge_*`, live probe, provider, crawler, downloader, or registry mutation commands.
- Do not migrate or rename source/evidence/index validators.
- Do not rewrite contracts or runtime validation modules.
- Do not copy generated audit samples into canonical product state.
