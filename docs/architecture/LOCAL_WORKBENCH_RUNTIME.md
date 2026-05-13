# Local Workbench Runtime

The local workbench is the required proof surface for future product-scoped work where a user-facing loop is relevant.

The intended loop is:

1. Clone the repo.
2. Initialize an explicit local instance.
3. Start a localhost service.
4. Open the HTML workbench.
5. Search the reviewed index.
6. Create Search Hunt Sessions.
7. Queue WorkUnits.
8. Run bounded source probes.
9. Review evidence.
10. Rebuild the reviewed index.
11. Run smoke and eval suites.

The workbench is not implemented in LOCAL-00. Future work must keep localhost as the default, keep LAN disabled until the LAN gate, and avoid broad crawling, scraping, downloads, package install, package execution, deployment, production readiness claims, and public launch claims.
