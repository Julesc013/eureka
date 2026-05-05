# SWHID, Origin, Repository Review And Normalization Plan

Allowed future identity sources:

- reviewed source record
- reviewed search need
- source pack record
- manual observation record
- fixture example

Forbidden identity sources:

- raw public query parameter
- private repository
- credentialed repository
- local repository path
- localhost URL
- file URL
- uploaded file
- arbitrary URL
- unreviewed origin URL

Future normalization:

- SWHID syntax validation
- SWHID object-type classification
- origin URL normalization
- origin URL privacy review
- repository owner/name/origin review where applicable
- credential stripping/rejection
- localhost/private-network/file/data/javascript URL rejection
- Unicode/confusable caution
- repository rename/transfer caution
- public-safe fingerprint for sensitive refs
- no raw private origin/repository publication

No implementation is added in P92.
