# Connector Policy Evaluation Contract

Connector policy evaluation is an offline decision record. It evaluates a
requested connector operation against source and connector policy, then returns a
decision such as `allowed_fixture_replay`, `allowed_dry_run_only`,
`blocked_missing_approval`, or `blocked_by_forbidden_operation`.

The evaluator does not execute the connector. It does not call a network, write
runtime state, mutate indexes, or accept truth. Descriptive capabilities and
supported operations remain descriptive only.
