# Current Policy

`control/policies/instance_layout_policy.json` makes the sibling
`../instances/default` layout canonical for local development.

Required posture:

- Repo root: `workspace_root/eureka`
- Instances root: `workspace_root/instances`
- Default instance: `workspace_root/instances/default`
- Legacy sibling: `workspace_root/eureka-instance`, explicit only
- Repo-nested runtime state: forbidden
- Automatic operator instance move/delete/copy: forbidden

This policy is local development doctrine only. It does not claim production
readiness or public launch readiness.
