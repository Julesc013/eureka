# Autonomous Eval Oracle

The autonomous E2E evaluation oracle is a deterministic evaluator for the
Eureka local reference system. It composes existing hard-query fixtures, the
E2E runner, Preview Index, Workbench exploration projection, synthetic truth
path, SurfaceKernel renderers, snapshot validation, and safety boundaries.

The oracle is not a runtime engine, search service, index, Review Ledger,
model judge, public dashboard, or full-discovery replacement.

## Architecture

The implementation lives under `evals/e2e_reference/oracle/`.

The flow is:

```text
EvalCase registry
-> product adapter
-> observed artifacts
-> deterministic assertions
-> case result
-> suite gate
-> immutable local report
```

The registry defines suites, cases, budgets, and a reference baseline. Product
adapters call existing local seams. The assertion layer records explicit
expected and observed facts. Suite gating uses criticality, not weighted
averages.

## Safety

The oracle must record:

```text
model calls: false
network/provider calls: false
real review decisions: false
production truth mutation: false
reviewed/master mutation: false
public-index mutation: false
public exposure: false
downloads/execution: false
```

If an eval finds a product defect, the eval records the failing case and a
separate repair task. Product runtime behavior is not patched under eval
authority.

## Output

Generated runs are written under:

```text
.eureka/e2e-reference/eval/<execution-id>/
```

Each run contains an oracle manifest, case results, summary, failures, proof
matrix, resource metrics, boundary report, Markdown report, and per-case
artifacts. Execution IDs are unique and previous runs are not overwritten.
