# Route Matrix

```json
{
  "routes": [
    {
      "download_enabled": false,
      "extraction_enabled": false,
      "live_source_call_enabled": false,
      "method": "GET",
      "mutation_enabled": false,
      "no_js_required": true,
      "projection_profile": "public_web",
      "public_read_only": true,
      "route": "/",
      "template": "home_page.html",
      "view_model": "SearchHomePageViewModel"
    },
    {
      "download_enabled": false,
      "extraction_enabled": false,
      "live_source_call_enabled": false,
      "method": "GET",
      "mutation_enabled": false,
      "no_js_required": true,
      "projection_profile": "public_web",
      "public_read_only": true,
      "route": "/search",
      "template": "search_results_page.html",
      "view_model": "SearchResultsPageViewModel"
    },
    {
      "download_enabled": false,
      "extraction_enabled": false,
      "live_source_call_enabled": false,
      "method": "GET",
      "mutation_enabled": false,
      "no_js_required": true,
      "projection_profile": "public_web",
      "public_read_only": true,
      "route": "/object/{id}",
      "template": "object_page.html",
      "view_model": "ObjectPageViewModel"
    },
    {
      "download_enabled": false,
      "extraction_enabled": false,
      "live_source_call_enabled": false,
      "method": "GET",
      "mutation_enabled": false,
      "no_js_required": true,
      "projection_profile": "public_web",
      "public_read_only": true,
      "route": "/candidate/{id}",
      "template": "candidate_page.html",
      "view_model": "CandidatePageViewModel"
    },
    {
      "download_enabled": false,
      "extraction_enabled": false,
      "live_source_call_enabled": false,
      "method": "GET",
      "mutation_enabled": false,
      "no_js_required": true,
      "projection_profile": "public_web",
      "public_read_only": true,
      "route": "/need/{id}",
      "template": "need_page.html",
      "view_model": "NeedPageViewModel"
    },
    {
      "download_enabled": false,
      "extraction_enabled": false,
      "live_source_call_enabled": false,
      "method": "GET",
      "mutation_enabled": false,
      "no_js_required": true,
      "projection_profile": "public_web",
      "public_read_only": true,
      "route": "/source/{id}",
      "template": "source_page.html",
      "view_model": "SourcePageViewModel"
    },
    {
      "download_enabled": false,
      "extraction_enabled": false,
      "live_source_call_enabled": false,
      "method": "GET",
      "mutation_enabled": false,
      "no_js_required": true,
      "projection_profile": "public_web",
      "public_read_only": true,
      "route": "/evidence/{id}",
      "template": "evidence_page.html",
      "view_model": "EvidencePageViewModel"
    },
    {
      "download_enabled": false,
      "extraction_enabled": false,
      "live_source_call_enabled": false,
      "method": "GET",
      "mutation_enabled": false,
      "no_js_required": true,
      "projection_profile": "public_web",
      "public_read_only": true,
      "route": "/status",
      "template": "status_page.html",
      "view_model": "StatusPageViewModel"
    }
  ],
  "schema_version": "public_search_ux_mvp_route_matrix.v0",
  "task": "PUBLIC-SEARCH-UX-MVP-00"
}
```
