# Roadmap

The roadmap is staged so each step adds evidence and governance before it adds
public promises. Eureka's current state is a local-first Python reference
backend with public-alpha read-only foundations and a passed launch-candidate
gate.

## Current Gate

`PUBLIC-ALPHA-LAUNCH-CANDIDATE-00` has passed and recommends:

1. `PUBLIC-ALPHA-DEPLOY-DRY-RUN-00`
2. `PUBLIC-ALPHA-LAUNCH-00`
3. `PUBLIC-DEMAND-SIGNAL-00`
4. `PUBLIC-SOURCE-REQUEST-QUEUE-00`
5. live metadata pilots
6. `NATIVE-SNAPSHOT-CLIENT-00`
7. `ACTION-MANIFEST-00`

A launch candidate is not launch. A deploy dry run is not public launch. Launch
requires explicit manual approval.

## Current Workable Baseline

- Local product loop promoted.
- Workbench local operator loop present.
- Public-alpha read-only routes present.
- Snapshot/relay foundations present.
- Source Action Kernel and Source Wave foundations present.
- Full discovery has prior external pass evidence for the promoted baseline.
- No deployment, public launch, production readiness, public mutation, live
  source fanout, downloads, uploads, broad extraction, or model/provider calls.

## Near-Term Sequence

### Deploy Dry Run

`PUBLIC-ALPHA-DEPLOY-DRY-RUN-00` should rehearse deployment mechanics without
making public launch claims. It should produce operator evidence, rollback
evidence, environment checks, and safety validation.

### Launch Approval

`PUBLIC-ALPHA-LAUNCH-00` requires explicit manual approval. It must not infer
approval from the launch candidate or dry run.

### Demand Signal

`PUBLIC-DEMAND-SIGNAL-00` should collect public or operator demand signals
without turning requests into accepted truth or automatic source/index
mutation.

### Source Request Queue

`PUBLIC-SOURCE-REQUEST-QUEUE-00` should model source requests as review
candidates. It must keep public mutation, live fanout, downloads, extraction,
and source truth acceptance gated.

### Live Metadata Pilots

Live metadata pilots may only run behind explicit source policy and operator
approval. They should start with bounded metadata, not crawling, downloading,
or extraction.

### Native Snapshot Client

`NATIVE-SNAPSHOT-CLIENT-00` should consume read-only snapshots/relays. It must
not become a downloader, installer, marketplace manager, or live source client.

### Action Manifest

`ACTION-MANIFEST-00` should define safe action manifests and review handoffs. It
must not enable public action execution, install, download, or marketplace
behavior by default.

## Detailed Roadmaps

- [Backend Roadmap](roadmap/BACKEND_ROADMAP.md)
- [Public Alpha](roadmap/PUBLIC_ALPHA.md)
- [Rust Migration](roadmap/RUST_MIGRATION.md)
- [Native Apps Later](roadmap/NATIVE_APPS_LATER.md)
- [Track Execution Plan](roadmap/TRACK_EXECUTION_PLAN.md)

## Roadmap Non-Claims

Roadmap entries are planned or gated work. They are not public launch,
deployment, production readiness, broad corpus coverage, rights clearance,
malware safety, native distribution readiness, or AI authority.
