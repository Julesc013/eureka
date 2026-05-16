# Existing Tool Systems

## Discovered Tool Surface

- `scripts/` contains hundreds of repo support scripts.
- Count summary from current script names:
  - validate: 309
  - check: 19
  - audit: 30
  - build: 16
  - run: 37
  - dry_run: 28
  - demo: 12
  - summarize: 88
  - generate: 9
  - source/connectors/probe-related names: 149
  - evidence-related names: 29
  - index-related names: 16
  - release/deploy/changelog-related names: 17
  - pack/package-related names: 72
  - migration/remediation-related names: 5
- `tests/` contains 814 `test_*.py` files across actions, architecture, audits, connectors, contracts, end-to-end, evals, extraction, hardening, hosting, integration, native, operations, packs, parity, relay, runtime, scripts, search quality, and snapshots.

## Architecture Checks

- `scripts/check_architecture_boundaries.py`: safe and quick; Q54 ran it and it passed.
- `tests/architecture/test_check_architecture_boundaries.py`: exists as test coverage.
- Additional boundary/safety scripts include hosting, public-alpha, public-search, generated artifact drift, repository layout, native, relay, and runtime leakage validators.

## Source/Evidence/Index Validators

Representative discovered validators and tools include:

- `validate_source_pack.py`, `validate_source_cache_contract.py`, `validate_source_cache_store.py`, `validate_source_observation_seam.py`, `validate_source_sync_worker_contract.py`, `validate_source_sync_worker_job.py`;
- `validate_evidence_pack.py`, `validate_evidence_ledger_contract.py`, `validate_evidence_ledger_store.py`, `validate_evidence_ledger_record.py`, `bridge_source_cache_to_evidence.py`;
- `validate_index_pack.py`, `validate_reviewed_public_index.py`, `validate_reviewed_public_index_rebuild_contract.py`, `rebuild_reviewed_public_index.py`;
- `validate_master_index_review_queue.py`, `validate_review_queue_store.py`, `validate_pack_import_*`, `validate_pack_export_runtime.py`, `validate_pack_quarantine_runtime.py`;
- live-probe-named scripts exist but were not run in Q54 because live probes/network are forbidden.

## Capability Families

- validate: present and extensive.
- test: present through `tests/**`; no `scripts/test_*` family.
- build: present; not run because many build commands can mutate generated artifacts.
- audit: present; not broadly run because audits write reports outside Q54 scope.
- repo_policy: present through AIDE Git policy, command matrix, docs, and guard scripts.
- docs: present through large `docs/**` and AIDE reports; not rewritten.
- release: present in scripts and AIDE release bundle; no release publishing run.
- package: present through source/evidence/index packs and AIDE release pack; no package apply/import run.
- migration: present; no migration/remediation run.
- source_policy/evidence_policy/index_policy: present and extensive.
- unknown: any script not classified above must be observed before execution.

## Q56 Absorption Rule

Use `discover -> classify -> wrap -> adapt -> migrate -> retire with evidence`.

No validator, script, source/evidence/index store, or product tool should be deleted, renamed, moved, or replaced by AIDE. Q56 should inventory/wrap the existing tool surface and keep unknown commands non-executing until classified.

## Discovered But Not Run

- Live probe commands such as `run_*_live_probe.py` and `run_one_source_live_test.py`.
- Build/generate commands that can update `site/dist`, snapshots, public data, packs, indexes, source cache, evidence ledger, or other generated product artifacts.
- Broad unittest lanes and full command matrix lanes, because Q54 is evidence-only and already ran the safe AIDE and architecture checks.
