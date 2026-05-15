# AI Escalation Disabled Boundary

HUNT-11 adds gate and preflight records only.

Disabled boundaries:

- provider/model calls
- browser calls
- source probes
- extraction
- artifact acquisition
- artifact runtime actions
- review decisions
- public index mutation
- master index mutation
- site output writes
- deployment

Preflight may write a local record showing eligibility and missing requirements. It must not run future research work.
