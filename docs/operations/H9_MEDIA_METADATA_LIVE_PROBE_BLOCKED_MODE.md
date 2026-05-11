# H9 Media Metadata Live Probe Blocked Mode

Missing approvals produce BLOCKED reports with request_count 0 and network_used false. Blocked mode is the expected current posture.

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
