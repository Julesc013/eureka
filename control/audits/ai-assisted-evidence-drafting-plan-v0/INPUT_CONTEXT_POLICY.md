# Input Context Policy

Public-safe contexts include public result cards, public source summaries,
public evidence summaries, evidence-policy-compliant snippets, static demo
records, synthetic fixtures, and public-safe pack records.

Restricted contexts include local staged pack manifests, local-private source
or evidence packs, local cache metadata, user notes, local file metadata, and
user-selected private snippets. Restricted contexts require local/private mode
by default.

Remote providers must not receive private local paths, credential values, raw
private files, raw local caches, long copyrighted text, executable payloads,
unredacted user search history, or unreviewed private source records by
default.
