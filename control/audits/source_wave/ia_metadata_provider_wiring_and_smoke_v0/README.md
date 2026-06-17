# IA Metadata Provider Wiring And Smoke v0

Task: `IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00`

This audit packet records the bounded Internet Archive metadata smoke path for
local operator validation. It ties the existing IA metadata provider path into
the governed local source-action/index flow as dry-run evidence: source
observations, evidence summaries, provisional candidates, candidate-index delta
status, and review previews.

The tracked smoke report records fixture-backed execution plus a flag-gated
small live metadata probe. The live probe records only redacted preview status;
it does not commit raw responses or create accepted truth.

## Evidence

- `SMOKE_RESULTS.md` summarizes the smoke result and safety flags.
- `ia_metadata_provider_smoke_report.json` is the structured smoke report.

## Boundaries

- source observations are not reviewed truth
- metadata is evidence support, not verified artifact truth
- provisional candidates are not reviewed records
- candidate-index delta is dry-run only
- no public live fanout
- no public mutation
- no downloads
- no file fetching
- no Wayback replay
- no rights, safety, malware, or authenticity claims
- no reviewed, public, or master-index mutation
- public-alpha posture is unchanged
- license posture is unchanged

## Reproduction

Fixture-only local smoke:

```powershell
python scripts/eureka_ia_metadata_smoke.py --mode fixture --json
```

Optional bounded live metadata smoke requires explicit operator opt-in:

```powershell
python scripts/eureka_ia_metadata_smoke.py --mode fixture-and-live --allow-live-metadata --json
```

Full unittest discovery is not claimed by this packet.
