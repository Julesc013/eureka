# Deep Extraction Runtime Architecture Plan

Future modules only:

- `runtime/extraction/request.py`: future request validator and policy gate.
- `runtime/extraction/sandbox.py`: future sandbox/workspace manager.
- `runtime/extraction/resource_limits.py`: future depth/size/time/member guard.
- `runtime/extraction/detect.py`: future container type detector.
- `runtime/extraction/enumerate.py`: future member listing adapter.
- `runtime/extraction/manifests.py`: future manifest metadata extractor.
- `runtime/extraction/text.py`: future selective text summary extractor.
- `runtime/extraction/ocr.py`: future OCR hook adapter, disabled by default.
- `runtime/extraction/transcribe.py`: future transcription hook adapter, disabled by default.
- `runtime/extraction/normalize.py`: future extraction summary normalizer.
- `runtime/extraction/report.py`: future extraction report builder.
- `runtime/extraction/policy.py`: future privacy/executable/mutation policy guard.
- `runtime/extraction/errors.py`: future bounded error model.
- `runtime/extraction/README.md`: future runtime docs.

P105 creates none of these runtime files.

Required future flags:

- `EUREKA_DEEP_EXTRACTION_RUNTIME_ENABLED=0`
- `EUREKA_DEEP_EXTRACTION_DRY_RUN=1`
- `EUREKA_DEEP_EXTRACTION_SANDBOX_REQUIRED=1`
- `EUREKA_DEEP_EXTRACTION_NETWORK=0`
- `EUREKA_DEEP_EXTRACTION_EXECUTION=0`
- `EUREKA_DEEP_EXTRACTION_ARBITRARY_PATHS=0`
- `EUREKA_DEEP_EXTRACTION_URL_FETCH=0`
- `EUREKA_DEEP_EXTRACTION_RECURSIVE=0`
- `EUREKA_DEEP_EXTRACTION_OCR=0`
- `EUREKA_DEEP_EXTRACTION_TRANSCRIPTION=0`
- `EUREKA_DEEP_EXTRACTION_MUTATE_SOURCE_CACHE=0`
- `EUREKA_DEEP_EXTRACTION_MUTATE_EVIDENCE_LEDGER=0`
- `EUREKA_DEEP_EXTRACTION_MUTATE_CANDIDATE_INDEX=0`
- `EUREKA_DEEP_EXTRACTION_MUTATE_PUBLIC_INDEX=0`
- `EUREKA_DEEP_EXTRACTION_MUTATE_MASTER_INDEX=0`

