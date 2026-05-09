# Source Registry V2

Source Registry v2 is the governed inventory format for Eureka source records.
It is descriptive, review-gated, and policy-only in H0-BUNDLE-01.

A registry records source records, source families, source capability refs,
policy refs, index-depth policy, trust-lane policy, approval gates, operation
policy, and source expansion policy. It does not enable live source access,
source sync, downloads, public fanout, public-index mutation, master-index
mutation, or truth acceptance.

Current allowed registry statuses:

- `example_only`
- `planning_only`
- `local_policy_only`
- `fixture_only`
- `no_live_source_access`

The registry prepares future H0/H1 source-family work by keeping connectors
family-driven instead of one-off site integrations.
