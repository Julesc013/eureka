# Query Intelligence Privacy

Status: P59 contract-only operations guidance.

Query intelligence is not telemetry. P59 adds no persistent query logging, no
analytics, no IP storage, no account identifiers, no raw private-looking query
retention, no public observation feed, and no runtime hook from public search.

## Operator Posture

- Treat all raw public query text as potentially private.
- Keep raw query retention disabled unless a future legal/privacy milestone
  explicitly changes the policy.
- Permit public aggregate summaries only after privacy filtering and poisoning
  review.
- Do not publish individual observations by default.
- Keep query learning separate from master-index truth.

## Current Local Tools

`scripts/dry_run_query_observation.py` emits a non-persistent example
observation to stdout only. It is useful for validating the contract shape, not
for collecting user data.

`scripts/validate_query_observation.py` validates committed examples and rejects
private paths, private URLs, credential markers, and hard mutation flags.

## Operator-Gated Future Work

Hosted deployment, edge/rate-limit evidence, public aggregate publication,
retention/deletion controls, poisoning protection, and any query collection
runtime remain operator-gated or future-milestone work.

P59 does not add probes, result caches, miss ledgers, candidate indexes,
telemetry, uploads, accounts, live source calls, or production public-query
learning claims.
