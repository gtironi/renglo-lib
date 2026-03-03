# search_controller.py - Search API with mandatory tenant isolation

from typing import Any, Dict, List, Optional

from renglo.search.search_index_service import SearchIndexService


class SearchController:
    """
    Search API controller. All searches require tenant_id - no cross-tenant results.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.search_index = SearchIndexService(config=self.config)

    def search(
        self,
        tenant_id: str,
        query: str,
        datatypes: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Full-text search with MANDATORY tenant_id filter.
        Never returns cross-tenant results.
        """
        if not self.search_index.is_enabled():
            return {
                'success': False,
                'message': 'Search is not configured',
                'items': [],
                'total': 0,
            }

        if not tenant_id:
            return {
                'success': False,
                'message': 'tenant_id is required',
                'items': [],
                'total': 0,
            }

        try:
            must = [{'term': {'tenant_id': tenant_id}}]

            if datatypes:
                must.append({'terms': {'datatype': datatypes}})

            if filters:
                for field, value in filters.items():
                    if isinstance(value, list):
                        must.append({'terms': {f'attributes.{field}': value}})
                    else:
                        must.append({'term': {f'attributes.{field}': value}})

            bool_query = {'must': must}

            if query and query.strip():
                bool_query['should'] = [
                    {'match': {'_search_text': {'query': query, 'operator': 'or'}}},
                ]
                bool_query['minimum_should_match'] = 1

            search_body = {
                'query': {'bool': bool_query},
                'from': offset,
                'size': min(limit, 100),
                '_source': ['tenant_id', 'datatype', 'portfolio', 'doc_id', 'doc_index', 'attributes', 'added', 'modified'],
                'sort': [{'_score': 'desc'}] if (query and query.strip()) else [{'modified': 'desc'}],
            }

            response = self.search_index.client.search(
                index=self.search_index.index_name,
                body=search_body,
            )

            hits = response.get('hits', {})
            total = hits.get('total', {})
            if isinstance(total, dict):
                total_count = total.get('value', 0)
            else:
                total_count = total

            items = []
            for hit in hits.get('hits', []):
                doc = hit.get('_source', {})
                doc['_score'] = hit.get('_score')
                items.append(doc)

            return {
                'success': True,
                'items': items,
                'total': total_count,
                'query': query,
            }
        except Exception as e:
            self.search_index.logger.error(f"Search failed: {e}")
            return {
                'success': False,
                'message': str(e),
                'items': [],
                'total': 0,
            }
