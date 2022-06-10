import json
import logging
from typing import Dict, Iterable, List, Optional, Tuple


import elasticsearch.exceptions
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk, async_scan


from ...core.config import settings
from ...models.datastore import Datastore
from ...models.document import Document
from ...models.index import Index
from ...models.query import QueryResult
from ...models.stats import DatastoreStats
from .class_converter import ElasticsearchClassConverter

from ...core.es.connector import ElasticsearchConnector
from .class_converter import KnowledgeGraphClassConverter

logger = logging.getLogger(__name__)


class KnowledgeGraphConnector(ElasticsearchConnector):
    """Provides a connector for an KnowledgeGraphConnector backend."""

    datastore_suffix = "-kg-docs"
    datastore_search_suffix = "-kg-search-indices"    

    def __init__(self, host: str):
        """Initializes a new instance of KnowledgeGraphConnector.

        Args:
            host (str): Hostname of the Elasticsearch instance.
        """
        super().__init__(converter=KnowledgeGraphClassConverter(), host=host)


    async def get_kgs(self) -> List[Datastore]:
        """Returns a list of all knowledge graphs."""
        return await self.get_datastores()
        
    async def get_kg(self, kg_name: str) -> Optional[Datastore]:
        """Returns a knowledge graph by name.

        Args:
            kg_name (str): Name of the knowledge graph.
        """
        return await self.get_datastore(kg_name)

    async def add_kg(self, kg_name: Datastore) -> bool:
        """Adds a new knowledge graph.

        Args:
            Knowledge graph (Datastore): Knowledge graph to add.
        """
        return await self.add_datastore(kg_name)

    async def delete_kg(self, kg_name: Datastore) -> bool:
        """Deletes a knowledge graph.

        Args:
            kg_name (str): Name of the knowledge graph.
        """
        return await self.delete_datastore(kg_name)
        
    async def get_kg_stats(self, kg_name: Datastore) -> bool:
        """Returns statistics about a knowledge graph.

        Args:
            kg_name (str): Name of the knowledge graph.
        """
        return await self.get_datastore_stats(kg_name)

    ###  QUERIES
    async def get_all_relations(self, kg_name: Datastore) -> List[Dict[str,int]]:
        """Returns all relation names about a knowledge graph.

        Args:
            kg_name (str): Name of the knowledge graph.
        """
        docs_index = self._datastore_docs_index_name(kg_name)
        body = {
            "aggs": {
                "all_relations": {            
                    "filter": {
                        "term": {"type": 'edge'},
                    },
                    "aggs": {
                        "name": {
                            "terms": {"field": "name", "size": 10000}
                        }
                    }
                }
            }
        } 
        results = await self.es.search(index=docs_index, body=body)
        relations = results['aggregations']['all_relations']
        return relations

    async def get_node_by_name(self, kg_name, node_name):
        """Returns all relation names about a knowledge graph.

        Args:
            kg_name (str):      Name of the knowledge graph.
            node_name (str):    Name of the node.
        """
        docs_index = self._datastore_docs_index_name(kg_name)
        body = {
            "query": {
                "bool": {
                    "filter": {
                        "bool" : {
                            "must" : [
                                {"term" : { "name" : node_name } },
                                {"term" : { "type" : "node" } },
                            ]
                        }
                    }
                }
            }
        }  # 'must' for AND clause
        results = await self.es.search(index=docs_index, body=body, size=10000)
        nids = [hit['_id'] for hit in results["hits"]["hits"]]
        return nids

    async def edges_from_msearch(self, kg_name, nids):
        """Returns all edges names about a knowledge graph.

        Args:
            kg_name (str):      Name of the knowledge graph.
            node_name (str):    Name of the node.
        """
        index = f'{kg_name}{self.datastore_suffix}'

        body = []
        for nid in nids:
            body.append({'index': index})
            body.append({
                "query": {
                    "bool": {
                        "filter": {
                            "bool" : {
                                "should" : [
                                    {"term" : { "in_id" : nid } },
                                    # {"term" : { "out_id" : nid } },
                                ]
                            }
                        }
                    }
                },
                "size": 10000
            })

        response = await self.es.msearch(body=body)

        results = {}
        for nid, response in zip(nids, response['responses']):
            edges = {hit['_id']: dict(hit['_source'], **{'_id': hit['_id']}) for hit in response["hits"]["hits"]}

            results[nid] = edges
        return results

    async def get_object_by_id_msearch(self, kg_name, ids):
        """Returns all nodes/edges for the given ids.

        Args:
            kg_name (str):      Name of the knowledge graph.
            ids (List[str]):    List of names of the nodes.
        """
        index = f'{kg_name}{self.datastore_suffix}'
        result = await self.es.mget(index=index, body={'ids': list(ids)})
        objs = {}
        for obj in result['docs']:
            objs[obj['_id']] = dict(obj['_source'], **{'_id': obj['_id']})

        return objs

    async def extract_subgraph(self, kg_name, nids: List[str], hops=2):
        """Returns a subgraph as a Set of nodes and edges.

        Args:
            kg_name (str):      Name of the knowledge graph.
            nids (List[node]):  List of nodes.
            hops (int):         Number of hops.
        """
        assert hops >= 1
        # nids = sorted(list(set(nids)))
        nids = set(nids)

        nid2edges = await self.edges_from_msearch(kg_name, nids)
        paths = []
        for edges in nid2edges.values():
            for edge in edges.values():
                paths.append([edge])

        paths_closed = []  # Represent the paths with both ends in nids
        for _ in range(1, hops):
            # Get the frontier node for each path
            # If a froniter node reaches one of the nids, 
            # the path will be included in the final results
            frontier =  [path[-1]['out_id'] for path in paths]
            for out_id, path in zip(frontier, paths):
                if out_id in nids:
                    paths_closed.append(path)

            # Search along all the paths
            nid2edges = await self.edges_from_msearch(kg_name, set(frontier))
            paths_extended = []
            for i, nid in enumerate(frontier):
                edges = nid2edges[nid]
                path = paths[i]
                paths_extended.extend([path + [e] for e in edges.values()])  # One step forward
            paths = paths_extended
        # Check again the frontier nodes
        frontier =  [path[-1]['out_id'] for path in paths]
        for out_id, path in zip(frontier, paths):
            if out_id in nids:
                paths_closed.append(path)

        edges = {}
        for path in paths_closed:
            for edge in path:
                edges[edge['_id']] = edge

        for edge in edges.values():
            nids.add(edge['in_id'])
            nids.add(edge['out_id'])

        nodes = await self.get_object_by_id_msearch(kg_name, nids)

        return nodes, edges

    async def get_node_by_name_msearch(self, kg_name, names):
        """Returns a List of nodes for the given name.

        Args:
            kg_name (str):      Name of the knowledge graph.
            names (List[str]):   List of names of the nodes.
        """
        index = f'{kg_name}{self.datastore_suffix}'
        body = []
        for name in names:
            body.append({'index': index})
            body.append({
                "query": {
                    "bool": {
                        "filter": {
                            "bool" : {
                                "must" : [
                                    {"term" : { "name" : name } },
                                    {"term" : { "type" : "node" } },
                                ]
                            }
                        }
                    }
                },
                "size": 10000
            })  # 'must' for AND clause
        responses = await self.es.msearch(body=body)

        results = []        
        for response in responses['responses']:
            nids = [hit['_id'] for hit in response["hits"]["hits"]]
            results.append(nids)
        return results

    async def extract_subgraph_by_names(self, kg_name, names, hops=2):
        """Returns a subgraph as a Set of nodes and edges.

        Args:
            kg_name (str):      Name of the knowledge graph.
            names (List[str]):  List of names of the nodes.
            hops (int):         Number of hops.
        """
        nids = set()
        for _nids in await self.get_node_by_name_msearch(kg_name, names):
            nids.update(_nids)
        
        return await self.extract_subgraph(kg_name, nids, hops)