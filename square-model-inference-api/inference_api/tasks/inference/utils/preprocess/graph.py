import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import torch
# from multiprocessing import Pool
from billiard.pool import Pool
from scipy.sparse import coo_matrix
from tqdm import tqdm

concept2id = None
id2concept = None


cpnet = None
cpnet_all = None
cpnet_simple = None

merged_relations = [
    "antonym",
    "atlocation",
    "capableof",
    "causes",
    "createdby",
    "isa",
    "desires",
    "hassubevent",
    "partof",
    "hascontext",
    "hasproperty",
    "madeof",
    "notcapableof",
    "notdesires",
    "receivesaction",
    "relatedto",
    "usedfor",
]

id2relation = merged_relations
relation2id = {r: i for i, r in enumerate(id2relation)}


def concepts2adj(node_ids):
    cids = np.array(node_ids, dtype=np.int32)
    n_rel = len(id2relation)
    n_node = cids.shape[0]
    adj = np.zeros((n_rel, n_node, n_node), dtype=np.uint8)
    for s in range(n_node):
        for t in range(n_node):
            s_c, t_c = cids[s], cids[t]
            if cpnet.has_edge(s_c, t_c):
                for e_attr in cpnet[s_c][t_c].values():
                    # print("edge attributes:", e_attr)
                    if e_attr["rel"] >= 0 and e_attr["rel"] < n_rel:
                        adj[e_attr["rel"]][s][t] = 1
    # cids += 1  # note!!! index 0 is reserved for padding
    adj = coo_matrix(adj.reshape(-1, n_node))
    return adj, cids


def get_LM_score(cids, question, model, tokenizer):
    cids = cids[:]
    cids.insert(0, -1)  # QAcontext node
    sents, scores = [], []
    sents = [
        tokenizer.encode(question.lower(), add_special_tokens=True)
        if cid == -1
        else tokenizer.encode(
            "{} {}.".format(question.lower(), " ".join(id2concept[cid].split("_"))),
            add_special_tokens=True,
        )
        for cid in cids
    ]
    n_cids = len(cids)
    # print(n_cids)
    cur_idx = 0
    batch_size = 128
    while cur_idx < n_cids:
        # Prepare batch
        input_ids = sents[cur_idx : cur_idx + batch_size]
        max_len = max([len(seq) for seq in input_ids])
        for j, seq in enumerate(input_ids):
            seq += [tokenizer.pad_token_id] * (max_len - len(seq))
            input_ids[j] = seq
        input_ids = torch.tensor(input_ids)
        mask = (input_ids != 1).long()
        # Get LM score
        with torch.no_grad():
            outputs = model(input_ids, attention_mask=mask, masked_lm_labels=input_ids)
            loss = outputs[0]  # [B, ]
            _scores = list(-loss.detach().cpu().numpy())
        scores += _scores
        cur_idx += batch_size
    assert len(sents) == len(scores) == len(cids)
    cid2score = OrderedDict(
        sorted(list(zip(cids, scores)), key=lambda x: -x[1])
    )  # score: from high to low

    return cid2score


def concepts_to_adj_matrices_part1(data):
    qc_ids, ac_ids, question = data
    qa_nodes = set(qc_ids) | set(ac_ids)
    extra_nodes = set()

    for qid in qa_nodes:
        for aid in qa_nodes:
            if qid != aid and qid in cpnet_simple.nodes and aid in cpnet_simple.nodes:
                extra_nodes |= set(cpnet_simple[qid]) & set(
                    cpnet_simple[aid]
                )  # list of node ids
    extra_nodes = extra_nodes - qa_nodes

    return (sorted(qc_ids), sorted(ac_ids), question, sorted(extra_nodes))


def concepts_to_adj_matrices_part3(data):
    qc_ids, ac_ids, question, extra_nodes, cid2score = data
    schema_graph = (
        qc_ids + ac_ids + sorted(extra_nodes, key=lambda x: -cid2score[x])
    )  # score: from high to low
    arange = np.arange(len(schema_graph))
    qmask = arange < len(qc_ids)
    amask = (arange >= len(qc_ids)) & (arange < (len(qc_ids) + len(ac_ids)))
    # print("schema: ", schema_graph)
    adj, concepts = concepts2adj(schema_graph)
    return {
        "adj": adj,
        "concepts": concepts,
        "qmask": qmask,
        "amask": amask,
        "cid2score": cid2score,
    }


def generate_adj_data_from_grounded_concepts__use_LM(
    statements,
    grounded,
    concept2id,
    _cpnet_vocab,
    _cpnet,
    _cpnet_simple,
    model,
    tokenizer,
    num_processes=1,
):
    """
    This function will save
        (1) adjacency matrices (each in the form of
            a (R*N, N) coo sparse matrix)
        (2) concepts ids
        (3) qmask that specifies whether a node is a question concept
        (4) amask that specifies whether a node is an answer concept
        (5) cid2score that maps a concept id to its
            relevance score given the QA context
    to the output path in python pickle format

    statement_json: json (dict)
    grounded: 5 dicts as
    cpnet_graph_path: str
    cpnet_vocab_path: str

    num_processes: int
    """
    # print(concept2id)
    global cpnet
    cpnet = _cpnet
    del _cpnet

    global cpnet_simple
    cpnet_simple = _cpnet_simple
    del _cpnet_simple

    global id2concept
    id2concept = _cpnet_vocab
    del _cpnet_vocab

    qa_data = []
    for ex in grounded:
        # use API to get q_ids and a_ids (?)
        # API input :  entity, output : id
        q_ids = set(concept2id[c] for c in ex["qc"])
        a_ids = set(concept2id[c] for c in ex["ac"])
        q_ids = q_ids - a_ids
        QAcontext = "{} {}.".format(statements["question"], ex["ans"])
        qa_data.append((q_ids, a_ids, QAcontext))

    # start = time.time()
    with Pool(num_processes) as p:
        res1 = list(
            tqdm(p.imap(concepts_to_adj_matrices_part1, qa_data), total=len(qa_data))
        )

    global concepts_to_adj_matrices_part2

    def concepts_to_adj_matrices_part2(data):
        qc_ids, ac_ids, question, extra_nodes = data
        cid2score = get_LM_score(
            qc_ids + ac_ids + extra_nodes, question, model, tokenizer
        )
        return (qc_ids, ac_ids, question, extra_nodes, cid2score)

    workers = 5
    with ThreadPoolExecutor(workers) as pool:
        res2 = list(pool.map(concepts_to_adj_matrices_part2, res1))

    with Pool(num_processes) as p:
        res3 = list(tqdm(p.imap(concepts_to_adj_matrices_part3, res2), total=len(res2)))
    # print(f"concepts_to_adj_matrices_2hop_all_pair__use_LM__Part3 takes {end-start}")

    return res3
