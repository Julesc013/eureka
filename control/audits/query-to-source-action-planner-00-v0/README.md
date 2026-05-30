# QUERY-TO-SOURCE-ACTION-PLANNER-00

This audit records the domain-aware query planner added after the public-alpha
launch track was deferred for discovery coverage.

The planner routes raw queries into review-only candidate source plans and
feeds the Archive.org metadata candidate lane with a domain-aware query rewrite.
It does not deploy, launch publicly, download files, run extraction, call model
providers, promote candidates, or mutate indexes.
