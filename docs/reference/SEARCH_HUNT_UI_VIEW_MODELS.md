# Search Hunt UI View Models

HUNT-02 adds these server-rendered view models:

- `SearchHuntListPageView`
- `SearchHuntCardView`
- `SearchHuntDetailPageView`
- `SearchHuntLayerView`
- `SearchHuntTransitionView`
- `SearchHuntUnavailableActionView`
- `SearchHuntNotFoundPageView`

Builders accept records and summaries from the Search Hunt store. They do not hold store handles and do not expose mutation methods.

All display text is escaped by the local workbench HTML helpers at render time.

