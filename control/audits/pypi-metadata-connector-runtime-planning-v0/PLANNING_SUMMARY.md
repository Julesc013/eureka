# Planning Summary

P90 plans a future PyPI metadata connector runtime. It keeps runtime blocked because P74 is present but `connector_approved_now` remains false and operator gates for package identity, dependency metadata caution, token/auth, source policy, User-Agent/contact, rate limit, timeout, cache, evidence attribution, package download/install/dependency boundaries, and kill switch are still pending.

The future connector is package-metadata-only and source-sync-worker driven. Public queries must never fan out live to PyPI.
