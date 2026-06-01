# SNAPSHOT-REFRESH-02

`SNAPSHOT-REFRESH-02` is a projection-only refresh after live metadata candidate review.

It packages existing reviewed records, fixture candidates, live metadata candidates, review decisions, reviewed metadata record previews, reviewed source-lead previews, useful leads, needs-more-evidence decisions, rejected/duplicate decisions, needs, and absences into read-only snapshot and relay packets.

It does not apply previews as truth. Reviewed metadata/source-lead previews require a separate local-apply gate before any reviewed-index mutation.

Boundaries:

- no raw live responses
- no verified-download, malware-clean, or rights-clearance claims
- no reviewed/master/public index mutation
- no `site/dist` write
- no deployment or launch claim
