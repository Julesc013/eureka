# Example Pack Registry

The example registry lives at `control/inventory/packs/example_packs.json`.

Registered examples:

| Pack type | Root | Expected |
| --- | --- | --- |
| `source_pack` | `examples/source_packs/minimal_recorded_source_pack_v0` | pass |
| `evidence_pack` | `examples/evidence_packs/minimal_evidence_pack_v0` | pass |
| `index_pack` | `examples/index_packs/minimal_index_pack_v0` | pass |
| `contribution_pack` | `examples/contribution_packs/minimal_contribution_pack_v0` | pass |
| `master_index_review_queue` | `examples/master_index_review_queue/minimal_review_queue_v0` | pass |

The registry lists repo-owned examples only. The aggregate validator does not
recursively scan arbitrary directories to discover packs.

