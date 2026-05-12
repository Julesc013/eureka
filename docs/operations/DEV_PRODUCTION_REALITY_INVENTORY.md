# Dev Production Reality Inventory

R0-01 audited the current dev branch as a control/audit-only task. It classified repo-visible artifacts under `.aide/`, `contracts/`, `control/`, `docs/`, `examples/`, `runtime/`, `scripts/`, `tests/`, `surfaces/`, `site/`, `native/`, and `crates/` using static path, name, extension, and content hints.

The audit does not execute product runtime, call sources, call models/providers, mutate source caches, mutate evidence ledgers, mutate review queues, rebuild public indexes, or promote dev to main.

## Headline

- Status: `pass_with_warnings`
- Artifacts classified: `14823`
- Runtime files: `1148`
- Contract files: `633`
- Architecture leakage findings: `4347`
- F0 continuation: `blocked`
- dev-to-main promotion: `blocked`

## Why Bundle Completion Is Not Product Completion

The H/Audit series produced queue records, contracts, policies, fixtures, previews, audit reports, and validators. Those artifacts are useful evidence and planning material, but they do not by themselves prove a live-tested product pipeline.

Product completion requires runtime behavior, persistent state where applicable, review decisions, public index output, surface/API behavior, and tests that assert those behaviors. Artifact existence alone is not acceptance.

## Product Seam Reality

| Seam | Exists | Maturity | Blocker Count |
| --- | --- | --- | --- |
| `source_observation` | `true` | `preview_only` | `1` |
| `source_cache_durable_store` | `true` | `fixture_only` | `2` |
| `evidence_ledger_durable_store` | `true` | `fixture_only` | `2` |
| `review_queue` | `true` | `preview_only` | `2` |
| `candidate_promotion` | `true` | `preview_only` | `1` |
| `public_index_rebuild` | `true` | `preview_only` | `2` |
| `static_public_surface` | `true` | `preview_only` | `1` |
| `source_connector_runtime` | `true` | `preview_only` | `1` |
| `live_metadata_probe` | `true` | `preview_only` | `2` |
| `extraction_runtime` | `true` | `preview_only` | `1` |
| `search_quality_ranking` | `true` | `preview_only` | `1` |
| `snapshot_relay` | `true` | `preview_only` | `1` |
| `native_client` | `true` | `preview_only` | `1` |
| `hosting_deployment` | `true` | `fixture_only` | `1` |

## Unsafe To Promote Unchanged

- Runtime artifacts containing H-series/task/preview vocabulary.
- Fixture-only source cache and evidence ledger helpers presented as runtime-shaped modules.
- Contracts that are audit, fixture, policy, or preview schemas but live beside product/domain contracts.
- Validators that prove files, JSON syntax, booleans, or forbidden strings without proving product behavior.

## Salvageable

- Policies, fixtures, preview outputs, and audits can remain as control evidence or fixture oracles.
- Normalizers and dry-run helpers can inform R0 product seams after task vocabulary is quarantined.
- Boundary validators can become useful gates once separated from product-completion claims.

## What Blocks F0

F0 remains blocked until R0-02 at minimum because production-looking paths still contain task/phase vocabulary. The stronger product blocker remains the missing durable source observation -> evidence -> review -> public index loop planned across R0-04 through R0-09.
