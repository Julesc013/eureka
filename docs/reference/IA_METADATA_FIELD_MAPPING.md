# IA Metadata Field Mapping

This reference is a policy mapping, not a runtime connector schema.

| IA metadata field class | Future Eureka use | Boundary |
| --- | --- | --- |
| identifier | source locator candidate | Not accepted identity without review |
| title | title claim candidate | Source-provided only |
| mediatype | mediatype claim candidate | Not compatibility or safety truth |
| creator | creator claim candidate | Only if present |
| date | date claim candidate | Only if present |
| description | description claim candidate | Source-provided text, not verified fact |
| files.name | file-list claim candidate | No item file fetch |
| files.size | file metadata candidate | Not availability proof |
| files.format | format metadata candidate | Not compatibility truth |
| files.md5 / crc32 / sha1 | checksum/file metadata candidate | Not local artifact verification unless later reviewed |

All field mappings remain candidates until review. IA-00 performs no source-cache
writes, evidence writes, index mutation, or live calls.

IA-01 fixture replay uses these mappings only against committed fixtures. Its
normalized records remain source-observation candidates and always require
review.

IA-02 may use these mappings against an approved, tiny live metadata response,
but only to produce redacted source-observation candidate previews. The current
IA-02 live attempt did not obtain a response body, so no live field mapping was
performed.

IA-03 writes mapped fixture/live-preview observations into the source cache.
IA-04 converts source-cache fields into evidence claim candidates. IA-05 groups
those evidence candidates into provisional candidate-index records for review.
None of these stages creates accepted truth, reviewed records, download proof,
rights clearance, compatibility truth, safety truth, or master-index truth.
