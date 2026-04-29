# Native Local Cache Contract

Native Local Cache Contract v0 defines the future native-client cache rules
that must exist before any native cache runtime is implemented. It is contract
work only and does not create cache code, private ingestion, native GUI
projects, accounts, telemetry, or sync behavior.

## Future Cache Roots

Future native clients must use user-controlled cache roots. A client must not
write private state outside an explicitly selected root, and portable mode must
be able to keep its state inside that selected root.

Public cache and private cache must be separate:

- public cache may contain already-public metadata and snapshot validation
  results
- private cache may contain only explicit user-selected state after a future
  opt-in implementation exists
- public reports must not include private cache paths

## Public Data And Artifacts

Static public data can be cached separately from private state. Snapshot
manifests, checksums, source summaries, eval summaries, route summaries, and
page registries are appropriate future public-cache inputs.

Artifacts require the Native Action / Download / Install Policy and future
rights/security implementation before they can become cacheable beyond current
fixture/developer-local behavior. Executable artifacts require executable-risk
warnings, checksum/hash display, provenance display, and explicit user
confirmation before any future handoff.

## Private Files And Local Scanning

Native clients must not automatically scan user directories, removable drives,
archives, downloads folders, or application folders. Private file ingestion is
disabled by default and not implemented.

If private ingestion is ever added, it requires a separate source policy,
privacy review, user-selected root, exclusion rules, redaction rules, and clear
deletion/export/reset controls.

## User Controls

Before private cache implementation, future clients must provide:

- clear cache metadata inspection
- clear public cache
- clear private cache
- reset preferences
- reset local strategy or resolution memory
- delete diagnostics
- export only user-selected metadata
- portable mode reset

These controls are future requirements, not implemented behavior.

## Public Reports And Relay Views

Native clients must not leak private local paths, credentials, source tokens,
private inventories, or account/session state into public reports, snapshots,
static public data, public-alpha status, or old-client relay projections.

Relay integration remains future and public/read-only by default. Private data
through a relay requires a future security/privacy policy and must not be
available to old or insecure clients by default.

## Offline And Portable Operation

Future offline mode should prefer static snapshots and public data. Portable
mode must be explicit, user-controlled, resettable, and free of hidden writes
outside the selected root. Portable mode must not turn private cache into a
public snapshot or upload target.

## Not Implemented

This contract does not implement a cache runtime, encrypted cache, private
index, local archive scanner, account store, telemetry sink, cloud sync, native
snapshot reader, relay sidecar, or native GUI project.
