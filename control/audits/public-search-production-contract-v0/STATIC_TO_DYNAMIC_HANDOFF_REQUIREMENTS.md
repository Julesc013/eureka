# Static To Dynamic Handoff Requirements

The static site must remain useful when the backend is absent.

Requirements:

- Backend URL must be inventory/config driven.
- No fake hosted URL.
- No hardcoded localhost in deployed static pages as a public endpoint.
- No hosted search claim unless evidence exists.
- Search form must respect the 160-character query limit.
- No JavaScript requirement.
- Lite/text/files surfaces must explain limitations.
- GitHub Pages remains static-only and cannot run Python.
