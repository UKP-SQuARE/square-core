#!/usr/bin/env python3
import json
import requests
import transformers

tokenizer = transformers.DPRQuestionEncoderTokenizer.from_pretrained('facebook/dpr-question_encoder-single-nq-base')
model = transformers.DPRQuestionEncoder.from_pretrained('facebook/dpr-question_encoder-single-nq-base')
pipeline = transformers.Pipeline(model=model, tokenizer=tokenizer)


def query(query_text, index="dpr", hits=10):
    if index == "bm25":
        yql = "select * from sources wiki where userQuery();"
    elif index == "dpr":
        yql = 'select * from sources wiki where ([{"targetNumHits":100, "hnsw.exploreAdditionalHits":100}]nearestNeighbor(dpr_embedding,dpr_query_embedding)) or userQuery();'
    else:
        raise ValueError()

    query_embedding = pipeline([query_text])[0].tolist() + [0]
    json_request = {
        "query": query_text,
        "type": "any",
        "yql": yql,
        "hits": hits,
        "ranking.features.query(dpr_query_embedding)": query_embedding,
        "ranking.profile": index
    }

    r = requests.post('http://localhost:7070/search/', json=json_request)
    response = r.json()
    return response


if __name__ == '__main__':
    while True:
        query_text = input("Insert query: ")
        response = query(query_text)
        print(json.dumps(response, indent=4))
