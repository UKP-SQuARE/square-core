from html import entities
import requests
from easy_conn import get_token, base_url
import json
from tqdm import auto


import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--name', required=True, help="Name of the KG")
args = parser.parse_args()

kg_name = args.name


nodes = {}
nids = {}
edges = []

with open('data/cpnet/conceptnet.en.csv', 'r') as f:
    for line in f:
        items = line.strip().split('\t')
        rel, head, tail, weight = items
        for entity_name in [head, tail]:
            if entity_name in nodes:
                continue

            nid = f'n{len(nodes)}'
            node = {
                'id': nid,
                'name': entity_name,
                'type': 'node',
                # 'description': '',
                'description': entity_name.replace('_', ' '),
                'weight': None,
                'in_id': None,
                'out_id': None,
                'in_out_id':None
            }
            nodes[entity_name] = node
            nids[entity_name] = nid
        
        eid = f'e{len(edges)}'
        edge = {
            'id': eid,
            'name': rel,
            'type': 'edge',
            'description': '',
            'weight': float(weight),
            'in_id': nids[head],
            'out_id': nids[tail],
            'in_out_id': nids[head]+"_"+nids[tail]
        }
        edges.append(edge)

for data in [list(nodes.values()), edges]:
    batch_size = 5000
    for b in auto.tqdm(range(0, len(data), batch_size)):
        response = requests.post(
            f'{base_url}/datastores/kg/{kg_name}/nodes',
            headers={
                "Authorization": f"Bearer {get_token()}"
            },
            json=data[b:b+batch_size]
        )
        print(response.json())