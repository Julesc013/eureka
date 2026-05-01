# Deploy Templates

This directory contains operator-facing deployment templates only. They do not
deploy Eureka, configure DNS, create accounts, call provider APIs, or prove that
a hosted backend exists.

The current template target is the P54 hosted public search wrapper. It runs
`scripts/run_hosted_public_search.py` in `local_index_only` mode with live
probes, downloads, uploads, install actions, local paths, arbitrary URL fetch,
telemetry, accounts, external calls, and AI runtime disabled.

Operators must record the deployed URL, commit SHA, host, environment, and route
checks in a later evidence pack before any public hosted-search claim is made.
