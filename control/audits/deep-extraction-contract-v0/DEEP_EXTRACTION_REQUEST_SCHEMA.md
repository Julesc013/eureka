# Deep Extraction Request Schema

`contracts/extraction/deep_extraction_request.v0.json` defines a contract-only request envelope with `extraction_request_kind: deep_extraction_request`.

Required fields include `request_scope`, `target_ref`, `extraction_policy_ref`, `requested_tiers`, `container_hints`, `safety_requirements`, `privacy`, `rights_risk`, expected outputs, limitations, no-runtime guarantees, and no-mutation guarantees.

Hard guarantees are false: runtime extraction, file opening, archive unpacking, payload execution, installer execution, package manager invocation, emulator or VM launch, OCR, transcription, live source calls, external calls, URL fetching, source-cache mutation, evidence-ledger mutation, candidate mutation, public/local/master-index mutation, and telemetry export.
