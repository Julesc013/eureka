# Freshness And Invalidation Policy

Cache entries are stale if any governing input changes:

- public index rebuild
- source cache refresh
- contract version change
- candidate promotion
- rights policy change
- safety policy change

P60 examples use `ttl_policy: none_for_example`. No retention runtime or
automatic invalidation runtime exists yet.
