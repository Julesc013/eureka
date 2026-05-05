# Privacy And Public Safety Review

P99 rejects or flags:

- Private paths.
- Secrets.
- Tokens.
- IP/account identifiers.
- Private URLs.
- Raw payload dumps.
- Executable payloads.

Examples are synthetic and public-safe. The dry-run does not publish anything,
does not expose private inputs, and does not create public artifacts from
operator-provided data.
