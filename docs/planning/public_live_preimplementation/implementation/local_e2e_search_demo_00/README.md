# LOCAL-E2E-SEARCH-DEMO-00

Task: `LOCAL-E2E-SEARCH-DEMO-00`

This package records a deterministic local product-proof demo for Eureka hard
queries.

The demo uses repo-local fixtures, SurfaceKernel projection, and baseline
renderers only. It does not call live source providers, download files, mutate
reviewed/public/master indexes, create reviewed artifact records, or create
verified artifact claims.

Primary command:

```text
python scripts/run_local_e2e_search_demo.py --all --profile json_v0
```

Fixture output:

```text
evals/hard_queries/local_e2e_demo/demo_00/
```

