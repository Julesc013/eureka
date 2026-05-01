# Local Staging Path Policy

Local Staging Path Policy v0 defines where future local quarantine/staging
state may live. It is policy only and does not implement a staging runtime or
create local staging directories.

No staging runtime exists in Local Quarantine/Staging Model v0, and this policy does not create, does not import, does not stage, does not index, does not upload, and does not mutate public search or the master index.

## Allowed Future Root Classes

Future local state may use:

- a user-configured cache root
- an application-local data root
- a repo-local ignored root for development only

The suggested development root is `.eureka-local/`. The companion ignored roots
are `.eureka-cache/`, `.eureka-staging/`, and `.eureka-reports/`. These entries
are ignored to protect private state from accidental commits, but this
milestone creates no such directories.

Staging Report Path Contract v0 adds the report-path layer on top of this
policy. It keeps report output on stdout by default, requires explicit output
paths for file writes, blocks forbidden committed roots, and requires redaction
of private absolute paths before reports can be committed or exposed publicly.

Local Staging Manifest Format v0 adds the future manifest envelope for staged
candidate metadata. The committed example under `examples/local_staging_manifests/`
is synthetic and validated by `scripts/validate_local_staging_manifest.py`.
No staging runtime exists, no `.eureka-local/` state is created, and the
manifest format does not mutate public search, local indexes, runtime source
registry state, or the master index.

Staged Pack Inspector v0 is read-only. It may inspect explicit manifests,
explicit manifest roots, or committed synthetic examples and summarize
candidate metadata, but it does not stage, does not import, does not index,
does not upload, does not mutate public search, does not mutate a local index,
and does not mutate the master index. It also creates no local staging
directories.

## Prohibited Roots

Future staging must not write under:

- `site/dist`
- `site/`
- public data
- `external`
- `runtime`
- canonical `control/inventory` source files
- `evals`
- `snapshots/examples` committed examples
- `crates`
- `docs`

Staging under these roots would blur private state, generated static artifacts,
runtime code, public docs, examples, evals, or canonical governance metadata.

## Git Policy

Future local staging state must be ignored and must not be committed. The
required ignore entries are:

```text
.eureka-local/
.eureka-cache/
.eureka-staging/
.eureka-reports/
```

Committed examples may describe staging formats, but they must be synthetic and
must not contain private staged content.

## Path Leakage

Local paths are private by default. Public reports, snapshots, static data,
relay views, diagnostics, and contribution candidates must not contain
unredacted private absolute paths. Repo-relative public fixture paths are the
only ordinary exception.

## Not Implemented

This policy does not implement staging, cache runtime, local index mutation,
public-search mutation, native-client storage, relay exposure, snapshot reader
runtime, uploads, accounts, telemetry, or master-index submission.
