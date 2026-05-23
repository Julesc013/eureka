# Product Boundary Preservation

## Product Roots Discovered

- Canonical contracts and product truth: `contracts/**`.
- Runtime/product behavior: `runtime/**`.
- Gateway and public API behavior: `runtime/gateway/**`, `contracts/api/**`, `contracts/gateway/**`.
- Engine boundaries: `runtime/engine/**`.
- Connectors and source acquisition adapters: `runtime/connectors/**`, connector contracts and source contracts.
- User surfaces: `surfaces/web/**`, `surfaces/native/**`, `native/**`.
- Public/static artifacts and generator inputs: `site/**`, especially generated `site/dist/**`.
- Snapshot substrate and examples: `snapshots/**`.
- Source/evidence/index examples and fixtures: `examples/**`, `evals/**`, `control/**`.
- Rust candidate lane: `crates/**`.

## Architecture Boundaries

- `AGENTS.md` defines the control/contracts/runtime/surfaces split and dependency law.
- `scripts/check_architecture_boundaries.py` exists and passed: checked 692 Python files with no boundary violations.
- Key docs include `docs/architecture/RUNTIME_NAMING_BOUNDARY.md`, `LOCAL_RUNTIME_COMPOSITION_BOUNDARY.md`, `LOCAL_SERVICE_STORE_WORKER_BOUNDARY.md`, `SOURCE_OBSERVATION_SEAM.md`, `SOURCE_CACHE_STORE.md`, `EVIDENCE_LEDGER_STORE.md`, `REVIEWED_PUBLIC_INDEX.md`, and `PUBLICATION_PLANE.md`.

## Source/Evidence/Index Systems

Preserve and do not absorb destructively:

- source registry/cache/observation/sync: `contracts/source/records/**`, `contracts/source/cache/**`, `contracts/source/registry/**`, `contracts/source/sync/**`, `runtime/source/registry/**`, `runtime/source/cache/**`, `runtime/source/observation/**`;
- evidence ledger and evidence packs: `contracts/evidence/**`, `contracts/evidence/ledger/**`, `contracts/stores/evidence_*`, `runtime/evidence/ledger/**`, `examples/evidence_*`;
- public/master index and review queue: `contracts/index/master/**`, `contracts/stores/public_index_*`, `runtime/index/public/**`, `runtime/review/queue/**`;
- pack import/export/quarantine: `contracts/pack/**`, `examples/packs/source/**`, `examples/packs/evidence/**`, `runtime/local/foundry/pack_*`;
- site/static public data: `site/pages/**`, `site/data/**`, `site/dist/**`, `snapshots/examples/**`.

## Q55 Never-Overwrite Rules

Q55 must not overwrite or normalize these as generic AIDE state:

- any product root: `runtime/**`, `contracts/**`, `surfaces/**`, `site/**`, `snapshots/**`, `native/**`, `crates/**`, `examples/**`, `evals/**`;
- product docs and operation manuals under `docs/**` unless Q55 writes an explicit compact AIDE upgrade reference after review;
- validators/scripts/tests under `scripts/**` and `tests/**`;
- source cache, evidence ledger, public index, review queue, source-pack, evidence-pack, or pack-import generated/product files;
- public/static generated artifacts unless a later product task explicitly scopes them;
- `.aide/memory/**`, `.aide/queue/**`, target golden tasks, target evidence, target reports, and `AGENTS.md` manual content.

## Safety Constraints

- Connectors must not invent object truth or own trust semantics.
- AIDE must not define runtime behavior or product truth.
- No live source probes, crawls, downloads, source-sync, public-index mutation, evidence-ledger mutation, provider/model calls, hosted deployment, or public release behavior is authorized by Q54 or Q55.
- Generated AIDE outputs remain evidence unless explicitly promoted by a later reviewed task.
