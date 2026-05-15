# Evidence / Review / Index Flow

Evidence candidate:

- Evidence candidate id: `evc_7a58fa86edc377ef`
- Evidence kind: `metadata`
- Source id: `source.fixture.local.metadata`
- Initial evidence status: `candidate`
- Ledger status after local gate: `needs_review`

Review decision:

- Review item id: `rvi_eba5b8afd11a4cf4`
- Review decision id: `rvd_fixture_demo_project_accept_v0`
- Decision kind: `accept`
- Decision status: `accepted`
- Actor: `operator:fixture-q58`
- Limitation: local fixture decision only; not production or hosted review.

Reviewed index candidate:

- Public index record id: `pir_f4453ae8f3ab6d41`
- Source cache entry id: `sce_166f90a6738492c5`
- Rebuild id: `pireb_0aeae405f5bf1576`
- Included records: `1`
- Excluded records: `0`

Isolated stores:

- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/fixture-run/evidence-ledger.sqlite`
- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/fixture-run/review-queue.sqlite`
- `.aide/queue/EUREKA-SOURCE-SLICE-01/evidence/fixture-run/public-index.sqlite`

Production-state proof:

- The rebuild report records `input_stores_mutated: false`, `master_index_mutated: false`, and `site_dist_mutated: false`.
- All stores are Q58 evidence-local and are not canonical product stores.

