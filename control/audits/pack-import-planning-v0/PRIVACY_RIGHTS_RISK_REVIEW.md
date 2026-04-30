# Privacy, Rights, And Risk Review

Future import must quarantine uncertainty instead of normalizing it away.

Required checks:

- private absolute path detection
- credentials and secrets detection
- `local_private` versus `shareable_candidate` mismatch detection
- rights/access document presence
- no malware-safety claim
- no rights-clearance claim
- no executable payloads in v0 public/shareable import
- no raw SQLite database, local cache, or arbitrary cache dump import
- no long copyrighted text dumps
- no private local filesystem tree ingestion
- quarantine on unknown privacy, rights, or executable-risk posture

Import reports may say that a pack validated structurally. They must not say
that the imported data is rights-cleared, malware-safe, canonical truth, or
accepted for the hosted/master index.

