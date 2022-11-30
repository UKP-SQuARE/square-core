import os
import requests
from trafilatura import fetch_url, extract
from trafilatura.settings import use_config
from ..models.query import QueryResult
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio

class BingSearch:
    """Wraps access to the Bing Search API."""

    datastore_name = "bing_search"

    def __init__(self):
        # TODO: make sure to set the environment variable BING_SEARCH_KEY in your .env file
        self.subscription_key = "e7f1863c98084549951c5c80ee702d72"
        self.search_url = "https://api.bing.microsoft.com/v7.0/search"
        self.headers = {"Ocp-Apim-Subscription-Key": self.subscription_key}

    async def search(self, query, count=10):
        if count > 50:
            count = 50
        elif count < 1:
            count = 1
        params = {"q": query, "textDecorations": True,
                  "textFormat": "HTML", "count": count}
        response = requests.get(
            self.search_url, headers=self.headers, params=params)
        response.raise_for_status()
        search_results = response.json()
        results = []
        new_config = use_config()
        # setting this to anything but zero will raise an exception during testing
        new_config.set('DEFAULT', 'EXTRACTION_TIMEOUT', "0")
        urls = [result['url'] for i, result in enumerate(search_results["webPages"]["value"])]
        async def get_text(url: str):
            '''
            Wrap the fetch() and extract() as an async function to speed up

            '''
            doc = await fetch_url(url)
            text = await extract(doc, include_comments=False, include_formatting=False,
                                 no_fallback=True, include_tables=False, config=new_config)
            return text

        texts = [get_text(url) for url in urls]


        for i, (text, result) in enumerate(zip(texts, search_results["webPages"]["value"])):
            results.append(QueryResult(
                document={
                    "id": result["url"],
                    "title": result["name"],
                    "text": text,
                },
                score=(count - i) / count,
                id=result["url"]
            ))


        return results


class BingMiddleware(BaseHTTPMiddleware):

    def __init__(self, app) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        allowed_paths = [
            {'verb': 'GET', 'path': f'/datastores/{BingSearch.datastore_name}/search'},
            {'verb': 'GET', 'path': f'/datastores/{BingSearch.datastore_name}'},
        ]
        if path.startswith(f"/datastores/{BingSearch.datastore_name}") \
        and not any([path == p['path'] and request.method == p['verb'] for p in allowed_paths]):
            return Response(status_code=404, content="This operation is not supported for the Bing Search datastore.")

        return await call_next(request)
