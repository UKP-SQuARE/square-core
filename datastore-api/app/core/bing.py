from ..models.query import QueryResult
import requests
from trafilatura import extract
from trafilatura.downloads import add_to_compressed_dict, buffered_downloads, load_download_buffer
from trafilatura.settings import use_config
import concurrent.futures
from typing import Tuple, Dict
from collections import defaultdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class BingSearch:
    """Wraps access to the Bing Search API."""

    datastore_name = "bing_search"

    def __init__(self):
        # TODO: make sure to set the environment variable BING_SEARCH_KEY in your .env file
        self.subscription_key = "e7f1863c98084549951c5c80ee702d72"
        self.search_url = "https://api.bing.microsoft.com/v7.0/search"
        self.headers = {"Ocp-Apim-Subscription-Key": self.subscription_key}

    def __process_html(self, doc: Tuple[str, str]) -> Dict[str, str]:
        """
        Extracts text from html using trafilatura.
        doc: Tuple[str, str] = (url, html)
        """

        # set configuration for trafilatura
        new_config = use_config()
        new_config.set('DEFAULT', 'EXTRACTION_TIMEOUT', "0") # must be zero
        
        # provide error message in case the website was fetched but no text was extracted
        text = "Website fetch failed."
        if type(doc[1]) == type('') and doc[1] != "":
            text = extract(doc[1], include_comments=False, include_formatting=False, no_fallback=True, include_tables=False, config=new_config)

        return {doc[0]: text}


    async def search(self, query: str, count=10):
        """Searches Bing for the given query and returns a list of QueryResults."""

        if count > 50:
            count = 50
        elif count < 1:
            count = 1

        # call Bing API to get urls 
        params = {"q": query, "textDecorations": True, "textFormat": "HTML", "count": count}
        response = requests.get(self.search_url, headers=self.headers, params=params)
        response.raise_for_status()
        search_results = response.json()


        # create a dictionary of urls and their search results
        values_dict = {} # values_dict[url] = search result
        [values_dict.update({result['url']: result}) for result in search_results["webPages"]["value"]]


        # download the html for each url in parallel
        threads = count
        backoff_dict = dict()
        dl_dict = add_to_compressed_dict(values_dict.keys()) # values_dict.keys() = urls
        docs = dict() # docs[url] = html
        while dl_dict:
            buffer, threads, dl_dict, backoff_dict = load_download_buffer(dl_dict, backoff_dict)
            for url, html in buffered_downloads(buffer, threads):
                docs.update({url: html})


        # extract text from html in parallel
        # provide error message again in case the a website url was not used at all
        texts = defaultdict(lambda: "Website fetch failed.") # texts[url] = text
        with concurrent.futures.ThreadPoolExecutor() as executor: 
            futures = [executor.submit(self.__process_html, doc) for doc in docs.items()]
            [texts.update(future.result()) for future in futures]


        # create a list of QueryResults
        results = [] # list of QueryResults
        for i, (url, values) in enumerate(values_dict.items()): 
            results.append(QueryResult(
                document={
                    "id": url,
                    "title": values["name"],
                    "text": texts[url],
                },
                score = (len(texts) - i) / len(texts),
                id= url
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
