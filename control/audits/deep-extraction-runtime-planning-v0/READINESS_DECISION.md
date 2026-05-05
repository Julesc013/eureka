# Readiness Decision

Readiness decision: `blocked_resource_limit_policy_missing`.

Reason:

- Deep Extraction Contract v0 exists.
- Synthetic extraction examples exist.
- Contract validators exist.
- Privacy/path/secret, executable payload, OCR/transcription, no-runtime, and
  mutation-boundary policy documents exist.
- Sandbox requirements are documented, but no sandbox runtime is implemented.
- Resource-limit policy still contains operator-defined future values for member
  size and total uncompressed size.
- Operator approval for sandbox/resource/payload policy is not recorded.

Planning can proceed. Runtime implementation must remain blocked until concrete
resource limits, sandbox policy approval, and operator approval are recorded.

