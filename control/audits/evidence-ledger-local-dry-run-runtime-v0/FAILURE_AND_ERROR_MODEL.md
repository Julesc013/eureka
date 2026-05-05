# Failure And Error Model

Bounded errors include:

- Invalid JSON.
- Missing required fields.
- Unsupported evidence kind.
- Unsupported claim kind.
- Missing source/provenance.
- Private path detected.
- URL or live-source parameter rejected.
- Secret-like field detected.
- Truth acceptance detected.
- Promotion decision detected.
- Output path rejected.
- Strict-mode failure.
- Non-strict warning.

Errors avoid private payload dumps and remain safe for operator review.
