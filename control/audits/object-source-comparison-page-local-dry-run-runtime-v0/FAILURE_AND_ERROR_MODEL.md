# Failure And Error Model

Bounded failures:

- Invalid JSON.
- Missing required fields.
- Unsupported page kind.
- Unsupported page status.
- Private path detected.
- URL or live-source parameter rejected.
- Secret-like field detected.
- Raw payload detected.
- Unsafe action claim detected.
- Output path rejected.
- Strict-mode failure.
- Non-strict warning.

Errors are bounded and do not include private payload dumps.
