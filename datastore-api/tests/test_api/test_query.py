import pytest
from app.core.db import DatastoreDB
from app.models.query import QueryResult, QueryResultDocument
from pytest_mock import MockerFixture
from vespa.application import Vespa, VespaResponse

from .utils import async_return


class TestQuery:
    @pytest.fixture
    def query_result(self, query_document):
        return QueryResult(
            coverage=100,
            covered_documents=2,
            documents=[QueryResultDocument(relevance=0, document=query_document)],
        )

    def test_search_bm25(self, mocker: MockerFixture, client, wiki_schema, bm25_index, query_document, query_result):
        mocker.patch.object(DatastoreDB, "get_schema", return_value=async_return(wiki_schema))
        mocker.patch.object(DatastoreDB, "get_index", return_value=async_return(bm25_index))
        mocker.patch.object(DatastoreDB, "get_index", return_value=async_return(bm25_index))
        reponse = VespaResponse({'root': {'id': 'toplevel', 'relevance': 1.0, 'fields': {'totalCount': 1}, 'coverage': {'coverage': 100, 'documents': 2, 'full': True, 'nodes': 1, 'results': 1, 'resultsFull': 1}, 'children': [{'id': 'id:wiki:wiki::2', 'relevance': 0.6682932975916605, 'source': 'square_datastore_content', 'fields': {'sddocname': 'wiki', 'documentid': 'id:wiki:wiki::2', 'title': 'document title', 'text': 'document containing the query word quack', 'id': 2}}]}}, 200, "", "")
        mocker.patch.object(Vespa, "query", return_value=reponse)

        response = client.get(
            "/datastores/wiki/indices/{}/search".format(bm25_index.name),
            params={"query": "quack"},
        )
        assert response.status_code == 200
        assert response.json()["coverage"] == query_result.coverage
        assert len(response.json()["documents"]) == len(query_result.documents)
        assert response.json()["documents"][0]["document"] == query_result.documents[0].document.__root__

    def test_search_not_found(self, mocker: MockerFixture, client, wiki_schema):
        mocker.patch.object(DatastoreDB, "get_schema", return_value=async_return(wiki_schema))
        mocker.patch.object(DatastoreDB, "get_index", return_value=async_return(None))
        response = VespaResponse({}, 404, "", "")
        mocker.patch.object(Vespa, "query", return_value=response)

        response = client.get(
            "/datastores/wiki/indices/unknown_index/search",
            params={"query": "quack"},
        )
        assert response.status_code == 404
        assert "detail" in response.json()

    def test_score(self, mocker: MockerFixture, client, wiki_schema, bm25_index, query_document, query_result):
        mocker.patch.object(DatastoreDB, "get_schema", return_value=async_return(wiki_schema))
        mocker.patch.object(DatastoreDB, "get_index", return_value=async_return(bm25_index))
        reponse = VespaResponse({'root': {'id': 'toplevel', 'relevance': 1.0, 'fields': {'totalCount': 1}, 'coverage': {'coverage': 100, 'documents': 2, 'full': True, 'nodes': 1, 'results': 1, 'resultsFull': 1}, 'children': [{'id': 'id:wiki:wiki::2', 'relevance': 0.6682932975916605, 'source': 'square_datastore_content', 'fields': {'sddocname': 'wiki', 'documentid': 'id:wiki:wiki::2', 'title': 'document title', 'text': 'document containing the query word quack', 'id': 2}}]}}, 200, "", "")
        mocker.patch.object(Vespa, "query", return_value=reponse)

        response = client.get(
            "/datastores/wiki/indices/{}/score".format(bm25_index.name),
            params={"query": "quack", "doc_id": query_document["id"]},
        )
        assert response.status_code == 200
        assert "document" in response.json()
        assert response.json()["document"] == query_result.documents[0].document.__root__

    def test_score_not_found(self, mocker: MockerFixture, client, wiki_schema, bm25_index):
        mocker.patch.object(DatastoreDB, "get_schema", return_value=async_return(wiki_schema))
        mocker.patch.object(DatastoreDB, "get_index", return_value=async_return(bm25_index))
        reponse = VespaResponse({'root': {'id': 'toplevel', 'relevance': 1.0, 'fields': {'totalCount': 0}, 'coverage': {'coverage': 100, 'documents': 2, 'full': True, 'nodes': 1, 'results': 1, 'resultsFull': 1}}}, 200, "", "")
        mocker.patch.object(Vespa, "query", return_value=reponse)

        response = client.get(
            "/datastores/wiki/indices/{}/score".format(bm25_index.name),
            params={"query": "quack", "doc_id": 99999},
        )
        assert response.status_code == 404
        assert "detail" in response.json()
