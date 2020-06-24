from flask import Blueprint, jsonify, request

api = Blueprint("api", __name__)


def _to_result(text):
    return {"type": "plain_text", "result": text}


@api.route("/query", methods=["POST"])
def query():
    """
    Endpoint to query the skill with a question
    :return:
    """
    question = request.json["question"]
    options = request.json["options"]

    maxRes = options["maxResults"]

    # A key_value result
    result = [{"type": "key_value", "result": [("Title", "The title"), ("Question", question)]}]
    # A raw_html result
    result += [{"type": "raw_html", "result": "<p class='text-muted'>Harmless html {{result}} <script>alert('Not harmless!')</script>"}]
    # plain_text results
    result += [_to_result("Result {}".format(i+1)) for i in range(maxRes-2)]

    return jsonify(result), 200

@api.route("/ping", methods=["GET"])
def ping():
    """
    Endpoint to check if the server is available
    """
    return jsonify({"msg": "Pong"}), 200
