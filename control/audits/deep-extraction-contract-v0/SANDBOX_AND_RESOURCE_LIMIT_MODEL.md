# Sandbox And Resource Limit Model

Runtime extraction is blocked until a sandbox policy exists and is approved.

Required future sandbox posture:

- network disabled
- execution disabled
- filesystem scope limited
- temporary workspace required
- cleanup required
- resource limits enforced
- no arbitrary local path scanning
- no arbitrary URL fetching
- no source/evidence/candidate/index mutation during extraction

Without this policy, extraction runtime remains blocked.
