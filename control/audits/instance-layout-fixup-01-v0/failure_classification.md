# Failure Classification

The original full discovery run reported 4,557 tests with 21 failures.

A targeted rerun after the tree was clean reproduced 12 failures:

- 2 clean-machine failures caused by the new instance path policy exposing old
  helpers that still place instances inside temporary checkouts.
- 10 legacy queue/latest-task validators that reject the reviewed PLAY-00
  handoff or assert old task packets after those tracks completed.

The 9 remaining original failures were transient dirty-tree or remote-state
failures and did not reproduce after `INSTANCE-LAYOUT-01` was committed and
present at `origin/dev`.

The clean-machine repairs should be handled by a future scoped task because the
needed scripts are outside this fixup task's allowed edit paths.
