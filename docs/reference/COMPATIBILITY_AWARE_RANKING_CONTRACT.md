# Compatibility-Aware Ranking Contract v0

This is a contract-only definition for future compatibility-aware ranking. Compatibility-aware ranking is not runtime yet. Compatibility-aware ranking is not compatibility truth, is not installability proof, is not dependency safety proof, and is not malware safety or rights clearance.

Compatibility-aware ranking does not launch emulators/VMs or package managers. It does not enable downloads, installs, execution, uploads, mirroring, arbitrary URL fetch, package manager invocation, emulator launch, or VM launch.

## Compatibility Target Profile

The compatibility target profile model records a public-safe target environment: platform, OS/version, architecture, CPU, ABI/API, runtime dependencies, hardware/peripheral/driver needs, emulator/VM/reconstruction goals, and safe action preferences. It is not a local machine fingerprint and it does not track users.

## Matching Models

The platform/OS/version model distinguishes exact match, compatible range, likely compatible, unknown, likely incompatible, incompatible, and conflicting. The architecture/CPU/ABI/API model is separate from the runtime/dependency model and the hardware/peripheral/driver model.

The emulator/VM/reconstruction feasibility model is evidence-gated and launch-disabled. Feasibility is not proof that software will run.

## Evidence And Gaps

Compatibility evidence strength is stronger than platform-name similarity, but compatibility evidence is not truth. Platform name match alone is weak. Package metadata is not dependency resolution. Absence of evidence is not incompatibility unless explicitly scoped and evidenced.

Unknown and incompatibility gaps remain visible. Conflicts must not be hidden and incompatible or unknown results must not be suppressed without explanation.

## Caution And Actions

Source/provenance/candidate caution is required: source trust is not claimed, provenance is not truth, and candidate confidence is not compatibility truth. Action safety/installability caution requires installability evidence before any installability claim. Rights/risk caution makes no rights clearance, malware safety, or dependency safety claim.

## Tie Breaks And Projection

Tie-break policy preserves current order in v0, forbids random tie breaks, and keeps future compatibility-evidence tie-breaks deterministic. Public projection is future-only: result-card badges, result groups, object pages, source pages, comparison pages, and public search API responses may later include user-visible compatibility explanations with no numeric score in v0.

## Boundaries

No runtime ranking, no public search order change, no hidden suppression, no popularity/telemetry/ad/user-profile ranking, no model call, no candidate promotion, no source cache mutation, no evidence ledger mutation, no candidate index mutation, no public/local/runtime/master index mutation, no connector execution, and no live source calls are implemented. No mutation is performed by this contract.

## Relationships

P85 builds on evidence-weighted ranking, result merge/deduplication, cross-source identity resolution, object pages, source pages, comparison pages, public search result cards, public index contracts, source cache/evidence ledger contracts, candidate index, and promotion policy. Future runtime planning remains gated by hosted deployment evidence, eval evidence, compatibility evidence packs, and explicit approval.
