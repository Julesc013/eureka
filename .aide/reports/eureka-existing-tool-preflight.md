# Eureka Existing Tool Preflight

Eureka has a large existing tool surface. Q55/Q56 must wrap and adapt it rather than replacing it.

Detected families:

- validate: 309 scripts
- check: 19 scripts
- audit: 30 scripts
- build: 16 scripts
- run: 37 scripts
- dry_run: 28 scripts
- demo: 12 scripts
- summarize: 88 scripts
- generate: 9 scripts
- source/connectors/probe-related: 149 scripts
- evidence-related: 29 scripts
- index-related: 16 scripts
- release/deploy/changelog-related: 17 scripts
- pack/package-related: 72 scripts
- migration/remediation-related: 5 scripts
- tests: 814 `test_*.py` files

Preservation principle:

`discover -> classify -> wrap -> adapt -> migrate -> retire with evidence`

Do not delete, rename, move, or overwrite validators. Live probe and mutation-oriented commands remain discovered-but-not-run.
