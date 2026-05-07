# Changed Files

## Scope Summary

- Imported portable AIDE Lite metadata and scripts under `.aide/**`.
- Added committed example-only local-state docs under `.aide.local.example/**`.
- Updated `.gitignore` so actual `.aide.local/` stays private.
- Added managed AIDE Lite token guidance to `AGENTS.md`.
- Added compact Eureka-specific memory under `.aide/memory/**`.
- Generated Eureka-local context, review, verification, ledger, adapter, route, cache, and golden-task outputs.
- Added this queue evidence packet and a compact docs reference.

## Product-Code Boundary

No Eureka product implementation files were changed under `runtime/**`,
`contracts/**`, `surfaces/**`, `site/**`, or `crates/**`.

## Commit Range

Initial baseline: `4c726f849c39763476fa24b81529c7d0d282c844`.

Implementation commits before this evidence packet:

- `672bcc8` `chore: import aide lite pack`
- `0d283f5` `chore: initialize eureka aide state`
- `cdbbc9a` `chore: generate eureka aide snapshot and task packet`
