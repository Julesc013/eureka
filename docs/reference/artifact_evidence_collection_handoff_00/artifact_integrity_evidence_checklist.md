# Artifact Integrity Evidence Checklist

Integrity evidence is stricter than identity evidence. Use this checklist only
when the external collector observed source-backed checksums, signatures, or
equivalent integrity metadata.

## Acceptable Integrity References

- source-published checksum with algorithm and value
- source-published signature reference
- release manifest that binds the artifact name and version to a digest
- archive item metadata that names a file and digest
- package registry integrity metadata from the source reference

## Required Fields

- source reference id
- artifact identity fields
- checksum or signature type
- checksum or signature value, if observed
- source locator for the integrity metadata
- observed date
- limitations or mismatch notes

## Not Enough

These are not integrity evidence by themselves:

- filename only
- size only
- user memory
- unreviewed mirror listing
- search result snippet
- AI/model summary
- local private file path

## Boundary

Integrity evidence does not authorize download, execution, installation,
malware safety claims, rights clearance, or verified artifact status unless a
future reviewed policy explicitly gates those claims.
