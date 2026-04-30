# Native, Snapshot, And Relay Impact

P39 does not implement native clients, snapshot readers, relay runtime, or
pack import.

Future native clients may import packs only into private local staging and must
follow the Local Cache Privacy Policy. A native client must not expose private
staged packs through public search, old-client file-tree surfaces, or sync
features by default.

Future snapshots may include pack-derived records only after the records become
reviewed public records through a separate review and publication path.

Future relay clients must not expose private staged packs by default. Relay
support needs separate review of privacy, authorization, public fields, and
hosted/public data boundaries before it can touch pack-derived records.

