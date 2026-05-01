# Miss Cause Model

Miss causes explain why the current checked scope did not produce a strong
public result.

Allowed cause types include no public index hit, low-score result, result-shape
mismatch, source not covered, placeholder source, disabled live probe, missing
connector, missing deep extraction, missing OCR, missing member enumeration,
missing compatibility evidence, exact-version gap, unknown platform support,
rights/access unknown, ambiguous query, policy block, external baseline pending,
and unknown.

Cause records may include `source_id`, `source_family`, explanation,
evidence references, and limitations. They do not include raw source payloads or
private local paths.

