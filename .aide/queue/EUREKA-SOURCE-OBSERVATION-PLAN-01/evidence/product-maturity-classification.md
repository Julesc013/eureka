# Product Maturity Classification

| Subsystem | Current maturity | Evidence refs | Risks | Next need |
|---|---|---|---|---|
| source policy gate | implemented_runtime | `runtime/source/observation/policy.py`, `tests/runtime/test_source_observation_seam.py` | Must keep live/source-sync/download/write operations blocked | Reuse default policy and assert blocked operations in Q58 |
| source observation | implemented_runtime | `runtime/source/observation/observations.py`, `normalization.py`, `scripts/demo_source_observation_seam.py` | Synthetic/local only; no durable write by itself | Compose into a single vertical-slice harness |
| connector/source adapter | fixture_runtime | `examples/sources/cache/dry_run/dry_run/**`, `scripts/replay_*_fixtures.py`, connector validators | Network-branded fixtures may be mistaken for live access | Use synthetic fixture only for Q58; keep live connectors disabled |
| source cache/persistence | implemented_runtime | `runtime/source/cache/store.py`, `scripts/demo_source_cache_store.py`, `tests/runtime/test_source_cache_integration.py` | File-backed writes are possible if pointed at a real DB | Use temp or Q58 evidence-local DB only |
| evidence candidate | implemented_runtime | `runtime/source/observation/evidence.py`, `runtime/evidence/ledger/records.py` | Candidate must not be accepted as truth | Keep status review-required/candidate until explicit local review |
| evidence ledger/persistence | implemented_runtime | `runtime/evidence/ledger/store.py`, `scripts/demo_evidence_ledger_store.py`, `tests/runtime/test_evidence_ledger_integration.py` | Ledger writes are mutation-capable | Use temp or Q58 evidence-local DB only; no canonical ledger |
| review queue/decision | implemented_runtime | `runtime/review/queue/store.py`, `runtime/local/review/decisions.py`, `scripts/demo_review_queue_store.py` | Accept decisions require explicit local-only semantics | Q58 may record a local fixture accept decision only in temp/evidence DB |
| index builder/output | implemented_runtime | `runtime/index/public/rebuild.py`, `scripts/demo_reviewed_public_index.py`, `tests/runtime/test_public_index_rebuild.py` | Public-index writes are mutation-capable | Use isolated temp/evidence-local public index DB; never site/master index |
| search API/surface | prototype_runtime | `runtime/index/public/search.py`, `runtime/gateway/public_api/public_search.py`, `scripts/validate_local_public_search_runtime.py` | Hosted/live public search remains out of scope | Q58 uses local `PublicIndexStore.search`, not hosted API |
| object/result rendering | contract_only | `contracts/view/pages/search_page.v0.json`, `contracts/view/pages/source_page.v0.json`, `contracts/view/pages/absence_page.v0.json` | UI/surface changes would expand scope | Q58 should output structured record/search/absence JSON only |
| absence reporting | implemented_runtime | `runtime/index/public/absence.py`, `tests/runtime/test_public_index_search_absence.py`, `contracts/query/known_absence_record.v0.json` | Absence must stay scoped; no global absence claims | Q58 should assert limitations and checked source scope |
| validators/tests | implemented_runtime | `scripts/validate_*`, `tests/runtime/**`, `tests/operations/**`, `control/inventory/tests/command_matrix.json` | Some validators are mutation/live-adjacent | Run only known safe validators and targeted tests |
| safety/side-effect gates | implemented_runtime | validation modules, demo output root checks, hard booleans in dry-run examples | Bypass via wrong output path or live-family confusion | Q58 must assert no network/provider and use temp/evidence-local stores |

## Counts

- `implemented_runtime`: 10
- `fixture_runtime`: 1
- `preview_only`: 0
- `contract_only`: 1
- `missing_or_unknown`: 0
