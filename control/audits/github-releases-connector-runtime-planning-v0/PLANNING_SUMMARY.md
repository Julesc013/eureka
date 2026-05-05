# Planning Summary

P89 plans a future GitHub Releases connector runtime. It keeps runtime blocked because P73 is present but `connector_approved_now` remains false and operator gates for repository identity, token/auth, source policy, User-Agent/contact, rate limit, timeout, cache, evidence attribution, and kill switch are still pending.

The future connector is release-metadata-only and source-sync-worker driven. Public queries must never fan out live to GitHub.
