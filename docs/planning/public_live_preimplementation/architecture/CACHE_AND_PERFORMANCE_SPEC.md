# Cache And Performance Spec

## Request Path

```text
request
-> route resolution
-> capability negotiation
-> canonical view model lookup/build
-> policy filter
-> renderer dispatch
-> representation cache
-> response
```

## Cache Layers

- L1 request-local cache
- L2 rendered representation cache
- L3 canonical view-model cache
- L4 reviewed object/evidence store
- L5 search index
- L6 source observation cache

## Cache Key Fields

`route`, `entity_id`, `view_model_version`, `renderer_id`,
`representation_profile`, `skin_id`, `language`, `public/private posture`,
`policy posture`, and `data_version`.

