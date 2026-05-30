# Batch Promotion Preview

Batch promotion preview is a preview-only packet created by `accept_local_reviewed_preview`.

The preview can describe a possible local-reviewed record, but it does not write reviewed truth. Local apply remains a separate operator gate, and snapshot refresh remains a separate handoff.

All preview records keep `accepted_truth` false.
