#!/usr/bin/env python3

# Copyright Verizon Media. Licensed under the terms of the Apache 2.0 license. See LICENSE in the project root.

import os
import sys
import json
import requests
import transformers

tokenizer = transformers.DPRQuestionEncoderTokenizer.from_pretrained('facebook/dpr-question_encoder-single-nq-base')
model = transformers.DPRQuestionEncoder.from_pretrained('facebook/dpr-question_encoder-single-nq-base', return_dict=True)
pipeline = transformers.Pipeline(model=model, tokenizer=tokenizer)

def query(query_text, rank_profile='dense-retrieval', hits=40):
    query_embedding = pipeline([query_text])[0].tolist() + [0]
    json_request = {
        "query": query_text,
        "type": "any",
        "yql": 'select * from sources wiki where ([{"targetNumHits":100, "hnsw.exploreAdditionalHits":100}]nearestNeighbor(text_embedding,query_embedding)) or userQuery();',
        "hits": hits,
        "ranking.features.query(query_embedding)": query_embedding,
        "ranking.profile": rank_profile 
    }

    r = requests.post('http://localhost:8080/search/', json=json_request)
    r.raise_for_status() 
    response = r.json()
    return response


if __name__ == '__main__':
    while True:
        query_text = input()
        response = query(query_text)
        print(json.dumps(response, indent=4))


