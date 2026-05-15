# Search Hunt Track

HUNT-00 inserts the planning spine. HUNT-01 persists sessions, HUNT-02 exposes workbench state, HUNT-03 adds pause/resume/cancel/steer commands, HUNT-04 produces exhaustion reports, HUNT-05 and HUNT-06 feed SearchNeed and WorkUnit paths, and later tasks add deterministic replay and disabled-by-default AI gates.

After HUNT-02, the current proof is durable session storage plus read-only workbench/API visibility. Steering semantics, WorkUnit creation, background runners, source probes, SYN, F0 extraction, and AI escalation remain later work.

After HUNT-03, pause/resume/cancel/block/wait commands and steering preferences are available through the CLI, local JSON API, and local workbench controls. The command layer remains a control surface only: WorkUnit creation waits for HUNT-06, source probes remain behind future source gates, and AI/model providers remain disabled.

After HUNT-04, exhaustion reports are available through CLI, local JSON API, and the workbench. They explain local checked/deferred state and recommend future categories, but HUNT-05 is still required before durable SearchNeed generation exists.
