from ..models.query import QueryResult
import requests
from trafilatura import extract
from trafilatura.settings import use_config
import concurrent.futures
from typing import Tuple, Dict, List
from collections import defaultdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import aiohttp
import asyncio
from .config import settings

import logging
logger = logging.getLogger(__name__)

class BingSearch:
    """Wraps access to the Bing Search API."""

    datastore_name = "bing_search"

    def __init__(self):
        self.subscription_key = settings.BING_KEY
        self.search_url = "https://api.bing.microsoft.com/v7.0/search"
        self.headers = {"Ocp-Apim-Subscription-Key": self.subscription_key}
        self.min_search_pages = 1
        self.max_search_pages = 50

    def __process_html(self, doc: Tuple[str, str]) -> Dict[str, str]:
        """
        Extracts text from html using trafilatura.
        doc: Tuple[str, str] = (url, html)
        returns: Dict[str, str] = {url: text}
        """

        # set configuration for trafilatura
        new_config = use_config()
        new_config.set('DEFAULT', 'EXTRACTION_TIMEOUT', "0") # must be zero
        
        # provide error message in case the website was fetched but no text was extracted
        text = "Error downloading or processing document."
        if type(doc[1]) == type('') and doc[1] != "":
            text = extract(doc[1], include_comments=False, include_formatting=False, no_fallback=True, include_tables=False, config=new_config)
            if type(text) == type(''):
                text = text.replace("\n", " ")
            else: 
                text = "Error downloading or processing document."

        return {doc[0]: text}

    async def __web_scrape_task(self, url: str) -> Dict[str, str]:
        """
        Downloads the html for the given url.
        params: url: str
        returns: Dict[str, str] = {url: html}
        """
        async with aiohttp.ClientSession() as session:
            timeout = aiohttp.ClientTimeout(total=5)
            try:
                async with session.get(url, timeout=timeout) as resp:
                    content = await resp.text()
                    return {url: content}
            except Exception as e:
                logger.error(f"Error downloading {url}: {e}")
                return {url: ""}


    async def __download_pages(self, urls: List[str]) -> List[Dict[str, str]]:
        """
        Downloads the html for the given urls in parallel.
        params: urls: List[str]
        returns: List[Dict[str, str]] = [{url: html}]
        """
        tasks = []
        for url in urls:
            tasks.append(self.__web_scrape_task(url))
        return await asyncio.gather(*tasks)


    async def search(self, query: str, count=10, region: str = None):
        """Searches Bing for the given query and returns a list of QueryResults."""

        if count > self.max_search_pages: count = self.max_search_pages
        elif count < self.min_search_pages: count = self.min_search_pages

        # call Bing API to get urls 
        params = {"q": query, "textDecorations": True, "textFormat": "HTML", "count": count, "mkt": region}
        response = requests.get(self.search_url, headers=self.headers, params=params)
        response.raise_for_status()
        search_results = response.json()

        # create a dictionary of urls and their search results
        values_dict = {} # values_dict[url] = search result
        [values_dict.update({result['url']: result}) for result in search_results["webPages"]["value"]]

        # download html in parallel
        docs = dict() # docs[url] = html
        dicts = await self.__download_pages(values_dict.keys())
        [docs.update(d) for d in dicts]

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
                    "text": texts[url]
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
            {'verb': 'GET', 'path': f'/datastores/{BingSearch.datastore_name}/indices'},
        ]
        if path.startswith(f"/datastores/{BingSearch.datastore_name}") \
        and not any([path == p['path'] and request.method == p['verb'] for p in allowed_paths]):
            return Response(status_code=404, content="This operation is not supported for the Bing Search datastore.")

        return await call_next(request)
