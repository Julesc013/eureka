# Search Hunt Track

HUNT-00 inserts the planning spine. HUNT-01 persists sessions, HUNT-02 exposes workbench state, HUNT-03 adds pause/resume/cancel/steer commands, HUNT-04 produces exhaustion reports, HUNT-05 and HUNT-06 feed SearchNeed and WorkUnit paths, and later tasks add deterministic replay and disabled-by-default AI gates.

After HUNT-02, the current proof is durable session storage plus read-only workbench/API visibility. Steering semantics, WorkUnit creation, background runners, source probes, SYN, F0 extraction, and AI escalation remain later work.

After HUNT-03, pause/resume/cancel/block/wait commands and steering preferences are available through the CLI, local JSON API, and local workbench controls. The command layer remains a control surface only: WorkUnit creation waits for HUNT-06, source probes remain behind future source gates, and AI/model providers remain disabled.

After HUNT-04, exhaustion reports are available through CLI, local JSON API, and the workbench. They explain local checked/deferred state and recommend future categories, but HUNT-05 is still required before durable SearchNeed generation exists.
## HUNT-05 Result

HUNT-05 adds durable SearchNeeds and the hunt-to-SearchNeed pipeline. The next recommended task is HUNT-06, which may add the separate Hunt-to-WorkUnit pipeline.

Current boundary remains: no WorkUnit creation, source probes, extraction execution, model/provider calls, review mutation, public/master index mutation, deployment, production readiness claim, or public launch readiness claim.
## HUNT-06 Status

HUNT-06 adds the Hunt-to-WorkUnit pipeline. HUNT-07 remains next for background runner integration. F0 stays deferred, and SYN remains the alternative/follow-up planning track.

## HUNT-07 Status

HUNT-07 adds a background hunt runner over deterministic local workers. The next recommended task is HUNT-08 for full workbench integration and smoke tests.

Current boundary remains: no source probes, extraction, agent research, model/provider calls, acquisition actions, LAN worker mutation, deployment, review mutation, master index mutation, production readiness claim, or public launch readiness claim.
## HUNT-08 Result

HUNT-08 adds integrated workflow, workbench, and API smoke scripts for the local Search Hunt loop. The next recommended task is HUNT-09, the agent research task contract with providers disabled; SYN remains an alternative/follow-up and F0 remains deferred.
