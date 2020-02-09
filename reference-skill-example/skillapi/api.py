from flask import Blueprint, jsonify, request

api = Blueprint("api", __name__)


@api.route("/query", methods=["POST"])
def query():
    question = request.json["question"]
    options = request.json["options"]

    maxRes = options["maxResults"]

    result = ["Your question was: {}".format(question)]
    result += ["Result {}".format(i+1) for i in range(maxRes-1)]
    return jsonify(result), 200