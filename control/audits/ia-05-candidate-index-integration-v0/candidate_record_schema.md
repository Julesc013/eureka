# Candidate Record Schema

IA candidate records include source-cache record IDs, evidence IDs,
observation IDs, source locator, claim summaries, uncertainty, limitations,
risk flags, rights flags, and review status.

Required invariants:

- review required
- no accepted truth
- no reviewed record creation
- no reviewed/master index mutation
- no raw response commit
- no download
