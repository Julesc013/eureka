# Redaction Policy

Committed and public reports must redact:

- absolute local paths
- home directories
- drive letters
- usernames where possible
- credentials
- API keys
- passwords
- auth tokens
- private keys

Pack-root-relative paths are preferred. Explicit local/private reports may
include local paths only under `local_private` classification and must not be
copied into committed examples, public static output, snapshots, relay views,
contribution candidates, or master-index review records without review and
redaction.
