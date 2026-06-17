# IA Candidate Index Refresh v0

Task: `IA-CANDIDATE-INDEX-REFRESH-00`

This audit packet records the governed local candidate-index refresh delta
generated from the completed IA source-observation cache delta.

## Evidence

- `CANDIDATE_INDEX_REFRESH.md` summarizes the delta result.
- `candidate_index_refresh_report.json` is the structured audit report.
- Generated local artifacts were written under
  `.eureka/source-wave/ia-metadata/candidate-index/latest/`.

## Boundary

- candidates are provisional and unreviewed
- candidates are not reviewed truth
- evidence-ledger materialization was not performed
- review or promotion was not performed
- reviewed/master mutation remained false
- public-index mutation remained false
- candidate-index store mutation remained false
- public exposure remained paused
- downloads, file fetches, and Wayback replay remained false
- license posture remained unchanged

Full unittest discovery is not claimed by this packet.
