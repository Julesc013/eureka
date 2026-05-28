# API Matrix

Public alpha API routes:

- `/api/v1/alpha/status`
- `/api/v1/alpha/search`
- `/api/v1/alpha/object/{object_id}`
- `/api/v1/alpha/source/{summary_id}`
- `/api/v1/alpha/evidence/{summary_id}`
- `/api/v1/alpha/absence/{summary_id}`
- `/api/v1/alpha/needs`

Allowed methods are `GET` and `HEAD`. Public write actions, public mutation,
live source fanout, downloads, uploads, extraction, model/provider calls, and
accounts are disabled.
