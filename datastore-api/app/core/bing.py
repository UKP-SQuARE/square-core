import os
import requests
from trafilatura import fetch_url, extract
from trafilatura.settings import use_config
from ..models.query import QueryResult


class BingSearch:
    """Wraps access to the Bing Search API."""

    def __init__(self):
        #TODO: make sure to set the environment variable BING_SEARCH_KEY in your .env file
        self.subscription_key = os.environ.get("BING_SEARCH_KEY")
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
        new_config.set('DEFAULT', 'EXTRACTION_TIMEOUT', "5") # 5 seconds timeout
        for i, result in enumerate(search_results["webPages"]["value"]):
            doc = fetch_url(result["url"])
            text = extract(doc, include_comments=False, include_formatting=False,
                           no_fallback=True, include_tables=False, config=new_config)
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