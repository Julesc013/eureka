# Snapshot Local Apply Section

Schema: `contracts/snapshot/snapshot_local_apply_section.v0.json`

The local apply section summarizes the temp explicit instance proof used by `SNAPSHOT-REFRESH-03`.

It records:

- eligible preview count
- reviewed metadata records created
- reviewed source leads created
- reviewed record delta count
- non-applied useful leads, needs-more-evidence candidates, and rejected/duplicate candidates
- operator/public/master mutation flags

All mutation flags remain false.
