# Source Registry Schema

The source registry should become the governed control plane for connector
growth. It should describe what a source is allowed to claim about itself before
runtime code turns that source into resolver behavior.

## Purpose

The registry should answer questions such as:

- what kind of source is this
- what roles does it play
- what surfaces does it expose
- what identifiers does it emit
- what kinds of artifacts or objects does it speak about
- what trust lane and authority class should apply
- what freshness, legal, or extraction caveats matter

## Draft Field Set

The first schema should likely include fields such as:

- source id
- display name
- source family
- roles
- surfaces
- trust lane
- authority class
- protocols
- object types
- artifact types
- identifier types
- connector entrypoint
- extraction policy
- rights or legal notes
- health or freshness notes

## Seed Candidates

The first governed seed records should likely cover:

- synthetic fixtures
- GitHub Releases
- Internet Archive placeholder
- Wayback or Memento placeholder
- Software Heritage placeholder
- local files placeholder

## Status

Source Registry v0 is accepted as the next implementation milestone, but the
schema and runtime implementation are not yet present.
