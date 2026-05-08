# Node Capability Review

Use this checklist when adding or changing Eureka Node capabilities.

## Checklist

- Confirm the capability ID is in the governed vocabulary.
- Confirm allowed node modes exist in the node mode registry.
- Confirm current capabilities are repo-local, validation-only, dry-run-only, or blocked.
- Confirm future capabilities are marked future, deferred, approval-gated, operator-gated, human-operated, or blocked.
- Confirm network, source access, model/provider, credential, and local-state requirements are explicit.
- Confirm current examples keep those requirement flags false.
- Confirm future requirements keep current enabled flags false and include review gates, source policy, operator approval, kill switch, and rate or budget policy.
- Confirm forbidden inputs and outputs are listed.
- Confirm truth-boundary and product-boundary booleans are false.
- Confirm no private paths, credentials, API keys, production claims, rights clearance, malware safety, verified installability, exhaustive search, or master index mutation claims appear.

## Stop Conditions

Stop for legal or rights decisions, private data risk, credentials, unapproved source access, live-source ambiguity, irreversible actions, hosted behavior, model/provider calls, or any public truth promotion.

## Validation

```text
python scripts/validate_eureka_node_capability.py
python -m unittest tests.contracts.test_eureka_node_capability
```
