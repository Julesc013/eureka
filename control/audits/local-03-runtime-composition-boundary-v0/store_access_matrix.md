# Store Access Matrix

| Store | Manifest Key | Relative Path | Open | Integrity | Read-only Mode | Direct Mutation In LOCAL-03 |
| --- | --- | --- | --- | --- | --- | --- |
| source cache | `source_cache` | `db/source_cache.sqlite` | yes | yes | yes | no |
| evidence ledger | `evidence_ledger` | `db/evidence_ledger.sqlite` | yes | yes | yes | no |
| review queue | `review_queue` | `db/review_queue.sqlite` | yes | yes | yes | no |
| reviewed public index | `public_index` | `db/public_index.sqlite` | yes | yes | yes | no |

Store paths must come from `config/store_manifest.json`. Ad hoc store paths are forbidden.
