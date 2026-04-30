# Examples

Fixture-safe examples live under `contracts/api/examples/`:

- `search_result_card_member_driver.v0.json`: member driver inside a support CD
  bundle, showing smallest-actionable-unit context and blocked download/install
  behavior.
- `search_result_card_firefox_xp_candidate.v0.json`: compatibility candidate
  with partial evidence and future-gated install handoff.
- `search_result_card_article_segment.v0.json`: article or scan segment result
  with citation/read actions and no raw scan payload.
- `search_result_card_documentation_only.v0.json`: documentation-only result
  that preserves usefulness while blocking install/execution.
- `search_result_card_absence_next_steps.v0.json`: bounded absence card with
  next steps and no claim that the wider web was checked.

The examples avoid private paths, live URLs, raw source payloads, executable
downloads, installer handoffs, malware-safety claims, and rights-clearance
claims.
