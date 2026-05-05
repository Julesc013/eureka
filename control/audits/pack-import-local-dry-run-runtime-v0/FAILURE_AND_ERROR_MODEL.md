# Failure And Error Model

Bounded errors include:

- missing manifest
- invalid JSON
- unknown pack kind
- missing schema version
- validator missing
- validator failure
- private path detected
- path traversal detected
- secret-like field detected
- URL fetch attempt detected
- executable/run-script claim detected
- mutation claim detected
- promotion claim detected
- output path rejected
- strict-mode failure
- non-strict warning

Errors must not include private payload dumps. Validator output excerpts are
bounded and report paths are repo-relative.
