# Bounded Member Access

This package holds Eureka's first bounded member-readback / preview seam.

Scope in this slice:

- build on the existing acquisition and decomposition seams
- support reading ZIP members from fixture-backed payloads
- return compact metadata plus a short text preview when the member is text-like
- return explicit `unsupported`, `unavailable`, or `blocked` results for everything else

Out of scope in this slice:

- general extraction frameworks
- writing members to disk by default
- broad archive or document format coverage
- installers, importers, or execution

This is a bootstrap seam proving that Eureka can move from:

`representation -> member list -> chosen member -> bounded readback`

without committing to a final package-management or extraction architecture.

Member-Level Synthetic Records v0 may project member target refs and parent
lineage that point back to these existing bounded readback paths. The readback
scope remains explicit `target_ref + representation_id + member_path` requests
against fixture-backed ZIP payloads; it is not broad extraction or arbitrary
local filesystem access.
