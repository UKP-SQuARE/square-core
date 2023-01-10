import requests
import json
import concurrent.futures
from typing import Tuple, Dict, List
from collections import defaultdict
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import aiohttp
import asyncio

import logging
logger = logging.getLogger(__name__)

class WikiData:
    """Wraps access to the Bing Search API."""

    kg_name = "wikidata"    

    def __init__(self):
        self.sparql_url = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"

    def __json_to_doubles(self, data):
        result = []
        for line in data['results']['bindings']:
            value_line=()
            # BUG: MAYBE TO BIG
            for value in line.values():
                value_line += (value['value'],)
            result.append(value_line)
        return result

    async def is_alive(self):
        return True

    async def get_entity_by_names(self, names: list):
        '''
        names - A list of the names of the preferred label
        Return - List of all entites, which are found for the given name entity.
        '''
        queriefied_list = ""
        for name in names:
            queriefied_list += f"\"{name}\"@en "

        query = ''' SELECT ?item ?prefLabel
            WHERE {
                values ?prefLabel {'''+queriefied_list+'''}
                ?item rdfs:label|skos:altLabel ?prefLabel.
            }'''
        try:
            response = requests.get(self.sparql_url, params={'query': query, 'format': 'json'}).json()
            results = {name: [] for name in names}

            for res in response['results']['bindings']:
                results[res['prefLabel']['value']].append(res['item']['value'])

        except Exception as e:
            logger.error(f"Error searching WikiData for {query}: {e}")
            return {
                "error": f"Error searching WikiData for {query}"
            }

        return results

    async def get_edges_by_name(self, entity_pair_list: list):
        query = "select "
        for i, pair in enumerate(entity_pair_list):
            query += f"?relation{i} "
        query += " WHERE {"

        for i, pair in enumerate(entity_pair_list):
            if i != 0:
                query += " UNION "
            query += "{wd:"+pair[0]+ f"?relation{i} wd:"+pair[1]+" . }"
        query += " }"

        data = requests.get(self.sparql_url, params={'query': query, 'format': 'json'}).json()
        response_clean =  set(self.__json_to_doubles(data))

        return response_clean


    # Not finished
    async def get_subgraph_by_id(self, entity_id: str, hops = 2):
        
        query = '''select ''' + ' '.join(["?relation"+str(hop)+" ?obj"+str(hop) for hop in range(hops)]) + ''' where { wd:'''+str(entity_id)+" ?relation0 ?obj0 . " + ' . '.join(["?obj"+str(hop) +" ?relation"+str(hop+1)+" ?obj"+str(hop+1) for hop in range(hops-1)])+''' }'''

        data = requests.get(self.sparql_url, params={'query': query, 'format': 'json'}).json()
        return set(self.__json_to_doubles(data))


class WikiDataMiddleware(BaseHTTPMiddleware):

    def __init__(self, app) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        allowed_paths = [
            {'verb': 'POST', 'path': f'/datastores/kg/{WikiData.kg_name}/nodes/query_by_name'},
            {'verb': 'POST', 'path': f'/datastores/kg/{WikiData.kg_name}/subgraph/query_by_node_name'},
            {'verb': 'POST', 'path': f'/datastores/kg/{WikiData.kg_name}/edges/query_by_name'},
            {'verb': 'GET', 'path': f'/datastores/kg/{WikiData.kg_name}'},
        ]
        if path.startswith(f"/datastores/kg/{WikiData.kg_name}") \
        and not any([path == p['path'] and request.method == p['verb'] for p in allowed_paths]):
            return Response(status_code=404, content="This operation is not supported for the Wikidata knowledge graph.")

        wikidata = WikiData()
        try: 
            if path == f'/datastores/kg/{WikiData.kg_name}/nodes/query_by_name':
                response = await wikidata.get_entity_by_names(names = await request.json())
                return Response(status_code=200, content=str(response))

            elif path == f'/datastores/kg/{WikiData.kg_name}/subgraph/query_by_node_name':               
                response = await wikidata.get_entity_by_names(names = await request.json())
                return Response(status_code=200, content=str(response))

            elif path == f'/datastores/kg/{WikiData.kg_name}/edges/query_by_name':
                response = await wikidata.get_edges_by_name(entity_pair_list = await request.json())
                return Response(status_code=200, content=str(response))

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        # This should not be reached
        return await call_next(request)