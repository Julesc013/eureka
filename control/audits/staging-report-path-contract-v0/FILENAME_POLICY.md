# Filename Policy

Future report filenames should use filesystem-safe components:

- sanitized pack ID
- short SHA-256 checksum
- mode
- timestamp or run ID

Recommended future pattern:

```text
import-report__<pack_id_sanitized>__<short_sha256>__<mode>.json
```

Filenames must not include raw local paths, raw user query text, full source
URLs, credentials, secrets, API keys, or path separators from pack IDs.

Machine-readable reports use `.json`. Future human summaries may use `.txt` or
`.md`.
