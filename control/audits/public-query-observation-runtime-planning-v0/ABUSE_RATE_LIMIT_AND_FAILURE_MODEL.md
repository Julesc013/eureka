# Abuse Rate Limit And Failure Model

Future runtime requires query length cap, result count cap, body size cap, timeout cap, rate-limit prerequisite, circuit breaker for observation store failures, and bounded write timeout. Observation write failure must not block a safe search response, expose private data, or log raw queries.
