# Public Alpha Launch Deferred

Status: `DEFERRED`

`PUBLIC-ALPHA-LAUNCH-00` is intentionally paused. This is a product-direction
correction, not a launch failure.

The read-only public alpha shell, launch-candidate evidence, deployment dry-run
evidence, and local preview checks are preserved. They prove that the shell can
run in a constrained local/prototype posture. They do not prove that Eureka is
useful enough as a public search engine.

## Reason

The current public alpha is structurally ready but product-thin:

- routes exist
- snapshot and relay posture exists
- read-only public API posture exists
- launch gates exist
- reviewed/searchable corpus coverage remains too small
- weak queries do not yet produce enough candidate leads automatically

Public launch should wait until active discovery can produce useful candidate
results and review throughput.

## Preserved Evidence

- `control/inventory/public_alpha_launch_candidate_result.json`
- `control/inventory/public_alpha_deploy_dry_run_result.json`
- `control/inventory/public_alpha_launch_result.json`

The preserved evidence must keep:

- `deployment_performed: false`
- `public_launch_performed: false`
- `production_readiness_claimed: false`
- `public_launch_readiness_claimed: false`

## New Gate

Before staging or public launch, Eureka must support Archive.org-wide metadata
candidate discovery. This means querying Internet Archive item metadata search
surfaces as governed candidate sources, not crawling arbitrary web pages and not
downloading files.

The initial approved design target is:

```text
query
-> reviewed local results
-> local candidates/source cache
-> approved Archive.org metadata search
-> per-identifier metadata read
-> candidate records
-> review queue
-> accepted local reviewed records
-> snapshot refresh
-> public read-only results
```

Internet Archive references:

- `https://archive.org/developers/item-search-apis.html`
- `https://archive.org/developers/md-read.html`
- `https://archive.org/developers/metadata-schema/index.html`

## Non-Claims

No deployment, staging deployment, or public launch is approved by this
deferral.

This deferral does not approve:

- staging deployment
- public launch
- production readiness
- public launch readiness
- arbitrary crawling
- file downloads
- extraction
- execution
- uploads
- accounts
- telemetry
- automatic reviewed truth
- public or master index mutation from live source results

Next task: `ACTIVE-DISCOVERY-AND-CANDIDATE-INTAKE-00`.
