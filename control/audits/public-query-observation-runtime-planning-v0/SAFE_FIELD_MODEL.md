# Safe Field Model

Allowed future public-safe fields: observation_id, schema_version, normalized_query_fingerprint, query_intent, target_object_kind, platform_hint, artifact_type_hint, result_count_bucket, top_result_lane, miss_type, gap_type, checked_index_id, search_mode, safety_decision, created_at_bucket, retention_class.
Forbidden fields: raw query, full query string if sensitive, IP address, account ID, session ID, browser fingerprint, precise geolocation, private path, private URL, secret/token/API key, uploaded file name, local machine details, exact user-agent string unless separately policy-approved.
