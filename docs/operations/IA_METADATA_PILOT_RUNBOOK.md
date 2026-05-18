# IA Metadata Pilot Runbook

IA-00 does not run a pilot. This runbook records the approval sequence for a
future pilot.

## IA-00

Approve metadata-only policy with runtime disabled. Validate:

```powershell
python scripts/validate_ia_metadata_policy.py
```

No live call is allowed in IA-00.

## IA-01

Harden fixture replay before any live request:

- metadata search fixture
- exact item metadata fixture
- file-list metadata fixture
- missing item fixture
- malformed/partial fixture
- 429/Retry-After fixture
- large file-list fixture
- no-download proof

Run:

```powershell
python scripts/eureka_ia_fixture_replay.py --fixture-dir examples/internet_archive_metadata --json
python scripts/validate_ia_fixture_replay.py
```

IA-01 output is source-observation candidate material only. It is not source
truth, and it performs no live calls, downloads, source-cache writes, evidence
writes, or index mutation.

## IA-02

Only after IA-01, an operator may approve a tiny local live metadata probe. The
probe must be one-shot, row-capped, cached, kill-switch guarded, and identified
by a descriptive User-Agent with contact.

IA-02 command:

```powershell
python scripts/eureka_ia_live_metadata_probe.py --approve-live --query sampleproject --rows 1 --max-requests 2 --user-agent "EurekaLocalPilot/0.1 (metadata-only; contact: local-operator)" --contact "local-operator" --json --redacted-output control/audits/ia-02-local-live-metadata-probe-v0/generated/live_probe_redacted_summary.json --boundary-output control/audits/ia-02-local-live-metadata-probe-v0/generated/live_probe_boundary_report.json
```

The current IA-02 run is partial: the bounded live request was attempted under
policy, but local Python TLS verification failed before an IA HTTP response was
available. No raw response, source-cache write, evidence write, download, or
index mutation occurred.

Still forbidden in IA-02:

- downloads
- uploads/write APIs
- public fanout
- source-cache writes by default
- evidence writes
- candidate or reviewed index mutation

## Later Gates

IA-03 may define source-cache writes only after a successful approved IA-02
live response summary exists. IA-04 may define evidence candidates. IA-05
through IA-07 may define candidate, review, and reviewed local index integration.

No gate may convert live metadata directly into public truth.
