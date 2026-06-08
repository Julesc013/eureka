# Artifact Record Definition

A reviewed artifact record is a reviewed decision about a specific artifact, not merely a reviewed support fact.

Minimum requirements:

- A review event exists.
- The reviewed item reaches at least `artifact_level_3_artifact_identity_evidence`.
- The identity evidence constrains the artifact name, version/date/build or edition, source/publisher context, and object type.
- Public projection does not imply download availability, install safety, malware safety, rights clearance, or reproducible acquisition unless later gates prove those claims.

A verified artifact requires `artifact_level_5_verified_acquisition_or_reproducibility_path`.

Non-qualifying records:

- reviewed support fact
- metadata lead
- source lead
- artifact lead below level 3
- candidate
- need
- near miss
- superseded duplicate support link
- synthetic eval fixture
