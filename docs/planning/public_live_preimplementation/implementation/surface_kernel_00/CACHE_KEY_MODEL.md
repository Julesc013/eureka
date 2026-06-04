# Cache Key Model

Implemented:

```text
runtime/surface/cache_key.py
build_surface_cache_key(...)
```

Included dimensions:

```text
route
entity_id
view_model_version
representation_profile
renderer_id
skin_id
language
visibility_posture
policy_posture
data_version
```

Unavailable dimensions use explicit placeholders:

```text
renderer_unselected
default
und
unknown
```

Tests prove cache keys change by route, entity, representation profile, public/private posture, and policy posture.
