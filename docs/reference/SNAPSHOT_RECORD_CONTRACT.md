# Snapshot Record Contract

`contracts/snapshots/snapshot_record.v0.json` defines one renderable record inside a snapshot.

Supported record types include search results, object records, source records, need records, candidate records, evidence summaries, known absence records, safe action manifests, acquisition/citation/export/preservation manifests, blocked actions, and policy-blocked records.

Each record carries source, evidence, compatibility, rights, risk, action, and limitation posture. These fields must be preserved by text, lite HTML, file-tree, and JSON manifest renderers.

Snapshot records do not create public truth or certify rights, risk, installability, or compatibility.
