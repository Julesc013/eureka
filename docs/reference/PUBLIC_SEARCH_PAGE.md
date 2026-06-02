# Public Search Page Reference

The MVP uses a no-JS GET form:

```html
<form method="get" action="/search">
  <label for="q">Search public alpha</label>
  <input id="q" name="q" type="search">
  <button type="submit">Search</button>
</form>
```

Search results are rendered from public-safe view-model packets. No HTML page owns truth semantics independently of the view model.
