# Extraction Tier Taxonomy

Deep extraction tiers:

- `tier_0_outer_metadata`: container-level metadata only.
- `tier_1_container_member_listing`: bounded member listing without payload reads.
- `tier_2_manifest_extraction`: manifest/metadata summary only.
- `tier_3_selective_text_summary`: short reviewed text summaries, not raw dumps.
- `tier_4_recursive_deep_extraction`: future recursive extraction, requires sandbox approval.
- `tier_5_on_demand_deepening`: future explicit deepening, requires on-demand approval.
- `OCR_hook_future`: contract hook only; no OCR runtime.
- `transcription_hook_future`: contract hook only; no transcription runtime.
- `unknown`: explicit unknown tier.

P95 examples may describe tiers but do not execute them. Tier 4 and Tier 5 are blocked until sandbox, resource, and operator policies are approved.
