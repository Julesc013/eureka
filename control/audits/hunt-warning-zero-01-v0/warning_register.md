# Warning Register

|warning_id|status|category|evidence|
|---|---|---|---|
|local-total-runtime-naming-debt|resolved|runtime_leakage|Later HUNT remediation continuation and runtime leakage validators report zero new unallowlisted production findings.|
|final-runtime-naming-debt|resolved|runtime_leakage|Resolved by current HUNT/AIDE/LOCAL validation evidence and preserved as historical audit context.|
|final-aide-verify-context-metadata|resolved|aide_verify|Current AIDE doctor, validate, test, eval, review-pack, and verify are green after AIDE-EVAL-GREEN-01 and AIDE-LEDGER-SIZE-01.|
|final-external-lan-client-not-performed|resolved|lan_external_proof|No external LAN coverage claim is made; same-machine LAN smoke and LAN safety gates are sufficient for HUNT/SYN/F0 handoff readiness.|
|missing-hunt-remediation-continue-warning-disposition|resolved|stale_inventory|The continuation result and issue register already report warnings_remaining 0; the missing disposition was backfilled.|
|guard-task-branch-name-generic-dev|false_positive_with_evidence|git_branch_state|The current branch is dev, which is the expected integration branch for the task stack; no branch mutation is requested here.|
|guard-unpushed-dev-work|false_positive_with_evidence|git_branch_state|The two ahead commits are the completed AIDE eval and ledger-size tasks; this task does not push or promote main.|
