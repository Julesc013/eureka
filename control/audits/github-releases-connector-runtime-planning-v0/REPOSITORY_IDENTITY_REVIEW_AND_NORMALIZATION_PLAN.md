# Repository Identity Review And Normalization Plan

Allowed future repository sources:

- reviewed source record
- reviewed search need
- source pack record
- manual observation record
- fixture example

Forbidden repository sources:

- raw public query parameter
- private repository
- credentialed repository
- localhost URL
- file URL
- uploaded file
- local path
- arbitrary URL

Future normalization:

- owner/repo lowercase policy where appropriate
- Unicode/confusable caution
- repository rename/transfer caution
- organization/user scope caution
- private repo rejection
- credential stripping or rejection
- owner/repo public-safe fingerprint for sensitive refs
- no raw private repository publication

No implementation is added in P89.
