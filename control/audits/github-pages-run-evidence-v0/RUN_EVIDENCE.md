# Run Evidence

Evidence collection tools:

- `gh`: unavailable in the local shell.
- GitHub connector: commit workflow-run wrapper returned no runs for the current commit;
  job log fetch was available and used for the selected job.
- GitHub public repository REST API: used for workflow, run, job, artifact, Pages, and
  deployment metadata for `Julesc013/eureka`.

Current local HEAD at evidence collection:

`8372ca71a3877de18503acfa34fb15d5685b38c6`

Origin `main` HEAD at evidence collection:

`8372ca71a3877de18503acfa34fb15d5685b38c6`

Latest relevant Pages workflow run:

- Run ID: `25171991131`
- Run number: `28`
- Workflow: `Deploy static public site to GitHub Pages`
- Event: `push`
- Head branch: `main`
- Head SHA: `8372ca71a3877de18503acfa34fb15d5685b38c6`
- Display title: `docs(publication): record static artifact promotion metadata`
- Status: `completed`
- Conclusion: `failure`
- Created: `2026-04-30T14:46:01Z`
- Updated: `2026-04-30T14:46:19Z`
- URL: `https://github.com/Julesc013/eureka/actions/runs/25171991131`
- Matches current HEAD at evidence collection: yes.

Job evidence:

- Job ID: `73793663478`
- Job name: `Validate and deploy site/dist`
- Job status: `completed`
- Job conclusion: `failure`
- Job URL: `https://github.com/Julesc013/eureka/actions/runs/25171991131/job/73793663478`
- Failed step: `Configure GitHub Pages`

Successful workflow steps before failure:

- Check out repository
- Set up Python
- Build static site
- Check generated public data summaries
- Check compatibility surfaces
- Check static resolver demos
- Validate publication inventory
- Validate static public site
- Check GitHub Pages static artifact
- Check static site generated artifact drift

Failure summary:

`actions/configure-pages@v5` failed with a Pages site lookup error. The job log states:
`Get Pages site failed. Please verify that the repository has Pages enabled and configured
to build using GitHub Actions, or consider exploring the enablement parameter for this
action.`

Skipped after failure:

- Upload static public site artifact
- Deploy static public site to GitHub Pages
