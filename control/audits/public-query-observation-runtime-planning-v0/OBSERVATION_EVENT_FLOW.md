# Observation Event Flow

1. Public search request arrives.
2. Request is bounded and validated.
3. Query guard classifies privacy/poisoning risk.
4. Unsafe query is rejected or redacted.
5. Public search runs local_index_only.
6. Result envelope is generated.
7. Observation candidate is built from public-safe fields only.
8. Observation is stored only if enabled by explicit runtime flag.
9. Observation may later feed result cache/miss ledger/search need.
10. No master-index mutation occurs.

Required future flags: EUREKA_QUERY_OBSERVATION_ENABLED=0 by default; EUREKA_QUERY_OBSERVATION_STORE=disabled by default; EUREKA_QUERY_OBSERVATION_RAW_QUERY_RETENTION=none; EUREKA_QUERY_OBSERVATION_PUBLIC_AGGREGATE=0 by default; EUREKA_QUERY_OBSERVATION_BLOCK_PRIVATE_DATA=1; EUREKA_QUERY_OBSERVATION_BLOCK_POISONING=1.
