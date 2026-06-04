# Supersession And Duplicate Control

Batch 02 adds `supersession_map.json` to prevent supporting references from
inflating reviewed-record counts.

The three superseded Batch 01 decisions are preserved as audit-visible duplicate
or supporting references. None counts as a new reviewed seed record.

This keeps the reviewed corpus honest:

- Supporting Mozilla references remain useful.
- Duplicate Firefox support observations stay linked.
- Reviewed counts increase only when a promote decision creates a distinct
  reviewed seed record.
