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

## Source Registry v0 Now Exists

The repo already has:

- a governed synthetic connector family
- a bounded GitHub Releases recorded-fixture connector family

Source Registry v0 is now implemented through:

- draft schemas under `contracts/source_registry/`
- governed seed records under `control/inventory/sources/`
- stdlib-only runtime loading under `runtime/source_registry/`
- bounded public projection through current web, CLI, and local HTTP API surfaces

That means future connector work can land within one consistent model for
roles, surfaces, trust lanes, protocols, rights notes, and freshness
expectations without pretending placeholder sources are already implemented.

## Current Seed Set

The current registry seed set includes:

- synthetic fixtures
- GitHub Releases recorded fixtures
- Internet Archive placeholder
- Wayback or Memento placeholder
- Software Heritage placeholder
- local files placeholder

## Immediate Follow-On Work

Now that source inventory is explicit, the next backend step should be to add a
bounded Resolution Run Model v0 rather than broadening connector coverage first.
