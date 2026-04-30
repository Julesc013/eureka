# Native, Relay, And Snapshot Impact

Future native clients may offer a local staging UI. Native staging remains
private by default and must use app-local or user-selected roots.

Relay must not expose staged data by default. Old-client projections must not
include staged private data, private paths, credentials, or staged user
history.

Snapshots exclude staged/private data by default. Any public-safe export must
pass pack/report validation and privacy review.
