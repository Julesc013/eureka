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
are `.eureka-cache/` and `.eureka-staging/`. These entries are ignored to
protect private state from accidental commits, but this milestone creates no
such directories.

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
```

Committed examples may describe staging formats later, but they must be
synthetic and must not contain private staged content.

## Path Leakage

Local paths are private by default. Public reports, snapshots, static data,
relay views, diagnostics, and contribution candidates must not contain
unredacted private absolute paths. Repo-relative public fixture paths are the
only ordinary exception.

## Not Implemented

This policy does not implement staging, cache runtime, local index mutation,
public-search mutation, native-client storage, relay exposure, snapshot reader
runtime, uploads, accounts, telemetry, or master-index submission.
