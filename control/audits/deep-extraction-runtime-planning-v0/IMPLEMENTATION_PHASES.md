# Implementation Phases

Phase 0:

- keep runtime disabled
- complete planning and validation

Phase 1:

- local dry-run request/report builder over synthetic examples only
- no file opening or unpacking

Phase 2:

- local fixture-only metadata detector with prebuilt synthetic fixture files
- no arbitrary paths
- no recursion
- no mutation

Phase 3:

- sandboxed local Tier 0/Tier 1 extraction for approved fixtures
- strict resource limits
- no public search integration

Phase 4:

- sandboxed local Tier 2/Tier 3 extraction
- manifest/text summaries only
- no OCR/transcription runtime unless separately approved

Phase 5:

- source-cache/evidence-ledger candidate effect reporting
- still no authoritative writes

Phase 6:

- extraction integration with pack/page/search systems only after separate approval

