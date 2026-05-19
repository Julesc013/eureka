# Failure Inventory

The prior promotion review reported full discovery red with 17 failures and 5 errors.

Reproduced repair groups:

| Area | Root Cause |
| --- | --- |
| candidate-index records | Generic record validator scanned IA integration expected-output fixtures as CANDIDATE_INDEX_RECORD examples. |
| contract taxonomy inventory | contracts/repo layout canon contracts were missing from the taxonomy inventory. |
| runtime/source-observation leakage | IA runtime modules contained task/control vocabulary and banned direct transport import spelling. |
| HUNT/LOCAL promotion state | Historical validators did not recognize the dev/IA promotion repair lane. |
| HUNT historical promotion evidence | HUNT promotion evidence was recomputed against the active repair branch. |
| IA/LOCAL/HUNT historical validators | Older queue-sensitive validators rejected the dev/IA promotion review lane even after their tasks were completed. |
