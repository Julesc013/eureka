# Materialization Proof

Synthetic-only materialization consumes the candidate, review item, and canonical Review Ledger decision. It rejects non-synthetic input, wrong namespaces, missing local-only confirmation, mismatched refs, and output outside `.eureka/test/e2e-reference/synthetic-truth-path/`.

The reviewed record is accepted only inside `truth_scope: synthetic_test_only`.

