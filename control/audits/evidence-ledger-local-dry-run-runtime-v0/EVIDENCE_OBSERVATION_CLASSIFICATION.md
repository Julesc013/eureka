# Evidence Observation Classification

The dry-run classifier uses conservative dimensions:

- `evidence_kind`: source metadata, availability, capture presence/absence,
  release metadata, package metadata, software identity, compatibility,
  file listing, scoped absence, conflict, or unknown.
- `claim_kind`: metadata, availability, identity, version, compatibility,
  source presence, scoped absence, conflict, or unknown.
- `source_family`: Internet Archive, Wayback/CDX/Memento, GitHub Releases,
  PyPI, npm, Software Heritage, local fixture, or unknown.
- `provenance_status`: synthetic example, fixture-backed, recorded fixture,
  source-cache candidate/future, manual observation future, or unknown.
- `review_status`: structurally valid, review required, policy review
  required, conflict review required, rejected, or unknown.
- `privacy_status`: public-safe, redacted, local-private, rejected-sensitive,
  or unknown.
- `rights_risk_status`: metadata-only, source terms apply, review required,
  executable reference, malware review required, restricted, or unknown.
- `promotion_readiness`: not ready, review required, future candidate-ready,
  rejected, or unknown.

Unknown or unsupported values are invalid in strict dry-run candidates.
