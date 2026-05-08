# Source Cache To Evidence Ledger Bridge Plan

The source-cache-to-evidence bridge is a future reviewed conversion from
source-cache observations into evidence candidates and provenance links. B-14
does not implement the bridge.

## Current Status

- Bridge phase: `bridge_phase_0_planning_only`
- Bridge runtime: not implemented
- Review before bridge: required
- Truth conversion: forbidden
- Master-index mutation: forbidden

## Allowed Future Inputs

Future bridge inputs may include reviewed source-cache fixture records, source
metadata records, source locator records, source policy records, source health
records, source coverage records, and source lead records.

Each bridge input should carry source-cache ref, source locator or source ref,
source policy posture, provenance summary, privacy posture, rights/risk posture,
limitations, and review status.

## Future Outputs

Future outputs are evidence candidates and provenance records only:

- source observation
- source-cache-derived claim
- metadata claim
- identity claim
- compatibility claim
- checksum claim
- filename/member claim
- source locator
- provenance link
- conflict record

## Forbidden Conversions

- source-cache record to accepted evidence
- source observation to accepted truth
- evidence candidate to verified fact
- AI draft to evidence truth
- contribution claim to accepted public record
- metadata claim to rights clearance
- checksum claim to authenticity proof without evidence
- compatibility claim to verified compatibility without review

## Review And Conflict Rules

Bridge output must preserve conflicts, uncertainty, provenance, source locator
context when available, review state, rights/risk posture, and limitations.

The bridge cannot promote a candidate, export a pack, update public search,
mutate a local index, or mutate the master index. Those require later reviewed
tasks and validators.
