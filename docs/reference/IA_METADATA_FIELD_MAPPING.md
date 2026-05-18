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
