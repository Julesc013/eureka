# Review / Index Boundary Proof

Accepted indexing proof:

- The fixture review decision status is `accepted`.
- The reviewed local index contains one record.
- The positive search result references the accepted reviewed index record.

Non-accepted exclusion proof:

- Q59 test `test_rejected_review_decision_is_not_indexed` uses a rejected decision and rebuilds a local public index.
- The rebuild report has `included_count: 0` and `excluded_count: 1`.
- The local index summary has `record_count: 0`.

Local-only proof:

- All Q59 fixture stores are under `.aide/queue/EUREKA-SOURCE-SLICE-HARDENING-01/evidence/fixture-run/`.
- Default output uses a temp root and is asserted not to be under product roots.
- Product output roots such as `runtime/q58-fixture` are rejected.

No production mutation proof:

- Rebuild report records `input_stores_mutated: false`.
- Rebuild report records `master_index_mutated: false`.
- Rebuild report records `site_dist_mutated: false`.
- Q59 digest test proves source/evidence/review input DB files are unchanged by rejected-decision rebuild.
