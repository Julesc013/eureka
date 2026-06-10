# Operator Instructions

Collection mode:

```text
external_manual_evidence_collection
```

Allowed:

- collect compact source-reference summaries
- record source title, URL, publisher/source family, observed evidence fields, and collection date
- record checksums or signatures as text metadata when they are available from source references
- record whether a target remains unresolved

Forbidden in this handoff:

- executable binary downloads
- installer execution
- archive extraction
- emulation
- malware safety claims
- rights-clearance claims
- public artifact availability claims
- repo-local raw HTML dumps, screenshots, binaries, private caches, or logs

Preferred external output root:

```text
../eureka-evidence-runs/artifact_evidence_collection_00/
```

Return only the compact summary JSON to the AI session unless targeted excerpts are requested later.
