# Staged Pack Inspection

Staged Pack Inspector v0 is a read-only inspection tool for Local Staging
Manifest Format v0. It helps an operator or developer inspect what a manifest
describes without creating staged state.

No staging runtime exists. The inspector does not stage packs, does not import
packs, does not index records, does not upload, does not mutate public search,
does not mutate a local index, does not mutate the runtime source registry,
and does not mutate the master index.

## Commands

List committed synthetic examples:

```bash
python scripts/inspect_staged_pack.py --list-examples
```

Inspect all committed examples:

```bash
python scripts/inspect_staged_pack.py --all-examples
python scripts/inspect_staged_pack.py --all-examples --json
```

Inspect one explicit manifest or manifest root:

```bash
python scripts/inspect_staged_pack.py --manifest examples/local_staging_manifests/minimal_local_staging_manifest_v0/LOCAL_STAGING_MANIFEST.json
python scripts/inspect_staged_pack.py --manifest-root examples/local_staging_manifests/minimal_local_staging_manifest_v0
```

The default behavior is equivalent to `--all-examples` when no explicit
manifest or root is supplied. `--strict` passes strict mode to the manifest
validator. `--no-validate` is diagnostic-only; future staging, export, or
review flows must validate first.

## Human Output

Human output shows:

- manifest ID, status, and staging mode
- validation status
- validate-only report reference
- staged pack reference summaries
- staged entity counts and candidate types
- privacy, rights, and risk posture
- no-mutation guarantees
- future reset, delete, and export policy
- limitations and next safe action

The output states that inspection is read-only and that no staging, import,
index, search, or master-index mutation was performed.

## JSON Output

`--json` emits a deterministic summary with:

- `ok`
- `schema_version`
- `inspector_id`
- `mode`
- `inspected_manifests`
- summary counts
- hard false side-effect flags
- notes

Each manifest summary includes candidate-only staged entity information and
does not echo raw pack payloads.

## Validation Behavior

The inspector validates manifests by default using
`scripts/validate_local_staging_manifest.py`. Validation failure makes the
inspection fail. `--no-validate` may be used to inspect malformed local files
for diagnostics, but it does not make them eligible for any future action.

## Redaction Behavior

The inspector redacts obvious private local paths and secret-like values before
displaying them. It redacts Windows user paths, POSIX home paths, temporary
private path patterns, API-key-like values, private-key blocks, and values under
secret-like field names.

Redaction is not rights clearance, malware safety, or public-safety review.
Local/private manifests remain local/private by default.

## Relationships

Local Staging Manifest Format v0 defines the manifest shape. Staging Report
Path Contract v0 defines stdout defaults, explicit output path policy, and
redaction posture. Validate-Only Pack Import Tool v0 produces Pack Import
Report v0 before any future staging decision. Local Quarantine/Staging Model v0
defines private-by-default staging policy.

The inspector sits after those contracts and before any future Local
Quarantine/Staging Tool v0. Future native staging UI may reuse its summary
model, but no native client is implemented. Relay and snapshots must not expose
local/private staged data by default. Public search remains unaffected.

AI-Assisted Evidence Drafting Plan v0 may later inspect staged manifests as
local/private context only after typed output validation and explicit future
policy. Staged inspection does not send private staged data to remote providers
by default, does not accept AI output as evidence or contribution truth, and
does not mutate public search, local indexes, runtime source registry state, or
the master index.

## Not Implemented

The inspector does not create `.eureka-local/`, `.eureka-cache/`,
`.eureka-staging/`, or `.eureka-reports/`. It does not copy pack files, inspect
pack payload bytes, crawl directories, fetch URLs, call models, create accounts,
emit telemetry, submit contributions, or accept anything into a master index.

Future work remains: Local Quarantine/Staging Tool v0 only after explicit
approval, delete/reset tooling, local index candidate planning, native staging
UI planning, and contribution queue export.
