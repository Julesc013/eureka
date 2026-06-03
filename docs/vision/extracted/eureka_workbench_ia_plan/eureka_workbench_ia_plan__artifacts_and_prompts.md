# Artifacts and Prompts — Eureka Workbench, IA Connector, and Production Path

## Generated prompt families

### Commit discipline / AIDE policy prompt material

Type: planning/policy prompt content.

Purpose: Define commit format, changelog-ready bodies, trailers, commit linting, WorkUnit recovery, and replay-safe task policy.

Status: Discussed and used as a standard in later prompts.

Preserve: Yes.

Future aggregation: Should feed into developer workflow and AIDE operating doctrine.

Caveats: Actual implementation must be verified in the repository.

### Track A/B/D/C/E/F/G/H/I/J/K/L master planning material

Type: roadmap and task queue planning.

Purpose: Define the broad Eureka track spine from queue control to representation, observation, source/evidence/review, IA, snapshots, native clients, hosting, extraction, ranking, source expansion, packs, actions, AI, and wider ecosystem.

Status: Superseded as an active queue by later live branch states, but still valuable as background architecture.

Preserve: Yes.

Future aggregation: Use as roadmap source material, with note that later Workbench/IA/SYN sequencing refined it.

Caveats: Do not treat every listed task as current.

### F-BUNDLE-01 and F-BUNDLE-02 prompts

Type: generated Codex prompts.

Purpose: Extraction sandbox, Tier 0–2 fixture extraction, candidate effects, and search integration.

Status: Prompt text generated. Later F work was deferred until after Workbench/SYN/DOMAIN/SCOUT.

Preserve: Yes as future extraction planning.

Caveats: Not evidence of implementation.

### G-BUNDLE-01 and G-BUNDLE-02 prompts

Type: generated Codex prompts.

Purpose: Result explanations, near misses, known absence, ranking shadow runtime, and search-quality harness.

Status: Prompt text generated; search quality remains future.

Preserve: Yes.

Caveats: Later SYN/Workbench should shape actual G implementation.

### I-BUNDLE-01 prompt

Type: generated Codex prompt.

Purpose: Pack quarantine, fixity, signature envelope, import preview, contribution review.

Status: Planning/generation in chat.

Preserve: Yes.

Caveats: Do not infer pack federation is built.

### J0-BUNDLE-01 prompt

Type: generated Codex prompt.

Purpose: Safe action manifests, citation/export/acquisition/preservation manifests, blocked actions.

Status: Planning/generation in chat.

Preserve: Yes.

Caveats: Risky actions remain deferred.

### D-BUNDLE-01 and D-BUNDLE-02 prompts

Type: generated Codex prompts.

Purpose: Snapshot envelope, manifest, verification, text/lite/file-tree renderers, localhost read-only relay, old-browser and terminal modes.

Status: Planning/generation in chat.

Preserve: Yes.

Caveats: Later Workbench plan should determine actual implementation timing.

### C-BUNDLE-01/02/03 prompts

Type: generated Codex prompts.

Purpose: Native directory skeleton, native matrix, C89 library, WinForms proof, Win32/AppKit/Carbon skeletons, smoke evidence, packaging manifests.

Status: Planning/generation in chat.

Preserve: Yes.

Caveats: Native clients remain later and read-only.

### E-BUNDLE-01/02 prompts

Type: generated Codex prompts.

Purpose: Hosting and operations readiness, hosted wrapper rehearsal, public launch evidence.

Status: Planning/generation in chat.

Preserve: Yes.

Caveats: Public hosting remains false/deferred.

### MVP-ALPHA-AUDIT, OPERATOR-REVIEW, DEPLOYMENT-PLAN, LOCAL-MVP-ITERATION prompts

Type: generated Codex prompts.

Purpose: Audit local MVP readiness, create operator review/launch decision packet, deployment planning without deployment, choose next non-deploy local expansion.

Status: Planning/generation in chat, partly superseded by later HUNT/PLAY/IA state.

Preserve: Yes.

Caveats: Do not treat deployment planning as deployment approval.

### R0-LITE-01 / R0-01 recovery prompts

Type: generated or proposed Codex prompts.

Purpose: Production reality audit, expansion freeze, artifact classification, runtime leakage audit, source-observation seam recovery.

Status: Proposed during scaffold crisis.

Preserve: Yes as guardrail.

Caveats: Later branch state improved, but the principle remains valuable.

### IA Workbench and IA-HUNT prompt ideas

Type: proposed future prompts.

Purpose: Workbench foundation, result lanes, event model, IA-HUNT bridge, IA WorkUnit, IA UI, local apply gate.

Status: Final recommended direction; not shown as implemented.

Preserve: Yes; high priority.

Caveats: Needs current repo verification.

## Repository artifacts discussed

### `.aide/reports/eureka-repo-health.json`

Type: repo health/status file.

Purpose: Track current recommended task, eval status, source probe/extraction/provider/deployment booleans, HUNT/PLAY/IA status.

Status: Referenced multiple times with changing contents across branch states.

Preserve: Yes.

Future aggregation: Use as evidence of project state transitions, but date each version.

Caveats: State is time-sensitive and must be reverified.

### `.aide/context/latest-task-packet.md`

Type: AIDE task context.

Purpose: Identify current task and allowed/forbidden paths.

Status: At one point stale or generic; later HUNT promotion packet was visible; inconsistency with health files was noted.

Preserve: Yes.

Caveats: Do not assume it always matches repo health.

### `.aide/queue/SYN-00/task.yaml`

Type: AIDE queue file.

Purpose: Synthetic Query Foundry planning over Local/HUNT/PLAY/IA, planning-only and forbidding source probes, extraction, provider calls, deployment, and production/public launch claims.

Status: Referenced as current recommended task after HUNT/IA stages.

Preserve: Yes.

Caveats: The final recommendation was to insert Workbench Foundation before or around SYN.

### IA audit directories and inventory files

Type: control/audit evidence.

Purpose: Record IA policy approval, fixture replay, live metadata probe, TLS trust, source-cache write, evidence integration, candidate index, review/promotion, reviewed index rebuild, pilot closeout.

Status: Discussed as existing on `dev`.

Preserve: Yes.

Future aggregation: Important evidence for the first external metadata source vertical slice.

Caveats: Need to distinguish temp-instance proof from production runtime.

### PLAY audit directories and smoke artifacts

Type: control/audit evidence.

Purpose: Known hit, known absence, demo Hunts, SearchNeeds, WorkUnits, operator play session, smoke pack.

Status: Discussed as available.

Preserve: Yes.

Caveats: Verify whether they are in main or only dev.

### HUNT promotion artifacts

Type: control/audit evidence.

Purpose: Record HUNT completion and promotion gates.

Status: Discussed as completed/promoted in one branch state.

Preserve: Yes.

Caveats: Branch state changed; recheck.

## Final archive package files

This archive request itself created seven Markdown files and a ZIP package. These are preservation artifacts, not project implementation artifacts. They should feed into future aggregation/book work but not into Eureka runtime.
