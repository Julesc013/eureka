# Active Merge State Before Rescue

- Branch before rescue: `main`
- Local HEAD before rescue: `2f63e190964d19bd7f7d6c9130e716ecbd61b6ac`
- Origin main observed: `f83b005dcd68bc9710bccefe8d788b64c5fce461`
- MERGE_HEAD before rescue: `6c852097ec812ddd2c8584dbff5b847bdebd94c5`
- MERGE_HEAD subject: `ops(observation): add candidate review queue`
- MERGE_MSG: `Merge branch 'main' of https://github.com/Julesc013/eureka`
- Unmerged index entries: `0`
- Staged paths before rescue: `317`
- Unstaged paths before rescue: `3`
- Untracked paths before rescue: `0`

Committing while `MERGE_HEAD` existed was unsafe because it would have concluded
the in-progress merge. The rescue therefore quit merge metadata before making
any preservation commit.
