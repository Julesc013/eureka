# Quarantine Staging And Inspection Flow

- Quarantine root is explicit operator-approved path, not user-controlled request param.
- Staging paths are deterministic and bounded.
- Pack content is copied or referenced according to policy.
- No execution.
- No URL fetching.
- No decompression bombs without future extraction policy.
- Staged-pack inspector reads metadata/reports only.
- Stage can be discarded without mutation.
- Staged reports are auditable.
