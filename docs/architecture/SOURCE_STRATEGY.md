# Source Strategy

Eureka should grow through governed source families rather than one-off
connector additions with hidden semantics.

## Adapter Families

Important source families include:

- structured live web
- repository harvest and sync surfaces
- digitized cultural and document collections
- web archives and replay systems
- software identity and package ecosystems
- public records and official data
- community and long-tail archives
- local files and local preserved material

## Source Roles

Each source should be understood through one or more roles:

- authority
- preservation anchor
- discovery surface
- verification overlay
- action provider
- sync provider
- community mirror

## Source Surfaces

Each source may expose different usable surfaces:

- search
- item record
- artifact download
- bulk export
- delta or change feed
- replay
- metadata-only

## Why Source Registry v0 Is Next

The repo already has:

- a governed synthetic connector family
- a bounded GitHub Releases recorded-fixture connector family

The next backend step should not be "add another connector first." It should be
to define a governed source registry so future connector work lands within one
consistent model for roles, surfaces, trust lanes, protocols, rights notes, and
freshness expectations.

## Immediate Seed Candidates

The first registry seed set should likely include:

- synthetic fixtures
- GitHub Releases
- Internet Archive placeholder
- Wayback or Memento placeholder
- Software Heritage placeholder
- local files placeholder
