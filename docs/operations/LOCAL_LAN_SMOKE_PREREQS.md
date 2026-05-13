# Local LAN Smoke Prerequisites

LOCAL-12 is expected to perform the read-only LAN smoke.

Prerequisites:

- initialize and validate an explicit local instance root
- start the service with `--bind-lan`
- show the operator/firewall warning
- use another client device when available
- verify read-only pages/API routes over LAN
- verify LAN mutation routes are blocked
- verify no source probes, WorkUnit execution, extraction, agents, downloads,
  install/execute actions, or deployment occur
- stop the server with Ctrl+C
- confirm `eureka-instance/**` remains ignored/uncommitted

If no second device is available, LOCAL-12 may record a loopback-simulated report
with the limitation stated explicitly.

LOCAL-12 records the automated run as same-machine LAN-bind smoke. External
second-client smoke was not performed in that run and remains optional evidence
for a later operator pass.
