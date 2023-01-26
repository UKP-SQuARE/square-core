import requests
import json
import concurrent.futures
from typing import Tuple, Dict, List
from collections import defaultdict
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import aiohttp
import asyncio

import logging
logger = logging.getLogger(__name__)

class WikiData:
    """Wraps access to the Bing Search API."""

    kg_name = "wikidata-kg"    

    def __init__(self):
        self.sparql_url = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"
        
    def __without_link(self, link):
        return link.split("/")[-1]

    async def is_alive(self):
        return True
    
    
    async def get_entity_by_names(self, names: list):
        '''
        names - A list of the names of the preferred label
        Return - List of all entites, which are found for the given name entity.
        '''
        querified_names = ""
        for name in names:
            querified_names += f" \"{name}\"@en "

        query = '''SELECT ?item ?name ?description 
            WHERE {
            VALUES ?name { '''+querified_names+''' }
            ?item rdfs:label ?name .
            OPTIONAL { ?item schema:description ?description. }
            FILTER(LANG(?description) = "en")
            SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }'''
        
        try:
            response = requests.get(self.sparql_url, params={'query': query, 'format': 'json'}).json()

            nodes = {}
            for res in response['results']['bindings']:
                node_temp =  {
                                "name": res['name']['value'],
                                "type": "node",
                                "description": res['description']['value'],
                                "weight": None,
                                "in_id": None,
                                "out_id": None,
                                "id": self._WikiData__without_link(res['item']['value'])
                            }
                nodes[self._WikiData__without_link(res['item']['value'])] = node_temp
            
        except Exception as e:
            logger.error(f"Error searching WikiData for {query}: {e}")
            return {
                "error": f"Error searching WikiData for {query}"
            }
    
        return nodes

    async def get_entity_by_ids(self, ids: list):
        '''
        names - A list of the entity ids
        Return - List of all entity-nodes, which are found for the given name entity-id.
        '''
        nids = ""
        for id in ids:
            nids += f" wd:{id} "

        query = '''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?entity ?label ?description
            WHERE {
            VALUES ?entity {'''+ nids+''' }
            ?entity rdfs:label ?label .
            OPTIONAL { ?entity schema:description ?description }
            FILTER(LANG(?label) = "en")
            FILTER(LANG(?description) = "en")
            }
            '''

        response = requests.get(self.sparql_url, params={'query': query, 'format': 'json'}).json()

        nodes = {}
        for res in response['results']['bindings']:
            node_temp =  {
                            "name": res['label']['value'],
                            "type": "node",
                            "description": res['description']['value'],
                            "weight": None,
                            "in_id": None,
                            "out_id": None,
                            "id": self._WikiData__without_link(res['entity']['value'])
                        }
            nodes[self._WikiData__without_link(res['entity']['value'])] = node_temp

        return nodes
  



    async def get_edges_for_id_pairs(self, entity_pair_list: list):
        '''
        entity_pair_list - List of entityID-pairs. E.g. [["Q32", "Q53"], ["Q32", "Q53"]]
        Return - List of edges in SQuARE-KG-Schema.
        '''

        query = "select"
        for i, pair in enumerate(entity_pair_list):
            query += f" ?relation{i} ?entOne{i} ?entTwo{i} ?h{i} ?h{i}Label ?h{i}Description ?h{i}AltLabel"
        query += " WHERE {"

        for i, pair in enumerate(entity_pair_list):
            if i != 0:
                query += " UNION "
            query += "{BIND(wd:"+pair[0]+ f" as ?entOne{i}) BIND(wd:"+pair[1]+ f" as ?entTwo{i}) ?entOne{i} ?relation{i} ?entTwo{i} . ?h{i} wikibase:directClaim ?relation{i} . }}"
        query += " SERVICE wikibase:label { bd:serviceParam wikibase:language '[AUTO_LANGUAGE],en'. }}"
        data = requests.get(self.sparql_url, params={'query': query, 'format': 'json'}).json()

        ids = [i for i in range(len(data['results']['bindings']))]

        edges = {}
        for rel in data['results']['bindings']:
            for i in ids:
                try:
                    edge_type = rel[f'relation{i}']['value']
                    edge_label = rel[f'h{i}Label']['value']
                    edge_description = rel[f'h{i}Description']['value']
                    entOne = self.__without_link(rel[f'entOne{i}']['value'])
                    entTwo = self.__without_link(rel[f'entTwo{i}']['value'])

                    # entity with link -> http://www.wikidata.org/entity/Q76
                    # entity without link -> Q76
                    id = entOne+"_"+entTwo
                    # egde_type with link -> http://www.wikidata.org/prop/direct/P39
                    # egde_type without link -> P39
                    edge = {
                        "id": id,
                        "name": edge_label,
                        "type": "node",
                        "description": self.__without_link(edge_type) + "; " + edge_description.replace("\"", "\-"),
                        "weight": None,
                        "in_id": entOne,
                        "out_id": entTwo,
                        "in_out_id":id
                    }
                    edges[id] = edge
                    break

                except Exception as e:
                    continue

        return edges


class WikiDataMiddleware(BaseHTTPMiddleware):

    def __init__(self, app) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        allowed_paths = [
            {'verb': 'POST', 'path': f'/datastores/kg/{WikiData.kg_name}/nodes/query_by_name'},
            {'verb': 'POST', 'path': f'/datastores/kg/{WikiData.kg_name}/nodes/query_by_ids'},
            {'verb': 'POST', 'path': f'/datastores/kg/{WikiData.kg_name}/edges/query_by_ids'},
            {'verb': 'GET', 'path': f'/datastores/kg/{WikiData.kg_name}'},
        ]
        if path.startswith(f"/datastores/kg/{WikiData.kg_name}") \
        and not any([path == p['path'] and request.method == p['verb'] for p in allowed_paths]) \
        and not path.startswith(f"/datastores/kg/{WikiData.kg_name}/Q"):
            return Response(status_code=404, content="This operation is not supported for the Wikidata knowledge graph.")

        wikidata = WikiData()
        try: 
            if path == f'/datastores/kg/{WikiData.kg_name}/nodes/query_by_name':
                response = await wikidata.get_entity_by_names(names = await request.json())
                return JSONResponse(status_code=200, content=response)

            elif  path == f'/datastores/kg/{WikiData.kg_name}/nodes/query_by_ids':
                return JSONResponse(status_code=200, content=await wikidata.get_entity_by_ids(ids = await request.json()))

            elif path == f'/datastores/kg/{WikiData.kg_name}/edges/query_by_ids':
                response = await wikidata.get_edges_for_id_pairs(entity_pair_list = await request.json())
                return JSONResponse(status_code=200, content=response)

            # This should only be used to search certain entities, saved as :
            # /datastores/kg/{WikiData.kg_name}/{entity_id}
            elif path.startswith(f'/datastores/kg/{WikiData.kg_name}/'):
                response = await wikidata.get_entity_by_ids([path.split("/")[-1]])
                return JSONResponse(status_code=200, content=response)
            
            elif path == f'/datastores/kg/{WikiData.kg_name}' :
                response = "Wikidata API is alive"
                return JSONResponse(status_code=200, content=response)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        # This should not be reached
        return await call_next(request)