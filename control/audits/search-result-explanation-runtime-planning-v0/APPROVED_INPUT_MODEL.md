# Approved Input Model

Future allowed inputs:

- public search result envelope
- public index document
- public-safe result-card fields
- reviewed object/source/comparison page refs
- reviewed source/evidence refs
- ranking dry-run output future
- result merge dry-run output future
- synthetic examples

Forbidden inputs:

- raw private query
- IP/account/session data
- user profile
- telemetry
- private source-cache records
- private evidence-ledger records
- arbitrary local paths
- arbitrary URLs
- live connector responses
- model responses
- private uploaded files
- unreviewed private cache entries

Inputs must be bounded, explicit, public-safe, and never supplied directly by
arbitrary request parameters. Unknown or private inputs are rejected or redacted.

