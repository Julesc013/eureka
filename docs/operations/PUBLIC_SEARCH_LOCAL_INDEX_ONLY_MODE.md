# Public Search Local-Index-Only Mode

Status: implemented as policy and contract text only.

`local_index_only` is the first allowed public search execution mode. It is a
future runtime mode, not a current hosted API. The mode exists so later route
work has a governed boundary before implementation starts.

## Allowed Shape

Future `local_index_only` search may:

- accept a bounded public query with a 160 character maximum;
- use a controlled local index owned by the future public-search runtime;
- return at most 25 results in contract v0, defaulting to 10;
- expose result lanes, user-cost hints, compatibility summaries, evidence
  summaries, source summaries, warnings, and bounded absence reports;
- emit result cards governed by Public Search Result Card Contract v0 only after
  a future runtime implements them;
- produce `standard_web`, `lite_html`, `text`, and `api_client` projections;
- return the stable error envelope defined by Public Search API Contract v0.

The mode may read only governed public/local-index records selected by the
future runtime milestone. It must not accept caller-provided index roots, store
roots, local filesystem paths, URLs, credentials, uploaded files, or source
secrets.

## Explicitly Forbidden In v0

`local_index_only` does not allow:

- live external calls;
- live Internet Archive, Wayback, Google, GitHub, package-registry, or search
  engine queries;
- arbitrary URL fetch;
- scraping, crawling, or source fanout;
- local path search or private file ingestion;
- downloads, executable mirrors, installer handoff, or package-manager handoff;
- uploads, accounts, telemetry, cloud sync, auth credentials, or private user
  state;
- executable trust claims, rights-clearance claims, or malware-scan claims;
- production API stability or production readiness claims.

## Error And Safety Expectations

Invalid queries should use `query_required` or `query_too_long`. Unsupported
modes, profiles, and include values should use the corresponding unsupported
error codes. Forbidden fields should use `forbidden_parameter` or the more
specific `local_paths_forbidden`, `downloads_disabled`, `installs_disabled`,
`uploads_disabled`, or `live_probes_disabled` codes.

The future Public Search Safety / Abuse Guard v0 milestone must define runtime
controls before the contract is hosted. This policy does not implement rate
limiting, TLS, auth, abuse detection, process management, logging, or runtime
deployment.

## Privacy And Logging Notes

Future public search logs must avoid private local paths, credentials, uploaded
payloads, user files, raw source payloads, and account identifiers. Query
logging remains a future policy decision and must be bounded/redacted before any
hosted use. Static GitHub Pages publication remains separate from hosted backend
runtime evidence.

## Relationship To Other Surfaces

Static `site/dist` remains the active publication artifact and does not host
live search. Public data, lite, text, files, and demo surfaces may describe the
future contract, but they must not claim that public search is live. Native
clients, relay surfaces, and snapshots may consume future stable fields only
after their own contracts allow it.
