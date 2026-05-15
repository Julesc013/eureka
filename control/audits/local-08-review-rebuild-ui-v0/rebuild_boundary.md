# Rebuild Boundary

Rebuild reads local source cache, evidence ledger, and review queue records. It
writes only the explicit local reviewed public index store. It does not mutate
source cache input records, evidence input records, master index files,
`site/dist`, LAN state, or deployment outputs.
