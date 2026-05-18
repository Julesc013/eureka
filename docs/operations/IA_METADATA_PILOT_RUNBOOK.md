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

Still forbidden in IA-02:

- downloads
- uploads/write APIs
- public fanout
- source-cache writes by default
- evidence writes
- candidate or reviewed index mutation

## Later Gates

IA-03 may define source-cache writes. IA-04 may define evidence candidates.
IA-05 through IA-07 may define candidate, review, and reviewed local index
integration.

No gate may convert live metadata directly into public truth.
