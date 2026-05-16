# Q32 Remaining Risks

- Older Eureka commits may not satisfy the newly imported structured commit
  policy; changelog preview reports them as malformed rather than rewriting
  history.
- The commit hook template is present but intentionally not installed into
  `.git/hooks`.
- Git helper commands remain dry-run/report-only for Q32. Branch creation,
  merge, promotion, push, prune, GitHub protection, and CI enforcement remain
  future/operator-gated work.
- Target-specific branch detection was generated for the current local `dev`
  tree only; it is not remote branch protection evidence.
- Budget warnings remain for generated eval reports and cache reports, not for
  the current task packet.
- Exact tokenizer/provider billing remains absent.
- Q32 does not prove arbitrary Eureka product implementation quality and does
  not authorize product changes.
- Dominium still needs its separate canonical-pack sync.
