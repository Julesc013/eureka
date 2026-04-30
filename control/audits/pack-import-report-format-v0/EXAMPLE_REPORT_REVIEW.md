# Example Report Review

The example set is synthetic and deterministic:

- `validate_only_all_examples.passed.json` records successful validation over
  the current pack and typed-output examples.
- `validate_only_private_path.failed.json` records a blocked redacted private
  path finding.
- `validate_only_unknown_pack_type.failed.json` records an unsupported input.

All examples keep import, staging, indexing, upload, runtime mutation,
master-index mutation, and network fields false.
