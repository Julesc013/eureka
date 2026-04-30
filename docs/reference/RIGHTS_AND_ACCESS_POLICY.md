# Rights And Access Policy

Rights And Access Policy v0 defines the caution language Eureka must use
around source metadata, public indexing, artifact distribution, downloads, and
mirrors.

This is policy only. Eureka does not claim rights clearance, does not host an
executable download surface, and does not mirror software artifacts in v0.

## Core Rules

- Source metadata is not rights clearance.
- Indexing or describing a source does not imply permission to distribute the
  referenced artifact.
- Public pages must distinguish metadata and evidence from artifact
  distribution.
- Fixture records and snapshot seed examples are not broad mirroring rights.
- Users and operators remain responsible for source terms, licenses, and local
  law.
- Future downloads, mirrors, package-manager handoff, and relay distribution
  require rights/access review.
- Public-alpha remains read-only and metadata-first.

## Labels

Future risky actions must show a rights/access label before handoff. Valid
labels include:

- rights_unknown
- metadata_only
- fixture_only
- user_supplied_private
- source_terms_review_required
- redistribution_review_required
- operator_approved_future

Unknown is not clearance. Metadata-only is not distribution permission.

Public Search Result Card Contract v0 carries this posture through the `rights`
block. Cards may record `unknown`, `public_metadata_only`,
`source_terms_apply`, `restricted`, `review_required`, or `not_applicable`, but
they must not claim rights clearance and must not convert public metadata into a
download, mirror, or redistribution permission.

## Public Static Surfaces

Static Pages may show source summaries, eval state, route state, snapshot
format contracts, checksums, and limitations. They must not imply artifact
redistribution rights or offer executable downloads.

The file-tree surface remains a static compatibility surface for manifests,
checksums, and public summaries. It is not a software mirror.

## Future Mirrors

Any future mirror or cache behavior must define:

- allowed data classes
- rights/access review process
- source terms review
- operator signoff
- takedown/disable procedure
- private-data exclusion
- hash/signature/provenance display
- logging/privacy posture

No rights clearance claim exists in v0.
