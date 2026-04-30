# Base Path Review

GitHub Pages project base path policy: `/eureka/`

Future custom domain/root path policy: `/`, pending separate custom-domain
approval and evidence.

Current status:

- project Pages target uses `site/dist`
- links are relative and base-path safe
- root-relative internal links are not allowed by the current static artifact
  checker
- `site/dist/data/`, `site/dist/lite/`, `site/dist/text/`, `site/dist/files/`,
  and `site/dist/demo/` remain relative artifact paths
- local file preview is suitable for static inspection but is not deployment
  evidence

No `CNAME`, DNS/provider configuration, custom domain setup, backend provider
configuration, or alternate host deployment was added by this review.
