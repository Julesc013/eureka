# Search Hunt Exhaustion Boundaries

HUNT-04 generation is deliberately narrow:

- allowed: persist a local exhaustion report for a Search Hunt Session
- allowed: append local command history for report generation
- allowed: show report state in local JSON API and workbench pages
- forbidden: WorkUnit creation
- forbidden: source probes
- forbidden: extraction
- forbidden: external network search
- forbidden: model/provider calls
- forbidden: review decision mutation
- forbidden: public/master index mutation
- forbidden: LAN generation
- forbidden: deployment
- forbidden: production readiness claim
- forbidden: public launch readiness claim

An exhaustion report may recommend future categories, but those categories remain inert until later reviewed tasks enable specific pipelines.
