import json

from kg_utils import Predicate, post_process, query_virtuoso
from square_model_client import SQuAREModelClient
from square_skill_api.models import QueryOutput, QueryRequest
from value_class import ValueClass

square_model_client = SQuAREModelClient()

# this is the standard input that will be given to every predict function.
# See the details in the `square_skill_api` package for all available inputs.
async def predict(
    request: QueryRequest,
) -> QueryOutput:

    # prepare the request to the Model API. For details, see Model API docs
    model_request = {
        "input": [request.query],
        "task_kwargs": {"max_length": 500},
        "adapter_name": "",
    }

    # Call Model using the `model_api` object
    model_response = await square_model_client(
        model_name="BART_SPARQL_KQAPro",
        pipeline="generation",
        model_request=model_request,
    )
    sparql: str = model_response["generated_texts"][0][0]

    # process generated sparql before querying KG.
    sparql = post_process(sparql)
    answer = get_sparql_answer(sparql)
    model_response["answer"] = [answer]
    model_response["question"] = [request.query]

    return QueryOutput.from_generation(
        questions=request.query, model_api_output=model_response
    )


def get_sparql_answer(sparql: str, rel2type="./skill/relation2type.json"):
    """
    this function has two componets: post-process sparql and query it against a KG.
    """
    with open(rel2type, "r") as f:
        relation2type = json.load(f)

    try:
        # infer the parse_type based on sparql
        if sparql.startswith("SELECT DISTINCT ?e") or sparql.startswith("SELECT ?e"):
            parse_type = "name"
        elif sparql.startswith("SELECT (COUNT(DISTINCT ?e)"):
            parse_type = "count"
        elif sparql.startswith("SELECT DISTINCT ?p "):
            parse_type = "pred"
        elif sparql.startswith("ASK"):
            parse_type = "bool"
        else:
            tokens = sparql.split()
            tgt = tokens[2]
            for i in range(len(tokens) - 1, 1, -1):
                if tokens[i] == "." and tokens[i - 1] == tgt:
                    key = tokens[i - 2]
                    break
            key = key[1:-1].replace("_", " ")
            t = relation2type[key]
            parse_type = "attr_{}".format(t)

        parsed_answer = None
        res = query_virtuoso(sparql)

        if res.vars:
            res = [[binding[v] for v in res.vars] for binding in res.bindings]
            if len(res) != 1:
                return None
        else:
            res = res.askAnswer
            assert parse_type == "bool"

        if parse_type == "name":
            node = res[0][0]
            sp = "SELECT DISTINCT ?v WHERE {{ <{}> <{}> ?v .  }}".format(
                node, Predicate.PRED_NAME
            )
            res = query_virtuoso(sp)
            res = [[binding[v] for v in res.vars] for binding in res.bindings]
            name = res[0][0].value
            parsed_answer = name
        elif parse_type == "count":
            count = res[0][0].value
            parsed_answer = str(count)
        elif parse_type.startswith("attr_"):
            node = res[0][0]
            v_type = parse_type.split("_")[1]
            unit = None
            if v_type == "string":
                sp = "SELECT DISTINCT ?v WHERE {{ <{}> <{}> ?v .  }}".format(
                    node, Predicate.PRED_VALUE
                )
            elif v_type == "quantity":
                # Note: For those large number, ?v is truncated by virtuoso (e.g., 14756087 to 1.47561e+07)
                # To obtain the accurate ?v, we need to cast it to str
                sp = "SELECT DISTINCT ?v,?u,(str(?v) as ?sv) WHERE {{ <{}> <{}> ?v ; <{}> ?u .  }}".format(
                    node, Predicate.PRED_VALUE, Predicate.PRED_UNIT
                )
            elif v_type == "year":
                sp = "SELECT DISTINCT ?v WHERE {{ <{}> <{}> ?v .  }}".format(
                    node, Predicate.PRED_YEAR
                )
            elif v_type == "date":
                sp = "SELECT DISTINCT ?v WHERE {{ <{}> <{}> ?v .  }}".format(
                    node, Predicate.PRED_DATE
                )
            else:
                raise Exception("unsupported parse type")
            res = query_virtuoso(sp)
            res = [[binding[v] for v in res.vars] for binding in res.bindings]
            # if there is no specific date, then convert the type to year
            if len(res) == 0 and v_type == "date":
                v_type = "year"
                sp = "SELECT DISTINCT ?v WHERE {{ <{}> <{}> ?v .  }}".format(
                    node, Predicate.PRED_YEAR
                )
                res = query_virtuoso(sp)
                res = [[binding[v] for v in res.vars] for binding in res.bindings]
            if v_type == "quantity":
                value = float(res[0][2].value)
                unit = res[0][1].value
            else:
                value = res[0][0].value
            value = ValueClass(v_type, value, unit)
            parsed_answer = str(value)
        elif parse_type == "bool":
            parsed_answer = "yes" if res else "no"
        elif parse_type == "pred":
            parsed_answer = str(res[0][0])
            parsed_answer = parsed_answer.replace("_", " ")
        return parsed_answer
    except Exception as e:
        raise e
