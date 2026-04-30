# Provenance And Claim Model

Imported records remain claims, candidates, summaries, or review inputs. They
do not become canonical truth by being imported.

Future import provenance must preserve:

- pack type
- pack ID
- pack version
- manifest schema version
- checksum digest
- validation command and validator version or script path
- validation report ID
- source/evidence/index/contribution record IDs
- privacy, rights, and risk classifications
- limitations and review notes

Conflicting claims must be preserved as conflicts. A later review step may
compare claims, but import must not destructively merge identities,
compatibility statements, member paths, absence observations, aliases, or index
coverage summaries.

AI-generated suggestions, if added in a later milestone, remain suggestions.
They need provenance and evidence before they can become public review
candidates.

