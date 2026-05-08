# WorkUnit Dry-Run Review

WorkUnit dry-run review checks whether a WorkUnit can be safely simulated and
whether its resulting WorkUnitResult preserves the contract boundary. Review is
required because a dry-run result may suggest future SearchNeed, source-lead,
candidate, evidence, pack, or WorkUnit seed work, but it is not accepted truth.

## Reviewer Checks

- Confirm the input was an explicit WorkUnit file.
- Confirm no WorkUnit action was executed.
- Confirm `executed_actions` is empty.
- Confirm forbidden actions were recorded only as `forbidden_checked`.
- Confirm source access, network, model, credential, and local-state
  requirements are blocked or deferred.
- Confirm outputs are review-gated proposals or reports.
- Confirm truth and product boundary booleans remain false.
- Confirm the result does not mutate the master-index.

## Noop, Blocker, And Recovery

Repeated or already-satisfied WorkUnits may produce a noop WorkUnitResult. A
gated or unsafe WorkUnit may produce `blocked`, `policy_blocked`,
`approval_gated`, `operator_gated`, or `permission_needed`. Failed validation
can produce a quarantined result. These postures are evidence for review, not
permission to execute.

## No-Goals

Dry-run review does not enable a node runtime, source sync, live probes,
crawling, scraping, downloads, uploads, accounts, telemetry, model/provider
calls, review runtime, pack import runtime, public hosting behavior, or
master-index mutation.

## Commands

```bash
python scripts/validate_workunit_dry_run_runner.py
python scripts/run_workunit_dry_run.py --workunit examples/work_units/search_need_review_v0/work_unit.json --check
python -m unittest discover -s tests -t .
```
