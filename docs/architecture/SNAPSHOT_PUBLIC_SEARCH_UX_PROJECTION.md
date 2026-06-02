# Snapshot Public Search UX Projection

The public search UX projection records routes, page view models, no-JS HTML/text examples, and result-card references from the public search UX MVP.

The projection is read-only. It does not own search behavior, execute public queries, fan out to live sources, or mutate any index. Its job is to expose the existing snapshot state in a UI-ready form that can be reassessed later.

Required boundaries:

- no JavaScript is required for the public search path
- public projection is read-only
- no deployment or site/dist write occurs
- candidate and reviewed states stay visually distinct
- no results pages surface known needs and bounded absences without creating truth
