# Merge Plan

Default: plan-only.

No branch mutation occurred in this task.

Explicit apply command:

```bash
python scripts/prepare_r0_dev_to_main_merge.py --apply --json
```

Explicit push command:

```bash
python scripts/prepare_r0_dev_to_main_merge.py --apply --push-main --json
```

The merge helper never force-pushes, never rewrites history, never tags a release, never deploys, and never regenerates `site/dist`.

Rollback uses a normal revert commit on `main` if a pushed promotion must be backed out.
