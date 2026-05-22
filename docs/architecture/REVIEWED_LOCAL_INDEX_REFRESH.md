# Reviewed Local Index Refresh

The reviewed local index refresh proof is temp scoped in this foundation. It seeds deterministic fixture records into a temporary local runtime, records an accepted local review decision, rebuilds the local reviewed projection, and searches the temp index to prove the reviewed result can appear.

This is intentionally narrower than an operator apply flow:

- no default operator instance mutation
- no master index mutation
- no committed `data/public_index` mutation
- no production/public launch claim
- no rollback contract beyond discarding the temp instance

Real operator-instance apply requires `LOCAL-APPLY-GATE-01`, including preview, backup, audit log, explicit token, and rollback.
