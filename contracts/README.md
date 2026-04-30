# Contracts

`contracts/` holds governed assets that define shared meaning across Eureka. Bootstrap starts with archive-facing contracts first, then adds gateway public APIs, shared surface contracts, and portable pack contracts in later commits.

This tree is for governed semantics and public boundaries. It is not the place for hidden runtime coupling.

`contracts/packs/source_pack.v0.json` defines Source Pack Contract v0 for
portable source metadata and fixture-evidence bundles. It is contract and
validation only; it does not implement import, indexing, uploads, live
connectors, executable plugins, or master-index acceptance.

`contracts/master_index/` defines Master Index Review Queue Contract v0 for
future review queue manifests, entries, and decisions. It is contract and
validation only; it does not implement queue runtime, uploads, accounts,
moderation UI, hosted master-index writes, live connectors, or automatic
acceptance.
