# Renderer Parity Harness Contract

`contracts/representation/renderer_parity_harness.v0.json` defines the Track A harness shape for checking rendered or projected outputs against canonical view-model meaning.

The harness is semantic parity, not pixel parity. A projection may simplify layout, styling, density, icons, previews, or interaction, but it must preserve identity, source posture, evidence posture, candidate or review state, compatibility caveats, rights and risk posture, limitations, unresolved gaps, allowed actions, blocked actions, and public/static capability limits.

## Contract Shape

The contract supports:

- harness identity and status
- source view-model references
- projection output bindings
- representation profile and design profile bindings
- semantic categories
- required text markers and JSON paths
- forbidden omissions and product claims
- parity result records
- product-boundary booleans
- no-goals and notes

Parity cases are governed records. Each case names one view family, one route family, a source view-model fixture when active, output bindings, semantic requirement references, required markers, forbidden markers, allowed degradations, and expected status.

## Output Bindings

Output bindings describe a single artifact under test. Current output kinds include standard static HTML, lite HTML, text, file-tree README, and static JSON handoff. Future kinds cover HTML 3.2-ish, snapshot, relay, terminal, native-card, and print projections.

Output bindings do not create renderers or write outputs. They tell the harness what evidence already exists and which semantic checks are required.

## Product Boundary

Current Track A parity cases must keep product-boundary fields false. The harness fails active outputs that claim hosted backend behavior, live probes, source sync, source connectors, downloads, installers, execution, uploads, accounts, telemetry, master-index mutation, rights clearance, malware safety, verified installability, exhaustive global search, automatic merge or promotion, or search-engine affiliation.

## No-Goals

- No product runtime behavior change.
- No site/dist regeneration.
- No renderer implementation.
- No public route activation.
- No hosted, live-source, download, upload, account, telemetry, native, node, pack import, review runtime, or master-index mutation claim.
