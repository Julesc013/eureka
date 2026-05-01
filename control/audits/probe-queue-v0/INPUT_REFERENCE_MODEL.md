# Input Reference Model

Probe queue items may reference query observations, shared result cache entries,
search miss ledger entries, search need records, and future reviewed manual or
pack refs.

Refs are references only. P63 does not consume runtime observations, create
queue entries from public search, or mutate referenced records.
