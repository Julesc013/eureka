# H9 Media Metadata Live Probe

The live-probe envelope is a controlled metadata observation plan. Default mode is offline preflight; no source call occurs unless a future committed source policy approves one exact metadata-only request.

## Boundary

- metadata only
- no broad media/music/image/video/map search
- no public query fanout
- no API or catalog query without exact future committed approval
- no media downloads, uploads, thumbnail fetches, fingerprint submission, or fingerprint generation
- no scraping, crawling, browser automation, bypass, or restricted-source access
- no source cache, evidence ledger, review queue, public index, or master index mutation
- no media authenticity, music identity, rights clearance, public-domain, Creative Commons, content safety, privacy safety, malware safety, authenticity, or production coverage claim

## Validation

Run:

```powershell
python scripts/validate_h9_media_metadata_live_probe.py
python scripts/run_h9_media_metadata_live_probe.py --source-id musicbrainz --request-key example_recording_metadata --check
python scripts/summarize_h9_media_metadata_live_probe_outputs.py --input examples/connectors/h9_media_metadata/live_probe_results --check
```
