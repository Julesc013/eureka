# Eureka Documentation

This directory is the public documentation hub for Eureka. It should orient
first-time readers without turning the root README into an operator log or a
mega-spec.

Use this boundary when navigating the repo:

- public docs orient
- architecture explains how the system is shaped
- status explains what is real now
- roadmap explains what comes next
- operations define safe procedures and gates
- evidence prevents overclaiming

## Start Here

| Need | Read |
| --- | --- |
| Public overview | [Root README](../README.md) |
| Current branch and maturity posture | [Status](STATUS.md) |
| Baseline summary and non-claims | [Bootstrap Status](BOOTSTRAP_STATUS.md) |
| Product direction | [Vision](VISION.md) |
| System boundaries | [Architecture](ARCHITECTURE.md) |
| Staged next work | [Roadmap](ROADMAP.md) |
| Repo layout | [Repo Layout](REPO_LAYOUT.md) |
| License posture | [Root license](../LICENSE.md) |

## Vision And Doctrine

- [Vision overview](VISION.md)
- [Vision docs](vision/README.md)
- [Eureka Thesis](vision/EUREKA_THESIS.md)
- [Product Promise](vision/PRODUCT_PROMISE.md)
- [Doctrine](vision/DOCTRINE.md)

Vision describes direction. It is not a claim that every described capability is
implemented today.

## Architecture

- [Architecture overview](ARCHITECTURE.md)
- [Architecture docs](architecture/README.md)
- [Temporal Object Resolver](architecture/TEMPORAL_OBJECT_RESOLVER.md)
- [Logical Graphs](architecture/LOGICAL_GRAPHS.md)
- [Physical Subsystems](architecture/PHYSICAL_SUBSYSTEMS.md)
- [Data Model](architecture/DATA_MODEL.md)
- [Local Product Loop](architecture/LOCAL_PRODUCT_LOOP.md)
- [Workbench Local Loop](architecture/WORKBENCH_LOCAL_LOOP.md)
- [Public Alpha Launch Candidate](architecture/PUBLIC_ALPHA_LAUNCH_CANDIDATE.md)
- [Rust Backend Lane](architecture/RUST_BACKEND_LANE.md)
- [AI Policy](architecture/AI_POLICY.md)

Architecture documents may include future models. Check status, validators, and
evidence before treating a model as implemented runtime behavior.

## Roadmap And Status

- [Status](STATUS.md)
- [Bootstrap Status](BOOTSTRAP_STATUS.md)
- [Roadmap](ROADMAP.md)
- [Roadmap docs](roadmap/README.md)
- [Public Alpha Roadmap](roadmap/PUBLIC_ALPHA.md)
- [Backend Roadmap](roadmap/BACKEND_ROADMAP.md)
- [Rust Migration](roadmap/RUST_MIGRATION.md)
- [Native Apps Later](roadmap/NATIVE_APPS_LATER.md)
- [Open Questions](OPEN_QUESTIONS.md)
- [Decisions](DECISIONS.md)

Status pages carry volatile branch and validation detail. The root README should
stay stable and public-facing.

## Operations And Public Alpha

- [Operations docs](operations/README.md)
- [Test and Eval Lanes](operations/TEST_AND_EVAL_LANES.md)
- [Local HTML Workbench Runbook](operations/LOCAL_HTML_WORKBENCH_RUNBOOK.md)
- [Workbench Local Loop Runbook](operations/WORKBENCH_LOCAL_LOOP_RUNBOOK.md)
- [Local Apply Gate Runbook](operations/LOCAL_APPLY_GATE_RUNBOOK.md)
- [Public Alpha Read-Only Closeout](operations/PUBLIC_ALPHA_READONLY_CLOSEOUT.md)
- [Public Alpha Launch Candidate Runbook](operations/PUBLIC_ALPHA_LAUNCH_CANDIDATE_RUNBOOK.md)
- [Public Alpha Deploy Dry-Run Plan](operations/PUBLIC_ALPHA_DEPLOY_DRY_RUN_PLAN.md)
- [Public Alpha Manual Approval Gate](operations/PUBLIC_ALPHA_MANUAL_APPROVAL_GATE.md)
- [Source Action Kernel Runbook](operations/SOURCE_ACTION_KERNEL_RUNBOOK.md)
- [Source Wave Runbook](operations/SOURCE_WAVE_RUNBOOK.md)
- [Snapshot Relay Runbook](operations/SNAPSHOT_RELAY_RUNBOOK.md)

Operational docs define procedures and gates. They do not, by themselves, prove
deployment or production readiness.

## Standards And Contracts

- [Standards docs](standards/README.md)
- [Identifier Policy](standards/IDENTIFIER_POLICY.md)
- [Privacy And Shared Evidence](standards/PRIVACY_AND_SHARED_EVIDENCE.md)
- [Source Registry Schema](standards/SOURCE_REGISTRY_SCHEMA.md)
- [Reference docs](reference/README.md)
- [Local HTTP API](reference/LOCAL_HTTP_API.md)
- [Local HTML Routes](reference/LOCAL_HTML_ROUTES.md)
- [Public Alpha Launch Gates](reference/PUBLIC_ALPHA_LAUNCH_GATES.md)
- [Master Index Review Queue Contract](reference/MASTER_INDEX_REVIEW_QUEUE_CONTRACT.md)

Contracts and standards are governing material. They still require runtime,
validation, and evidence before becoming product claims.

## Research

- [Research index](../control/research/README.md)
- [Temporal Object Resolution Engine research note](../control/research/temporal-object-resolution-engine.md)

Research notes can inform future accepted direction, but research is not product
truth until promoted through accepted docs, contracts, implementation, and
validation.

## Evals

- [Eval docs](evals/README.md)
- [Search Benchmark Design](evals/SEARCH_BENCHMARK_DESIGN.md)
- [Repo evals](../evals/README.md)
- [Control audits](../control/audits/README.md)

Evals are evidence tools. They are not production claims and should preserve
truth boundaries.

## Rust Migration

- [Rust Backend Lane](architecture/RUST_BACKEND_LANE.md)
- [Rust Migration Roadmap](roadmap/RUST_MIGRATION.md)
- [crates/](../crates/README.md)

Rust work is a parity and future migration lane. Python remains the reference
oracle until future gates say otherwise.

## Contributor And Agent Docs

- [Contributing](../CONTRIBUTING.md)
- [Security](../SECURITY.md)
- [Code of Conduct](../CODE_OF_CONDUCT.md)
- [License](../LICENSE.md)
- [License Summary](../LICENSE-SUMMARY.md)
- [Notice](../NOTICE.md)
- [Agent Instructions](../AGENTS.md)
- [Scripts](../scripts/README.md)
- [Tools](../tools/README.md)

Agents and contributors should keep changes scoped, run validators that match
the touched paths, and avoid claims of deployment, public launch, production
readiness, broad corpus coverage, or AI authority without evidence.

## Documentation Posture

Do not use docs prose to bypass gates. Eureka currently remains a local-first
Python reference prototype with read-only public-alpha foundations. It has not
launched publicly and does not claim production readiness.

Eureka is source-available under a custom restricted license. It is not
open-source software.
