# renglo.search - OpenSearch Integration

Document indexing and full-text search using AWS OpenSearch Service.

## Configuration

Add to `system/env_config.py` or environment variables:

```python
OPENSEARCH_ENDPOINT = 'https://your-domain.us-east-1.es.amazonaws.com'
OPENSEARCH_INDEX = 'renglo-documents'
OPENSEARCH_REFRESH = False  # Set True for immediate visibility (slower writes)
```

If `OPENSEARCH_ENDPOINT` is not set, search indexing is disabled and the app runs normally.

## Blueprint: searchable Fields

Add `"searchable": true` to blueprint fields to index them:

```json
{
  "name": "title",
  "type": "string",
  "searchable": true,
  ...
}
```

Only fields with `searchable: true` are indexed. Default is `false`.

## Indexing

Documents are indexed automatically on:
- **POST** `/_data/<portfolio>/<org>/<ring>` (create)
- **PUT** `/_data/<portfolio>/<org>/<ring>/<id>` (update)
- **DELETE** `/_data/<portfolio>/<org>/<ring>/<id>` (delete)

## Search API

**POST** `/_search/<portfolio>/<org>`

```json
{
  "query": "search terms",
  "datatypes": ["noma_travels", "noma_rel"],
  "filters": {"status": "confirmed"},
  "limit": 20,
  "offset": 0
}
```

- `tenant_id` = `org` (mandatory, from URL)
- Results are always scoped to the tenant

## Tenant Isolation

All documents include `tenant_id`. Search queries always filter by `tenant_id` - no cross-tenant results.
