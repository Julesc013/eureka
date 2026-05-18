# Internet Archive Metadata Fixture Replay

These fixtures are deterministic local inputs for IA-01. They are not live
Internet Archive responses and they do not contain downloaded file contents.

The fixture replay lane proves that Eureka can parse, normalize, and
boundary-check representative metadata shapes before any future operator-
approved live metadata probe.

Run:

```powershell
python scripts/eureka_ia_fixture_replay.py --fixture-dir examples/internet_archive_metadata --json
python scripts/validate_ia_fixture_replay.py
```

Boundaries:

- no live IA calls
- no source probes
- no source-cache writes
- no evidence writes
- no candidate, reviewed, or master index mutation
- no downloads/uploads
- no public fanout
- no production/public launch claim
