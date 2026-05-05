# Failure And Error Model

Bounded error classes:

- invalid JSON
- missing required fields
- unsupported source family
- unsupported record kind
- private path detected
- URL-like value detected
- live source parameter rejected
- secret-like field detected
- output path rejected
- strict-mode failure
- non-strict warning

Errors identify the field or policy class and avoid private payload dumps.
