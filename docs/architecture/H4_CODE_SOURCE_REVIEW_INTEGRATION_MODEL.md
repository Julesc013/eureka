# H4 Code/Source/Release Review Integration Model

H4 review integration closes the code/source/release host wave by rehearsing
review and quality outputs from committed fixture replay results and blocked
or approved metadata-only live-probe reports. It is not promotion and it does
not change Eureka product behavior.

Inputs may include normalized code/source/release records, source identity
candidates, release identity candidates, source-to-binary relation candidates,
release asset metadata candidates, source-cache candidate previews, evidence
candidate previews, review seed previews, connector health summaries, coverage
previews, scorecards, fixture replay results, and blocked live-probe results.
If live approval is missing, blocked live-probe reports are recorded as gate
evidence only; no live evidence is invented.

Source identity, release identity, source-to-binary relation, release asset,
source-cache, evidence, and candidate promotion outputs remain candidates,
seeds, or previews. Repository metadata does not prove source authenticity.
Release metadata does not prove release authenticity. Tag, commit, SWHID,
checksum, SBOM, or signature metadata does not prove provenance, build
reproducibility, malware safety, rights clearance, installability, or
production source coverage.

H4 quality delta counts fixture, blocked, and review artifacts to measure
wave readiness. It is not production quality proof. H4 routes to H5 when the
policy, fixture, live-boundary, review, postmortem, and quality artifacts are
coherent enough for vendor, update, driver, and firmware source-family policy
packs. J1 risky actions, K semantic/AI behavior, L wider clients, and
deployment remain deferred unless explicit gates open.

No-goals: no live source calls by default, no repository clone, no source
archive download, no release asset download, no git/build/package-manager
invocation, no install, no execution, no source sync, no public/master index
mutation, no truth acceptance, no product behavior change.

Validation:

```bash
python scripts/validate_h4_code_source_review_quality_audit.py
python scripts/integrate_h4_code_source_review.py --input-dir examples/connectors/h4_code_source_release/replay_results --check
python scripts/summarize_h4_code_source_quality_delta.py --input-dir examples/connectors/h4_code_source_release/review_integration --check
python scripts/audit_h4_code_source_release_wave.py --check
```
