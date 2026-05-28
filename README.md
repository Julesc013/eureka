# Eureka

Eureka is a local-first artefact-resolution engine for hard-to-find software,
media, documents, source traces, and other technical/cultural objects.

Eureka is currently a Python reference backend and local-first prototype. It has
a promoted local product loop, read-only public-alpha route foundations, a
launch-candidate gate record, and snapshot-backed relay foundations. It has not
been deployed, has not launched publicly, and does not claim production
readiness.

## What Eureka Is

Eureka treats search as an investigation rather than a single ranked answer. It
helps an operator turn a vague request into reviewed, evidence-backed records:
what object may match, which source observed it, what evidence exists, what is
absent or uncertain, and what explicit next action is safe.

The current executable lane is a local Python reference backend. Rust, native,
marketplace, hosted deployment, and action-manager work are staged or planned
lanes, not current product claims.

## Current Status

The public alpha read-only baseline has been promoted to `main`. A subsequent
launch-candidate gate has passed on `dev` and recommends
`PUBLIC-ALPHA-DEPLOY-DRY-RUN-00` as the next task. A launch candidate is not a
launch, and a deploy dry run is not a public launch.

Current bounded facts:

- Local operator Workbench and local product loop foundations exist.
- Public-alpha read-only web and API route foundations exist.
- Public alpha routes are snapshot-backed and read-only.
- Public live source fanout is disabled.
- Public mutation is disabled.
- Downloads, uploads, executable actions, and installer behavior are disabled.
- Extraction is disabled except safe fixture/member-manifest foundations.
- Model/provider calls are disabled.
- Full unittest discovery is handled outside AI chat/model sessions through a
  harness or CI artifact flow.

## What Eureka Is Not

Eureka is not:

- a production hosted service
- a publicly launched product
- a full Archive.org search engine
- a full web crawler
- an app store, installer, downloader, or marketplace manager
- a native client ready for distribution
- an AI authority or LLM-first answer engine
- a broad corpus coverage claim
- a live public fanout service for source APIs

## Core Idea: Search As Investigation

Hard artefact search often fails because the useful unit is smaller or messier
than the source item: a driver inside a support CD, an article inside a scan, a
release asset inside a project, a dead link trace, or a package version with
compatibility constraints. Eureka records the investigation trail instead of
pretending one candidate is automatically truth.

Important boundaries:

- Candidates are not truth.
- Source observations are not truth.
- Review gates truth.
- Promotion previews are not promotion.
- Local apply is explicit and operator-gated.
- Snapshots and relays are read-only data products.

## Current Capabilities

### Local Product Loop

The local product loop supports the current reference flow:

1. Query.
2. Resolution run.
3. Result lanes.
4. Candidate.
5. Review.
6. Promotion preview.
7. Local apply gate.
8. Reviewed result.
9. Rollback.

This loop is local/operator-facing. It does not create public truth or mutate a
master/public index without review and promotion gates.

### Workbench

The Workbench is operator Mission Control for the local loop. It is a local
cockpit for inspecting runs, lanes, candidates, review handoffs, promotion
previews, local apply gates, reviewed results, and rollback evidence. It is not
a public mutation UI.

### Public Alpha Read-Only

The public-alpha foundation exposes read-only routes locally:

- `/alpha`
- `/alpha/object`
- `/alpha/source`
- `/alpha/evidence`
- `/alpha/absence`
- `/alpha/needs`
- `/api/v1/alpha/status`
- `/api/v1/alpha/search`
- `/api/v1/alpha/object/{object_id}`
- `/api/v1/alpha/source/{summary_id}`
- `/api/v1/alpha/evidence/{summary_id}`
- `/api/v1/alpha/absence/{summary_id}`
- `/api/v1/alpha/needs`

These routes are snapshot-backed and read-only. They do not enable live source
fanout, downloads, uploads, extraction, accounts, telemetry, model/provider
calls, public mutation, or deployment.

### Source Action Kernel

The Source Action Kernel records the generic source action seam:

- policy gate
- request plan
- transport
- normalizer
- mapping plans
- lane projection
- review handoff
- boundary report
- scorecard

It is a governed action shape, not permission to call sources live. Source
actions remain policy/operator gated.

### Source Wave

The current metadata source wave covers fixture/mock or governed metadata lanes
for:

- Internet Archive metadata
- Wayback/CDX metadata
- GitHub Releases metadata
- Software Heritage metadata
- package registry metadata
- Open Library metadata
- Wikidata metadata
- manual source packs

These are not a full web crawler and not full Archive.org search.

### Snapshot And Relay

Snapshot/relay foundations cover:

- reviewed records
- integrity manifests
- capability profiles
- read-only relay query

Snapshots and relays are read-only data products. They do not include private
local state, raw live source responses, public mutation, or deployment claims.

### Domains, Scout, F0, G0, SYN

Eureka keeps several foundations explicit:

- `SYN`: synthetic query and fixture foundations for deterministic local work.
- `DOMAIN`: domain packs and query interpretation boundaries.
- `SCOUT`: discovery trails and source-trust scaffolding.
- `F0`: safe extraction/member-discovery foundations, without broad extraction.
- `G0`: identity, near-miss, explanation, user-cost, and actionability signals.

## Local Quick Start

From a Windows checkout:

```powershell
cd D:\Projects\Eureka\eureka
python scripts/eureka_validate_instance.py --instance ..\instances\default --json
python scripts/eureka_local_server.py --instance ..\instances\default --host 127.0.0.1 --port 8765 --operator-token local-dev-token
```

Useful local URLs:

- <http://127.0.0.1:8765/>
- <http://127.0.0.1:8765/search?q=sampleproject>
- <http://127.0.0.1:8765/alpha>
- <http://127.0.0.1:8765/alpha/needs>

Use a local development token only for local operator testing. Do not commit
tokens.

## Workbench And Local Operator Loop

The local Workbench is the operator-facing projection of the product loop. It is
for inspecting evidence and applying reviewed local changes behind explicit
gates. Operators should use it with temporary or private local instances and
keep local state out of the repository.

Key references:

- [Local HTML Workbench runbook](docs/operations/LOCAL_HTML_WORKBENCH_RUNBOOK.md)
- [Workbench local loop runbook](docs/operations/WORKBENCH_LOCAL_LOOP_RUNBOOK.md)
- [Local apply gate runbook](docs/operations/LOCAL_APPLY_GATE_RUNBOOK.md)

## Public Alpha Read-Only Routes

For local route validation and public-alpha posture, use:

```powershell
python scripts/validate_public_alpha_readonly.py
python scripts/validate_public_alpha_hosting_readiness.py
python scripts/validate_public_alpha_launch_candidate.py
```

The launch-candidate gate says the baseline can move to a deploy dry run. It
does not deploy or launch Eureka.

References:

- [Public alpha read-only closeout](docs/operations/PUBLIC_ALPHA_READONLY_CLOSEOUT.md)
- [Public alpha launch candidate runbook](docs/operations/PUBLIC_ALPHA_LAUNCH_CANDIDATE_RUNBOOK.md)
- [Public alpha deploy dry-run plan](docs/operations/PUBLIC_ALPHA_DEPLOY_DRY_RUN_PLAN.md)

## Source Actions And Source Families

Source families and source actions are governed through contracts, inventories,
runbooks, validators, and audit evidence. They are intentionally separated from
truth acceptance.

An agent or operator may propose a source observation, candidate, scorecard, or
review handoff. Acceptance requires review. Live source actions require explicit
policy/operator approval.

References:

- [Source Action Kernel runbook](docs/operations/SOURCE_ACTION_KERNEL_RUNBOOK.md)
- [Source Wave runbook](docs/operations/SOURCE_WAVE_RUNBOOK.md)
- [Source policy gates](docs/operations/SOURCE_POLICY_GATES.md)

## Snapshot And Relay

Snapshot and relay work provides read-only reviewed-record data products for
static and local consumption. It does not make a public mutable service.

Use:

```powershell
python scripts/validate_snapshot_relay.py
```

References:

- [Snapshot relay runbook](docs/operations/SNAPSHOT_RELAY_RUNBOOK.md)
- [Snapshot to relay handoff](docs/operations/SNAPSHOT_TO_RELAY_HANDOFF.md)
- [Read-only relay model](docs/architecture/READ_ONLY_RELAY_MODEL.md)

## Testing And Validation

During normal development, use focused tests:

```powershell
python scripts/eureka_test_select.py --changed --failed-first --json
```

The public-alpha closeout/promotion gate wrapper is:

```powershell
python scripts/eureka_gate.py public-alpha-closeout --watch --clean
```

Full unittest discovery is a promotion/nightly/manual lane and must run outside
AI chat/model sessions through the harness or CI:

```powershell
python scripts/run_full_unittest_discovery.py --out ..\eureka-test-runs\manual_full_discovery
```

AI agents must not babysit full discovery. Full logs stay local/artifact-only.
AI reads compact summaries and handoffs.

The GitHub Actions workflow for full discovery is the preferred shared evidence
path when branch state has been pushed.

Reference:

- [Test and eval lanes](docs/operations/TEST_AND_EVAL_LANES.md)

## Safety Boundaries

| Capability | Current status |
| --- | --- |
| Public hosted service | Not launched |
| Production readiness | Not claimed |
| Public live source fanout | Disabled |
| Downloads | Disabled |
| Uploads | Disabled |
| Extraction | Disabled except safe fixture/member-manifest foundation |
| Model/provider calls | Disabled |
| Public mutation | Disabled |
| Master/public index mutation | Review/promotion-gated, not automatic |
| Native marketplace manager | Not implemented |

## Roadmap

Current next sequence:

1. `PUBLIC-ALPHA-DEPLOY-DRY-RUN-00`
2. `PUBLIC-ALPHA-LAUNCH-00`
3. `PUBLIC-DEMAND-SIGNAL-00`
4. `PUBLIC-SOURCE-REQUEST-QUEUE-00`
5. live metadata pilots
6. `NATIVE-SNAPSHOT-CLIENT-00`
7. `ACTION-MANIFEST-00`

The just-recorded `PUBLIC-ALPHA-LAUNCH-CANDIDATE-00` gate is not launch.
`PUBLIC-ALPHA-DEPLOY-DRY-RUN-00` is not public launch. Launch requires explicit
manual approval.

## Repository Layout

```text
.aide/       repo operating metadata and compact task context
control/     governance, audits, inventories, policies, evidence
contracts/   packet, schema, API, and shared contract authority
runtime/     Python reference runtime
surfaces/    web, CLI, API, text, file, lite, and native projections
site/        static site source and generated static artifact tree
snapshots/   snapshot schemas and public-safe examples
examples/    public-safe fixtures, packs, and examples
evals/       repo-level evaluations
tests/       cross-component and repo-operating tests
tools/       implementation helpers for validators/generators/auditors
scripts/     stable command wrappers
release/     release and hosting plans, not generated release output
archive/     retired, historical, or quarantined material
native/      canonical native client project root and skeletons
crates/      Rust parity/future migration lane
```

Scripts are stable command wrappers. Tools contain implementation helpers.
Runtime contains the Python reference runtime. Surfaces contain projections.
Contracts contain packet/schema authority. Control contains governance, audits,
and inventories.

More detail:

- [Docs index](docs/README.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Repo layout](docs/REPO_LAYOUT.md)
- [Roadmap](docs/ROADMAP.md)

## For Contributors And Agents

Humans and agents should use packet contracts and scripts. Agents may propose
candidates, summaries, and review handoff plans. Agents may not create accepted
truth.

Agents may not:

- mutate master/public indexes
- run live source actions without policy/operator approval
- run long full-discovery tests inside chat/model sessions
- commit tokens, credentials, raw private logs, raw live source responses, or
  local instance state
- claim deployment, public launch, production readiness, broad corpus coverage,
  native marketplace readiness, or AI authority without governed evidence

Read:

- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Agent instructions](AGENTS.md)

## License / Status Notes

No root `LICENSE` file is currently present, and licensing is not finalized.
Until a license is selected by the repository owner or an authorized legal
decision-maker, do not assume permission to copy, redistribute, package,
publish, or commercialize the code beyond permissions granted by the repository
owner and applicable platform terms.

See [License Selection Required](docs/operations/LICENSE_SELECTION_REQUIRED.md).
