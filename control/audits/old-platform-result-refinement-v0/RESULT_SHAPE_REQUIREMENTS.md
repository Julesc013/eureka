# Result Shape Requirements

Old-platform hard evals now evaluate a compact primary-candidate shape:

- `target_ref`
- `candidate_kind`
- `record_kind`
- `primary_lane`
- `user_cost_score`
- `user_cost_reasons`
- `source_id`
- `source_family`
- `evidence_count`
- `evidence_kinds`
- `compatibility_evidence_count`
- `representation_id`
- `member_path`
- `parent_target_ref` for member results when recoverable
- `artifact_locators`
- `has_direct_artifact_locator`
- `is_member_result`
- `is_parent_context`

Strict satisfaction requires the task minimum granularity to match the primary
candidate shape.

## Task-Specific Requirements

`driver_inside_support_cd`

- primary candidate must be a member or direct driver artifact
- member path should identify a driver-like file such as an INF
- requested hardware and platform evidence must be present
- lane must recognize member usefulness
- bad-result patterns must not be accepted

`latest_firefox_before_xp_drop`

- source-backed Firefox and Windows XP evidence is not enough by itself
- exact latest-compatible release identity and direct release asset evidence are
  required before satisfaction

`old_blue_ftp_client_xp`

- vague identity must remain uncertain unless a concrete product or direct
  installer is source-backed
- FTP function and Windows XP evidence keep this partial, not satisfied

`win98_registry_repair`

- registry-repair and Windows 98 evidence exists
- current primary lane is still preservation/context, so it remains partial
  until direct installable/member shape is clearer

`windows_7_apps`

- direct application representation evidence exists
- current primary lane still reads as inside-bundle/context rather than
  installable/best-direct, so it remains partial

`article_inside_magazine_scan`

- requires scan/OCR/article/page evidence
- no such bounded fixture exists yet
