# Commit Divergence

The safety branch is `10` commits ahead and `7` commits behind `origin/main`.

## Local-Only Commits

- `8a091f6` `audit(sync): record active merge rescue` - repo sync audit commit.
- `0335559` `chore(sync): preserve merge-rescued local work` - preservation commit containing mixed unreviewed local work.
- `2f63e19` `ops(evidence): plan local evidence ledger runtime` - Track B later than remote B06.
- `0906bb4` `ops(source-cache): plan local source cache runtime` - Track B later than remote B06.
- `bdbc36a` `runtime(candidate): add local candidate store runtime` - Track B runtime.
- `3df313d` `runtime(node): add policy evaluator` - Track B runtime.
- `2468da6` `runtime(workunit): add dry-run WorkUnit runner` - Track B runtime.
- `dea4c67` `runtime(observation): add local SearchNeed runtime` - Track B runtime.
- `bf8e89d` `runtime(observation): add local search miss ledger runtime` - Track B runtime.
- `aa3fb7f` `runtime(observation): add local query observation runtime` - Track B runtime.

## Remote-Only Commits

- `f83b005` `ops(observation): prepare human candidate review packet` - OBS-AGENT-07.
- `660777a` `audit(observation): synchronize obs candidates with track b` - OBS-AGENT-06.
- `3adf773` `ops(observation): draft workunit seed candidates` - OBS-AGENT-05.
- `1cb3124` `ops(observation): draft search need seed candidates` - OBS-AGENT-04.
- `6c85209` `ops(observation): add candidate review queue` - OBS-AGENT-03.
- `fe96586` `ops(observation): generate source gap candidates` - OBS-AGENT-02.
- `5273eb3` `ops(observation): mine local eval failure candidates` - OBS-AGENT-01.

## Interpretation

The local branch contains the rescued Track B spine and preservation evidence. The remote branch contains the OBS review/seed lane. These are related and overlapping, so the next step is a reviewed merge plan instead of an automatic convergence merge.
