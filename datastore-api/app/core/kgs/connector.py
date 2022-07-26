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
            nids (List[str]):   Node-pairs.
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

    async def edges_in_out_msearch(self, kg_name, nids):
        """Returns all edges which go either in or out from a knowledge graph.

        Args:
            kg_name (str):      Name of the knowledge graph.
            nids (List[str]):   List of nodes.
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
                                    {"term" : { "out_id" : nid } },
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

    async def extract_nodes(self,kg_name, nids):
        """Returns all nodes which go in or out a given node.

        Args:
            kg_name (str):          Name of the knowledge graph.
            nids (List[str]]):      List of nodes for which the in- and out-nodes should be retrieved.
        """
        edges = await self.edges_in_out_msearch(kg_name, nids)
        results_nids = [{} for _ in nids]
        for i,nid in enumerate(nids):
            extra_nodes =[]
            for edge in edges[nid]:
                if edges[nid][edge]["in_id"] == nid:
                    extra_node = edges[nid][edge]["out_id"]
                else:
                    extra_node = edges[nid][edge]["in_id"]
                extra_nodes.append(extra_node)
            results_nids[i] =  {nid:set(extra_nodes)}
        return results_nids
    
    async def get_nodes_for_nodepair(self, kg_name, nid_pair:Tuple[str, str]):
        """Returns all nodes in between for a given node_id-pair.

        Args:
            kg_name (str):                  Name of the knowledge graph.
            nid_pair (List[str,str]):      Node_id-pair.
        """
        index = f'{kg_name}{self.datastore_suffix}'
        body = []
        qid = nid_pair[0]
        aid = nid_pair[1]
        body.append({'index': index})
        body.append({
            "query": {
                "bool": {
                    "filter": {
                        "bool" : {
                            "should" : [
                                {"term" : { "in_id" : qid } },
                                {"term" : { "in_id" : aid } },
                                {"term" : { "out_id" : aid } },
                                {"term" : { "out_id" : qid } },
                            ]
                        }
                    }
                }
            },
            "size": 10000
        })
    
        response = await self.es.msearch(body=body)

        edges = {hit['_id']: dict(hit['_source'], **{'_id': hit['_id']}) for hit in response['responses'][0]["hits"]["hits"]}

        qid_list=[]
        aid_list=[]
        rest=[]
        for edge in edges.values():
            if edge['in_id']==qid:
                qid_list.append(edge['out_id'])
            elif edge['out_id']==qid:
                qid_list.append(edge['in_id'])
            elif edge['in_id']==aid:
                aid_list.append(edge['out_id'])
            elif edge['out_id']==aid:
                aid_list.append(edge['in_id'])
            else:
                rest.append(edge)
        extra_nodes = []
        for qids in qid_list:
            if qids in aid_list:
                extra_nodes.append(qids)

        return set(extra_nodes)

    async def get_nodes_for_nodepairs(self, kg_name, nid_pairs:Tuple[str, str]):
        """Returns all nodes in between a list of given node_id-pairs.

        Args:
            kg_name (str):                  Name of the knowledge graph.
            nid_pair (List[[str,str]]):     List of node_id-pairs.
        """
        results=[]
        for in_id, out_id in nid_pairs:
            results.append(await self.get_nodes_for_nodepair(kg_name, [in_id, out_id]))

        return results
    async def get_edge_msearch(self, kg_name, nids_pairs: List[Tuple[str, str]]):
        """Returns all edges for a given node-pair.

        Args:
            kg_name (str):                          Name of the knowledge graph.
            nids_pairs (List[Tuple[str, str]]):     Node-pair which is supposed to be retrieved.
        """
        index = f'{kg_name}{self.datastore_suffix}'
        body = []
        for in_id, out_id in nids_pairs:
            body.append({'index': index})
            body.append({
                "query": {
                    "bool": {
                        "filter": {
                            "bool" : {
                                "must" : [
                                    {"term" : { "in_id" : in_id } },
                                    {"term" : { "out_id" : out_id } },
                                ]
                            }
                        }
                    }
                }
            })
        responses = await self.es.msearch(body=body)
        found_edges = [{} for _ in nids_pairs]
        for response in responses['responses']:
            edges = {hit['_id']: dict(hit['_source'], **{'_id': hit['_id']}) for hit in response["hits"]["hits"]}
            for edge in edges.values():
                edge_in = edge['in_id']
                edge_out = edge['out_id']
                edge_in_out=[edge_in, edge_out]
                if edge_in != edge_out:
                    for i,in_out_id in enumerate(nids_pairs):
                        node_in_id = list(in_out_id)[0]
                        node_out_id = list(in_out_id)[1]
                        if node_in_id in edge_in_out and node_out_id in edge_in_out:
                            found_edges[i] = {edge['_id']:edge}           
        return found_edges

    async def get_relation(self, kg_name, nids_pairs: List[Tuple[str, str]]):
        """Returns relation-info for a given node-pair.

        Args:
            kg_name (str):                          Name of the knowledge graph.
            nids_pairs (List[Tuple[str, str]]):     Node-pair which is supposed to be retrieved.
        """
        edges = await self.get_edge_msearch(kg_name, nids_pairs)
        results=[]
        for edge in edges:
            relation_list=[]
            for edge_type in edge.values():
                if edge_type !=None:
                    relation_list.append({"relation-name":edge_type['name'], "weight":edge_type['weight']})
                else:
                    relation_list.append({"no edge"})
            results.append(relation_list)
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
            if obj['found']:
                objs[obj['_id']] = dict(obj['_source'], **{'_id': obj['_id']})
            else:
                logger.info("Not FOUND")
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
            kg_name (str):       Name of the knowledge graph.
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
        logger.info(responses)
        results = []        
        for response in responses['responses']:
            nids = [hit['_id'] for hit in response["hits"]["hits"]]
            results.append(nids)
        return results

    async def extract_subgraph_by_names(self, kg_name, nodes, hops=2):
        """Returns a subgraph as a Set of nodes and edges.

        Args:
            kg_name (str):      Name of the knowledge graph.
            names (List[str]):  List of names of the nodes.
            hops (int):         Number of hops.
        """
        nids = set()
        for _nids in await self.get_node_by_name_msearch(kg_name, nodes):
            nids.update(_nids)
        return await self.extract_subgraph(kg_name, nids, hops)

    async def extract_subgraph_by_ids(self, kg_name, nodes, hops=2):
        """Returns a subgraph as a Set of nodes and edges.

        Args:
            kg_name (str):      Name of the knowledge graph.
            nids (List[str]):   List of ids of the nodes.
            hops (int):         Number of hops.
        """
        return await self.extract_subgraph(kg_name, nodes, hops)
