# Red-Herring / Defer Audit

These are explicitly deferred and must not be started from ECHECK-01:

- Live source probes: no reviewed live-source permission exists.
- Internet Archive, PyPI, GitHub, Wayback, or other live connectors: not part of
  the fixture slice.
- Crawlers, downloaders, scrapers: forbidden for this checkpoint.
- Provider/model calls: not needed and not authorized.
- Public-index writes: Q58-Q61 wrote only evidence-local fixture stores.
- Production source-cache/evidence-ledger writes: deferred.
- Registry/source catalog mutation: deferred.
- Site deploy/public hosting: deferred.
- Release publication, tag creation, asset upload, package publishing: deferred.
- Broad connector expansion: deferred.
- Broad architecture refactor, root moves, path aliases, shims, reference
  rewrites: deferred.
- Tool migration/apply, install, repair, upgrade, rollback, uninstall apply:
  deferred.
- Active CI workflow installation or branch protection mutation: deferred.
- Gateway/model router, MCP/A2A, Commander/UI, and cross-repo cloud/fleet mode:
  deferred.

