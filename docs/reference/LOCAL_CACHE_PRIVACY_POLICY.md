# Local Cache Privacy Policy

Native Local Cache / Privacy Policy v0 defines future privacy rules for native
clients and local/offline components. It is policy and contract work only. It
does not implement a local cache, private file ingestion, local archive
scanning, telemetry, analytics, accounts, cloud sync, uploads, native clients,
relay runtime, or GUI behavior.

The default posture is privacy-first: no private user data by default, no
telemetry by default, no external uploads by default, no cloud sync by default,
no local archive scanning by default, no private paths in public reports, no
secrets in snapshots or public data, no account system, and no private data
through relay or old-client surfaces by default.

## Public Cache Versus Private Cache

Public cache is future storage for already-public metadata such as generated
public data summaries, snapshot manifests, route summaries, source summaries,
eval summaries, page registries, and checksum validation results. A public
cache must not contain private user files, private local paths, credentials,
account/session state, telemetry payloads, or private inventories.

Index Pack Contract v0 defines public-safe index coverage summaries, not a
local cache export. Index packs must not include raw SQLite databases, raw
local cache files, private local paths, credentials, executable payloads, or
private user search history.

Contribution Pack Contract v0 defines public-safe review-candidate summaries,
not a cache export or upload path. Contribution packs must not include raw
cache files, raw SQLite databases, private local paths, credentials, executable
payloads, telemetry payloads, or private user search history.

Master Index Review Queue Contract v0 preserves this boundary for future queue
entries. Queue entries do not grant local filesystem access and cannot convert
private cache records into accepted public records without separate privacy
review.

Validate-Only Pack Import Tool v0 preserves this boundary by reading only
explicit pack roots or known examples, redacting local absolute paths in
reports where possible, writing only an explicit report file when requested,
and not creating staging, import, cache, local index, upload, or master index
state.

Private cache is future explicit user state. It may later hold user-selected
artifacts, preferences, local strategy notes, private resolution memory, or
native-client working state. Private cache is disabled by default and requires
separate implementation review, user-selected roots, clear deletion/reset/export
controls, and privacy review before it exists.

## Local Artifacts And Local Paths

Local paths are private unless they are repo-relative public fixture paths or
explicitly public static artifact paths. Public-alpha status, static pages,
snapshots, public data, relay views, checkpoint reports, and support exports
must avoid private absolute paths and secrets.

Future native clients may show local paths only inside the local UI context
where the user selected them. Those paths must not be copied into public
reports, snapshots, static public data, or old-client relay projections.

## User Preferences And Strategy Memory

Future native clients may need local preferences, display settings, source
filters, or strategy memory. Those are local user state, not public resolver
truth. They must be optional, resettable, exportable by the user, and excluded
from public data and snapshots by default.

Resolution memory remains current local/reference behavior. Future native
private resolution memory must be governed by this policy before it is exposed
as a native feature.

## Logs, Diagnostics, And Crash Reports

Logs are not telemetry. Future logs must avoid private paths, credentials, and
secrets where possible. Diagnostic bundles and crash reports must be explicit
user exports in a future policy; they must not upload automatically.

Public-alpha logs and status views must not expose private local paths or
secrets. Manual external observations are user-entered records, not telemetry.

## Telemetry, Accounts, Credentials, And Sync

No telemetry is implemented. Telemetry must be off by default if it is ever
added. No analytics, crash-report upload, external diagnostics upload, account
system, source credential store, cloud memory, or cloud sync exists in v0.

Source credentials are unsupported. Credentials must not appear in snapshots,
public data, relay old-client projections, diagnostics, or support exports.
Future credential handling requires a separate auth/secrets policy.

Public Search Safety / Abuse Guard v0 follows this posture for future public
search. It forbids local path, user file, credential, telemetry-by-default,
query-log-upload, and private source parameters before any runtime route exists.

AI Provider Contract v0 follows this posture for future model providers. AI
providers are disabled by default, private data is disabled by default, prompt
and output logging are disabled by default, and remote providers require
explicit credentials and consent before any future runtime exists. Provider
manifests must not contain API keys, secrets, private paths, or credential
storage behavior.

Typed AI Output Validator v0 follows the same posture for recorded AI output
candidates. It rejects secret-like fields and private absolute paths in
public-safe output, records no prompt logs, performs no telemetry, calls no
model, and does not import output into evidence, contribution, local index, or
master-index state.

## Deletion, Reset, Export, And Portable Mode

Future native/private cache work requires controls to clear public cache, clear
private cache, clear local preferences, clear local resolution memory, clear
diagnostics, reset portable mode state, and export user-selected local metadata.

Portable/offline mode is future. It must use user-controlled roots, avoid writes
outside the selected root, support offline snapshots, and keep private state out
of public snapshots and public reports.

## Relationship To Snapshots, Relay, Native Clients, And Public Alpha

Snapshots are public/offline artifacts. They must not include private cache,
secrets, account data, telemetry, source credentials, or private user history.

Relay surfaces remain public/read-only by default. Old or insecure clients must
not receive private cache, credentials, user history, write/admin controls, or
private local paths.

Relay Prototype Planning v0 keeps the first future relay prototype public,
read-only, localhost-only by default, and static. It does not allow private
cache roots, arbitrary user directories, credentials, browser history, private
search history, telemetry, uploads, or private local paths as inputs or
outputs.

Native clients remain future. Before they implement a local cache, they must
follow this policy, the Native Client Contract, the Snapshot Consumer Contract,
the Relay Surface Design, and the Native Action / Download / Install Policy.

Public-alpha remains non-production and metadata-first. It blocks
caller-provided local paths and must not expose private local roots, user
storage, private cache, telemetry, accounts, cloud sync, or uploads.

Source/Evidence/Index Pack Import Planning v0 treats future pack staging as
private local state. Validate-only comes first; any later quarantine root must
be user controlled, not committed to git, outside `site/dist`, outside
`external`, and excluded from public reports unless explicitly redacted and
reviewed. Staged packs must not affect public search or the master index by
default.

Pack Import Report Format v0 records validate-only outcomes without creating
local staging state. Reports must not include unredacted private absolute paths,
credentials, or private cache contents, and successful reports do not authorize
cache import, local-index mutation, upload, or master-index mutation.

## Not Implemented

This policy does not implement:

- local cache runtime
- private file ingestion
- local archive scanning
- accounts
- telemetry or analytics
- diagnostics or crash-report upload
- cloud sync or cloud memory
- uploads
- native clients
- native GUI behavior
- relay runtime
- source credential storage
- private-data relay behavior
- production readiness
