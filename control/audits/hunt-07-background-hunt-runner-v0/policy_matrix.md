# Policy Matrix

| WorkUnit kind | Runner status | Reason |
| --- | --- | --- |
| regression_test | runnable | deterministic local worker |
| evidence_review | runnable | local review queue inspection only |
| source_probe | blocked | source probe worker disabled |
| extraction_task | blocked | extraction worker disabled |
| agent_task | blocked | agent and model workers disabled |
| index_rebuild | token-gated | reviewed-index rebuild worker has separate operator gate |

