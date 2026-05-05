# Deep Extraction Contract v0

Deep Extraction Contract v0 defines how Eureka can later describe safe metadata-first extraction requests and summaries for containers, archives, packages, disc images, WARC/WACZ files, source bundles, installers, scanned volumes, PDFs, OCR layers, and nested records.

P95 is contract-only. It adds no extraction runtime, no runtime extraction, no archive unpacking, no file opening, no OCR, no transcription, no URL fetching, no live source calls, no payload execution, no execution, no package manager invocation, no emulator or VM launch, no database tables, no persistent extraction queue, no source-cache mutation, no evidence-ledger mutation, no candidate promotion, no public/local/master-index mutation, no mutation, and no production extraction service.

## Contract Files

- `contracts/extraction/deep_extraction_request.v0.json`
- `contracts/extraction/extraction_result_summary.v0.json`
- `contracts/extraction/extraction_policy.v0.json`
- `contracts/extraction/extraction_member.v0.json`

## Tier Taxonomy

The contract defines `tier_0_outer_metadata`, `tier_1_container_member_listing`, `tier_2_manifest_extraction`, `tier_3_selective_text_summary`, `tier_4_recursive_deep_extraction`, `tier_5_on_demand_deepening`, `OCR_hook_future`, `transcription_hook_future`, and `unknown`.

Tier 4 and Tier 5 remain blocked until sandbox, resource, and operator approval. OCR and transcription hooks are future-only.

## Safety Boundary

Deep extraction is metadata-first. Member enumeration is not payload trust. Manifest extraction is not rights clearance. OCR/transcription is not truth. Synthetic records are provisional. Extracted evidence is not accepted truth. Executable payloads require risk labels and must not run.

## Relationships

Future extraction summaries may create reviewed source-cache candidates, evidence-ledger observation candidates, and candidate-index records only after separate runtime approvals. Public search, object pages, comparison pages, and result explanations may later cite reviewed summaries and gaps, but must never trigger live extraction from a public request.

<!-- P96-SEARCH-RESULT-EXPLANATION-CONTRACT-START -->
## P96 Search Result Explanation Contract v0

Search Result Explanation Contract v0 is contract-only. It defines future evidence-first explanations for why a result appeared, what matched, what evidence/provenance/source/identity/ranking/compatibility/gap/action posture applies, and what must not be claimed.

No runtime explanation generation, public search response change, public search order change, hidden score, result suppression, AI answer, model call, telemetry, live source call, source/evidence/candidate/public/local/master mutation, download, install, or execution is added.
<!-- P96-SEARCH-RESULT-EXPLANATION-CONTRACT-END -->
