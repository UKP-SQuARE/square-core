import re

import rdflib
from rdflib.plugins.stores import sparqlstore


class Predicate:
    gs1 = None
    PRED_INSTANCE = "pred:instance_of"
    PRED_NAME = "pred:name"

    PRED_VALUE = "pred:value"  # link packed value node to its literal value
    PRED_UNIT = "pred:unit"  # link packed value node to its unit

    PRED_YEAR = (
        "pred:year"  # link packed value node to its year value, which is an integer
    )
    PRED_DATE = "pred:date"  # link packed value node to its date value, which is a date

    PRED_FACT_H = "pred:fact_h"  # link qualifier node to its head
    PRED_FACT_R = "pred:fact_r"
    PRED_FACT_T = "pred:fact_t"

    # SPECIAL_PREDICATES = (PRED_INSTANCE, PRED_NAME, PRED_VALUE, PRED_UNIT, PRED_YEAR, PRED_DATE, PRED_FACT_H, PRED_FACT_R, PRED_FACT_T)


def post_process(text: str):
    pattern = re.compile(r'".*?"')
    nes = []
    for item in pattern.finditer(text):
        nes.append((item.group(), item.span()))
    pos = [0]
    for name, span in nes:
        pos += [span[0], span[1]]
    pos.append(len(text))
    assert len(pos) % 2 == 0
    assert len(pos) / 2 == len(nes) + 1
    chunks = [text[pos[i] : pos[i + 1]] for i in range(0, len(pos), 2)]
    for i in range(len(chunks)):
        chunks[i] = chunks[i].replace("?", " ?").replace(".", " .")
    bingo = ""
    for i in range(len(chunks) - 1):
        bingo += chunks[i] + nes[i][0]
    bingo += chunks[-1]
    return bingo


def query_virtuoso(
    q,
    endpoint="http://virtuoso.ukp.informatik.tu-darmstadt.de:8890/sparql",
    virtuoso_graph_uri="KQAPro",
):
    store = sparqlstore.SPARQLUpdateStore(endpoint)
    gs = rdflib.ConjunctiveGraph(store)
    gs.open((endpoint, endpoint))
    gs1 = gs.get_context(rdflib.URIRef(virtuoso_graph_uri))
    res = gs1.query(q)
    return res
