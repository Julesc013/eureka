# Artifact Identity Evidence Checklist

Use this checklist for identity evidence in the compact return. It helps a
human reviewer decide whether an observation supports an artifact identity
claim. It does not create reviewed truth by itself.

## Minimum Useful Fields

- collection target id
- source reference id
- artifact title or package name
- version, edition, release, or exact variant when relevant
- publisher, vendor, project, issue, or parent source identity
- platform, OS, device family, or compatibility context when relevant
- page, member, package, release asset, or catalog scope when relevant
- observed locator or citation
- remaining ambiguity

## Identity Level Guidance

| Level | Meaning |
|---|---|
| `level0_mention_only` | A mention exists, but it does not identify a concrete artifact. |
| `level1_metadata_or_source_lead` | Metadata suggests a possible artifact or source lead. |
| `level2_source_observed_artifact_listing` | A source visibly lists a likely artifact. |
| `level3_artifact_identity_evidence` | Evidence supports a concrete artifact identity or exact variant. |
| `level4_artifact_integrity_evidence` | Identity is paired with checksum, signature, or equivalent integrity reference. |
| `level5_verified_acquisition_or_reproducibility_path` | A reviewed policy supports acquisition or reproducibility evidence. |

## Do Not Inflate

- Do not turn a source lead into a reviewed artifact record.
- Do not turn a reviewed artifact record into a verified artifact.
- Do not treat a package name without exact variant evidence as exact identity.
- Do not treat AI/model text, synthetic fixtures, or old chat summaries as
  artifact evidence.
