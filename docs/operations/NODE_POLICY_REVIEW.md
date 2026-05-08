# Node Policy Review

Use this guide when adding or changing a Eureka Node policy.

## Review Checklist

- Confirm the policy references known node modes and manifests.
- Confirm allowed inputs are committed, manual, or future review-gated categories.
- Confirm forbidden inputs include live-source results, scraped content, credentials, browser sessions, downloads, telemetry streams, and unreviewed API payloads.
- Confirm forbidden actions include public truth promotion, accepted evidence, observed-baseline marking without a human, live probes, scraping, crawling, downloads, uploads, accounts, telemetry, and master index mutation.
- Confirm source access is repo-local, committed-fixture, manual-human, no-autonomous, or explicitly future/deferred.
- Confirm network and local state remain disabled for current examples.
- Confirm review gates are present before source policy, evidence, candidate, pack, rights, risk, privacy, network, hosted behavior, or master index decisions.

## Approval Boundary

Approving a node policy only approves the policy envelope. It does not run a node, create local state, fetch sources, perform observations, accept evidence, or mutate public records.

## Validation

Run:

```text
python scripts/validate_eureka_node_policy.py
python -m unittest tests.contracts.test_eureka_node_policy
```

Stop if legal, rights, privacy, credential, source-policy, irreversible action, or production-hosting ambiguity appears.
