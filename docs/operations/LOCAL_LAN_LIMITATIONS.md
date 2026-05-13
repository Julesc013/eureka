# Local LAN Limitations

LOCAL-12 is local appliance evidence only.

It does not prove public hosting, deployment, TLS posture, router/firewall
configuration, UPnP/NAT behavior, production readiness, or public launch
readiness.

Same-machine LAN-bind smoke proves that the server can bind with explicit
`--bind-lan` and serve read-only routes. It does not prove another device can
reach the service unless external-client evidence is recorded separately.

LAN clients remain read-only. Review decisions, rebuilds, WorkUnit execution,
source probes, extraction, agents, downloads, install/execute actions, config
mutation, `site/dist` writes, and master-index mutation remain blocked.
