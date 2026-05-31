# Snapshot Seed Batch Handoffs

Seed-batch handoffs are public-safe summaries produced by curated discovery
batches. Snapshot refresh reads their candidate summaries, SCOUT trail
summaries, review batch packets, known needs, absence summaries, and reassess
inputs.

Those handoffs are inputs to projection only. They are not reviewed truth and do
not authorize public index mutation. If a seed candidate should become reviewed
truth, it must pass operator review, local apply, and a separate snapshot gate.
