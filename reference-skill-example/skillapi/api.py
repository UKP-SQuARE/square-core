from flask import Blueprint, jsonify, request

api = Blueprint("api", __name__)

def to_result(text):
    return {"type": "plain_text", "text": text}

@api.route("/query", methods=["POST"])
def query():
    question = request.json["question"]
    options = request.json["options"]

    maxRes = options["maxResults"]

    result = [{"type": "key_value", "key_values": [("Title", "The title"), ("Question", question)]}]
    result += [to_result("Result {}".format(i+1)) for i in range(maxRes-1)]
    return jsonify(result), 200

@api.route("/ping", methods=["GET"])
def ping():
    return jsonify({"msg": "Pong"}), 200
