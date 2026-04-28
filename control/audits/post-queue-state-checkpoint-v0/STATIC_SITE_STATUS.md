# Static Site Status

`public_site/` is the current deployable static artifact. `site/` is the stdlib-only generator/source tree and `site/dist/` is generated output. Both validation paths passed.

Static content includes root pages, `data/`, `lite/`, `text/`, `files/`, and `demo/`. The site is no-JS and base-path aware for `/eureka/` and `/`.

The files surface references the signed snapshot seed format, but `public_site/` does not publish a production signed snapshot route or executable downloads.
