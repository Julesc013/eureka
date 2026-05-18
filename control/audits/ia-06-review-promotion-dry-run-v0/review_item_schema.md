# Review Item Schema

Review items retain:

- candidate id and kind
- source-cache ids
- evidence ids
- observation ids
- source locator
- provenance
- uncertainty, limitations, rights flags, and risk flags
- suggested decision

Required invariants:

- review is required
- accepted truth is false
- raw response committed is false
- reviewed-index mutation is false
- master-index mutation is false

