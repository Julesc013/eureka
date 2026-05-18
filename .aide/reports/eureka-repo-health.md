# Eureka Repo Health

Updated: 2026-05-18

Current recommended task: SYN-00 — Synthetic Query Foundry planning over Local/HUNT/PLAY/IA.

Last completed task: IA-02-TLS-TRUST-01 - Diagnose local Python TLS trust and rerun approved IA metadata probe.

Status: pass_with_warnings. The preferred local instance path remains `../instances/default`,
with legacy sibling `../eureka-instance` explicit-only. IA-02-TLS-TRUST-01 added
verified Python TLS diagnostics and validation around the IA-02 live-probe
failure.

The targeted broad subset still has 10 unrelated broad-lane validator failures
from the instance-layout clean-machine closeout. They do not block PLAY-02.

One approved IA metadata request was attempted under policy. It failed before
an IA HTTP response was available because the local Python TLS trust store
reported `ssl_certificate_verify_failed`.

The TLS diagnostic confirmed verification and hostname checking are enabled,
DNS resolution works, Python has no usable default CA file/capath here, `certifi`
is not available, and the verified handshake reports
`self_signed_certificate_in_chain`. No insecure TLS bypass was used. The
approved IA metadata probe was not rerun.

No raw response body, source-cache write, evidence write, index mutation,
extraction, model/provider call, download, upload, public fanout, deployment,
production readiness claim, or public launch readiness claim occurred. IA-03 is
blocked until IA-02 has a successful approved live response summary, normalized
preview, verified TLS success, and boundary report.
