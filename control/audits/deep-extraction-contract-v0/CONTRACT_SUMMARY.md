# Contract Summary

Deep Extraction Contract v0 adds request, result summary, policy, and member schemas under `contracts/extraction/`.

The contract is metadata-first and public-safe:

- Requests describe a reviewed future extraction need.
- Result summaries describe member, manifest, text, OCR/transcription-hook, and safety summaries without including raw payloads.
- Policies require sandboxing, resource limits, path/privacy/secret rejection, executable-risk labels, provenance, and review before any runtime.
- Synthetic examples validate contract shape without opening archives or fabricating real extracted records.

Deep extraction is not truth, rights clearance, malware safety, installability, source completeness, or production readiness.
