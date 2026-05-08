# WorkUnit Dry-Run Runner

The WorkUnit dry-run runner is a local-only simulator for explicit WorkUnit JSON
files. It reads one committed or test-supplied WorkUnit, checks node-mode,
capability, source-access, network, model, credential, and local-state
requirements, classifies actions, and builds a `work_unit_result.v0`
WorkUnitResult envelope.

The runner is not WorkUnit execution. It does not perform source access, browser
automation, external search, downloads, uploads, model calls, provider calls, or
master-index mutation. It writes no file unless an explicit `--output` path is
provided.

## Inputs

Allowed current inputs are explicit WorkUnit files under
`examples/work_units/**/work_unit.json` and explicit temp fixtures used by
tests. The runner refuses to infer work from public traffic, browser state,
private user files, credentials, telemetry streams, executable payloads, or
unreviewed external API payloads.

## Output

The only report shape is a WorkUnitResult envelope. A dry-run result may record:

- planned actions
- skipped or deferred future actions
- blocked actions
- forbidden actions checked
- noop, recovery, duplicate, and quarantine posture
- review gates and limitations

A dry-run result is not observed baseline truth, accepted evidence, public
truth, source validation, rights clearance, malware safety, verified
installability, exhaustive search proof, production readiness, or master-index
permission.

## CLI

```bash
python scripts/run_workunit_dry_run.py --list-examples
python scripts/run_workunit_dry_run.py --workunit examples/work_units/search_need_review_v0/work_unit.json --check
python scripts/run_workunit_dry_run.py --workunit examples/work_units/search_need_review_v0/work_unit.json --output control/audits/track-b-10-workunit-dry-run-runner-v0/generated/sample_workunit_dry_run_result.json
```

The command refuses forbidden output roots such as `site/dist/`, `runtime/`,
`contracts/`, `control/inventory/publication/`, `.aide.local/`,
`.local/eureka/`, and `.cache/eureka/`.

## Validation

```bash
python scripts/validate_workunit_dry_run_runner.py
python scripts/run_workunit_dry_run.py --workunit examples/work_units/search_need_review_v0/work_unit.json --check
python -m unittest discover -s tests -t .
```

No dry-run report can bypass review gates or mutate the master-index.
