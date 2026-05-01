# Deployment Template Review

P54 adds inert deployment templates:

- `Dockerfile`
- `.dockerignore`
- `deploy/README.md`
- `deploy/render/render.yaml`

The templates contain safe environment defaults and no secrets. They do not
call hosting providers, configure DNS, create TLS, deploy a service, or prove
hosted availability.

`deploy/render/render.yaml` is a manual operator template with `autoDeploy:
false` and `healthCheckPath: /healthz`.
