# Test and Eval Lanes

Eureka now has a repo-native test/eval operating layer under
`control/inventory/tests/`.

The layer exists to help humans, AIDE-style operators, and Codex workers choose
the right checks for a task. It is not a product runtime feature and it is not
a production-readiness claim.

## Taxonomy

Command records use these categories:

- `unit`: component-local Python tests
- `integration`: cross-component repo tests
- `architecture`: import and layering guardrails
- `contract`: governed schema or inventory validation
- `eval`: archive-resolution executable benchmark checks
- `audit`: usefulness or repo-governance audit checks
- `parity`: Python oracle and optional Rust candidate checks
- `operations`: public-alpha, hosting-pack, and audit-pack checks
- `public_alpha`: constrained demo posture checks
- `golden`: committed Python-oracle fixture checks
- `smoke`: narrow end-to-end posture checks
- `regression`: broad drift guards
- `hard_query`: future hard-query-specific checks

## Command Lanes

The command matrix defines these lanes:

- `fast`: architecture boundary plus whitespace diff checks
- `standard`: runtime, surfaces, repo tests, boundary checks, and operating
  layer validation
- `full`: standard checks plus public-alpha smoke, hosting-pack check, Python
  oracle golden check, archive eval runner, and search usefulness audit
- `docs_only`: docs/audit/index validation plus whitespace diff checks
- `public_alpha`: route inventory, smoke, and hosting-pack safety checks
- `parity`: Python oracle and source-registry validation checks
- `audit`: archive-resolution and search-usefulness eval/audit runners
- `hardening`: high-risk regression guards for eval truth, path safety,
  route/docs/README drift, parity/golden discipline, and AIDE/test registry
  consistency
- `rust_optional`: Cargo checks only when the local toolchain exists

## Required vs Advisory

Required commands are expected in the lane that names them. Optional commands
are useful local evidence but must not block Python verification when the
required local tooling is unavailable.

Current Rust commands are optional. Cargo may not be installed in every
execution environment, and Python remains the reference/oracle lane.

## Network Policy

Required lanes must stay local and deterministic. Search Usefulness Audit v0
does not scrape Google, Internet Archive, or any other external system.

External baseline observations are manual evidence records. If a future human
records one, the observation must say who observed it, what was observed, and
which system was used. A missing observation remains
`pending_manual_observation`.

## Codex Completion Expectations

For non-trivial tasks:

1. Inspect relevant paths.
2. Plan the bounded changes.
3. Implement only the requested layer.
4. Run the lane that matches the task.
5. Report exactly what passed, what was skipped, and why.
6. Sync origin at the end when the environment supports it.

Large tasks should use a two-pass flow: implementation first, hardening second.
The hardening pass should reread changed files, check claims against evidence,
and make sure hard evals or manual baselines were not weakened or fabricated.

## Hard Test Pack

Hard Test Pack v0 lives under `tests/hardening/` and is documented in
`docs/operations/HARD_TEST_PACK.md`.

Run it with:

```bash
python -m unittest discover -s tests/hardening -t .
```

These tests are regression guards, not product features. They should be run
before syncing changes that affect eval fixtures, external baseline wording,
public-alpha route policy, route inventory, README commands, docs links,
Python-oracle goldens, Rust parity scaffolding, source registry honesty,
resolution memory privacy claims, or AIDE/test metadata.
