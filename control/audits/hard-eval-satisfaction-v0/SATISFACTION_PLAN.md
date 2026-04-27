# Satisfaction Plan

The target scope was the five `not_satisfied` archive-resolution hard evals
that already had source-backed local candidates.

## Guardrails

- Keep all six task IDs.
- Keep task YAML expected-result fields intact.
- Do not remove bad-result patterns.
- Do not mark any task `satisfied` overall while lane placement and bad-result
  scoring are still not evaluable.
- Do not satisfy any task from planner output alone.
- Require bounded source-backed search results before movement.
- Leave article-inside-scan as a capability gap until an article/page/OCR
  fixture exists.

## Targeted Evidence Mapping

The runner now evaluates structured fields already present in top results:

- `source_id` and `source_family`
- `record_kind`
- `member_path`
- `representation_id`
- `result_lanes`
- `compatibility_evidence`
- evidence snippets
- artifact-like member/file locators
- task platform, hardware, product, and function constraints

This is still deterministic evidence matching. It is not semantic relevance,
fuzzy matching, vector search, LLM inference, or ranking.

## Expected Movement

| task | expected movement |
| --- | --- |
| `driver_inside_support_cd` | `not_satisfied` to `partial` |
| `latest_firefox_before_xp_drop` | `not_satisfied` to `partial` |
| `old_blue_ftp_client_xp` | `not_satisfied` to `partial` |
| `win98_registry_repair` | `not_satisfied` to `partial` |
| `windows_7_apps` | `not_satisfied` to `partial` |
| `article_inside_magazine_scan` | remain `capability_gap` |
