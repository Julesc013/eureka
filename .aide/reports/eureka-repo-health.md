# Eureka Repo Health

Updated: 2026-05-18

Current recommended task: IA-02 — IA Local Live Metadata Probe.

Last completed task: IA-02 - IA Local Live Metadata Probe.

Status: partial. The preferred local instance path remains `../instances/default`,
with legacy sibling `../eureka-instance` explicit-only. IA-02 added the bounded
metadata-only live-probe policy, transport, runtime, CLI, validator, tests, docs,
inventories, and audit evidence.

The targeted broad subset still has 10 unrelated broad-lane validator failures
from the instance-layout clean-machine closeout. They do not block PLAY-02.

One approved IA metadata request was attempted under policy. It failed before
an IA HTTP response was available because the local Python TLS trust store
reported `ssl_certificate_verify_failed`.

No raw response body, source-cache write, evidence write, index mutation,
extraction, model/provider call, download, upload, public fanout, deployment,
production readiness claim, or public launch readiness claim occurred. IA-03 is
blocked until IA-02 has a successful approved live response summary and boundary
report.
