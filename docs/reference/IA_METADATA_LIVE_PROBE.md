# IA Metadata Live Probe

IA-02 defines the first bounded Internet Archive metadata-only live probe. It is
not a connector rollout and it does not make IA metadata Eureka truth.

## Scope

Allowed only with explicit operator approval:

- one `metadata_search_small` request to `archive.org`
- at most one row
- at most one exact `item_metadata_read` if the search returns a safe identifier
- JSON metadata only
- redacted summary and boundary report only

Still forbidden:

- downloads or item file fetches
- uploads or write APIs
- authenticated APIs
- Wayback replay
- page scraping or arbitrary URL fetch
- public query fanout
- source-cache writes
- evidence writes
- candidate, reviewed, or master index mutation

## Required Controls

- `--approve-live` must be supplied for network access.
- User-Agent and contact must be present.
- The kill switch is checked before every live request.
- Total request and row caps are enforced before network access.
- Retry-After is represented as backoff state, not hammered retries.
- Raw live response bodies must not be committed.

## IA-02 Result

The IA-02 implementation and dry-run validation passed. The approved live
attempt was made once under policy, but the local Python TLS trust store rejected
the connection with `ssl_certificate_verify_failed` before an IA HTTP response
was available.

That result is partial. No live metadata was normalized into candidate previews
because no IA response body was obtained.

IA-02-TLS-TRUST-01 then diagnosed the machine TLS state. Python verification and
hostname checking are enabled, but `archive.org` still fails a verified TLS
handshake with `self_signed_certificate_in_chain`. The local Python OpenSSL
default CA file and capath do not exist, and no insecure bypass was used.

IA-02-TLS-TRUST-CONTINUE resolved the local trust path for the current shell by
using an existing local CA bundle via `SSL_CERT_FILE`. TLS verification and
hostname checking remained enabled. The approved metadata-only live probe then
succeeded with:

- `metadata_search_small`
- `item_metadata_read`
- total HTTP requests: 2
- raw response committed: false
- source-cache/evidence/index mutation: false

## Handoff

IA-03 has proceeded with the source-cache write path using the successful
redacted response summary, normalized preview, and boundary report from
IA-02-TLS-TRUST-CONTINUE. IA-03 writes only source-cache observation records to
an explicit temporary/local instance and still does not write evidence or mutate
indexes.

IA-04 is the next gate for evidence-ledger integration.
